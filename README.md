# elearning-doubt-bot
This project is an AI-powered Data Science tutor developed using Retrieval-Augmented Generation (RAG). It is designed to answer student queries using a custom knowledge base of PDF documents, ensuring that responses are accurate, relevant, and grounded in curated learning material rather than general internet sources.

The system includes several key features that enhance the learning experience. It generates responses based on a RAG pipeline, maintains conversational context through memory, and adapts replies using sentiment-aware mechanisms. Additionally, it incorporates a hallucination guard to prevent irrelevant or out-of-scope answers, supports a quiz mode with multiple-choice questions and scoring, and provides source citations for transparency.

The application is built using a modern technology stack, including Llama 3 (via the Groq API) as the language model, LangChain as the framework, ChromaDB as the vector database, and sentence-transformers for embeddings. The user interface is developed using Streamlit, and deployment is handled through Hugging Face Spaces.

To run the project locally, install the required dependencies and launch the application using Streamlit. A .env file must be configured with the appropriate Groq API key for authentication.

The project follows a structured architecture, with the main application logic in app.py, supporting modules in the src directory, and vector storage managed through ChromaDB. The system is designed to respond strictly based on the provided knowledge base and returns a fallback response when relevant information is unavailable.

Future enhancements include expanding the knowledge base, integrating voice interaction, and improving user interface design and personalization features.
