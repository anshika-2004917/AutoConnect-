
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

try:
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You are AutoConnect AI, a helpful assistant for a campus auto-rickshaw booking system."
            },
            {
                "role": "user",
                "content": "Introduce yourself and explain how you can help students book campus autos."
            }
        ],
        temperature=0.7,
        max_completion_tokens=300
    )

    print("\nGroq connected successfully!")
    print("\nAutoConnect AI:")
    print(response.choices[0].message.content)

except Exception as e:
    print("Groq connection failed:", str(e))
