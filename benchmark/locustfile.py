from locust import HttpUser, task, between, events
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== 配置区 ==========
MODEL_NAME = "qwen3-4b"
PROMPT_TEXT = "请详细介绍一下你们的退换货政策，包括时间期限、适用条件和具体流程。" * 3  # ~200 tokens
MAX_TOKENS = 512
WARMUP_REQUESTS = 5  # 前N个请求视为预热，不计入统计
# ============================

class VLLMBenchmark(HttpUser):
    wait_time = between(0.5, 1.0)
    
    def on_start(self):
        """每个虚拟用户启动时进行预热"""
        self._request_count = 0
        for i in range(WARMUP_REQUESTS):
            payload = {
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": "你好"}],
                "max_tokens": 16, "stream": False
            }
            self.client.post("/v1/chat/completions", json=payload)
            logger.info(f"[Warmup] Request {i+1}/{WARMUP_REQUESTS} done")

    @task
    def chat_completion(self):
        self._request_count += 1
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": "你是一个专业的客服助手，回答简洁准确。"},
                {"role": "user", "content": PROMPT_TEXT}
            ],
            "max_tokens": MAX_TOKENS,
            "temperature": 0.7,
            "stream": False
        }

        start = time.perf_counter()
        with self.client.post(
            "/v1/chat/completions", 
            json=payload, 
            catch_response=True,
            name="/v1/chat/completions"  # Locust 统计面板统一命名
        ) as resp:
            latency = time.perf_counter() - start

            if resp.status_code == 200:
                try:
                    data = resp.json()
                    out_tokens = data.get("usage", {}).get("completion_tokens", 0)
                    in_tokens = data.get("usage", {}).get("prompt_tokens", 0)

                    # 自定义指标：生成速度 tokens/s
                    if out_tokens > 0:
                        tps = out_tokens / latency
                        events.request.fire(
                            request_type="METRIC", name="tokens_per_sec",
                            response_time=tps, response_length=out_tokens
                        )
                    # 自定义指标：实际输出token数
                    events.request.fire(
                        request_type="METRIC", name="output_tokens",
                        response_time=out_tokens, response_length=out_tokens
                    )
                    resp.success()
                except Exception as e:
                    resp.failure(f"Parse error: {e}")
            else:
                resp.failure(f"HTTP {resp.status_code}: {resp.text[:200]}")