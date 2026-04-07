# Topic Shift 🧠📄

![Topic Shift Banner](banner.png)




**Topic Shift** is a modern, full-stack application designed to automatically extract topics, conceptual contents, and relationships from lecture slides and PDF documents. It transforms unstructured educational materials into interactive, easily digestible knowledge graphs.

This tool was built to help students, researchers, and educators visualize complex topics, identify key themes, and understand the underlying connections between different concepts presented in slide decks.

## ✨ Features

- **Advanced PDF Parsing**: Leverages IBM's `docling` to intelligently parse PDF layouts, including tables and structured text, optimized specifically for presentation slides.
- **AI-Powered NLP Pipeline**: Utilizes `haystack-ai` and OpenAI embeddings to process, clean, and semantically embed document segments.
- **Concept Clustering**: Automatically groups related concepts and slides together using semantic embeddings.
- **Relationship Extraction**: Classifies and extracts logical relationships between different conceptual clusters.
- **Interactive Knowledge Graphs**: Visualizes the extracted topics and their relationships using a highly interactive, node-based graph powered by `Vue Flow`.
- **Asynchronous Processing**: Implements non-blocking background task execution using FastAPI, ensuring a seamless user experience even when processing large, multi-page PDFs.
- **Local Storage**: Employs lightweight local data persistence using `TinyDB` for managing task states, clusters, and graph relations.

## 🛠️ Tech Stack

**Backend (Python 3.11+)**
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **AI & NLP**: [Haystack AI](https://haystack.deepset.ai/), [Docling](https://github.com/DS4SD/docling), OpenAI API
- **Database**: [TinyDB](https://tinydb.readthedocs.io/)
- **Package Management**: [Poetry](https://python-poetry.org/)

**Frontend (TypeScript)**
- **Framework**: [Vue 3](https://vuejs.org/) (Composition API)
- **Build Tool**: [Vite](https://vitejs.dev/)
- **Graph Visualization**: [Vue Flow](https://vueflow.dev/)
- **Styling**: [TailwindCSS](https://tailwindcss.com/) & [reka-ui](https://github.com/wobsoriano/reka-ui)

## 🚀 Getting Started

### Prerequisites

- **Python** `>= 3.11, < 3.13`
- **Node.js** `>= 18.x`
- **Poetry** (Python package manager)
- **OpenAI API Key** (Required for document embeddings and relationship classification)

### Backend Setup

1. Clone the repository and navigate to the project root:
   ```bash
   cd topic_shift
   ```

2. Install the backend dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Set up your environment variables. You will need an OpenAI API key for the embedding pipeline:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   ```

4. Start the FastAPI development server:
   ```bash
   poetry run uvicorn src.api:app --reload
   ```
   *The API will be available at `http://localhost:8000`. You can view the Swagger UI documentation at `http://localhost:8000/docs`.*

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install the frontend dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   *The frontend will be available at `http://localhost:5173`.*

## 🏗️ Architecture & AI Pipeline

Topic Shift processes documents through a highly optimized data pipeline orchestrated by Haystack:

1. **Ingestion & Conversion**: The uploaded PDF is processed by the `DoclingConverter`, which accurately extracts text while respecting document layout.
2. **Cleaning**: A `DocumentCleaner` removes unwanted artifacts, extra whitespaces, and specific user-defined substrings.
3. **Embedding**: Cleaned document segments are embedded using `OpenAIDocumentEmbedder` to capture their semantic meaning in vector space.
4. **Clustering**: The custom `EmbeddingClusteringComponent` groups conceptually similar document segments into coherent topics.
5. **Relationship Classification**: The `RelationshipClassificationComponent` analyzes the clusters to determine how different topics correlate and connect to each other.
6. **Graph Generation**: The resulting relationships and clusters are mapped into a directional graph structure, persisted in TinyDB, and served to the Vue frontend for interactive visualization.

## 👤 Author

**Linus Bierhoff** 
- Email: mail@linusbierhoff.com
