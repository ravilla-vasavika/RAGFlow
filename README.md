# 🚀 RAGFlow – End-to-End Retrieval-Augmented Generation System

RAGFlow is a full-stack **Retrieval-Augmented Generation (RAG)** application that enables users to upload documents, process them into embeddings, and query them using a conversational AI interface.

It combines **LLMs + Vector Search + Modern UI** to deliver accurate, context-aware answers from your own data.

---

## 🧠 Features

### 🔹 Backend (FastAPI + LangChain)

* 📄 Document ingestion pipeline (PDF upload)
* ✂️ Intelligent chunking with overlap
* 🧠 Embedding generation
* 🗄️ FAISS vector store integration
* 🔍 Similarity-based retrieval
* 🧾 Metadata tracking (document-level filtering)
* 💬 LLM-powered query answering

---

### 🔹 Frontend (React + TypeScript + Tailwind)

* 💬 Chat-based interface
* 📤 Drag-and-drop file upload
* 📚 Document management panel
* 🧩 Chunk viewer for retrieved context
* ⚡ Real-time query responses

---

## 🏗️ Architecture

```
User Query
    ↓
Frontend (React UI)
    ↓
Backend API (FastAPI)
    ↓
Retriever (FAISS Vector DB)
    ↓
Relevant Chunks
    ↓
LLM (OpenAI)
    ↓
Final Answer
```

---

## ⚙️ Tech Stack

### 🔹 Backend

* FastAPI
* LangChain
* FAISS
* OpenAI API
* SQLite (metadata storage)

### 🔹 Frontend

* React (Vite)
* TypeScript
* Tailwind CSS
* Axios

---

## 📂 Project Structure

```
RAGFlow/
│
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── services/     # ingestion, retrieval, embeddings
│   │   ├── models/       # schemas
│   │   ├── utils/        # logger, db
│   │   └── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── api/
│   │   ├── store/
│   │   └── App.tsx
│   └── package.json
│
├── data/                 # (ignored) vector DB + metadata
├── logs/                 # (ignored)
└── README.md
```

---

## 🚀 Getting Started

### 🔹 1. Clone the Repo

```bash
git clone https://github.com/ravilla-vasavika/RAGFlow.git
cd RAGFlow
```

---

### 🔹 2. Backend Setup

```bash
cd backend

python -m venv .venv
source .venv/bin/activate   # Mac/Linux
# .venv\Scripts\activate    # Windows

pip install -r requirements.txt
```

Create `.env` file:

```
OPENAI_API_KEY=your_api_key
```

Run backend:

```bash
uvicorn app.main:app --reload
```

---

### 🔹 3. Frontend Setup

```bash
cd frontend

npm install
npm run dev
```

---

## 💡 Usage

1. Upload documents (PDFs)
2. System performs ingestion:

   * chunking
   * embedding
   * storage in FAISS
3. Ask questions in chat
4. System retrieves relevant chunks and generates answers

---

## 🔍 Example Query

> “What are the symptoms of asthma?”

👉 RAGFlow:

* Retrieves relevant chunks from documents
* Passes context to LLM
* Generates accurate answer

---

## ⚠️ Important Notes

* `data/` and `logs/` are excluded via `.gitignore`
* FAISS index is generated dynamically
* Do NOT commit API keys

---

## 🔥 Future Improvements

* 🔄 Streaming responses
* 📊 Retrieval evaluation metrics
* 🧠 Re-ranking models
* 🌐 Multi-document filtering UI
* ☁️ Deployment (Docker + Cloud)

---

## 👤 Author

**Vasavika Ravilla**

---

## ⭐ Why This Project?

This project demonstrates:

* End-to-end RAG pipeline design
* LLM + vector database integration
* Full-stack AI application development
* Production-level architecture understanding

---

## 📜 License

This project is open-source and available under the MIT License.
