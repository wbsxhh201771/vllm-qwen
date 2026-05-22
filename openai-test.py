from openai import OpenAI

# Initialize client with your proxy URL
client = OpenAI(
    base_url="http://localhost:8000/v1",  # Your proxy URL
    api_key="sk-HwMLcHVLpfDoPXD7P3yEQPENVLeDZJbj3OHozVv5eQYipLKO"             # Your proxy API key
)

# Streaming response
response = client.responses.create(
    model="qwen3-4b",
    input="你好！请简单介绍一下你自己。",
    # stream=True
)

for event in response:
    print(event, end="", flush=True)  # 实时打印输出