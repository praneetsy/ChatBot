# Nexteer AI Dispatcher

An intelligent chat system that routes queries to specialized AI agents, built with Next.js, FastAPI, and LangChain.

## Features

- 💬 Real-time chat interface with agent switching
- 🤖 Intelligent query routing to specialized agents
- 📝 Document metadata extraction and processing
- 🎨 Clean, professional design with Tailwind CSS
- 📱 Fully responsive interface
- ⚡ Local LLM support via LM Studio
- 🔄 Multi-agent conversation handling

## Quick Start

### Prerequisites
- Node.js (v16.0.0 or higher)
- Python (v3.9 or higher)
- npm (v7.0.0 or higher)

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

OR 

Use docker compose to run the frontend and backend together


### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.tx

fastapi dev app.py
```

OR 

Use docker compose to run the frontend and backend together

### LM Studio Setup - IMPORTANT
Download LM Studio from [here](www.lmstudio.ai) and do the following steps:
1. Go in discover tab and download the mode `qwen2.5-coder-7b-instruct`
2. Go in developer tab and load the model `qwen2.5-coder-7b-instruct` with the model identifier `qwen2.5-coder-7b-instruct`
3. Ensure the server is running on port 1234 and has just in time model loading enabled


Optionally, to use Open AI API, change the env variables in app.py 

## Environment Variables

### Frontend (.env)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env)
```env
OPENAI_BASE_URL=http://localhost:1234/v1  # For LM Studio
OPENAI_API_KEY=test                       # For LM Studio
MODEL_NAME=nomic-embed-text-v1.5          # Embedding model
AGENT_MODEL_NAME=qwen2.5-coder-7b-instruct # Agent Model
SQLITE_DB_PATH=./database/vector_store.db  # Vector store location
```

## Tech Stack

### Frontend
- Next.js 15
- TypeScript
- Tailwind CSS
- Radix UI Components
- ShadcN UI

### Backend
- FastAPI
- LangChain
- SQLite
- LM Studio / OpenAI API
- Custom HTTP Embeddings

## API Endpoints

### GET /
- Health check endpoint
- Returns: `{"Hello": "World"}`

### POST /metadata
- Extracts metadata from documents
- Parameters:
  - `agent_name`: Name of the agent
  - `text`: Document text
- Returns: Status of operation

### GET /agents/triage
- Routes query to appropriate agent
- Parameters:
  - `query`: User's question
- Returns: 
  - `relevant_agent`: Primary agent for handling query
  - `other_agents`: Alternative agents that might help
  - `conversation_history`: Previous messages
  - `switched`: Boolean indicating if agent was switched

### GET /agents/search
- Performs similarity search across documents
- Parameters:
  - `query`: Search query
  - `top_k`: Number of results (default: 3)
- Returns: List of relevant documents with scores

## Project Structure

```
.
├── frontend/
│   ├── src/
│   │   ├── app/            # Next.js app router
│   │   ├── components/     # React components
│   │   └── lib/            # Utility functions
│   └── public/             # Static assets
│
└── backend/
    ├── agent/              # AI agent implementations
    │   ├── __init__.py
    │   ├── base.py         # Base agent class
    │   ├── triage.py       # Triage agent implementation
    │   └── router.py       # Agent routing logic
    ├── embeddings/         # Embedding implementations
    │   ├── __init__.py
    │   └── http.py         # HTTP-based embedding model
    ├── database/           # Database implementations
    │   ├── __init__.py
    │   └── vector_store.py # SQLite VSS implementation
    ├── documents/          # Document processing
    │   ├── __init__.py
    │   ├── embeddings.py   # Embedding model
    │   └── metadata.py     # Metadata extraction
    └── app.py              # FastAPI application
    └── requirements.txt    # Dependencies
```

## Development Commands

### Frontend
- `npm run dev` - Start development server
- `npm run build` - Build production bundle
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Backend
- `fastapi run app.py` - Start development server

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is fully under Nexteer Automotive.