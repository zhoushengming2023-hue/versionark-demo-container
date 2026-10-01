"""版本方舟示例应用：首页显示版本与配置，/healthz 供平台健康检查（只用 Python 标准库）。"""

import html
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip() if (ROOT / "VERSION").exists() else "dev"
# 故障演练：仓库里放一个名为 BREAK_HEALTH 的空文件再发版，健康检查就会失败，平台应自动回滚。
BROKEN = (ROOT / "BREAK_HEALTH").exists()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/healthz":
            self._send(500 if BROKEN else 200, "broken" if BROKEN else "ok", "text/plain")
            return
        mode = html.escape(os.getenv("APP_MODE", "（未设置）"))
        secret = "已设置" if os.getenv("SECRET_KEY") else "未设置"
        body = (
            "<!doctype html><meta charset='utf-8'><title>versionark-demo</title>"
            f"<h1>versionark-demo {html.escape(VERSION)}</h1>"
            f"<p>APP_MODE：{mode}</p><p>SECRET_KEY：{secret}</p>"
        )
        self._send(200, body, "text/html; charset=utf-8")

    def _send(self, status: int, body: str, content_type: str) -> None:
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    # 容器里固定监听 8000（Compose 把宿主机端口映射过来）；Systemd 直接监听平台分配的 CRS_PORT。
    port = int(os.getenv("PORT") or os.getenv("CRS_PORT") or "8000")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
