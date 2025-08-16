from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
import hmac, hashlib, json
import httpx

from .config import settings
from .db import get_session
from .models import Message

router = APIRouter(prefix="/webhook", tags=["whatsapp"]) 

@router.get("/whatsapp", response_class=PlainTextResponse)
async def verify(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode == "subscribe" and token == settings.WABA_VERIFY_TOKEN:
        return PlainTextResponse(content=challenge, status_code=200)
    raise HTTPException(status_code=403, detail="Verification failed")

def _verify_signature(request_body: bytes, signature_header: str | None) -> bool:
    if not settings.META_APP_SECRET:
        return True
    if not signature_header:
        return False
    try:
        algo, hexdigest = signature_header.split("=", 1)
        if algo != "sha256":
            return False
    except Exception:
        return False
    mac = hmac.new(settings.META_APP_SECRET.encode(), msg=request_body, digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), hexdigest)

async def _send_text(to: str, body: str):
    url = f"https://graph.facebook.com/v21.0/{settings.WABA_PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body}
    }
    headers = {"Authorization": f"Bearer {settings.WABA_ACCESS_TOKEN}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        return r.json()

@router.post("/whatsapp")
async def receive(request: Request, session: AsyncSession = Depends(get_session)):
    raw = await request.body()
    if not _verify_signature(raw, request.headers.get("X-Hub-Signature-256")):
        raise HTTPException(status_code=403, detail="Invalid signature")

    data = json.loads(raw.decode("utf-8"))
    entries = data.get("entry", [])
    saved_ids = []

    for entry in entries:
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages = value.get("messages", [])
            metadata = value.get("metadata", {})
            wa_to = metadata.get("display_phone_number")

            for m in messages:
                wa_from = m.get("from")
                wa_type = m.get("type")
                wa_message_id = m.get("id")
                text_body = m.get("text", {}).get("body") if wa_type == "text" else None

                msg = Message(
                    wa_message_id=wa_message_id,
                    wa_from=wa_from,
                    wa_to=wa_to,
                    wa_type=wa_type,
                    direction="inbound",
                    text=text_body,
                )
                session.add(msg)
                await session.flush()
                saved_ids.append(msg.id)

                if wa_from and text_body:
                    reply = f"Recibido: {text_body}"
                    await _send_text(wa_from, reply)

    await session.commit()
    return {"status": "ok", "stored": saved_ids}
