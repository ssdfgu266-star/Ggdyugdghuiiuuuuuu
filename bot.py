import asyncio
import os
import google.generativeai as genai
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import User

API_ID = 20741854
API_HASH = 'd9079116154158a9dbb02d076706b5eb'
SESSION_STRING = "1BVtsOJgBu66JfnENZC97Q9MPhALEZaSexzoc0tNGoYoZmuM6C9KpfdMCVhleBNod0gCrODeOscf79ZdtvWU31HUxZWpeBYbIy2pCx6_OLSnCjXUSjXPGybIDto7zw9AFD0xBnUVXW2RWJJ_lh0dhOMHpFjymVLR26erIWI5zMiSgP0jsGMFshP-2KhwnsDTZGRs-gExbJJnNLV29YmUkNe_dJTTEpQPknnANABgX67r8JntndmLHXWnIBCLJoZcwa0gX17VLVi-83GpZzOxV4klwMtc3dGwsKQpqW4l8g6noX0vuJU_qgx4WcWVKhLhpRQkDkIbvBRdf0NvUrMT3sNcQVAgABuc= "
GEMINI_API_KEY = "AIzaSyC56cie27Og1OVf6Fpi3yiHSvMMur_mOLY"

with open(os.path.join(os.path.dirname(__file__), "prompt.txt"), "r", encoding="utf-8") as _f:
    SYSTEM_PROMPT = _f.read().strip()

genai.configure(api_key=GEMINI_API_KEY)

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

_user_chats: dict = {}
_welcomed: set = set()
_paused: set = set()


def _get_chat(user_id: int):
    if user_id not in _user_chats:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT,
        )
        _user_chats[user_id] = model.start_chat(history=[])
    return _user_chats[user_id]


def _resume(user_id: int):
    _paused.discard(user_id)
    _user_chats.pop(user_id, None)
    _welcomed.discard(user_id)


@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def _on_incoming(event):
    sender = await event.get_sender()
    if not isinstance(sender, User) or sender.bot:
        return

    uid = sender.id

    if uid in _paused:
        return

    if uid not in _welcomed:
        try:
            await client.send_file(event.chat_id, "welcome.gif")
            await asyncio.sleep(0.8)
        except Exception:
            pass
        _welcomed.add(uid)

    text = (event.message.text or "").strip()
    if not text:
        return

    chat = _get_chat(uid)

    try:
        async with client.action(event.chat_id, "typing"):
            response = await asyncio.to_thread(chat.send_message, text)
        await event.respond(response.text)
    except Exception as exc:
        print(f"[Gemini error] uid={uid}: {exc}")
        await event.respond("❌ Xin lỗi, đã xảy ra lỗi. Vui lòng thử lại sau.")


@client.on(events.NewMessage(outgoing=True, func=lambda e: e.is_private))
async def _on_outgoing(event):
    try:
        peer = await event.get_chat()
        if isinstance(peer, User) and not peer.bot:
            _paused.add(peer.id)
    except Exception:
        pass


@client.on(events.NewMessage(outgoing=True, pattern=r"(?i)^/resume$", func=lambda e: e.is_private))
async def _cmd_resume(event):
    try:
        peer = await event.get_chat()
        if isinstance(peer, User):
            _resume(peer.id)
            await event.delete()
    except Exception:
        pass


@client.on(events.NewMessage(outgoing=True, pattern=r"(?i)^/status$", func=lambda e: e.is_private))
async def _cmd_status(event):
    try:
        peer = await event.get_chat()
        if isinstance(peer, User):
            uid = peer.id
            st = "⏸ Tạm dừng (bạn đang hỗ trợ trực tiếp)" if uid in _paused else "🤖 AI đang hoạt động"
            await event.edit(f"[Bot Status]\n{st}\n\nGõ /resume để bật lại AI cho người này.")
    except Exception:
        pass


async def main():
    await client.connect()
    if not await client.is_user_authorized():
        print("❌ Session không hợp lệ hoặc đã hết hạn. Hãy cập nhật SESSION_STRING.")
        return
    me = await client.get_me()
    print(f"✅ Đã đăng nhập: {me.first_name} (@{me.username or 'N/A'})")
    print("🤖 Support bot đang chạy...")
    print("   /resume  — bật lại AI cho hội thoại đang chọn")
    print("   /status  — xem trạng thái AI của hội thoại đó")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
