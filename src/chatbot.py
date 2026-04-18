import os, json, re, time
import numpy as np
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from sklearn.metrics.pairwise import cosine_similarity
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_collection("ds_knowledge")

llm = ChatGroq(
    groq_api_key=api_key,
    model_name="llama-3.1-8b-instant",
    temperature=0.3
)

analyzer = SentimentIntensityAnalyzer()

chat_history = []
MAX_HISTORY = 5

SYSTEM_PROMPT = """You are a friendly Data Science tutor. Answer ONLY using the provided context. Use simple language. If answer not found, say you don't know."""

def retrieve_context(question, n_results=4):
    query_vec = embed_model.encode([question]).tolist()
    results = collection.query(query_embeddings=query_vec, n_results=n_results)
    chunks = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
    context = "\n\n---\n\n".join(chunks)
    return context, sources

def ask_bot(question, history=[]):
    context, sources = retrieve_context(question)
    user_msg = HumanMessage(content=f"Context:\n{context}\n\nQuestion: {question}")
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    if history:
        messages += history
    messages.append(user_msg)
    response = llm.invoke(messages)
    return response.content, sources

def chat_with_memory(question):
    global chat_history
    answer, sources = ask_bot(question, chat_history)
    chat_history.append(HumanMessage(content=question))
    chat_history.append(AIMessage(content=answer))
    if len(chat_history) > MAX_HISTORY * 2:
        chat_history = chat_history[-MAX_HISTORY * 2:]
    return answer, sources

def reset_memory():
    global chat_history
    chat_history = []

def get_encouragement(text):
    score = analyzer.polarity_scores(text)["compound"]
    if score < -0.5:
        return "I understand it's difficult. Let me explain simply.\n\n", score
    elif score < -0.2:
        return "No worries, let's go step by step.\n\n", score
    return "", score

def chat_with_sentiment(question):
    prefix, score = get_encouragement(question)
    answer, sources = chat_with_memory(question)
    return prefix + answer, sources, score

RELEVANCE_THRESHOLD = 0.28

def is_relevant(question):
    q_vec = embed_model.encode([question])
    res = collection.query(query_embeddings=q_vec.tolist(), n_results=1, include=["embeddings"])
    top_vec = np.array(res["embeddings"][0][0]).reshape(1, -1)
    sim = cosine_similarity(q_vec, top_vec)[0][0]
    return float(sim) >= RELEVANCE_THRESHOLD, round(float(sim), 3)

def safe_chat(question):
    ok, sim = is_relevant(question)

    prefix, score = get_encouragement(question)

    if not ok and prefix == "":
        return "I don't have enough information on this topic.", [], sim

    answer, sources, _ = chat_with_sentiment(question)
    return answer, sources, sim

QUIZ_PROMPT = """Generate 3 multiple choice questions about: {topic}
Return ONLY valid JSON:
[{{"question":"...","options":["A) ...","B) ...","C) ...","D) ..."],
"answer":"A","explanation":"..."}}]"""

def generate_quiz(topic):
    response = llm.invoke([
        HumanMessage(content=QUIZ_PROMPT.format(topic=topic))
    ])
    
    match = re.search(r'\[.*\]', response.content, re.DOTALL)
    
    if match:
        try:
            return json.loads(match.group())
        except:
            return []
    
    return []
