import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
r = client.chat.completions.create(
    model="gpt-5.6-luna",
    messages=[{"role": "user", "content": "ping"}],
)
print(r.choices[0].message.content)
print(r.usage)