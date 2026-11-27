#!/usr/bin/env python3
"""
微信视频号 → MP3 提取工具
用法: wx_audio.py <分享链接> [-o 输出.mp3] [--cookie "hy_user=...; hy_token=..."]
Cookie 获取: 电脑浏览器登录 yuanbao.tencent.com → F12 → Application → Cookies → 复制 hy_user 和 hy_token
也可设置环境变量 YUANBAO_COOKIE
"""
import os, sys, json, re, subprocess, urllib.request, urllib.parse

YUANBAO_API = "https://yuanbao.tencent.com/api/weixin/get_parse_result"
FEED_API = "https://channels.weixin.qq.com/finder-preview/api/feed/get_feed_info"

def post_json(url, data, cookie=""):
    req = urllib.request.Request(url, data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json",
                 "Accept": "application/json",
                 "x-source": "web",
                 "Origin": "https://yuanbao.tencent.com",
                 "Referer": "https://yuanbao.tencent.com/",
                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0 Safari/537.36"})
    if cookie:
        req.add_header("Cookie", cookie)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def parse_share_url(url):
    m = re.search(r'sph/([A-Za-z0-9_-]+)', url)
    if not m: raise ValueError("不是有效的微信视频号分享链接")
    return f"https://weixin.qq.com/sph/{m.group(1)}"

def get_playable(share_url, cookie):
    j = post_json(YUANBAO_API, {"type": "video_channel_url", "url": share_url, "scene": 1}, cookie)
    if j.get("code") != 0:
        raise RuntimeError(f"Yuanbao 解析失败: {j.get('message') or j}")
    playable = (j.get("data") or {}).get("playable_url", "")
    token_m = re.search(r'[?&]token=([^&]+)', playable)
    eid_m = re.search(r'[?&]eid=([^&]+)', playable)
    if not (token_m and eid_m):
        raise RuntimeError(f"playable_url 中无 token/eid: {playable[:120]}")
    # eid/token 可能是 URL 编码的，需解码
    token = urllib.parse.unquote(token_m.group(1))
    eid = urllib.parse.unquote(eid_m.group(1))
    return token, eid, playable

def get_video_url(token, eid, playable_url):
    import random, time, secrets
    rid = f"{int(time.time()):x}-{secrets.token_hex(4)}"
    url = f"{FEED_API}?_rid={rid}&_pageUrl=" + urllib.parse.quote("https://channels.weixin.qq.com/finder-preview/pages/feed")
    req = urllib.request.Request(url, data=json.dumps(
        {"baseReq": {"generalToken": token}, "exportId": eid}).encode(),
        headers={"Content-Type": "application/json",
                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0 Safari/537.36",
                 "Origin": "https://channels.weixin.qq.com",
                 "Referer": playable_url})
    with urllib.request.urlopen(req, timeout=30) as r:
        j = json.loads(r.read())
    if j.get("errCode", 0) != 0:
        raise RuntimeError(f"get_feed_info 失败: {j.get('errMsg')}")
    fi = (j.get("data") or {}).get("feedInfo") or {}
    if fi.get("mediaType") not in (4, None):
        raise RuntimeError(f"非普通视频 (mediaType={fi.get('mediaType')})，暂不支持")
    vurl = ((fi.get("h264VideoInfo") or {}).get("videoUrl")
            or fi.get("videoUrl")
            or (fi.get("h265VideoInfo") or {}).get("videoUrl"))
    if not vurl:
        raise RuntimeError(f"未取到 videoUrl: {json.dumps(j)[:200]}")
    return vurl, fi.get("description", "")

def download(url, path):
    urllib.request.urlretrieve(url, path)

def to_mp3(video_path, mp3_path):
    subprocess.run(["ffmpeg", "-y", "-i", video_path, "-vn", "-c:a", "libmp3lame",
                    "-b:a", "128k", mp3_path], check=True, capture_output=True)

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__); return
    share = parse_share_url(sys.argv[1])
    out = sys.argv[sys.argv.index("-o")+1] if "-o" in sys.argv else "wechat_audio.mp3"
    cookie = ""
    if "--cookie" in sys.argv:
        cookie = sys.argv[sys.argv.index("--cookie")+1]
    else:
        cookie = os.environ.get("YUANBAO_COOKIE", "")
    if not cookie:
        print("ERROR: 需要 Yuanbao cookie。用 --cookie 或设 YUANBAO_COOKIE 环境变量。"); sys.exit(1)
    print("1/4 解析分享链接...")
    token, eid, playable = get_playable(share, cookie)
    print("2/4 获取视频地址...")
    vurl, title = get_video_url(token, eid, playable)
    print(f"   标题: {title[:40]}")
    print("3/4 下载视频...")
    vpath = "/tmp/wx_video.mp4"; download(vurl, vpath)
    print("4/4 转 MP3...")
    to_mp3(vpath, out)
    print(f"完成: {out} ({os.path.getsize(out)//1024}KB)")

if __name__ == "__main__":
    main()
