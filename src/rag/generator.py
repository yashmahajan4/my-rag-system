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

    return response.choices[0].message.content
