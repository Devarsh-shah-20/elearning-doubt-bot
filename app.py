from src.chatbot import safe_chat, reset_memory, chat_history, generate_quiz
import streamlit as st
import time
from src.chatbot import safe_chat, reset_memory, chat_history

st.set_page_config(
    page_title="DS Learning Bot",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
  .stChatMessage { border-radius: 12px; padding: 4px; }
  .source-tag { background:#E6F1FB; color:#0C447C; font-size:11px;
                padding:2px 8px; border-radius:99px; margin-right:4px; }
  .stButton > button { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# app.py — Part 2: Sidebar (paste below Part 1)
with st.sidebar:
    st.title("📚 DS Learning Bot")
    st.caption("Powered by Llama 3 + RAG")
    st.divider()
# Topic filter dropdown
    topic = st.selectbox(
        "📖 Study topic",
        ["All Topics", "Python Basics", "Statistics",
         "Machine Learning", "Deep Learning", "Pandas & NumPy"]
    )
# Mode toggle: Chat or Quiz
    mode = st.radio(
        "🎯 Mode",
        ["💬 Chat", "🧠 Quiz"],
        horizontal=True
    )
# Show sources toggle
    show_sources = st.toggle("Show sources", value=True)
    st.divider()
# Session stats
    q_count = len([m for m in st.session_state.get("messages", [])
                   if m["role"] == "user"])
    col1, col2 = st.columns(2)
    col1.metric("Questions", q_count)
    col2.metric("Topic", topic.split()[0])
    st.divider()
# Clear conversation button
    # Clear conversation button
if st.button("🗑️ Clear conversation", use_container_width=True):
    reset_memory()
    
    for key in ["messages", "quiz_questions", "quiz_answers", "quiz_submitted"]:
        if key in st.session_state:
            del st.session_state[key]
    
    st.rerun()
        # app.py — Part 3: Chat mode (paste below Part 2)
# Initialise message history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "💬 Chat" in mode:
    st.header("Data Science Tutor")
    st.caption("Ask me anything about Data Science from your knowledge base")
# Show welcome message if no history yet
    if not st.session_state.messages:
        st.info("👋 Hi! I'm your DS tutor. Ask me about ML, Python, "
                "Statistics, Neural Networks — anything in your study notes!")
# Render all past messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
# Show sources if toggle is on and message has sources
            if show_sources and msg.get("sources"):
                srcs = list(set(msg["sources"]))
                src_html = " ".join(
                    [f'<span class="source-tag">📄 {s}</span>'
                     for s in srcs])
                st.markdown(f"Sources: {src_html}",
                            unsafe_allow_html=True)
# Chat input box at bottom
    if prompt := st.chat_input("Ask your doubt here..."):
# Add user message to history and display it
        st.session_state.messages.append(
            {"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
# Get bot answer with spinner
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer, sources, sim = safe_chat(prompt)
            st.markdown(answer)
# Show sources below answer
            if show_sources and sources:
                srcs = list(set(sources))
                src_html = " ".join(
                    [f'<span class="source-tag">📄 {s}</span>'
                     for s in srcs])
                st.markdown(f"Sources: {src_html}",
                            unsafe_allow_html=True)
# Save assistant reply to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources
        })

        # app.py — Part 4: Quiz mode
elif "🧠 Quiz" in mode:
    st.header("Quiz Mode")
    st.caption("Test your Data Science knowledge")
# Topic input for quiz
    quiz_topic = st.text_input(
        "Enter topic for quiz",
        placeholder="e.g. decision trees, neural networks, pandas"
    )
# Generate quiz button
    if st.button("Generate Quiz", type="primary"):
        if not quiz_topic.strip():
            st.warning("Please enter a topic first!")
        else:
            with st.spinner("Generating questions..."):
                qs = generate_quiz(quiz_topic)
            if qs:
                st.session_state.quiz_questions = qs
                st.session_state.quiz_answers   = {}
                st.session_state.quiz_submitted = False
            else:
                st.error("Could not generate quiz. Try again.")
# Show quiz if generated
    if st.session_state.get("quiz_questions"):
        qs = st.session_state.quiz_questions
        for i, q in enumerate(qs):
            st.markdown(f"**Q{i+1}: {q['question']}**")
            chosen = st.radio(
                f"Select answer for Q{i+1}",
                q["options"],
                key=f"q_{i}",
                label_visibility="collapsed"
            )
            st.session_state.quiz_answers[i] = chosen[0]  
# first char = A/B/C/D
            st.divider()
# Submit button
        if st.button("Submit Quiz", type="primary"):
            score = 0
            for i, q in enumerate(qs):
                user_ans   = st.session_state.quiz_answers.get(i, "")
                correct    = q["answer"]
                if user_ans == correct:
                    st.success(f"Q{i+1}: Correct! ✓")
                    score += 1
                else:
                    st.error(f"Q{i+1}: Wrong. Correct: {correct}. {q['explanation']}")
            st.markdown(f"### Final Score: {score}/{len(qs)}")
            if score == len(qs):
                st.balloons() 

