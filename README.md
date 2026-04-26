# Fitness AI - Your Personal AI Fitness Coach

An AI-powered fitness app that creates personalized workout and diet plans using your own PDF knowledge base (RAG - Retrieval Augmented Generation).

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                        YOUR PDF FILES                           │
│  (workout plans, diet charts, nutrition guides, exercise PDFs)  │
└──────────────────────────┬──────────────────────────────────────┘
                           │ Ingest & Embed
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VECTOR DATABASE (ChromaDB)                    │
│         Searchable chunks of your PDF content                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │ Semantic Search
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RAG CHAIN (LangChain)                      │
│  User Query + Relevant PDF Chunks + User Profile → LLM → Plan  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PERSONALIZED RESPONSE                       │
│  Workout plan / Diet plan / Fitness advice based on YOUR PDFs   │
└─────────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python, FastAPI |
| **AI/RAG** | LangChain, OpenAI GPT-4o, ChromaDB |
| **Database** | PostgreSQL (users, chat history) |
| **Frontend** | React, TypeScript, Vite, Tailwind CSS |
| **Mobile** | React Native (Expo) — shares the same API |
| **Auth** | JWT + bcrypt |

## Features

- **AI Chat** — Free-form conversation about fitness, workouts, diet
- **Workout Plan Generator** — Form-based: pick goal, location (home/gym), experience level → get full plan
- **Diet Plan Generator** — Pick goal, diet type (veg/non-veg/vegan), calories → get meal plan
- **PDF Knowledge Base** — Upload your own workout/diet PDFs, the AI learns from them
- **User Profiles** — Age, weight, height, goals saved for personalization
- **Chat History** — Past conversations saved and searchable

## User Goals Supported

| Goal | Description |
|------|-------------|
| **Bulking** | Caloric surplus, heavy compound lifts, high protein |
| **Shredding** | Caloric deficit, high intensity, HIIT + weights |
| **Leaning** | Slight deficit, balanced approach, functional fitness |
| **General Fitness** | Maintenance, well-rounded program |
| **Weight Loss** | Significant deficit, circuit training, cardio focus |
| **Muscle Gain** | Hypertrophy focused, progressive overload |

## Project Structure

```
fitness-ai/
├── backend/
│   ├── app/
│   │   ├── ai/                  # AI/RAG engine
│   │   │   ├── ingestion.py     # PDF → chunks → vector DB
│   │   │   ├── rag_chain.py     # Query → search → LLM → answer
│   │   │   └── prompts.py       # Goal-specific prompt templates
│   │   ├── api/                 # REST API endpoints
│   │   │   ├── auth.py          # Login/Register
│   │   │   ├── users.py         # User profile CRUD
│   │   │   ├── chat.py          # AI chat + PDF upload
│   │   │   ├── workout.py       # Workout plan generation
│   │   │   └── diet.py          # Diet plan generation
│   │   ├── core/                # Config, DB, security
│   │   ├── models/              # SQLAlchemy models
│   │   └── schemas/             # Pydantic schemas
│   ├── data/pdfs/               # ← PUT YOUR PDF FILES HERE
│   ├── scripts/
│   │   └── ingest_pdfs.py       # CLI to ingest PDFs
│   └── pyproject.toml
├── frontend/
│   └── src/
│       ├── api/client.ts        # API client (axios)
│       ├── store/authStore.ts   # Auth state (zustand)
│       ├── components/Layout.tsx
│       └── pages/
│           ├── Chat.tsx         # AI chat interface
│           ├── Dashboard.tsx    # Home with quick actions
│           ├── WorkoutPlan.tsx  # Workout generator form
│           ├── DietPlan.tsx     # Diet generator form
│           ├── Profile.tsx      # User preferences
│           ├── Login.tsx
│           └── Register.tsx
└── README.md
```

## Getting Started

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -e .

# Copy env file and add your OpenAI API key
copy .env.example .env
# Edit .env → set OPENAI_API_KEY=sk-your-key

# Start PostgreSQL (use Docker or local install)
# Create database: fitness_ai

# Run the server
uvicorn app.main:app --reload
```

### 2. Ingest Your PDFs

```bash
# Place your workout/diet PDF files in backend/data/pdfs/
# Then run:
python -m scripts.ingest_pdfs

# Or upload via the API/frontend after starting the server
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

## What To Do With Your PDF Files

Your PDFs are the **knowledge base** for the AI. Here's how they're used:

1. **Place PDFs** in `backend/data/pdfs/` folder
2. **Run the ingestion script** — it reads all PDFs, splits text into chunks, and stores them as vector embeddings
3. **When a user asks a question**, the system searches these embeddings to find the most relevant chunks from your PDFs
4. **The LLM receives** these relevant chunks + the user's profile + the question, and generates a personalized plan

**Recommended PDF naming** (helps with auto-categorization):
- `workout_home_beginner.pdf`
- `workout_gym_advanced.pdf`
- `diet_vegetarian_bulking.pdf`
- `diet_nonveg_shredding.pdf`
- `nutrition_macros_guide.pdf`

## AI Provider Options

The app is set up for **OpenAI** by default, but you can switch:

| Provider | Cost | Setup |
|----------|------|-------|
| **OpenAI GPT-4o** (recommended) | ~$5-15/mo for personal use | Get API key from platform.openai.com |
| **Google Gemini** | Free tier available | Switch to `langchain-google-genai` |
| **Ollama (local)** | Free, runs on your machine | Switch to `langchain-ollama`, needs GPU |
| **Azure OpenAI** | Enterprise pricing | Switch to `langchain-openai` with Azure config |

## Next Steps

- [ ] Set up PostgreSQL database
- [ ] Get an OpenAI API key
- [ ] Place your PDF files in `backend/data/pdfs/`
- [ ] Run the ingestion script
- [ ] Start backend and frontend
- [ ] Create an account and set your profile
- [ ] Start chatting with the AI!

## Future Enhancements

- [ ] React Native mobile app (shares same API)
- [ ] Progress tracking (weight, measurements, PRs)
- [ ] Workout timer with exercise animations
- [ ] Social features (share plans, challenges)
- [ ] Integration with wearables (Apple Watch, Fitbit)
- [ ] Meal photo analysis (snap food → get macros)
