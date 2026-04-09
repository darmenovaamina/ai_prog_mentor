import os
from openai import OpenAI
from dotenv import load_dotenv
from core.prompts import SYSTEM_PROMPT, FORMAT_PROMPTS

load_dotenv()


def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.startswith("sk-..."):
        raise ValueError("OPENAI_API_KEY is not set in .env")
    return OpenAI(api_key=api_key)


def generate_copy(image_b64: str, output_format: str, language: str) -> str:
    """Send image + prompt to GPT-4o and return generated copy."""
    client = get_client()
    format_prompt = FORMAT_PROMPTS[output_format]
    user_text = f"{format_prompt}\n\nRespond in: {language}."

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=512,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}",
                            "detail": "low",
                        },
                    },
                    {"type": "text", "text": user_text},
                ],
            },
        ],
    )
    return response.choices[0].message.content.strip()
