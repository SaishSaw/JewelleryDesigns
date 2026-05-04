import chainlit as cl
import uuid
import base64
import requests
import os

from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("JEWELLERY_API")


# chainlit UI
@cl.on_chat_start
async def start():
    """Generates a custom session ID for each session"""
    session_id = str(uuid.uuid4())
    # store session ID
    cl.user_session.set("session_id", session_id)


@cl.on_message
async def chat_profile(message: cl.Message):
    """Gets the response from model"""
    # fetch the session ID
    print(message.content)
    from openai import OpenAI

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    # Generate an image
    response = client.chat.completions.create(
        model="sourceful/riverflow-v2-fast",
        messages=[{"role": "user", "content": message.content}],
        extra_body={"modalities": ["image"]},
    )

    # The generated image will be in the assistant message
    response = response.choices[0].message
    if response.images:
        for image in response.images:
            image_64 = image["image_url"]["url"]  # Base64 data URL
            print(f"Generated image: {image_64[:50]}...")
            if image_64.startswith("data:image"):
                mime, b64 = image_64.split(",", 1)
                mime_type = mime.split(":")[1].split(";")[0]

                image_bytes = base64.b64decode(b64)

        await cl.Message(
            content="Here is your jewellery:",
            elements=[cl.Image(content=image_bytes, mime=mime_type)],
        ).send()
