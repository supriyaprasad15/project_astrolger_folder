import os
import streamlit as st
from google import genai

st.set_page_config(
    page_title="Supriya-Suvesh Astrology Chatbot",
    page_icon="🔮",
    layout="wide",
)

API_KEY = "AIzaSyCk4kBgR5jupDZXJKvP2UsmKnwXteKp0n8"

if not API_KEY:
    st.title("🔮 Supriya-Suvesh Astrology Chatbot")
    st.error(
        "Missing Google GenAI API key.\n"
        "Set `GENAI_API_KEY` as an environment variable locally or add it to Streamlit secrets."
    )
    st.markdown(
        "---\n"
        "Local example (PowerShell): `setx GENAI_API_KEY \"YOUR_KEY\"`\n"
        "Streamlit Cloud: add `GENAI_API_KEY` under Secrets and redeploy."
    )
    st.stop()

client = genai.Client(api_key=API_KEY)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def build_astrology_prompt(question: str, birth_date: str, birth_time: str, birth_place: str) -> str:
    return (
        "You are AstroGuide, a friendly astrology chatbot. "
        "Answer the user's astrology question clearly and respectfully, using the provided birth details when appropriate. "
        "If the user asks about personality, relationships, or general horoscopes, keep the response positive and practical. "
        "Do not provide medical, legal, or financial advice. "
        "Always remind the user that astrology is for entertainment and self-reflection.\n\n"
        f"Birth date: {birth_date}\n"
        f"Birth time: {birth_time}\n"
        f"Birth place: {birth_place}\n\n"
        f"User question: {question}\n"
        "Provide a thoughtful astrology-style answer."
    )


def generate_response(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text.strip()


def main() -> None:
    st.title("🔮 Supriya-Suvesh Astrology Chatbot")
    st.write(
        "Ask astrology questions, get horoscope-style answers, and explore personality insights based on your birth details."
    )

    with st.sidebar:
        st.header("Your birth details")
        birth_date = st.date_input("Birth date")
        birth_time = st.text_input("Birth time", "12:00")
        birth_place = st.text_input("Birth place", "City, Country")
        st.markdown("---")
        st.write(
            "Enter your birth data so the chatbot can provide more personalized astrology-style answers. "
            "These details are used only to shape the response narrative." 
        )

    with st.form(key="astrology_form", clear_on_submit=False):
        user_question = st.text_area(
            "Ask your astrology question",
            placeholder="Example: What does my week look like for love and career?",
            height=150,
        )
        submit_button = st.form_submit_button("Ask AstroGuide")

    if submit_button and user_question:
        prompt = build_astrology_prompt(
            question=user_question,
            birth_date=str(birth_date),
            birth_time=birth_time or "Unknown",
            birth_place=birth_place or "Unknown",
        )

        with st.spinner("AstroGuide is composing your answer..."):
            try:
                answer = generate_response(prompt)
            except Exception as exc:
                st.error(f"Failed to generate astrology response: {exc}")
                return

        st.session_state.chat_history.append(("You", user_question))
        st.session_state.chat_history.append(("AstroGuide", answer))

    if st.session_state.chat_history:
        for speaker, message in st.session_state.chat_history:
            if speaker == "You":
                st.markdown(f"**You:** {message}")
            else:
                st.markdown(f"**AstroGuide:** {message}")

    st.markdown("---")
    st.markdown(
        "**Tip:** Use this chatbot for entertainment and self-reflection. "
        "It does not replace professional astrology or personal guidance."
    )


if __name__ == "__main__":
    main()
