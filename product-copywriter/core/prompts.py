SYSTEM_PROMPT = (
    "You are an expert e-commerce copywriter. "
    "Analyze the product image and create compelling, accurate copy. "
    "Write in the requested format and language. Be concise and conversion-focused."
)

FORMAT_PROMPTS: dict[str, str] = {
    "Short description": (
        "Write a short product description (2–3 sentences, max 60 words). "
        "Focus on the key benefit and who it's for. "
        "Tone: confident, clear, no fluff."
    ),
    "Bullet points": (
        "List 5 concise bullet points highlighting the product's main features and benefits. "
        "Each bullet: start with a bold keyword, then a short explanation. "
        "Example: **Durable** — made from 304 stainless steel for years of daily use."
    ),
    "SEO title + description": (
        "Produce:\n"
        "1. SEO Title (max 60 characters, include main keyword)\n"
        "2. Meta Description (max 155 characters, include a call to action)\n"
        "Format your response exactly as:\n"
        "Title: <title here>\n"
        "Description: <description here>"
    ),
}
