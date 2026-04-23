"""
AI Programming Mentor — точка входа.
Только UI. Вся логика в src/brain.py.
"""

import json
import streamlit as st
from src.brain import MentorEngine

st.set_page_config(
    page_title="AI Ментор",
    page_icon="🧠",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Unbounded:wght@400;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Unbounded', cursive; }

.stApp { background-color: #07070f; color: #e2e2f0; }

.main-title {
    font-family: 'Unbounded', cursive;
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #8b5cf6, #22d3ee);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 2px;
}
.sub-title {
    color: #555;
    font-size: 0.82rem;
    margin-top: 4px;
    margin-bottom: 32px;
    letter-spacing: 0.5px;
}

.card {
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 12px;
}
.card-analysis   { background: #10101e; border: 1px solid #1e1e38; border-left: 3px solid #8b5cf6; }
.card-root       { background: #110d1a; border: 1px solid #2a1a38; border-left: 3px solid #e879f9; }
.card-concept    { background: #0d1a12; border: 1px solid #1a3022; border-left: 3px solid #34d399; }
.card-questions  { background: #0d1620; border: 1px solid #1a2c40; border-left: 3px solid #22d3ee; }
.card-steps      { background: #0f130d; border: 1px solid #1e2e1a; border-left: 3px solid #a3e635; }
.card-transurfing{ background: #18130a; border: 1px solid #3a2a10; border-left: 3px solid #fbbf24; }

.label {
    font-family: 'Unbounded', cursive;
    font-size: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 2.5px;
    margin-bottom: 10px;
    opacity: 0.8;
}
.card-analysis    .label { color: #8b5cf6; }
.card-root        .label { color: #e879f9; }
.card-concept     .label { color: #34d399; }
.card-questions   .label { color: #22d3ee; }
.card-steps       .label { color: #a3e635; }
.card-transurfing .label { color: #fbbf24; }

.body-text {
    font-size: 0.93rem;
    line-height: 1.8;
    color: #c8c8e0;
}
.question-item {
    background: #0a1520;
    border: 1px solid #1a3050;
    border-radius: 10px;
    padding: 13px 18px;
    margin-bottom: 9px;
    font-size: 0.95rem;
    color: #d0eeff;
    line-height: 1.65;
}
.question-num {
    font-family: 'Unbounded', cursive;
    font-size: 0.6rem;
    color: #22d3ee;
    opacity: 0.6;
    margin-bottom: 4px;
}

.stTextArea textarea {
    background: #10101e !important;
    border: 1px solid #1e1e38 !important;
    border-radius: 10px !important;
    color: #e2e2f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.83rem !important;
    line-height: 1.6 !important;
}
[data-testid="stFileUploader"] {
    background: #10101e;
    border: 1px dashed #1e1e38;
    border-radius: 12px;
}
div.stButton > button {
    background: linear-gradient(90deg, #8b5cf6, #22d3ee);
    color: #fff;
    font-family: 'Unbounded', cursive;
    font-size: 0.72rem;
    font-weight: 700;
    border: none;
    border-radius: 12px;
    padding: 14px 28px;
    width: 100%;
    letter-spacing: 1px;
    transition: opacity 0.2s, transform 0.1s;
}
div.stButton > button:hover { opacity: 0.88; transform: translateY(-1px); }
hr { border-color: #1a1a2e; }

.empty-state {
    background: #10101e;
    border: 1px dashed #1e1e38;
    border-radius: 16px;
    padding: 64px 24px;
    text-align: center;
    color: #3a3a5a;
}
</style>
""", unsafe_allow_html=True)

PRICE_IN  = 5.00  / 1_000_000
PRICE_OUT = 25.00 / 1_000_000

def calc_cost(inp: int, out: int) -> float:
    return inp * PRICE_IN + out * PRICE_OUT

for key, default in [
    ("total_in", 0), ("total_out", 0),
    ("last_usage", None), ("result", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

with st.sidebar:
    st.markdown("### 🧮 FinOps")
    st.caption("OpenRouter (бесплатно) · цены как у Claude Opus")

    if st.session_state.last_usage:
        u = st.session_state.last_usage
        c = calc_cost(u["input"], u["output"])
        st.markdown("**Последний запрос**")
        col1, col2 = st.columns(2)
        col1.metric("Вход", f"{u['input']:,} tok")
        col2.metric("Выход", f"{u['output']:,} tok")
        st.metric("Стоимость на Claude", f"${c:.5f}")
    else:
        st.info("Стоимость появится после первого запроса.")

    st.divider()
    total_cost = calc_cost(st.session_state.total_in, st.session_state.total_out)
    st.markdown("**За сессию**")
    st.metric("Всего токенов", f"{st.session_state.total_in + st.session_state.total_out:,}")
    st.metric("Итого (если бы Claude)", f"${total_cost:.5f}")

    if st.button("Сбросить счётчик"):
        st.session_state.total_in = 0
        st.session_state.total_out = 0
        st.session_state.last_usage = None
        st.rerun()

    st.divider()
    st.caption("Реально потрачено: $0.00 (OpenRouter)\nГипотетически Claude Opus:\n$5/1M in · $25/1M out")

st.markdown('<div class="main-title">🧠 AI Programming Mentor</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Сократический метод · Никакого готового кода · Только правильные вопросы</div>',
    unsafe_allow_html=True,
)
st.divider()

col_left, col_right = st.columns([1, 1.3], gap="large")

with col_left:
    st.markdown("#### 📸 Скриншот ошибки *(необязательно)*")
    screenshot = st.file_uploader(
        label="screenshot",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
    )
    if screenshot:
        st.image(screenshot, use_container_width=True)

    st.markdown("#### 💻 Твой код")
    code = st.text_area(
        label="code",
        placeholder="Вставь сюда код с ошибкой...",
        height=220,
        label_visibility="collapsed",
    )

    st.markdown("#### 💬 Что происходит?")
    context = st.text_area(
        label="context",
        placeholder="Опиши проблему своими словами. Что ожидал? Что получил?",
        height=100,
        label_visibility="collapsed",
    )

    st.markdown("")
    ask_btn = st.button("🔍 Спросить ментора", use_container_width=True)

with col_right:
    st.markdown("#### 💡 Ответ ментора")

    if ask_btn:
        if not code.strip() and screenshot is None and not context.strip():
            st.warning("⚠️ Добавь код, скриншот или описание проблемы.")
        else:
            with st.spinner("Ментор думает..."):
                try:
                    engine = MentorEngine(api_key=st.secrets["OPENROUTER_API_KEY"])
                    result, usage = engine.analyze(
                        code=code,
                        screenshot=screenshot,
                        extra_context=context,
                    )
                    st.session_state.result = result
                    st.session_state.last_usage = usage
                    st.session_state.total_in  += usage["input"]
                    st.session_state.total_out += usage["output"]
                    st.rerun()
                except Exception as e:
                    err = str(e).lower()
                    if "api_key" in err or "unauthorized" in err:
                        st.error("❌ Неверный API-ключ.")
                    elif "rate" in err or "quota" in err or "429" in err:
                        st.error("❌ Лимит API. Подожди немного и попробуй снова.")
                    else:
                        st.error(f"❌ Ошибка: {e}")

    if st.session_state.result:
        r = st.session_state.result

        st.markdown(
            f'<div class="card card-analysis">'
            f'<div class="label">🔎 Анализ</div>'
            f'<div class="body-text">{r.get("analysis", "—")}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if r.get("root_cause"):
            st.markdown(
                f'<div class="card card-root">'
                f'<div class="label">⚡ Корень проблемы</div>'
                f'<div class="body-text">{r["root_cause"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        if r.get("concept"):
            st.markdown(
                f'<div class="card card-concept">'
                f'<div class="label">📚 Концепция</div>'
                f'<div class="body-text">{r["concept"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        questions = r.get("questions", [])
        if questions:
            qs_html = "".join(
                f'<div class="question-item"><div class="question-num">ВОПРОС {i+1}</div>{q}</div>'
                for i, q in enumerate(questions)
            )
            st.markdown(
                f'<div class="card card-questions">'
                f'<div class="label">🤔 Подумай над этим</div>'
                f'{qs_html}'
                f'</div>',
                unsafe_allow_html=True,
            )

        if r.get("next_steps"):
            st.markdown(
                f'<div class="card card-steps">'
                f'<div class="label">🚀 Следующий шаг</div>'
                f'<div class="body-text">{r["next_steps"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        if r.get("has_stress") and r.get("transurfing_tip"):
            st.markdown(
                f'<div class="card card-transurfing">'
                f'<div class="label">🌊 Снижение потенциала</div>'
                f'<div class="body-text">{r["transurfing_tip"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.download_button(
            label="⬇️ Скачать сессию JSON",
            data=json.dumps(r, ensure_ascii=False, indent=2),
            file_name="mentor_session.json",
            mime="application/json",
        )

    elif not ask_btn:
        st.markdown(
            """
            <div class="empty-state">
                <div style="font-size:2.8rem">🧠</div>
                <div style="margin-top:14px;font-size:0.9rem;line-height:1.7">
                    Вставь код или скриншот ошибки<br>и получи структурированный разбор
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
