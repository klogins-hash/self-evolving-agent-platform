# Self-Evolving Agent Platform - MVP

A self-evolving AI agent platform that builds and manages its own agent swarm with dual-agent architecture.

## 🚀 **LIVE DEMO** 

**✅ Currently deployed and running:**
- **Backend API**: http://51.15.214.182:8000
- **Frontend UI**: http://51.15.214.182:8001  
- **API Docs**: http://51.15.214.182:8000/docs

## 🚀 Quick Start (Docker)

```bash
# Clone and setup
git clone https://github.com/klogins-hash/self-evolving-agent-platform.git
cd self-evolving-agent-platform

# One-command deployment
make deploy

# Or manual Docker commands
docker-compose up --build -d
```

**Alternative: Manual Setup**
```bash
# Backend setup (if not using Docker)
cd backend && pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# Frontend setup (new terminal)
cd frontend && pip install -r requirements.txt
chainlit run app.py
```

## 📁 Project Structure

```
mvp/
├── README.md                 # This file
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app entry point
│   │   ├── core/            # Core business logic
│   │   ├── agents/          # Agent management
│   │   ├── api/             # API routes
│   │   └── models/          # Data models
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 # Chainlit UI
│   ├── app.py               # Chainlit app entry point
│   ├── components/          # UI components
│   ├── requirements.txt
│   └── Dockerfile
├── shared/                   # Shared utilities
│   ├── __init__.py
│   ├── config.py            # Configuration management
│   └── utils.py             # Common utilities
├── docs/                     # Documentation
│   ├── api.md               # API documentation
│   ├── architecture.md      # Architecture overview
│   └── deployment.md        # Deployment guide
├── tests/                    # Test suite
│   ├── backend/
│   ├── frontend/
│   └── integration/
├── scripts/                  # Utility scripts
│   ├── setup.sh             # Environment setup
│   └── deploy.sh            # Deployment script
├── docker-compose.yml        # Local development
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
└── pyproject.toml           # Python project configuration
```

## 🏗️ Architecture Overview

### Dual-Agent Architecture
- **Chief of Staff (CoS)**: Orchestrates and manages agent swarm
- **Master Operator (MO)**: Executes tasks and operations

### Core Features (MVP)
- [ ] Agent creation and management
- [ ] Basic dual-agent communication
- [ ] Simple task orchestration
- [ ] Web-based UI with Chainlit
- [ ] RESTful API backend
- [ ] Configuration management

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.11+
- **Frontend**: Chainlit (AI-native UI framework)
- **Database**: SQLite (MVP), PostgreSQL (production)
- **AI/ML**: OpenRouter (auto model selection), Groq, OpenAI API, LangChain
- **Deployment**: Docker, Docker Compose

## 📋 Development Phases

### Phase 1: MVP (Current)
- Basic agent framework
- Simple UI interface
- Core API endpoints
- Local development setup

### Phase 2: Intelligence (Future)
- Advanced agent capabilities
- Self-evolution mechanisms
- Enhanced UI features
- Multi-user support

### Phase 3: Scale (Future)
- Production deployment
- Advanced security
- Performance optimization
- Enterprise features

## 🔧 Configuration

Copy `.env.example` to `.env` and configure:

```bash
# API Keys
OPENROUTER_API_KEY=your_openrouter_key
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Database
DATABASE_URL=sqlite:///./agents.db

# Security
SECRET_KEY=your_secret_key
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/backend/
pytest tests/frontend/
pytest tests/integration/
```

## 📚 Documentation

- [API Documentation](docs/api.md)
- [Architecture Overview](docs/architecture.md)
- [Deployment Guide](docs/deployment.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**Built with ❤️ for the future of AI agents**
