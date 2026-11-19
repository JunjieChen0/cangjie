"""rag2 的本地检索服务：BM25 与 bge-m3 混合（RRF）后用 bge-reranker-v2-m3 重排，返回 top-3 文档片段。

检索方案由 retrieval_eval.py 的离线评估选出（rewrite_hybrid_rerank），参数在跑 rag2 实验前冻结；
查询改写由调用方（repair.py --feedback rag2）完成，本服务只负责对改写后的查询检索。
模型只加载一次，GPU 计算加锁串行，多个实验进程可共用。需要在检索环境中运行：
  .venv-retrieval/Scripts/python.exe src/retrieval_server.py          # 监听 127.0.0.1:8765
接口：POST /search  {"query": "..."}  →  {"chunks": [{"title": ..., "text": ...}, ...]}；GET /health → ok
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from doc_retrieval import get_index  # noqa: E402
from retrieval_eval import FUSE_DEPTH, K, OUT, RERANK_DEPTH, Dense, bm25_rank, rrf  # noqa: E402

DEFAULT_PORT = 8765


class Retriever:
    def __init__(self):
        self.chunks, _ = get_index()
        self.dense = Dense(os.path.join(OUT, "cache"))
        self.lock = threading.Lock()

    def search(self, query: str, k: int = K) -> list[dict]:
        with self.lock:
            cand = rrf([bm25_rank(query, FUSE_DEPTH), self.dense.rank(query, FUSE_DEPTH)])[:RERANK_DEPTH]
            ids = self.dense.rerank(query, cand)[:k]
        return [{"title": self.chunks[i]["title"], "text": self.chunks[i]["text"]} for i in ids]


def make_handler(retriever: Retriever):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, body: dict | str) -> None:
            data = (body if isinstance(body, str) else json.dumps(body, ensure_ascii=False)).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            self._send(200, "ok") if self.path == "/health" else self._send(404, {"error": "not found"})

        def do_POST(self):
            if self.path != "/search":
                return self._send(404, {"error": "not found"})
            try:
                query = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))["query"]
            except (ValueError, KeyError) as e:
                return self._send(400, {"error": f"bad request: {e}"})
            self._send(200, {"chunks": retriever.search(query)})

        def log_message(self, fmt, *args):   # 不逐条打印请求
            pass
    return Handler


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = ap.parse_args()
    retriever = Retriever()
    print(f"rag2 检索服务已就绪：http://127.0.0.1:{args.port}/search", flush=True)
    ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(retriever)).serve_forever()


if __name__ == "__main__":
    main()
