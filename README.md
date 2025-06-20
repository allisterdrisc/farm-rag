# 🌾 Farm-RAG: A Retrieval-Augmented Generation App for Farm Data

A Retrieval-Augmented Generation (RAG) system that allows users to ask questions about farm data sourced from PDFs. This application uses **LangChain**, **OpenAI GPT-4o**, and **pgvector** with **PostgreSQL** to retrieve and generate context-aware answers.

---

## What It Does

- Parses and processes PDF data about crops, harvests, and revenue
- Embeds the data using OpenAI and stores it in PostgreSQL with `pgvector`
- Enables users to query the data using natural language
- Returns intelligent, context-aware answers via a Flask API and React frontend

---

## Tech Stack

- **Backend:** Python, Flask, LangChain
- **AI/LLM:** OpenAI GPT-4o (via `openai` SDK)
- **Vector DB:** PostgreSQL with `pgvector`
- **PDF Parsing:** PyPDF2
- **Data Modeling:** Pydantic + Instructor
- **Frontend:** React + Vite
- **Environment Management:** `python-dotenv`
- **CORS Handling:** Flask-CORS

---

## Project Structure
```bash
farm-rag/
├── client/
│ └── src/
│ ├── components/
│ │ ├── MessageBox.jsx
│ │ └── QuestionForm.jsx
│ ├── App.css
│ ├── App.jsx
│ ├── index.css
│ ├── main.js
│ ├── services.js
│ ├── .gitignore
│ ├── index.html
│ ├── package.json
│ ├── package-lock.json
│ └── vite.config.js
├── server/
│ ├── data/
│ │ ├── full_farm_book.pdf
│ │ └── split_pdfs/
│ └── src/
│ ├── api.py # Flask API
│ ├── pre_processing.py # PDF parser + embedding pipeline
│ ├── rag_tools.py # Vector DB logic + query functions
│ └── farm_agent.py # LangChain agent logic
├── requirements.txt
├── .env # API keys (not committed)
├── .gitignore
└── README.md
```
---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/allisterdrisc/farm-rag.git
cd farm-rag
```

### 2. Set Up Python Virtual Environment (from project root)
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Backend Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create a .env file 
```env
OPENAI_API_KEY=your-openai-api-key
DATABASE_URL=postgresql://user:password@localhost:5432/yourdb
```

### 5. Pre-process the PDF Data
```bash
cd server/src
python pre_processing.py
```

### 6. Start the Backend Server
```bash
python api.py
```

### 7. Start the frontend
- In a separate terminal:
```bash
cd client
npm install
npm run dev
```

### 8. Access the App
- Once both servers are running, open your browser and go to:
http://localhost:5173/

## Future Improvements
- Support file uploads (for new PDF data)
- Add login/authentication
- Add user query history

## Author
Allister Driscoll
