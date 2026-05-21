from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY"
)

resp = client.chat.completions.create(
    model="qwen2.5-3B",
    messages=[
        {"role": "user", "content": "解释一下vLLM的作用"}
    ],
    max_tokens=200
)

print(resp.choices[0].message.content)