# wechat-channels-to-mp3

**Paste a WeChat Channels (视频号) share link, get an MP3.** A small,
dependency-light CLI that turns a `weixin.qq.com/sph/...` share link into
an audio file — for saving talks, music and lectures you have legitimate
access to.

![screenshot](docs/screenshot.png)
*(TODO before launch: terminal screenshot of a successful run.)*

## How it works

WeChat serves no anonymous direct links for Channels videos — every
working tool needs a login session, this one included. The pipeline:

1. Your **Tencent Yuanbao** (腾讯元宝) web session cookie resolves the
   share link via Yuanbao's parse API → a playable URL carrying
   `token` + `eid`.
2. `get_feed_info` on the Channels preview API returns the real video URL.
3. The video is downloaded and converted to MP3 with `ffmpeg`.

Pure Python standard library for the network parts; the only external
requirement is `ffmpeg`.

## Requirements

- Python 3.9+
- `ffmpeg` on PATH
- A Yuanbao web login (free) — for the cookie, see below

## Getting the cookie (one-time, ~1 minute)

1. Log in to <https://yuanbao.tencent.com> in your desktop browser.
2. Open DevTools (F12) → **Application** → **Cookies** → `yuanbao.tencent.com`.
3. Copy the values of `hy_user` and `hy_token`.
4. Save them (treat this file like a password — it *is* your session):

```bash
mkdir -p ~/.config/wechat-audio
echo 'hy_user=...; hy_token=...' > ~/.config/wechat-audio/cookie
chmod 600 ~/.config/wechat-audio/cookie
```

The cookie lasts a few weeks; when the tool starts failing with a parse
error, refresh it the same way.

## Usage

```bash
# with the saved cookie (wrapper script)
./wx_dl.sh "https://weixin.qq.com/sph/AbCdEf" -o talk.mp3

# or pass it explicitly / via environment
python3 wx_audio.py "https://weixin.qq.com/sph/AbCdEf" -o talk.mp3 --cookie "hy_user=...; hy_token=..."
YUANBAO_COOKIE="hy_user=...; hy_token=..." python3 wx_audio.py "https://weixin.qq.com/sph/AbCdEf"
```

## Limitations (read before filing an issue)

- **Login is mandatory.** This is a WeChat server-side design decision,
  not a limitation of this tool — anonymous access does not exist.
- Regular videos only. Image sets (mediaType 2) and live streams are not
  supported.
- Use plain HTTP clients. Browser-fingerprint spoofing libraries tend to
  break against these endpoints.
- For personal use with content you have the right to save. Respect the
  creators and the platform's terms.

## Support / Pro

- ⭐ Star the repo if it saved you a evening of screen-recording.
- 💖 GitHub Sponsors: *(link placeholder — add once Sponsors is enabled)*
- **Pro version (planned):** batch links, auto cookie health-check with
  expiry alerts, and a no-terminal one-click build: *(link placeholder:
  Gumroad / contact)*.

## License

MIT — see `LICENSE`.

---

## 中文说明

**粘贴微信视频号分享链接，得到 MP3。** 流程：用腾讯元宝网页版的登录 cookie
调解析接口拿到 token/eid → 调视频号预览接口取真实视频地址 → 下载后用
ffmpeg 转 MP3。网络部分只用 Python 标准库，唯一外部依赖是 ffmpeg。

要点（均为实测结论）：微信服务端不给匿名用户视频直链，**登录态是硬性前提**，
任何同类工具都一样；cookie 获取方法见上文英文部分（元宝官网 F12 → Application
→ Cookies，复制 hy_user 与 hy_token，存入 `~/.config/wechat-audio/cookie`
并设 600 权限）；cookie 有效期约数周，失效后同法刷新。仅支持普通视频，
不支持图集与直播。

免费、MIT 开源；批量版/免终端版的付费入口见上（占位）。
