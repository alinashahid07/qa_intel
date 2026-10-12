from openai import OpenAI

from app.config import settings

client = OpenAI(api_key=settings.hackclub_api_key, base_url=settings.hackclub_base_url)

# prints every model id the proxy exposes so we can pick the right ones
for model in client.models.list():
    print(model.id)