"""
MentorEngine — ядро AI Programming Mentor.
Использует OpenRouter (бесплатно) + Сократический метод.
Никогда не даёт готовый код — только наводящие вопросы.
"""

import base64
import json
import re
import io
from PIL import Image
from openai import OpenAI


_SYSTEM_PROMPT = """
Ты — опытный ментор по программированию. Твой метод — Сократический диалог.

АБСОЛЮТНЫЕ ПРАВИЛА:
1. НИКОГДА не давай исправленный код. Даже фрагмент. Даже намёк на синтаксис.
2. Пиши развёрнуто и структурированно — студент должен понять ситуацию глубоко.
3. Вопросы должны вести к самостоятельному открытию, а не объяснять ответ.
4. Если чувствуется стресс (слова: "не работает", "не понимаю", "помогите", "срочно", "паника") — добавь совет по Трансёрфингу.
5. Отвечай на том языке, на котором написан запрос.

ФОРМАТ ОТВЕТА — строго валидный JSON без текста снаружи:
{
  "analysis": "3-4 предложения: подробно объясни что происходит в коде и почему возникает проблема. Укажи конкретную строку или конструкцию.",
  "root_cause": "Одно чёткое предложение: назови корень проблемы (концепция/механизм языка).",
  "concept": "Объясни концепцию которую нужно понять (2-3 предложения). Например: область видимости, изменяемость, жизненный цикл и т.д.",
  "questions": ["Вопрос 1 — конкретный, про код?", "Вопрос 2 — про концепцию?", "Вопрос 3 — про последствия?"],
  "next_steps": "Что конкретно сделать дальше чтобы разобраться — без кода, только направление мысли (2-3 предложения).",
  "has_stress": true или false,
  "transurfing_tip": "Совет по снижению избыточного потенциала (только если has_stress=true, иначе пустая строка)"
}
""".strip()

_STRESS_MARKERS = [
    "не работает", "всё сломалось", "помогите", "не понимаю", "срочно",
    "deadline", "дедлайн", "паника", "ужас", "кошмар", "провал",
    "не могу", "сдаюсь", "всё плохо", "wtf", "??????????",
    "doesnt work", "broken", "help me", "i don't understand", "please help",
]


def _has_stress_markers(text: str) -> bool:
    return any(marker in text.lower() for marker in _STRESS_MARKERS)


def _image_to_base64(image_file) -> str:
    img = Image.open(image_file)
    img.thumbnail((1024, 1024), Image.LANCZOS)
    if img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


class MentorEngine:
    MODEL = "google/gemma-4-31b-it:free"

    def __init__(self, api_key: str):
        self._client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    def analyze(
        self,
        code: str,
        screenshot=None,
        extra_context: str = "",
    ) -> tuple[dict, dict]:
        user_text = self._build_user_message(code, extra_context)
        stress_hint = " [СТРЕСС ОБНАРУЖЕН]" if _has_stress_markers(user_text) else ""

        content: list[dict] = []

        if screenshot is not None:
            b64 = _image_to_base64(screenshot)
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
            })

        content.append({"type": "text", "text": user_text + stress_hint})

        response = self._client.chat.completions.create(
            model=self.MODEL,
            max_tokens=2048,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": content},
            ],
        )

        raw = response.choices[0].message.content
        raw = re.sub(r"```(?:json)?", "", raw).strip()
        result = json.loads(raw)

        usage = {
            "input":  response.usage.prompt_tokens,
            "output": response.usage.completion_tokens,
        }
        return result, usage

    @staticmethod
    def _build_user_message(code: str, extra_context: str) -> str:
        parts = []
        if extra_context.strip():
            parts.append(f"Контекст / описание проблемы:\n{extra_context.strip()}")
        if code.strip():
            parts.append(f"Мой код:\n```\n{code.strip()}\n```")
        if not parts:
            parts.append("Смотри на скриншот ошибки.")
        return "\n\n".join(parts)
