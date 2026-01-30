# 📚 Semantic Book Recommender

A production-ready semantic book recommendation system using OpenAI embeddings with an intuitive web interface.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.13%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Features

### 🔍 Smart Search
- **Semantic search** - Find books by describing what you want in natural language
- **Category filtering** - Filter by Fiction, Non-fiction, etc.
- **Emotional tone** - Sort by mood (Happy, Suspenseful, Sad, etc.)
- **Fast results** - In-memory caching for instant repeat searches

### 👤 User Features
- **Search history** - Track all your searches automatically
- **Favorites** - Save books you're interested in
- **User statistics** - See your search patterns and favorites count

### 🎨 Modern UI
- **Tabbed interface** - Organized Search, History, Favorites, and Settings tabs
- **Book details** - Click any book to see full information
- **Visual feedback** - Stars (⭐/☆) show favorite status
- **Responsive design** - Works on desktop and mobile

---

## 🚀 Quick Start

### Option 1: Local Development (Recommended for Development)

**Prerequisites:**
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager
- OpenAI API key

**Steps:**

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd llm_semantic_book_recommender

# 2. Create environment file
cp .env.example .env

# 3. Add your OpenAI API key to .env
# Edit .env and add: OPENAI_API_KEY=your_key_here

# 4. Install dependencies
uv sync

# 5. Initialize database
uv run python scripts/setup_db.py

# 6. Run the application
uv run python -m src.ui.app

# 7. Open your browser
# Navigate to http://localhost:7860
```

### Option 2: Docker Deployment (Recommended for Production)

**Prerequisites:**
- Docker
- Docker Compose
- OpenAI API key

**Steps:**

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd llm_semantic_book_recommender

# 2. Create environment file
cp .env.example .env

# 3. Add your OpenAI API key to .env
# Edit .env and add: OPENAI_API_KEY=your_key_here

# 4. Build and run with Docker Compose
docker-compose up -d

# 5. View logs (optional)
docker-compose logs -f

# 6. Open your browser
# Navigate to http://localhost:7860

# 7. Stop the application
docker-compose down
```


## 📖 How to Use

### Search for Books

1. **Go to the Search tab** 🔍
2. **Enter a description** of what you're looking for
   - Example: "A mystery thriller with unexpected twists"
   - Example: "A heartwarming story about friendship"
3. **Apply filters** (optional):
   - Category: Fiction, Non-fiction, etc.
   - Tone: Happy, Suspenseful, Sad, etc.
4. **Click "Search Books"**
5. **Browse results** in the gallery

### View Book Details

1. **Click on any book** in the search results
2. **See details** including:
   - Full description
   - Authors
   - Category
   - ISBN
   - Emotion scores
   - Favorite status

### Add to Favorites

1. **In the Search tab**, click a book
2. **Click "Add to Favorites"** button
3. **Star appears** on the book cover (⭐)

### View Favorites

1. **Go to the Favorites tab** ⭐
2. **See all your favorited books**
3. **Click a book** to see details
4. **Click "Remove from Favorites"** to unfavorite

### Check History

1. **Go to the History tab** 📜
2. **View all past searches** in a table
3. **See filters used** and results count
4. **Track when** you searched


## 🛠️ Tech Stack

### Core
- **Python 3.13+** - Modern Python with latest features
- **uv** - Fast Python package manager
- **Gradio** - Web UI framework

### AI & Embeddings
- **OpenAI API** - text-embedding-3-small model (1536 dimensions)
- **LangChain** - Framework for LLM applications
- **ChromaDB** - Vector database for semantic search

### Data & Storage
- **SQLAlchemy** - Database ORM
- **SQLite** - User data storage
- **Pandas** - Data processing
- **Pydantic** - Data validation

### Deployment
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration


## 📁 Project Structure

```
llm_semantic_book_recommender/
├── src/                          # Application source code
│   ├── config/                   # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py          # Pydantic settings
│   ├── core/                     # Core utilities
│   │   ├── __init__.py
│   │   └── exceptions.py        # Custom exceptions
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   └── database.py          # SQLAlchemy models
│   ├── services/                 # Business logic
│   │   ├── __init__.py
│   │   ├── embeddings.py        # OpenAI embedding service
│   │   ├── recommendations.py   # Book search logic
│   │   ├── user_data.py         # User management
│   │   └── cache.py             # In-memory caching
│   └── ui/                       # User interface
│       ├── __init__.py
│       └── app.py               # Gradio application
├── scripts/                      # Utility scripts
│   ├── setup_db.py              # Database initialization
│   └── check_vector_store.py   # Vector store validation
├── tests/                        # Test suite
│   ├── __init__.py
│   └── test_embeddings.py      # Service tests
├── data/                         # User database (gitignored)
├── vector_store/                 # ChromaDB data (gitignored)
├── logs/                         # Application logs (gitignored)
├── assets/                       # UI assets
├── Dockerfile                    # Docker image definition
├── docker-compose.yml           # Docker Compose config
├── .dockerignore                # Docker ignore rules
├── pyproject.toml               # Python dependencies
├── uv.lock                      # Locked dependencies
├── .env.example                 # Example environment variables
└── README.md                    # This file
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional - Customize if needed
DATABASE_PATH=./data/app.db
VECTOR_STORE_PATH=./vector_store
LOG_FILE=./logs/app.log
CACHE_TTL=3600

# Optional - OpenAI Settings
OPENAI_MAX_RPM=3000
OPENAI_MAX_RPD=1000000

# Optional - UI Settings
GRADIO_SERVER_NAME=0.0.0.0
GRADIO_SERVER_PORT=7860
GRADIO_SHARE=false
```

### Getting an OpenAI API Key

1. Go to [platform.openai.com](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new secret key
5. Copy and paste into your `.env` file

---

## 💰 Cost Estimation

### OpenAI API Costs

Using `text-embedding-3-small` model:

| Usage | Embeddings | Cost |
|-------|-----------|------|
| **Per search** | 1 embedding | ~$0.000002 |
| **100 searches** | 100 embeddings | ~$0.0002 |
| **1,000 searches** | 1,000 embeddings | ~$0.002 |
| **10,000 searches** | 10,000 embeddings | ~$0.02 |

**With caching (60%+ hit rate):**
- 10,000 searches → ~4,000 actual API calls → **~$0.008**

**Extremely cost-effective!** 💰

## 🐳 Docker Details

### Build Image

```bash
docker build -t book-recommender .
```

### Run Container

```bash
docker run -d \
  -p 7860:7860 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/vector_store:/app/vector_store \
  -v $(pwd)/logs:/app/logs \
  -e OPENAI_API_KEY=your_key_here \
  --name book-recommender \
  book-recommender
```

### Useful Commands

```bash
# View logs
docker-compose logs -f

# Restart application
docker-compose restart

# Stop application
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# Access container shell
docker-compose exec app /bin/bash
```


## 🧪 Testing

### Run Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest tests/test_embeddings.py -v
```

### Check Vector Store

```bash
# Verify vector store is working
uv run python scripts/check_vector_store.py
```

## 📊 Performance

### Caching Benefits

- **First search**: ~2.5 seconds (API call + vector search)
- **Cached search**: ~0.01 seconds (instant!)
- **Expected hit rate**: 60-70% for typical usage


## 🔧 Troubleshooting

### Application won't start

**Check environment:**
```bash
# Verify .env file exists
cat .env

# Check if OPENAI_API_KEY is set
grep OPENAI_API_KEY .env
```

### Database errors

**Reinitialize database:**
```bash
# Remove existing database
rm -rf data/app.db

# Reinitialize
uv run python scripts/setup_db.py
```

### Vector store errors

**Check vector store:**
```bash
# Validate vector store
uv run python scripts/check_vector_store.py

# Ensure vector_store directory exists
ls -la vector_store/
```

### Docker issues

**Check logs:**
```bash
# View application logs
docker-compose logs -f app

# Check if containers are running
docker-compose ps
```

**Rebuild from scratch:**
```bash
# Stop and remove everything
docker-compose down -v

# Rebuild and start
docker-compose up -d --build
```


## 📚 Documentation

- **[Week 1 Completion](WEEK1_COMPLETION.md)** - Foundation and OpenAI integration
- **[Week 2 Completion](WEEK2_COMPLETION.md)** - Service layer and caching
- **[Week 3 Completion](WEEK3_COMPLETION.md)** - UI enhancement and features
- **[Quick Start Guide](QUICKSTART.md)** - 5-minute setup
- **[Migration Guide](MIGRATION_TO_OPENAI.md)** - Gemini to OpenAI transition


## 🚧 Development

### Adding New Features

1. **Create feature branch**
2. **Add code in appropriate module** (src/services/, src/ui/, etc.)
3. **Write tests** in tests/
4. **Update documentation**
5. **Test locally**
6. **Submit PR**

### Code Style

```bash
# Format code (if using black)
black src/

# Lint code (if using ruff)
ruff check src/

# Type check (if using mypy)
mypy src/
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request


## 📄 License

MIT License - Feel free to use this for your own projects!


## 🎯 Roadmap

### Completed ✅
- [x] OpenAI embeddings integration
- [x] Semantic search with filtering
- [x] User features (history, favorites)
- [x] Tabbed Gradio UI
- [x] In-memory caching
- [x] Docker containerization
- [x] Comprehensive documentation

### Future Enhancements 🔮
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Recommendation explanations
- [ ] Social features (share favorites)
- [ ] Mobile app
- [ ] REST API
- [ ] Book cover uploads
- [ ] Reading progress tracking

## 🙏 Acknowledgments

- **OpenAI** for the embeddings API
- **ChromaDB** for vector storage
- **Gradio** for the amazing UI framework
- **Kaggle** for the books dataset

---

**Ready to find your next great read?** 🚀

```bash
# Get started in 3 commands:
cp .env.example .env
# Add OPENAI_API_KEY to .env
docker-compose up -d
```

**Happy Reading!** 📚✨