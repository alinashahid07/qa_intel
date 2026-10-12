from openai import OpenAI

from app.config import settings

client = OpenAI(api_key=settings.hackclub_api_key, base_url=settings.hackclub_base_url)

response = client.chat.completions.create(
    model=settings.llm_model,
    messages=[{"role": "user", "content": "Reply with the single word ready"}],
)
print(response.choices[0].message.content)