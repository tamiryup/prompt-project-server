from typing import Generator
from openai import OpenAI

client = OpenAI()

def send_message(message: str) -> Generator:
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": message}],
        stream=True,
    )

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content


# "write me a two parargraph love letter from dorian gray to his high school crush"