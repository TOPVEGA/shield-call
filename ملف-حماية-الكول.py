
# الترخيص: @TopVeGa
# العلامة التجارية: VEGA & Logic
# حقوق الطبع والنشر: © 2015 - 2025


import asyncio
import html
import io
import os
import re
import subprocess
import tempfile
import time
from datetime import datetime, timedelta, timezone
from random import randint
from types import SimpleNamespace

from pyrogram import Client, filters, idle
from pyrogram.enums import ChatMemberStatus, ChatType, ParseMode
from pyrogram.errors import UserNotParticipant
from pyrogram.raw import functions, types
from pyrogram.types import (
    CallbackQuery,
    ChatPrivileges,
    InlineKeyboardButton as _IKB,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioQuality, MediaStream

try:
    from pyrogram.enums import ButtonStyle
except Exception:
    ButtonStyle = None
    
# الترخيص: @TopVeGa
# العلامة التجارية: VEGA & Logic
# حقوق الطبع والنشر: © 2015 - 2025

def vega_btn(text, style="primary", **kw):
    if ButtonStyle is not None:
        try:
            return _IKB(text, style=getattr(ButtonStyle, style.upper()), **kw)
        except Exception:
            pass
    return _IKB(text, **kw)

#لوجيك | Logic وجهتك البرمجية الأولى  بالوطن العربي
# شروحات - أكواد - وأحدث تقنيات برمجية - وحلول تقنية
# بواسطه: @TopVeGa

API_ID = 
API_HASH = ""
BOT_TOKEN = ""
SESSION_STRING = ""

#لوجيك | Logic وجهتك البرمجية الأولى  بالوطن العربي
# شروحات - أكواد - وأحدث تقنيات برمجية - وحلول تقنية
# بواسطه: @TopVeGa

OWNER_ID = 481322119
OWNER_USERNAME = "TopVeGa"
CHANNEL = "vegaone"

#لوجيك | Logic وجهتك البرمجية الأولى  بالوطن العربي
# شروحات - أكواد - وأحدث تقنيات برمجية - وحلول تقنية
# بواسطه: @TopVeGa

MONGO_USER = ""
MONGO_PASS = ""
MONGO_HOST = ""
MONGO_URL = ""
DB_NAME = "call_notify"

vega = Client(
    "topvega",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True,
)
kim = Client(
    "Logii3",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    in_memory=True,
)
topvega = PyTgCalls(kim)

Downloads = os.path.join(tempfile.gettempdir(), "Downloads.mp3")
QUICK_LEAVE_SECONDS = 1.0
KICK_QUICK_LEAVERS = True
UTC_OFFSET_HOURS = 2

BOT_USERNAME = ""
ENABLED: set = set()
CALL_CHAT: dict = {}
JOINED_AT: dict = {}
_started = False
_restored = False
_joining: set = set()

COL = None


def _bg(coro):
    try:
        asyncio.get_running_loop().create_task(coro)
    except RuntimeError:
        coro.close()


async def db_set(key: str, data: dict):
    if COL is None:
        return
    try:
        await COL.replace_one({"_id": key}, {"_id": key, **data}, upsert=True)
    except Exception as e:
        print("خطأ في قاعدة البيانات:", e)


async def db_add_user(uid: int):
    if COL is None:
        return
    try:
        await COL.update_one({"_id": "users"}, {"$addToSet": {"ids": uid}}, upsert=True)
    except Exception as e:
        print("خطأ في قاعدة البيانات:", e)


def _save():
    _bg(db_set("enabled", {"chats": list(ENABLED)}))


async def init_db():
    global COL
    from urllib.parse import quote_plus

    url = MONGO_URL
    if not url and MONGO_USER and MONGO_PASS and MONGO_HOST:
        host = MONGO_HOST.strip().replace("mongodb+srv://", "").strip("/")
        url = (
            f"mongodb+srv://{quote_plus(MONGO_USER)}:{quote_plus(MONGO_PASS)}"
            f"@{host}/?retryWrites=true&w=majority"
        )
    if not url:
        print("بيانات قاعدة البيانات فاضية")
        return
    from pymongo import AsyncMongoClient

    COL = AsyncMongoClient(url)[DB_NAME]["data"]
    await COL.find_one({"_id": "config"})


async def load_all():
    if COL is None:
        return
    conf = await COL.find_one({"_id": "config"}) or {}
    for k in CONFIG:
        if k in conf:
            CONFIG[k] = conf[k]
    ENABLED.update((await COL.find_one({"_id": "enabled"}) or {}).get("chats", []))
    USERS.update((await COL.find_one({"_id": "users"}) or {}).get("ids", []))
    CHATS.update((await COL.find_one({"_id": "chats"}) or {}).get("map", {}))


def _make_silence():
    if os.path.exists(Downloads):
        return
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                "-t", "30", "-q:a", "9", Downloads,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


_make_silence()


async def ensure_started():
    global _started
    if _started:
        return
    try:
        await topvega.start()
    except Exception:
        pass
    _started = True


async def has_right(chat_id: int, user_id: int, right: str) -> bool:
    try:
        m = await vega.get_chat_member(chat_id, user_id)
    except Exception:
        return False
    if m.status == ChatMemberStatus.OWNER:
        return True
    if m.status == ChatMemberStatus.ADMINISTRATOR:
        if right == "any":
            return True
        return bool(m.privileges and getattr(m.privileges, right, False))
    return False


USER_HASH: dict = {}


async def ensure_peer(chat_id: int) -> bool:
    try:
        await kim.resolve_peer(chat_id)
        return True
    except Exception:
        pass
    try:
        async for d in kim.get_dialogs():
            if d.chat and d.chat.id == chat_id:
                break
        await kim.resolve_peer(chat_id)
        return True
    except Exception:
        return False


async def bot_know_assistant(chat_id: int, me) -> None:
    try:
        await vega.resolve_peer(me.id)
        return
    except Exception:
        pass
    if me.username:
        try:
            await vega.get_users(me.username)
            await vega.resolve_peer(me.id)
            return
        except Exception:
            pass
    try:
        m = await kim.send_message(chat_id, "اختبار")
        await asyncio.sleep(2)
        await m.delete()
    except Exception:
        pass


async def is_admin_msg(message: Message) -> bool:
    if message.chat.type == ChatType.CHANNEL:
        return True
    if message.sender_chat and message.sender_chat.id == message.chat.id:
        return True
    return bool(
        message.from_user
        and await has_right(message.chat.id, message.from_user.id, "any")
    )


async def get_input_call(chat_id: int):
    if not await ensure_peer(chat_id):
        raise RuntimeError("الحساب المساعد لا يرى المجموعة")
    peer = await kim.resolve_peer(chat_id)
    if isinstance(peer, types.InputPeerChannel):
        full = await kim.invoke(
            functions.channels.GetFullChannel(
                channel=types.InputChannel(
                    channel_id=peer.channel_id, access_hash=peer.access_hash
                )
            )
        )
    else:
        full = await kim.invoke(
            functions.messages.GetFullChat(chat_id=peer.chat_id)
        )
    call = getattr(full.full_chat, "call", None)
    if call:
        CALL_CHAT[call.id] = chat_id
    return call


async def ensure_call(chat_id: int):
    call = await get_input_call(chat_id)
    if call:
        return call
    peer = await kim.resolve_peer(chat_id)
    await kim.invoke(
        functions.phone.CreateGroupCall(peer=peer, random_id=randint(1, 2**31 - 1))
    )
    await asyncio.sleep(1)
    return await get_input_call(chat_id)


async def join_call(chat_id: int):
    await ensure_started()
    _joining.add(chat_id)
    try:
        await topvega.play(
            chat_id,
            MediaStream(
                Downloads,
                audio_parameters=AudioQuality.LOW,
                video_flags=MediaStream.Flags.IGNORE,
                ffmpeg_parameters="-stream_loop -1",
            ),
        )
    finally:
        await asyncio.sleep(2)
        _joining.discard(chat_id)


async def safe_send(chat_id, text, **kw):
    try:
        return await vega.send_message(chat_id, text, **kw)
    except Exception:
        plain = re.sub(r'<a href="tg://user\?id=\d+">(.*?)</a>', r"<b>\1</b>", text)
        if plain == text:
            raise
        return await vega.send_message(chat_id, plain, **kw)


def clock_str() -> str:
    n = datetime.now(timezone(timedelta(hours=UTC_OFFSET_HOURS)))
    return n.strftime("%I:%M:%S.") + f"{n.microsecond // 1000:03d} " + (
        "صباحا" if n.hour < 12 else "مساء"
    )


def now_str() -> str:
    tz = timezone(timedelta(hours=UTC_OFFSET_HOURS))
    n = datetime.now(tz)
    ampm = "صباحا" if n.hour < 12 else "مساء"
    return n.strftime("%Y-%m-%d  %I:%M:%S ") + ampm


async def kick_user(chat_id: int, user_id: int) -> bool:
    if is_dev(user_id):
        return False
    try:
        m = await vega.get_chat_member(chat_id, user_id)
        if m.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR):
            return False
    except Exception:
        pass
    try:
        await vega.ban_chat_member(chat_id, user_id)
        await asyncio.sleep(0.5)
        await vega.unban_chat_member(chat_id, user_id)
        return True
    except Exception:
        return False


async def member_state(chat_id: int, user_id: int) -> str:
    if is_dev(user_id):
        return "admin"
    try:
        m = await vega.get_chat_member(chat_id, user_id)
    except UserNotParticipant:
        return "outside"
    except Exception:
        return "member"
    if m.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR):
        return "admin"
    if m.status in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED):
        return "outside"
    return "member"


async def get_user_info(user_id: int, users=None):
    try:
        return await kim.get_users(user_id)
    except Exception:
        pass
    raw = (users or {}).get(user_id)
    return SimpleNamespace(
        id=user_id,
        first_name=getattr(raw, "first_name", None),
        last_name=getattr(raw, "last_name", None),
        username=getattr(raw, "username", None),
        is_bot=bool(getattr(raw, "bot", False)),
    )


def mention(user) -> str:
    name = html.escape(
        (user.first_name or "") + (" " + user.last_name if user.last_name else "")
    ).strip() or "مجهول"
    if getattr(user, "username", None):
        return f'<a href="https://t.me/{user.username}">{name}</a>'
    return f'<a href="tg://user?id={user.id}">{name}</a>'


def info_block(user) -> str:
    username = f"@{user.username}" if user.username else "لا يوجد"
    return (
        f"الاسم: {mention(user)}\n"
        f"اليوزر: {username}\n"
        f"الايدي: <code>{user.id}</code>"
    )


CHAT_IS_CHANNEL: dict = {}


async def chat_is_channel(chat_id: int) -> bool:
    if chat_id in CHAT_IS_CHANNEL:
        return CHAT_IS_CHANNEL[chat_id]
    try:
        chat = await vega.get_chat(chat_id)
        CHAT_IS_CHANNEL[chat_id] = chat.type == ChatType.CHANNEL
    except Exception:
        return False
    return CHAT_IS_CHANNEL[chat_id]


def buttons(chat_id: int, user_id: int, with_mute: bool = True, channel: bool = False):
    ban_text = "حظره من القناة" if channel else "حظره من المجموعة"
    rows = [
        [vega_btn(ban_text, callback_data=f"cn_ban_{chat_id}_{user_id}")]
    ]
    if with_mute:
        if not channel:
            rows.append(
                [
                    vega_btn(
                        "كتمه في المكالمة",
                        callback_data=f"cn_mute_{chat_id}_{user_id}",
                    )
                ]
            )
        rows.append(
            [
                vega_btn(
                    "السماح له بالتحدث",
                    callback_data=f"cn_unmute_{chat_id}_{user_id}",
                )
            ]
        )
    return InlineKeyboardMarkup(rows)


@vega.on_message(
    (filters.group | filters.channel) & filters.regex(r"^\s*تفعيل\s+(اشعارات|إشعارات)\s+الكول\s*$")
)
async def enable_call_notify(_, message: Message):
    chat_id = message.chat.id
    if not await is_admin_msg(message):
        return await message.reply_text("هذا الامر للمشرفين فقط.")

    if not allowed(chat_id):
        return await message.reply_text("الوضع المجاني معطل حاليا.")

    status = await message.reply_text("جار تفعيل اشعارات المكالمة...")

    try:
        me = await kim.get_me()

        in_chat = False
        if await ensure_peer(chat_id):
            try:
                m = await kim.get_chat_member(chat_id, "me")
                in_chat = m.status not in (
                    ChatMemberStatus.LEFT,
                    ChatMemberStatus.BANNED,
                )
            except Exception:
                in_chat = False

        if not in_chat:
            await bot_know_assistant(chat_id, me)
            try:
                await vega.unban_chat_member(chat_id, me.id)
            except Exception:
                pass
            link = await vega.export_chat_invite_link(chat_id)
            try:
                await kim.join_chat(link)
            except Exception as e:
                if "already" not in str(e).lower():
                    raise
            await asyncio.sleep(1.5)
            await ensure_peer(chat_id)

        await bot_know_assistant(chat_id, me)
        await vega.promote_chat_member(
            chat_id,
            me.id,
            privileges=ChatPrivileges(
                can_manage_chat=True,
                can_manage_video_chats=True,
                can_restrict_members=True,
                can_invite_users=True,
                can_delete_messages=True,
            ),
        )
        await asyncio.sleep(1)

        await ensure_call(chat_id)
        await join_call(chat_id)

        ENABLED.add(chat_id)
        _save()
        await status.edit_text(
            "تم تفعيل اشعارات المكالمة.\n"
            "الحساب المساعد انضم وتمت ترقيته مشرفا ودخل المكالمة وسيبقى فيها."
        )
    except Exception as e:
        await status.edit_text(
            "حدث خطأ اثناء التفعيل.\n"
            "تأكد ان البوت مشرف ولديه صلاحية اضافة مشرفين ودعوة مستخدمين.\n\n"
            f"<code>{html.escape(str(e))}</code>",
            parse_mode=ParseMode.HTML,
        )


@vega.on_message(
    (filters.group | filters.channel) & filters.regex(r"^\s*تعطيل\s+(اشعارات|إشعارات)\s+الكول\s*$")
)
async def disable_call_notify(_, message: Message):
    chat_id = message.chat.id
    if not await is_admin_msg(message):
        return await message.reply_text("هذا الامر للمشرفين فقط.")
    ENABLED.discard(chat_id)
    _save()
    try:
        await topvega.leave_call(chat_id)
    except Exception:
        pass
    await message.reply_text("تم تعطيل اشعارات المكالمة.")


async def _restore():
    for chat_id in list(ENABLED):
        if not allowed(chat_id):
            continue
        try:
            if await get_input_call(chat_id):
                await join_call(chat_id)
        except Exception:
            pass


def _chat_id_from_group_call_update(update):
    cid = getattr(update, "chat_id", None)
    if cid:
        return -1000000000000 - cid
    peer = getattr(update, "peer", None)
    if isinstance(peer, types.PeerChannel):
        return -1000000000000 - peer.channel_id
    if isinstance(peer, types.PeerChat):
        return -peer.chat_id
    return None


@kim.on_raw_update(group=-7)
async def call_watcher(client, update, users, chats):
    global _restored
    if not _restored:
        _restored = True
        asyncio.create_task(_restore())

    if isinstance(update, types.UpdateGroupCall):
        call = update.call
        if isinstance(call, types.GroupCallDiscarded):
            CALL_CHAT.pop(call.id, None)
            return
        chat_id = _chat_id_from_group_call_update(update)
        if chat_id and chat_id in ENABLED and allowed(chat_id):
            new_call = call.id not in CALL_CHAT
            CALL_CHAT[call.id] = chat_id
            if new_call and chat_id not in _joining:
                try:
                    await join_call(chat_id)
                except Exception:
                    pass
        return

    if not isinstance(update, types.UpdateGroupCallParticipants):
        return

    chat_id = CALL_CHAT.get(update.call.id)
    if not chat_id or chat_id not in ENABLED or not allowed(chat_id):
        return

    me = await kim.get_me()
    is_ch = await chat_is_channel(chat_id)

    for p in update.participants:
        if not isinstance(p.peer, types.PeerUser):
            continue
        user_id = p.peer.user_id
        if user_id == me.id:
            continue
        key = (update.call.id, user_id)
        _raw = users.get(user_id)
        if _raw is not None and getattr(_raw, "access_hash", None):
            USER_HASH[user_id] = _raw.access_hash

        try:
            if p.left:
                rec = JOINED_AT.pop(key, None)
                if rec is None:
                    continue
                joined, state, joined_clock = rec
                elapsed = time.monotonic() - joined
                if elapsed < QUICK_LEAVE_SECONDS:
                    user = await get_user_info(user_id, users)
                    if user.is_bot:
                        continue
                    kicked = False
                    if KICK_QUICK_LEAVERS and state == "member":
                        kicked = await kick_user(chat_id, user_id)
                    title = "شخص دخل وخرج من المكالمة في اقل من ثانية"
                    if state == "outside":
                        title = "شخص من خارج المجموعة دخل وخرج من المكالمة في اقل من ثانية"
                    await safe_send(
                        chat_id,
                        title
                        + "\n\n"
                        + info_block(user)
                        + f"\nوقت الدخول: {joined_clock}"
                        + f"\nوقت الخروج: {clock_str()}"
                        + f"\nالمدة: {elapsed:.2f} ثانية"
                        + ("\nتم طرده من المجموعة" if kicked else ""),
                        parse_mode=ParseMode.HTML,
                        reply_markup=buttons(chat_id, user_id, with_mute=False, channel=is_ch),
                    )
            elif p.just_joined:
                state = await member_state(chat_id, user_id)
                if state == "admin":
                    continue
                JOINED_AT[key] = (time.monotonic(), state, clock_str())
                user = await get_user_info(user_id, users)
                if user.is_bot:
                    JOINED_AT.pop(key, None)
                    continue
                if state == "outside":
                    title = "شخص من خارج المجموعة انضم للمكالمة الصوتية"
                else:
                    title = "شخص انضم للمكالمة الصوتية"
                await safe_send(
                    chat_id,
                    title
                    + "\n\n"
                    + info_block(user)
                    + f"\nالوقت: {now_str()}",
                    parse_mode=ParseMode.HTML,
                    reply_markup=buttons(chat_id, user_id, channel=is_ch),
                )
        except Exception:
            pass


@vega.on_callback_query(filters.regex(r"^cn_(ban|mute|unmute)_(-?\d+)_(\d+)$"))
async def call_notify_buttons(_, cq: CallbackQuery):
    action, chat_id, user_id = (
        cq.matches[0].group(1),
        int(cq.matches[0].group(2)),
        int(cq.matches[0].group(3)),
    )

    if action == "ban":
        if not await has_right(chat_id, cq.from_user.id, "can_restrict_members"):
            return await cq.answer("ليس لديك صلاحية الحظر.", show_alert=True)
        try:
            await vega.ban_chat_member(chat_id, user_id)
            await cq.answer("تم حظره من المجموعة.", show_alert=True)
            await cq.edit_message_reply_markup(None)
        except Exception as e:
            await cq.answer(f"فشل الحظر: {e}"[:190], show_alert=True)
        return

    muting = action == "mute"
    if not await has_right(chat_id, cq.from_user.id, "can_manage_video_chats"):
        return await cq.answer("ليس لديك صلاحية ادارة المحادثات الصوتية.", show_alert=True)
    try:
        call = await get_input_call(chat_id)
        if not call:
            return await cq.answer("لا توجد مكالمة نشطة.", show_alert=True)
        try:
            peer = await kim.resolve_peer(user_id)
        except Exception:
            if user_id not in USER_HASH:
                raise
            peer = types.InputPeerUser(user_id=user_id, access_hash=USER_HASH[user_id])
        await kim.invoke(
            functions.phone.EditGroupCallParticipant(
                call=call, participant=peer, muted=muting
            )
        )
        await cq.answer(
            "تم كتمه في المكالمة." if muting else "تم السماح له بالتحدث.",
            show_alert=True,
        )
    except Exception as e:
        what = "الكتم" if muting else "السماح بالتحدث"
        await cq.answer(f"فشل {what}: {e}"[:190], show_alert=True)


CONFIG = {
    "devs": [],
    "banned_groups": [],
    "banned_users": [],
    "paid_groups": [],
    "free_mode": True,
    "contact": False,
}


def _save_config():
    _bg(db_set("config", dict(CONFIG)))


def is_owner(uid: int) -> bool:
    return bool(OWNER_ID) and uid == OWNER_ID


def is_dev(uid: int) -> bool:
    return is_owner(uid) or uid in CONFIG["devs"]


def allowed(chat_id: int) -> bool:
    if chat_id in CONFIG["banned_groups"]:
        return False
    return CONFIG["free_mode"] or chat_id in CONFIG["paid_groups"]


async def _f_dev(_, __, update):
    u = getattr(update, "from_user", None)
    return bool(u and is_dev(u.id))


async def _f_banned_user(_, __, update):
    u = getattr(update, "from_user", None)
    return bool(u and u.id in CONFIG["banned_users"] and not is_dev(u.id))


async def _f_banned_group(_, __, message):
    return bool(message.chat and message.chat.id in CONFIG["banned_groups"])


dev_filter = filters.create(_f_dev)
banned_user_filter = filters.create(_f_banned_user)
banned_group_filter = filters.create(_f_banned_group)


@vega.on_message(banned_user_filter, group=-10)
async def block_banned_user_msg(_, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text("انت محظور من استخدام البوت.")
    message.stop_propagation()


@vega.on_callback_query(banned_user_filter, group=-10)
async def block_banned_user_cb(_, cq: CallbackQuery):
    await cq.answer("انت محظور من استخدام البوت.", show_alert=True)
    cq.stop_propagation()


@vega.on_message((filters.group | filters.channel) & banned_group_filter, group=-11)
async def leave_banned_group(_, message: Message):
    try:
        await vega.leave_chat(message.chat.id)
    except Exception:
        pass
    message.stop_propagation()


@vega.on_chat_member_updated(group=-11)
async def joined_banned_group(_, update):
    m = update.new_chat_member
    if m and m.user and m.user.is_self and update.chat.id in CONFIG["banned_groups"]:
        try:
            await vega.leave_chat(update.chat.id)
        except Exception:
            pass


BTN_ADD_DEV = "رفع مطور"
BTN_DEL_DEV = "تنزيل مطور"
BTN_BAN_GROUP = "حظر مجموعة"
BTN_UNBAN_GROUP = "الغاء حظر مجموعة"
BTN_BAN_USER = "حظر مستخدم"
BTN_UNBAN_USER = "الغاء حظر مستخدم"
BTN_FREE_ON = "تفعيل الوضع المجاني"
BTN_FREE_OFF = "تعطيل الوضع المجاني"
BTN_PAID = "قسم المدفوع"
BTN_CONTACT_ON = "تفعيل التواصل"
BTN_CONTACT_OFF = "تعطيل التواصل"
BTN_STATS = "الاحصائيات"


def RedKB(text: str):
    if ButtonStyle is not None:
        try:
            return KeyboardButton(text, style=ButtonStyle.DANGER)
        except Exception:
            pass
    return KeyboardButton(text)


PANEL_KB = ReplyKeyboardMarkup(
    [
        [RedKB(BTN_ADD_DEV), RedKB(BTN_DEL_DEV)],
        [RedKB(BTN_BAN_GROUP), RedKB(BTN_UNBAN_GROUP)],
        [RedKB(BTN_BAN_USER), RedKB(BTN_UNBAN_USER)],
        [RedKB(BTN_FREE_ON), RedKB(BTN_FREE_OFF)],
        [RedKB(BTN_CONTACT_ON), RedKB(BTN_CONTACT_OFF)],
        [RedKB(BTN_STATS), RedKB(BTN_PAID)],
    ],
    resize_keyboard=True,
)

PAID_KB = InlineKeyboardMarkup(
    [
        [vega_btn("اضافة مجموعة مدفوعة", callback_data="cn_paid_add", style="danger")],
        [vega_btn("ازالة مجموعة مدفوعة", callback_data="cn_paid_del", style="danger")],
        [vega_btn("المجموعات المدفوعة", callback_data="cn_paid_list", style="danger")],
    ]
)

CANCEL_NOTE = "\n\n(للالغاء اكتب /start)"
ASK_TEXT = {
    "add_dev": "ارسل يوزر او ايدي الشخص المطلوب ترقيته مطورا:",
    "del_dev": "ارسل يوزر او ايدي المطور المطلوب تنزيله:",
    "ban_group": "ارسل يوزر المجموعة او ايديها لحظرها:",
    "unban_group": "ارسل يوزر المجموعة او ايديها لالغاء حظرها:",
    "ban_user": "ارسل يوزر او ايدي المستخدم لحظره من البوت:",
    "unban_user": "ارسل يوزر او ايدي المستخدم لالغاء حظره:",
    "paid_add": "ارسل يوزر المجموعة او ايديها لاضافتها للمدفوع:",
    "paid_del": "ارسل يوزر المجموعة او ايديها لازالتها من المدفوع:",
}
BUTTON_ACTIONS = {
    BTN_ADD_DEV: "add_dev",
    BTN_DEL_DEV: "del_dev",
    BTN_BAN_GROUP: "ban_group",
    BTN_UNBAN_GROUP: "unban_group",
    BTN_BAN_USER: "ban_user",
    BTN_UNBAN_USER: "unban_user",
}
STATE: dict = {}


def status_text() -> str:
    mode = "مفعل" if CONFIG["free_mode"] else "معطل"
    contact = "مفعل" if CONFIG.get("contact") else "معطل"
    return f"الوضع المجاني: <b>{mode}</b>\nالتواصل: <b>{contact}</b>"


def _clean(t: str) -> str:
    t = t.strip()
    for pre in ("https://t.me/", "http://t.me/", "t.me/", "@"):
        if t.lower().startswith(pre):
            t = t[len(pre):]
    return t.strip("/ ")


async def _resolve_user(t: str):
    t = _clean(t)
    if t.lstrip("-").isdigit():
        uid = int(t)
        try:
            u = await vega.get_users(uid)
            return u.id, mention(u)
        except Exception:
            return uid, f"<code>{uid}</code>"
    u = await vega.get_users(t)
    return u.id, mention(u)


async def _resolve_chat(t: str):
    t = _clean(t)
    key = int(t) if t.lstrip("-").isdigit() else t
    try:
        c = await vega.get_chat(key)
        return c.id, html.escape(c.title or str(c.id))
    except Exception:
        if isinstance(key, int):
            return key, f"<code>{key}</code>"
        raise


async def _kick_from_chat(chat_id: int):
    ENABLED.discard(chat_id)
    _save()
    try:
        await topvega.leave_call(chat_id)
    except Exception:
        pass
    try:
        await kim.leave_chat(chat_id)
    except Exception:
        pass
    try:
        await vega.leave_chat(chat_id)
    except Exception:
        pass


async def _set_free(on: bool):
    CONFIG["free_mode"] = on
    _save_config()
    if on:
        asyncio.create_task(_restore())
    else:
        for cid in list(ENABLED):
            if cid not in CONFIG["paid_groups"]:
                try:
                    await topvega.leave_call(cid)
                except Exception:
                    pass


async def _process(uid: int, action: str, text: str) -> str:
    if action in ("add_dev", "del_dev"):
        if not is_owner(uid):
            return "رفع وتنزيل المطورين للمطور الاساسي فقط."
        tid, name = await _resolve_user(text)
        if action == "add_dev":
            if is_dev(tid):
                return f"{name} مطور بالفعل."
            CONFIG["devs"].append(tid)
            _save_config()
            return f"تم رفع {name} مطورا."
        if tid not in CONFIG["devs"]:
            return f"{name} ليس مطورا."
        CONFIG["devs"].remove(tid)
        _save_config()
        return f"تم تنزيل {name} من المطورين."

    if action in ("ban_user", "unban_user"):
        tid, name = await _resolve_user(text)
        if action == "ban_user":
            if is_dev(tid):
                return "لا يمكن حظر مطور."
            if tid in CONFIG["banned_users"]:
                return f"{name} محظور بالفعل."
            CONFIG["banned_users"].append(tid)
            _save_config()
            return f"تم حظر {name} من استخدام البوت."
        if tid not in CONFIG["banned_users"]:
            return f"{name} غير محظور."
        CONFIG["banned_users"].remove(tid)
        _save_config()
        return f"تم الغاء حظر {name}."

    cid, title = await _resolve_chat(text)

    if action == "ban_group":
        if cid in CONFIG["banned_groups"]:
            return f"المجموعة {title} محظورة بالفعل."
        CONFIG["banned_groups"].append(cid)
        if cid in CONFIG["paid_groups"]:
            CONFIG["paid_groups"].remove(cid)
        _save_config()
        await _kick_from_chat(cid)
        return f"تم حظر المجموعة {title} وخروج البوت منها."

    if action == "unban_group":
        if cid not in CONFIG["banned_groups"]:
            return f"المجموعة {title} غير محظورة."
        CONFIG["banned_groups"].remove(cid)
        _save_config()
        return f"تم الغاء حظر المجموعة {title}."

    if action == "paid_add":
        if cid in CONFIG["banned_groups"]:
            return f"المجموعة {title} محظورة، الغ حظرها اولا."
        if cid in CONFIG["paid_groups"]:
            return f"المجموعة {title} مدفوعة بالفعل."
        CONFIG["paid_groups"].append(cid)
        _save_config()
        asyncio.create_task(_restore())
        return (
            f"تم اضافة المجموعة {title} للمدفوع.\n"
            "البوت سيعمل فيها حتى لو الوضع المجاني معطل. "
            "يمكن لمشرف المجموعة كتابة: تفعيل اشعارات الكول"
        )

    if action == "paid_del":
        if cid not in CONFIG["paid_groups"]:
            return f"المجموعة {title} ليست في المدفوع."
        CONFIG["paid_groups"].remove(cid)
        _save_config()
        if not CONFIG["free_mode"]:
            try:
                await topvega.leave_call(cid)
            except Exception:
                pass
        return f"تم ازالة المجموعة {title} من المدفوع."

    return "اجراء غير معروف."


@vega.on_message(filters.command("start") & filters.private & dev_filter)
async def dev_start(_, message: Message):
    register_user(message.from_user.id)
    STATE.pop(message.from_user.id, None)
    await message.reply_text(
        "مرحبا بك يا مطور\n\n" + status_text(),
        parse_mode=ParseMode.HTML,
        reply_markup=PANEL_KB,
    )


@vega.on_message(
    filters.private & dev_filter & filters.text & ~filters.command(["start"])
)
async def dev_panel(_, message: Message):
    uid = message.from_user.id
    text = message.text.strip()

    if text in BUTTON_ACTIONS:
        action = BUTTON_ACTIONS[text]
        if action in ("add_dev", "del_dev") and not is_owner(uid):
            return await message.reply_text("رفع وتنزيل المطورين للمطور الاساسي فقط.")
        STATE[uid] = action
        return await message.reply_text(ASK_TEXT[action] + CANCEL_NOTE)

    if text == BTN_FREE_ON:
        STATE.pop(uid, None)
        await _set_free(True)
        return await message.reply_text(
            "تم تفعيل الوضع المجاني.\n" + status_text(), parse_mode=ParseMode.HTML
        )

    if text == BTN_FREE_OFF:
        STATE.pop(uid, None)
        await _set_free(False)
        return await message.reply_text(
            "تم تعطيل الوضع المجاني، توقف البوت في كل المجموعات ما عدا المدفوعة.\n"
            + status_text(),
            parse_mode=ParseMode.HTML,
        )

    if text == BTN_CONTACT_ON:
        STATE.pop(uid, None)
        CONFIG["contact"] = True
        _save_config()
        return await message.reply_text(
            "تم تفعيل التواصل.\n"
            "اي مستخدم يرسل /start او يراسل البوت ستصل رسالته اليك، "
            "ويمكنك الرد عليه بالرد على رسالته.\n\n" + status_text(),
            parse_mode=ParseMode.HTML,
        )

    if text == BTN_CONTACT_OFF:
        STATE.pop(uid, None)
        CONFIG["contact"] = False
        _save_config()
        return await message.reply_text(
            "تم تعطيل التواصل.\n\n" + status_text(), parse_mode=ParseMode.HTML
        )

    if text == BTN_STATS:
        STATE.pop(uid, None)
        return await message.reply_text(stats_text(), parse_mode=ParseMode.HTML)

    if text == BTN_PAID:
        STATE.pop(uid, None)
        return await message.reply_text(
            "قسم المدفوع", parse_mode=ParseMode.HTML, reply_markup=PAID_KB
        )

    action = STATE.get(uid)
    if not action:
        return
    try:
        result = await _process(uid, action, text)
    except Exception:
        return await message.reply_text(
            "لم اتمكن من ايجاد اليوزر او الايدي، تأكد وارسله مرة اخرى." + CANCEL_NOTE
        )
    STATE.pop(uid, None)
    await message.reply_text(result, parse_mode=ParseMode.HTML)


@vega.on_callback_query(filters.regex(r"^cn_paid_(add|del|list)$") & dev_filter)
async def paid_buttons(_, cq: CallbackQuery):
    which = cq.matches[0].group(1)
    uid = cq.from_user.id

    if which == "list":
        if not CONFIG["paid_groups"]:
            return await cq.answer("لا توجد مجموعات مدفوعة.", show_alert=True)
        lines = []
        for cid in CONFIG["paid_groups"]:
            try:
                c = await vega.get_chat(cid)
                lines.append(f"{html.escape(c.title or '')} ({cid})")
            except Exception:
                lines.append(f"{cid}")
        await cq.message.reply_text(
            "المجموعات المدفوعة:\n\n" + "\n".join(lines),
            parse_mode=ParseMode.HTML,
        )
        return await cq.answer()

    action = "paid_add" if which == "add" else "paid_del"
    STATE[uid] = action
    await cq.message.reply_text(ASK_TEXT[action] + CANCEL_NOTE)
    await cq.answer()


REPLY_MAP: dict = {}


def _remember(OWNER_ID: int, msg_id: int, user_id: int):
    REPLY_MAP[(OWNER_ID, msg_id)] = user_id
    if len(REPLY_MAP) > 3000:
        for k in list(REPLY_MAP)[:1000]:
            REPLY_MAP.pop(k, None)


def OWNER_IDs() -> set:
    ids = set(CONFIG["devs"])
    if OWNER_ID:
        ids.add(OWNER_ID)
    return ids


async def notify_devs(user, title: str, msg: Message = None):
    for did in OWNER_IDs():
        try:
            head = await safe_send(
                did,
                f"{title}\n\n{info_block(user)}\nالوقت: {now_str()}",
                parse_mode=ParseMode.HTML,
            )
            _remember(did, head.id, user.id)
            if msg is not None:
                copied = await msg.copy(did)
                _remember(did, copied.id, user.id)
        except Exception:
            pass


@vega.on_message(
    filters.private & ~dev_filter & ~filters.command(["start"]) & ~filters.service
)
async def user_to_dev(_, message: Message):
    if not CONFIG.get("contact") or not message.from_user:
        return
    await notify_devs(message.from_user, "رسالة جديدة من مستخدم", message)
    try:
        await message.reply_text("تم ارسال رسالتك للمطور.")
    except Exception:
        pass


@vega.on_message(filters.private & dev_filter & filters.reply, group=-2)
async def dev_reply_to_user(_, message: Message):
    key = (message.chat.id, message.reply_to_message_id)
    user_id = REPLY_MAP.get(key)
    if not user_id:
        return
    try:
        await message.copy(user_id)
        await message.reply_text("تم ارسال ردك للمستخدم.")
    except Exception:
        await message.reply_text("لم اتمكن من الارسال للمستخدم، ربما حظر البوت.")
    message.stop_propagation()


USERS: set = set()
CHATS: dict = {}


def _save_chats():
    _bg(db_set("chats", {"map": dict(CHATS)}))


def register_user(uid: int):
    if uid not in USERS:
        USERS.add(uid)
        _bg(db_add_user(uid))


def register_chat(chat) -> None:
    kind = "channel" if chat.type == ChatType.CHANNEL else "group"
    rec = {"kind": kind, "title": chat.title or ""}
    key = str(chat.id)
    if CHATS.get(key) != rec:
        CHATS[key] = rec
        _save_chats()


def unregister_chat(chat_id: int):
    if CHATS.pop(str(chat_id), None) is not None:
        _save_chats()


def stats_text() -> str:
    groups = sum(1 for v in CHATS.values() if v.get("kind") == "group")
    channels = sum(1 for v in CHATS.values() if v.get("kind") == "channel")
    return (
        "احصائيات البوت\n\n"
        f"المستخدمون الذين ارسلوا /start: <b>{len(USERS)}</b>\n"
        f"المجموعات: <b>{groups}</b>\n"
        f"القنوات: <b>{channels}</b>\n\n"
        f"اشعارات المكالمة مفعلة في: <b>{len(ENABLED)}</b>\n"
        f"المدفوعة: <b>{len(CONFIG['paid_groups'])}</b>"
    )


@vega.on_message(filters.group | filters.channel, group=-12)
async def track_chats(_, message: Message):
    if message.chat.id in CONFIG["banned_groups"]:
        return
    register_chat(message.chat)


@vega.on_chat_member_updated(group=-9)
async def bot_added_or_removed(_, update):
    new = update.new_chat_member
    old = update.old_chat_member
    if not (new and new.user and new.user.is_self):
        return
    chat = update.chat
    if chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL):
        return

    if new.status in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED):
        unregister_chat(chat.id)
        return
    if chat.id in CONFIG["banned_groups"]:
        return

    was_in = bool(old and old.status not in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED))
    register_chat(chat)
    if was_in:
        return

    is_channel = chat.type == ChatType.CHANNEL
    kind = "قناة" if is_channel else "مجموعة"

    link = f"https://t.me/{chat.username}" if chat.username else None
    if not link:
        try:
            link = await vega.export_chat_invite_link(chat.id)
        except Exception:
            link = None

    try:
        count = await vega.get_chat_members_count(chat.id)
    except Exception:
        count = "غير معروف"

    adder = "غير معروف"
    if update.from_user:
        adder = mention(update.from_user)

    text = (
        f"تمت اضافة البوت في {kind}\n\n"
        f"الاسم: <b>{html.escape(chat.title or '')}</b>\n"
        f"الايدي: <code>{chat.id}</code>\n"
        f"اليوزر: {('@' + chat.username) if chat.username else 'خاص'}\n"
        f"عدد الاعضاء: <b>{count}</b>\n"
        f"الذي اضافه: {adder}\n"
        f"الوقت: {now_str()}"
    )
    markup = None
    if link:
        markup = InlineKeyboardMarkup(
            [[vega_btn(f"فتح {kind}", url=link)]]
        )
    for did in OWNER_IDs():
        try:
            await safe_send(
                did, text, parse_mode=ParseMode.HTML, reply_markup=markup,
                disable_web_page_preview=True,
            )
        except Exception:
            pass


DEV_CARD = {"ts": 0.0, "photo": None, "text": None, "name": None}


def _bio(data: bytes):
    b = io.BytesIO(data)
    b.name = "photo.jpg"
    return b


async def get_dev_card():
    if DEV_CARD["text"] and time.time() - DEV_CARD["ts"] < 600:
        return DEV_CARD
    key = OWNER_USERNAME.lstrip("@") if OWNER_USERNAME else OWNER_ID
    chat = await vega.get_chat(key)

    name = html.escape(
        ((chat.first_name or "") + (" " + chat.last_name if chat.last_name else "")).strip()
        or "المطور"
    )
    username = f"@{chat.username}" if chat.username else "لا يوجد"
    bio = html.escape(chat.bio) if getattr(chat, "bio", None) else "لا يوجد"

    photo = None
    if chat.photo:
        try:
            photo = (
                await vega.download_media(chat.photo.big_file_id, in_memory=True)
            ).getvalue()
        except Exception:
            photo = None

    DEV_CARD.update(
        ts=time.time(),
        photo=photo,
        name=name,
        text=(
            "مطور البوت\n\n"
            f"الاسم: <b>{name}</b>\n"
            f"اليوزر: {username}\n"
            f"الايدي: <code>{chat.id}</code>\n"
            f"البايو: {bio}"
        ),
    )
    return DEV_CARD


@vega.on_message(
    filters.group & filters.regex(r"^\s*(المطور|مطور البوت)\s*$"), group=1
)
async def dev_card_cmd(_, message: Message):
    if not (OWNER_ID or OWNER_USERNAME):
        return
    try:
        card = await get_dev_card()
    except Exception:
        return
    url = _dev_url()
    markup = None
    if url:
        markup = InlineKeyboardMarkup(
            [[vega_btn(f"{card['name']}", url=url)]]
        )
    for mk in (markup, None):
        if card["photo"]:
            try:
                return await message.reply_photo(
                    _bio(card["photo"]),
                    caption=card["text"],
                    parse_mode=ParseMode.HTML,
                    reply_markup=mk,
                )
            except Exception:
                pass
        try:
            return await message.reply_text(
                card["text"], parse_mode=ParseMode.HTML, reply_markup=mk
            )
        except Exception:
            pass


START_TEXT = (
    "مرحبا بك في بوت اشعارات المكالمة الصوتية\n\n"
    "البوت يراقب المكالمة الصوتية في مجموعتك ويبلغك فورا بكل ما يحدث فيها:\n\n"
    "اي شخص ينضم للمكالمة يصلك اشعار فيه اسمه ويوزره وايديه.\n"
    "لو احد دخل المكالمة وخرج في اقل من ثانية يصلك اشعار بذلك.\n"
    "تحت كل اشعار زرين: حظره من المجموعة وكتمه في المكالمة.\n\n"
    "اضغط على قائمة الاوامر لمعرفة طريقة التفعيل والاستخدام."
)

COMMANDS_TEXT = (
    "قائمة الاوامر\n\n"
    "طريقة التفعيل:\n"
    "1 - اضف البوت لمجموعتك وارفعه مشرفا بصلاحية اضافة مشرفين ودعوة مستخدمين.\n"
    "2 - اكتب في المجموعة: تفعيل اشعارات الكول\n\n"
    "ماذا يحدث بعد التفعيل:\n"
    "الحساب المساعد ينضم للمجموعة والبوت يرقيه مشرفا تلقائيا.\n"
    "المساعد يدخل المكالمة الصوتية ويبقى فيها، ولو لا توجد مكالمة يفتحها.\n"
    "اي شخص ينضم للمكالمة يصلك اشعار باسمه ويوزره مع زر حظر وزر كتم.\n"
    "لو احد دخل وخرج في اقل من ثانية يصلك اشعار بذلك.\n\n"
    "الاوامر:\n"
    "تفعيل اشعارات الكول - لتشغيل الاشعارات\n"
    "تعطيل اشعارات الكول - لايقاف الاشعارات وخروج المساعد من المكالمة\n\n"
    "الاوامر للمشرفين فقط، والحظر والكتم يعملان فقط اذا كان المستخدم مشرفا لديه الصلاحية."
)


def _dev_url():
    if OWNER_USERNAME:
        return f"https://t.me/{OWNER_USERNAME.lstrip('@')}"
    if OWNER_ID:
        return f"tg://user?id={OWNER_ID}"
    return None


def _source_url():
    c = CHANNEL.strip()
    if not c:
        return None
    if c.startswith("http"):
        return c
    return f"https://t.me/{c.lstrip('@')}"


def home_markup():
    rows = [[vega_btn("قائمة الاوامر", callback_data="cn_menu")]]
    url = _dev_url()
    src = _source_url()
    row = []
    if url:
        row.append(vega_btn("المطور", url=url))
    if src:
        row.append(vega_btn("قناة", url=src))
    if row:
        rows.append(row)
    if BOT_USERNAME:
        rows.append(
            [
                vega_btn(
                    "اضف البوت الى مجموعتك",
                    url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
                    "&admin=manage_chat+promote_members+invite_users+restrict_members"
                    "+delete_messages+manage_video_chats",
                )
            ]
        )
    return InlineKeyboardMarkup(rows)


BOT_PHOTO = None
PHOTO_SPOILER = True


async def load_bot_photo():
    global BOT_PHOTO
    try:
        chat = await vega.get_chat(BOT_USERNAME)
        if chat.photo:
            BOT_PHOTO = await vega.download_media(
                chat.photo.big_file_id, in_memory=True
            )
            BOT_PHOTO.name = "bot.jpg"
    except Exception:
        BOT_PHOTO = None


async def _edit_card(cq: CallbackQuery, text: str, markup):
    if cq.message.photo:
        await cq.edit_message_caption(
            caption=text, parse_mode=ParseMode.HTML, reply_markup=markup
        )
    else:
        await cq.edit_message_text(
            text, parse_mode=ParseMode.HTML, reply_markup=markup
        )
# الترخيص: @TopVeGa
# العلامة التجارية: VEGA & Logic
# حقوق الطبع والنشر: © 2015 - 2025
@vega.on_message(filters.command("start") & filters.private & ~dev_filter)
async def start_cmd(_, message: Message):
    global BOT_PHOTO
    if message.from_user:
        register_user(message.from_user.id)
    if CONFIG.get("contact") and message.from_user:
        asyncio.create_task(
            notify_devs(message.from_user, "مستخدم ضغط /start في البوت")
        )
    if BOT_PHOTO:
        try:
            if hasattr(BOT_PHOTO, "seek"):
                BOT_PHOTO.seek(0)
            sent = await message.reply_photo(
                BOT_PHOTO,
                caption=START_TEXT,
                parse_mode=ParseMode.HTML,
                reply_markup=home_markup(),
                has_spoiler=PHOTO_SPOILER,
            )
            if sent.photo:
                BOT_PHOTO = sent.photo.file_id
            return
        except Exception:
            BOT_PHOTO = None
    await message.reply_text(
        START_TEXT, parse_mode=ParseMode.HTML, reply_markup=home_markup()
    )


@vega.on_callback_query(filters.regex(r"^cn_menu$"))
async def open_menu(_, cq: CallbackQuery):
    await _edit_card(
        cq,
        COMMANDS_TEXT,
        InlineKeyboardMarkup(
            [[vega_btn("رجوع", callback_data="cn_home", style="danger")]]
        ),
    )
    await cq.answer()


@vega.on_callback_query(filters.regex(r"^cn_home$"))
async def back_home(_, cq: CallbackQuery):
    await _edit_card(cq, START_TEXT, home_markup())
    await cq.answer()


async def main():
    global _restored, BOT_USERNAME
    await init_db()
    await load_all()
    await vega.start()
    BOT_USERNAME = (await vega.get_me()).username
    await load_bot_photo()
    for cid in list(ENABLED):
        try:
            register_chat(await vega.get_chat(cid))
        except Exception:
            pass
    await kim.start()
    await ensure_started()
    _restored = True
    await _restore()
    print("البوت يعمل")
    await idle()
    await vega.stop()
    await kim.stop()
# الترخيص: @TopVeGa
# العلامة التجارية: VEGA & Logic
# حقوق الطبع والنشر: © 2015 - 2025
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())