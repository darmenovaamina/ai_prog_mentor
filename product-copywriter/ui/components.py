import streamlit as st


def result_card(title: str, content: str) -> None:
    """Display generated copy in a styled card with a copy button."""
    st.markdown(f"### {title}")
    st.markdown(
        f"""
        <div style="
            background:#f8f9fa;
            border-left:4px solid #4A90D9;
            border-radius:6px;
            padding:16px 20px;
            font-size:15px;
            line-height:1.6;
            white-space:pre-wrap;
        ">{content}</div>
        """,
        unsafe_allow_html=True,
    )
    st.code(content, language=None)  # gives the one-click copy button


def error_banner(message: str) -> None:
    st.error(f"**Error:** {message}")
