import streamlit as st
import openai
import base64
import json
import re
from PIL import Image
import io

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Копирайтер",
    page_icon="✍️",
    layout="wide",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Unbounded:wght@400;700&family=Inter:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Unbounded', cursive; }

.stApp { background-color: #0e0e11; color: #f0f0f0; }

.main-title {
    font-family: 'Unbounded', cursive;
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #c8ff00, #00e5ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}
.sub-title {
    color: #888;
    font-size: 0.9rem;
    margin-top: 4px;
    margin-bottom: 32px;
}

.card {
    background: #1a1a22;
    border: 1px solid #2e2e3a;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    transition: border-color 0.2s;
}
.card:hover { border-color: #c8ff00; }

.card-label {
    font-family: 'Unbounded', cursive;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 12px;
}
.card-insta  .card-label { color: #e040fb; }
.card-kaspi  .card-label { color: #ff6d00; }
.card-website .card-label { color: #00e5ff; }

.card-body {
    font-size: 0.95rem;
    line-height: 1.7;
    color: #d0d0d0;
    white-space: pre-wrap;
}

div.stButton > button {
    background: linear-gradient(90deg, #c8ff00, #00e5ff);
    color: #0e0e11;
    font-family: 'Unbounded', cursive;
    font-size: 0.8rem;
    font-weight: 700;
    border: none;
    border-radius: 12px;
    padding: 12px 32px;
    cursor: pointer;
    width: 100%;
    transition: opacity 0.2s;
}
div.stButton > button:hover { opacity: 0.85; }

.stTextInput input, .stTextArea textarea {
    background: #1a1a22 !important;
    border: 1px solid #2e2e3a !important;
    border-radius: 10px !important;
    color: #f0f0f0 !important;
}

[data-testid="stFileUploader"] {
    background: #1a1a22;
    border: 1px dashed #2e2e3a;
    border-radius: 14px;
    padding: 8px;
}

hr { border-color: #2e2e3a; }
</style>
""", unsafe_allow_html=True)


# ── Pricing (GPT-4o-mini) ──────────────────────────────────────────────────────
PRICE_INPUT_PER_TOKEN  = 0.150 / 1_000_000   # $0.150 per 1M input tokens
PRICE_OUTPUT_PER_TOKEN = 0.600 / 1_000_000   # $0.600 per 1M output tokens


def calc_cost(input_tokens: int, output_tokens: int) -> float:
    return input_tokens * PRICE_INPUT_PER_TOKEN + output_tokens * PRICE_OUTPUT_PER_TOKEN


# ── Session state ──────────────────────────────────────────────────────────────
if "total_input_tokens"  not in st.session_state:
    st.session_state.total_input_tokens  = 0
if "total_output_tokens" not in st.session_state:
    st.session_state.total_output_tokens = 0
if "last_usage" not in st.session_state:
    st.session_state.last_usage = None


# ── Sidebar — cost tracker ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 💰 Стоимость")
    st.caption("Цены GPT-4o-mini")

    if st.session_state.last_usage:
        u = st.session_state.last_usage
        last_cost = calc_cost(u["input"], u["output"])
        st.markdown("**Последний запрос**")
        col1, col2 = st.columns(2)
        col1.metric("Вход", f"{u['input']:,} tok")
        col2.metric("Выход", f"{u['output']:,} tok")
        st.metric("Стоимость", f"${last_cost:.5f}")
    else:
        st.info("Здесь появится стоимость после первой генерации.")

    st.divider()

    total_cost = calc_cost(
        st.session_state.total_input_tokens,
        st.session_state.total_output_tokens,
    )
    st.markdown("**За сессию**")
    st.metric("Всего токенов",
              f"{st.session_state.total_input_tokens + st.session_state.total_output_tokens:,}")
    st.metric("Итого", f"${total_cost:.5f}")

    if st.button("Сбросить счётчик", use_container_width=True):
        st.session_state.total_input_tokens  = 0
        st.session_state.total_output_tokens = 0
        st.session_state.last_usage = None
        st.rerun()

    st.divider()
    st.caption("Input: $0.15 / 1M tok\nOutput: $0.60 / 1M tok")


# ── OpenAI client ──────────────────────────────────────────────────────────────
def get_client() -> openai.OpenAI:
    return openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


# ── System prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
Ты — профессиональный копирайтер для e-commerce и социальных сетей.
Твоя задача: изучить фото товара и ключевые слова, затем создать три варианта продающего текста.

ПРАВИЛА (строго обязательны):
1. Верни ответ ИСКЛЮЧИТЕЛЬНО в виде валидного JSON. Никакого текста до или после.
2. Структура JSON:
   {
     "instagram": "...",
     "kaspi": "...",
     "website": "..."
   }

ТРЕБОВАНИЯ к каждому формату:
- "instagram": 3-5 коротких абзацев. Эмодзи уместны. Хэштеги в конце (5-7 штук).
  Цель — вызвать эмоцию и желание. Разговорный тон.
- "kaspi": Лаконичный заголовок (до 60 символов) + 3-5 буллетов с ключевыми
  характеристиками и выгодами. Без эмодзи. Акцент на практичность и цену/качество.
- "website": SEO-ориентированный абзац (80-120 слов). Полное предложение стоимости.
  Упомяни материал, применение, преимущества. Заверши призывом к действию.

Если на фото видна цена — используй её. Если язык ключевых слов — русский, пиши на русском.
Не придумывай несуществующих характеристик, которых нет на фото или в описании.
""".strip()


# ── Core function ──────────────────────────────────────────────────────────────
def image_to_base64(image_file) -> tuple[str, str]:
    img = Image.open(image_file)
    img.thumbnail((1024, 1024), Image.LANCZOS)
    buffer = io.BytesIO()
    fmt = img.format or "JPEG"
    img.save(buffer, format=fmt)
    return base64.b64encode(buffer.getvalue()).decode("utf-8"), fmt.lower()


def generate_copy(image_file, keywords: str) -> tuple[dict, dict]:
    """Returns (result_dict, usage_dict)."""
    client = get_client()
    b64, fmt = image_to_base64(image_file)
    mime = f"image/{'jpeg' if fmt in ('jpg', 'jpeg') else fmt}"

    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime};base64,{b64}",
                            "detail": "high",
                        },
                    },
                    {
                        "type": "text",
                        "text": f"Ключевые слова / описание товара: {keywords}",
                    },
                ],
            },
        ],
        max_tokens=1500,
        temperature=0.7,
    )

    raw = response.choices[0].message.content
    raw = re.sub(r"```(?:json)?", "", raw).strip()

    usage = {
        "input":  response.usage.prompt_tokens,
        "output": response.usage.completion_tokens,
    }
    return json.loads(raw), usage


# ── UI helpers ─────────────────────────────────────────────────────────────────
def render_result_card(text: str, css_class: str):
    st.markdown(
        f'<div class="card {css_class}"><div class="card-body">{text}</div></div>',
        unsafe_allow_html=True,
    )


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">✍️ AI Копирайтер</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Загрузи фото товара → получи тексты для Instagram, Kaspi и сайта</div>',
    unsafe_allow_html=True,
)
st.divider()

# ── Layout ─────────────────────────────────────────────────────────────────────
col_input, col_output = st.columns([1, 1.4], gap="large")

with col_input:
    st.markdown("#### 📸 Фото товара")
    uploaded_file = st.file_uploader(
        label="Перетащи или выбери файл",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
    )

    # ── Image preview ──────────────────────────────────────────────────────────
    if uploaded_file:
        st.image(uploaded_file, use_container_width=True)

    st.markdown("#### 🏷️ Ключевые слова")
    keywords = st.text_input(
        label="Ключевые слова",
        placeholder="напр.: беспроводные наушники, шумоподавление, 30 часов работы",
        label_visibility="collapsed",
    )

    st.markdown("")
    generate_btn = st.button("⚡ Сгенерировать тексты", use_container_width=True)

with col_output:
    st.markdown("#### 📋 Результат")

    if generate_btn:
        if not uploaded_file:
            st.warning("⚠️ Загрузи изображение товара.")
        elif not keywords.strip():
            st.warning("⚠️ Добавь хотя бы несколько ключевых слов.")
        else:
            with st.spinner("GPT-4o анализирует товар..."):
                try:
                    result, usage = generate_copy(uploaded_file, keywords)

                    # Обновляем счётчик токенов
                    st.session_state.last_usage = usage
                    st.session_state.total_input_tokens  += usage["input"]
                    st.session_state.total_output_tokens += usage["output"]

                    # ── Tabs ───────────────────────────────────────────────────
                    tab_insta, tab_kaspi, tab_site = st.tabs(
                        ["📱 Instagram", "🛒 Kaspi", "🌐 Сайт"]
                    )

                    with tab_insta:
                        render_result_card(result.get("instagram", "—"), "card-insta")

                    with tab_kaspi:
                        render_result_card(result.get("kaspi", "—"), "card-kaspi")

                    with tab_site:
                        render_result_card(result.get("website", "—"), "card-website")

                    st.download_button(
                        label="⬇️ Скачать JSON",
                        data=json.dumps(result, ensure_ascii=False, indent=2),
                        file_name="copy_result.json",
                        mime="application/json",
                    )

                    st.rerun()  # обновляем sidebar с новыми токенами

                except openai.AuthenticationError:
                    st.error("❌ Неверный API-ключ. Проверь `.streamlit/secrets.toml`.")
                except openai.RateLimitError:
                    st.error("❌ Превышен лимит OpenAI. Подожди немного.")
                except json.JSONDecodeError:
                    st.error("❌ Модель вернула невалидный JSON. Попробуй ещё раз.")
                except Exception as e:
                    st.error(f"❌ Ошибка: {e}")
    else:
        st.markdown(
            """
            <div style="
                background:#1a1a22;
                border:1px dashed #2e2e3a;
                border-radius:16px;
                padding:48px 24px;
                text-align:center;
                color:#555;
            ">
                <div style="font-size:2.5rem">🤖</div>
                <div style="margin-top:12px;font-size:0.9rem">
                    Результаты появятся здесь
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
