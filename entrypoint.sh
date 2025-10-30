#!/bin/bash

# Get the mode from the first argument, default to 'api'
MODE="${1:-api}"

case "$MODE" in
  api)
    echo "🚀 Starting API server..."
    uvicorn src.api:app --host 0.0.0.0 --port 8000
    ;;
  gui)
    echo "🎨 Starting GUI application..."
    streamlit run src/gui.py --server.port 8501 --server.address 0.0.0.0
    ;;
  *)
    echo "❌ Unknown mode: $MODE"
    echo "Available modes:"
    echo "  - api    : Start FastAPI server (default)"
    echo "  - gui    : Start Streamlit GUI"
    echo ""
    echo "Usage: docker run topic-shift [MODE]"
    exit 1
    ;;
esac
