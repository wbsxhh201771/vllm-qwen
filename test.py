import litellm

# 你的 LiteLLM 代理地址和主密钥
LITELLM_PROXY_URL = "http://localhost:8000/v1"
MASTER_KEY = "sk-HwMLcHVLpfDoPXD7P3yEQPENVLeDZJbj3OHozVv5eQYipLKO"

print("正在通过 LiteLLM SDK 发送 /responses 请求...\n")

try:
    # 使用 responses 接口
    response = litellm.responses(
        model="openai/qwen3-4b",
        input="请介绍一下 vllm的使用",
        api_base=LITELLM_PROXY_URL,
        api_key=MASTER_KEY,
        stream=True,
        # use_chat_completions_api=True
    )

    # 遍历流式响应
    for chunk in response:
        print(chunk.delta, end="", flush=True)
    
    print("\n\n✅ 请求完成！")

except Exception as e:
    print(f"\n❌ 请求失败: {e}")