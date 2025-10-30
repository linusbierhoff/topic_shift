# Topic Shift 📚

An intelligent Python tool for automatic extraction of topics and content from PDF documents. Optimized for analyzing large lecture slides and educational materials.

## 🎯 Features

- **Intelligent Topic Extraction**: Uses OpenAI's GPT-5-mini with structured output for precise topic identification
- **Scalable for Large PDFs**: Chunking strategy for efficient processing of large documents
- **Context-aware Aggregation**: Summarization of related content under existing topics
- **Prioritization**: Automatic importance rating (High/Medium/Low)
- **FastAPI REST-API**: Easy integration via HTTP endpoints
- **Robust PDF Processing**: Support for complex PDF structures with PyMuPDF

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- OpenAI API Key

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd topic_shift

# Install dependencies
poetry install

# Set environment variables
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### Start the Server

```bash
poetry run python -m uvicorn src.app:app --reload
```

The server will then run at `http://localhost:8000`

## 🐳 Docker Deployment

You can run Topic Shift in Docker with dynamic mode selection (API or GUI).

### Build the Docker Image

```bash
docker build -t topic-shift .
```

### Run with API Mode (Default)

```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your-api-key-here \
  topic-shift api
```

The FastAPI server will be available at `http://localhost:8000`

### Run with GUI Mode (Streamlit)

```bash
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your-api-key-here \
  topic-shift gui
```

The Streamlit interface will be available at `http://localhost:8501`

### Environment Setup

Make sure to pass your OpenAI API key via the `-e` flag or create a `.env` file:

```bash
# Using environment file
docker run -p 8000:8000 \
  --env-file .env \
  topic-shift api
```

### Mount Local Files

To process local PDF files, mount a volume:

```bash
docker run -p 8000:8000 \
  -v /path/to/pdfs:/app/pdfs \
  -e OPENAI_API_KEY=your-api-key-here \
  topic-shift api
```

## 📖 API Documentation

### POST `/extract-topics`

Extracts topics from an uploaded PDF file.

**Parameters:**

- `description` (string, required): Context description of the PDF (e.g., "Lecture on Machine Learning Fundamentals")
- `file` (UploadFile, required): The PDF file to analyze

**Response:**

```json
[
  {
    "title": "Neural Networks",
    "importance": "high",
    "contents": [
      "Basic architecture and structure",
      "Forward and backward propagation",
      "Activation functions and their properties"
    ]
  },
  {
    "title": "Hyperparameter Optimization",
    "importance": "medium",
    "contents": [
      "Grid Search vs. Random Search comparison",
      "Best practices for learning rate and batch size"
    ]
  }
]
```

**Example with cURL:**

```bash
curl -X POST "http://localhost:8000/extract-topics" \
  -F "description=Machine Learning lecture script" \
  -F "file=@lecture.pdf"
```

**Example with Python:**

```python
import httpx

with open("lecture.pdf", "rb") as f:
    response = httpx.post(
        "http://localhost:8000/extract-topics",
        data={"description": "Lecture on Machine Learning"},
        files={"file": f}
    )
    topics = response.json()
```

## 📦 Dependencies

| Package   | Version  | Purpose                |
| --------- | -------- | ---------------------- |
| FastAPI   | ≥0.120.2 | REST-API Framework     |
| Pydantic  | ≥2.12.3  | Data Validation        |
| PyMuPDF   | ≥1.26.5  | PDF Parsing            |
| LangGraph | ≥1.0.1   | Workflow Orchestration |
| LangChain | ≥0.4.1   | LLM Framework          |
| OpenAI    | ≥1.0.1   | GPT-API Integration    |
| Loguru    | ≥0.7.3   | Structured Logging     |

## 🔐 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-...

# Optional: OpenAI API Base (for custom deployments)
OPENAI_API_BASE=https://api.openai.com/v1

# Optional: Logging Level
LOG_LEVEL=INFO
```

## 📝 Development

### Setup

```bash
# Install all dependencies including dev tools
poetry install

# Format code
poetry run black src/
```

### Logging

The project uses `loguru` for structured logging:

```python
from loguru import logger

logger.info("Initialization complete")
logger.warning("Page too small, merging")
logger.error("PDF parsing failed")
```

Logs are displayed on the console with:

- Timestamp
- Log level
- Module and function
- Message

## 🐛 Troubleshooting

### PDF parsing fails

- Ensure the PDF is not password protected
- Try opening the PDF with another tool
- Check file sizes and complexity

### OpenAI API errors

- Check your API key in `.env`
- Ensure you have credits assigned
- Check rate limits and quotas

### Topics are too general/too specific

- Adjust the `description` parameter
- Increase/decrease chunk size in `extract_topics()`
- Modify prompt instructions in `extract()`

## 📄 License

MIT License - see LICENSE file

## 👤 Author

**Linus Bierhoff**

- Email: mail@linusbierhoff.com

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📚 Weiterführende Ressourcen

- [FastAPI Dokumentation](https://fastapi.tiangolo.com/)
- [LangGraph Dokumentation](https://langchain-ai.github.io/langgraph/)
- [OpenAI API Referenz](https://platform.openai.com/docs/api-reference)
- [Pydantic Dokumentation](https://docs.pydantic.dev/)

---

**Last Updated:** October 2025
**Version:** 0.1.0
