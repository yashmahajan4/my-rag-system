from openai import OpenAI

from src.config import Config


def generate_answer(prompt):

    client = OpenAI(
        api_key=Config.get_api_key(),
        base_url=Config.get_base_url(),
    )

    response = client.chat.completions.create(
        model=Config.get_chat_model(),
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=Config.TEMPERATURE,
    )

    if not response.choices:
        raise ValueError("❌ Empty response from chat model")

    message = response.choices[0].message

    if not message or not getattr(message, "content", None):
        raise ValueError("❌ Chat model returned empty content")

    return message.content.strip()