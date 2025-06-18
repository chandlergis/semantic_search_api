# Semantic Search API

A FastAPI-based semantic search service with document processing and BM25 retrieval capabilities.

## Features

- Document upload and processing
- Text chunking and storage
- BM25 retrieval system
- User authentication
- Project management
- Document similarity matching

## Project Structure

```
semantic_search_api/
├── app/
│   ├── core/              # Core configurations
│   ├── db/                # Database models and sessions
│   ├── models/            # SQLAlchemy models
│   ├── routers/           # API route handlers
│   ├── schemas/           # Pydantic models
│   ├── services/          # Business logic
│   ├── utils/             # Utility functions
│   └── main.py            # FastAPI app
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## API Endpoints

- `/api/users` - User authentication
- `/api/documents` - Document management
- `/api/search` - Search operations
- `/api/projects` - Project management

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure database in `app/core/config.py`

3. Run with Docker:
```bash
docker-compose up -d --build
```

4. Test document processing:
```bash
curl -X POST -F "file=@path/to/mypdf.pdf" http://localhost:8500/process_file
