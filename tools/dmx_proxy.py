"""留档：修订实验中 DeepSeek 接入 DMXAPI 时，在运行主机本地启动的转发代理（docs/实验偏离记录.md 第 7 节、docs/修订实验方案.md 第十节）。

不属于实验代码，仓库中的实验脚本不调用它。按实验作者提供的原样保存（2026-11-28），未改动逻辑。
用法（当时）：在主机上运行本脚本，进程环境变量 LLM_BASE_URL=http://127.0.0.1:18081/v1、LLM_API_KEY=<DMXAPI Key>；
代理只把请求中的模型名 deepseek-v4-1-flash-261017 改写为 DMXAPI 的 deepseek-v4.1-flash-1017，
其余请求内容与 Authorization 头原样转发到 DMXAPI，回包原样返回。脚本中不含 Key。
"""
import json
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UPSTREAM = "https://www.dmxapi.cn"

class Proxy(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    def log_message(self, fmt, *args):
        pass
    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(n)
        try:
            body = json.loads(raw)
            if body.get("model") == "deepseek-v4-1-flash-261017":
                body["model"] = "deepseek-v4.1-flash-1017"
            raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        except Exception:
            pass
        path = self.path if self.path.startswith("/v1") else "/v1" + self.path
        headers = {"Content-Type": "application/json"}
        if "Authorization" in self.headers:
            headers["Authorization"] = self.headers["Authorization"]
        req = urllib.request.Request(UPSTREAM + path, data=raw, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=1800) as resp:
                data = resp.read()
                code = resp.status
                ct = resp.headers.get("Content-Type", "application/json")
        except urllib.error.HTTPError as e:
            data = e.read()
            code = e.code
            ct = e.headers.get("Content-Type", "application/json")
        self.send_response(code)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

ThreadingHTTPServer(("127.0.0.1", 18081), Proxy).serve_forever()
