YT → TikTok Reup <10s (Desktop App)
Mục tiêu: từ lúc YouTube ra video mới → phát hiện → edit đúng 61s → post lên TikTok ≤ 10 giây (điều kiện mạng tốt).
Điểm mạnh: đa kênh, đa luồng, WebSub (push), ffmpeg ultrafast, ưu tiên TikTok PULL_FROM_URL (TikTok tự kéo video, bỏ thời gian upload).

1) Tính năng chính


Theo dõi nhiều kênh: nhập @handle, URL kênh, channelId UC…, hoặc link có si=....


Phát hiện gần real-time: YouTube WebSub (push vào webhook – nhanh hơn poll).


Xử lý video 61s tự động:


Nếu ≥ 61s: cắt cứng 0..61s (libx264, preset ultrafast, -tune zerolatency).


Nếu < 61s: slow-motion đến đúng 61s (setpts + chuỗi atempo cho audio), scale/pad 9:16.




Đăng TikTok siêu nhanh:


PULL_FROM_URL (khuyến nghị – TikTok tự kéo, giảm độ trễ uplink).


Fallback FILE_UPLOAD (nhận upload_url rồi PUT binary).




Quản lý bằng App (Tkinter): thêm/xoá kênh, Start/Stop dịch vụ, log realtime, chỉnh số workers.


Đa luồng: hàng đợi + nhiều worker encode/upload song song.


Chống lặp: đánh dấu video đã xử lý.


SLA mục tiêu: 5–9 giây với mạng ổn (≥ 100 Mbps down / ≥ 50 Mbps up), input 360p/480p.

2) Kiến trúc tóm tắt


App GUI (Tkinter) điều khiển Service:


server_websub (FastAPI + Uvicorn): nhận WebSub callback /websub/callback.


channels: chuẩn hoá & lưu danh sách kênh.


detector: enqueue job khi có video mới.


worker (N threads): lấy meta → cắt/slow 61s → PULL_FROM_URL hoặc upload.


uploader: mini CDN nội bộ (dev) / map sang CDN đã verify (prod).


tiktok_client: gọi Content Posting API (init/PUT).





3) Yêu cầu hệ thống


Windows 10/11, Python 3.11/3.12 (khuyến nghị – 3.13 có gói chưa theo kịp).


ffmpeg và ffprobe (đặt trong ffmpeg/ hoặc cài vào PATH).


yt-dlp (từ PyPI).


Truy cập Internet ổn định (YouTube, TikTok API, tunnel).



4) Cài đặt
D:
cd D:\ytreup-tiktok-app
py -3 -m venv .venv
.\.venv\Scripts\activate
python -m pip install -U pip wheel
pip install -r requirements.txt


Nếu lỗi phiên bản yt-dlp trong requirements.txt, sửa thành:
yt-dlp>=2024.10.0,<2026.0.0


Kiểm tra công cụ:
ffmpeg -version
ffprobe -version
yt-dlp --version


5) Cấu trúc thư mục
ytreup-tiktok-app/
├─ README.md
├─ requirements.txt
├─ .env.example
├─ .env
├─ run_app.bat
├─ ffmpeg/                 # ffmpeg.exe, ffprobe.exe (tùy chọn)
└─ src/
   ├─ __init__.py
   ├─ app.py               # GUI Tkinter
   ├─ service.py           # manage server + worker loops
   ├─ server_websub.py     # FastAPI webhook server
   ├─ channels.py          # multi-channel management
   ├─ detector.py          # enqueue on new video
   ├─ worker.py            # encode/upload workers
   ├─ fetcher.py           # yt-dlp helpers
   ├─ editor.py            # ffmpeg 61s pipeline
   ├─ tiktok_client.py     # TikTok Content Posting API
   ├─ uploader.py          # mini CDN (dev) / S3/R2 mapping
   ├─ storage.py           # state, logs, queue
   └─ config.py            # .env loader


Quan trọng: có src/__init__.py để chạy dưới dạng module.


6) Cấu hình .env
Mở .env (copy từ .env.example) và điền:
# App / Webhook
HOST=127.0.0.1
PORT=8080
PUBLIC_BASE_URL=https://<public-https-url-vao-may-ban>

# YouTube
YOUTUBE_HUB=https://pubsubhubbub.appspot.com

# FFmpeg / yt-dlp
FFMPEG_PATH=ffmpeg/ffmpeg.exe
FFPROBE_PATH=ffmpeg/ffprobe.exe
YT_DLP_PATH=yt-dlp

# Encode (TikTok dọc)
TARGET_WIDTH=1080
TARGET_HEIGHT=1920
TARGET_FPS=30
TARGET_DURATION=61

# TikTok
TIKTOK_BASE=https://open.tiktokapis.com
TIKTOK_ACCESS_TOKEN=xxx_user_access_token_xxx
TIKTOK_USE_PULL_FROM_URL=true
TIKTOK_DIRECT_POST_INIT=/v2/post/publish/video/init/
TIKTOK_VERIFIED_CDN_BASE=https://cdn.yourdomain.com/reup/

# Mini CDN (dev)
CDN_LOCAL_ENABLE=true
CDN_LOCAL_PORT=9090
CDN_LOCAL_BASE_URL=http://127.0.0.1:9090/reup/
CDN_LOCAL_DIR=.cdn_store

# Workers
ENCODE_WORKERS=3

6.1. PUBLIC_BASE_URL (bắt buộc)
Cần HTTPS public URL để YouTube Hub gọi vào …/websub/callback.
Dùng Cloudflare quick tunnel
cloudflared.exe tunnel --url http://127.0.0.1:8080 --ha-connections 2 --no-autoupdate

Lấy URL https://xxxx.trycloudflare.com → dán vào PUBLIC_BASE_URL.
Hoặc dùng ngrok
winget install ngrok.ngrok
ngrok config add-authtoken <YOUR_NGROK_TOKEN>
ngrok http 8080

Lấy https://…ngrok-free.app → dán vào PUBLIC_BASE_URL.

Test: mở https://<PUBLIC_BASE_URL>/websub/callback thấy OK.

6.2. TikTok ACCESS_TOKEN (bắt buộc)


Tạo app trên TikTok Developer, bật Content Posting.


OAuth URL:
https://www.tiktok.com/v2/auth/authorize/
  ?client_key=YOUR_CLIENT_KEY
  &scope=video.publish%20video.upload
  &response_type=code
  &redirect_uri=ENCODED_REDIRECT_URI
  &state=xyz



Đổi code → access_token:
POST https://open.tiktokapis.com/v2/oauth/token/
Content-Type: application/x-www-form-urlencoded

client_key=...&client_secret=...&grant_type=authorization_code
&code=...&redirect_uri=...



Dán access_token vào TIKTOK_ACCESS_TOKEN=...


Refresh định kỳ (grant_type=refresh_token) khi sắp hết hạn.


6.3. PULL_FROM_URL (khuyến nghị)


Verify domain/prefix trong TikTok Dev console (prod).


Set TIKTOK_USE_PULL_FROM_URL=true + TIKTOK_VERIFIED_CDN_BASE=https://cdn.yourdomain.com/reup/.


Dev có thể bật mini CDN cục bộ, nhưng TikTok không thể kéo từ 127.0.0.1; dùng cái này chỉ để test pipeline. Production cần CDN public thật.



7) Chạy app
Cách khuyên dùng (module)
run_app.bat

Nội dung:
@echo off
setlocal
if not exist .venv ( py -3 -m venv .venv )
call .venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
python -m src.app

Hoặc chạy tay
.\.venv\Scripts\activate
python -m src.app


8) Sử dụng GUI


Nhập kênh: dán @handle, URL kênh, channelId UC…, hoặc link có si=... → Thêm kênh.


Start dịch vụ: app sẽ subscribe WebSub cho tất cả kênh.


Theo dõi log realtime.


Workers: chỉnh số worker (1–16) trước khi Start để tối ưu throughput.


Khi kênh ra video mới:


Log: [NEW] channelId:videoId queued


Worker: cắt/slow 61s, scale/pad 9:16, encode ultrafast


Đăng TikTok:


PULL_FROM_URL (nếu bật/verify) → log [OK] ... in X.XXs


hoặc FILE_UPLOAD (init → PUT) → log [OK] ... in X.XXs







9) Tối ưu tốc độ ≤10s


WebSub bắt buộc để phát hiện nhanh (poll làm dự phòng sẽ chậm hơn).


yt-dlp --download-sections "*0-61" khi video dài ≥ 61s (giảm IO).


ffmpeg: -preset ultrafast -tune zerolatency -crf 28, fps=30, scale+pad 9:16.


PULL_FROM_URL loại bỏ thời gian upload máy bạn → TikTok tự kéo bằng băng thông inbound lớn.


Prewarm (start trước, giữ tunnel sống).


SSD, CPU đa nhân; tăng ENCODE_WORKERS hợp lý (3–6).



10) Xử lý sự cố (FAQ)
A. ImportError: attempted relative import with no known parent package
→ Chạy bằng module & có src/__init__.py:
python -m src.app (hoặc dùng run_app.bat).
B. cloudflared is not recognized


Đặt cloudflared.exe cạnh run_app.bat hoặc cài qua winget.


Nếu timeout trycloudflare: dùng ngrok tạm thời.


C. /websub/callback không hiển thị OK


Kiểm tra app đã chạy chưa.


Kiểm tra PUBLIC_BASE_URL đúng chưa (HTTPS), tunnel đang mở chưa.


D. TikTok trả 401/403


TIKTOK_ACCESS_TOKEN sai/hết hạn/thiếu scope → làm lại OAuth + refresh.


Kiểm tra TIKTOK_DIRECT_POST_INIT đúng /v2/post/publish/video/init/.


E. TikTok 429 (rate limit)


Giảm tốc, bật queue; kiểm soát số lần gọi init/phút.


Không spam nhiều video cùng lúc từ 1 user.


F. Video < 61s nghe méo tiếng


Chuỗi atempo đã băm nhỏ (0.5..2.0) để giữ chất lượng.


Có thể tăng CRF xuống 26 nếu muốn đẹp hơn (đổi trong editor.py).


G. ffmpeg/ffprobe not found


Đặt exe vào ffmpeg/ và giữ FFMPEG_PATH, FFPROBE_PATH trong .env.


Hoặc cài vào PATH.


H. yt-dlp lỗi phiên bản


pip install -U yt-dlp hoặc chỉnh requirements.txt theo khoảng đề xuất.



11) Nâng cấp/tuỳ biến


Đóng gói .exe (PyInstaller): gói kèm ffmpeg portable → chạy 1 file.


S3/R2 CDN: thay uploader.py bằng uploader AWS S3/Cloudflare R2 (public URL cùng prefix đã verify).


Caption template/hashtags: thêm trường cấu hình & UI.



12) Lưu ý pháp lý


Tôn trọng điều khoản/bản quyền của YouTube & TikTok.


Công cụ này mô tả kỹ thuật; người dùng chịu trách nhiệm về nội dung đăng tải và quyền sử dụng.



13) Góp ý & hỗ trợ


Gặp lỗi? Dán log đầy đủ trong GUI hoặc file .state/events.log.


Cho biết Windows/Python version, tốc độ mạng, và các bước đã làm.



Done. Bạn chỉ cần:


Cài deps, điền .env.


Mở tunnel (cloudflared/ngrok) → update PUBLIC_BASE_URL.


run_app.bat → Thêm kênh → Start.


Test ra video mới → xem log [OK] in X.XXs.


