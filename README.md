# UTM Course Assistant 🎓

An intelligent course exploration system for UTM students, powered by advanced NLP and graph visualization.

![Uploading Screen Recording 2025-04-19 at 4.10.32 PM (4).gif…]()


## 🌟 Key Features

- **Intelligent Course Search**: Semantic search capabilities using BM25 retrieval
- **Interactive Course Graph**: Visual representation of course prerequisites and relationships
- **Smart Course Assistant**: DSPy-powered chatbot for course-related queries
- **Modern UI**: Responsive design with dark mode support

## 🛠️ Technology Stack

### Frontend
- React with TypeScript
- Tailwind CSS for styling
- Force Graph for course relationship visualization
- Axios for API communication

### Backend
- FastAPI for high-performance API endpoints
- DSPy for intelligent query processing
- BM25 for semantic search capabilities
- Graph-based course relationship modeling

## 🧠 Intelligent Components

### DSPy Integration
- Custom-trained language model for course-related queries
- Optimized for UTM course context
- Handles complex queries about prerequisites, course content, and program requirements

### Course Prerequisite Graph
- Interactive visualization of course relationships
- Directional graph showing prerequisite dependencies
- Color-coded nodes for easy identification
- Real-time exploration of course connections

### Semantic Search
- BM25-based retrieval system
- Contextual understanding of course descriptions
- Efficient indexing of course content
- Relevance-based result ranking

## 🚀 Getting Started

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/UTM-Course-LLM.git
   cd UTM-Course-LLM
   ```

2. **Install Dependencies**
   ```bash
   # Frontend
   cd frontend
   npm install

   # Backend
   cd backend
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   ```bash
   # Create .env file in backend directory
   OPENAI_API_KEY=your_api_key
   ```

4. **Run the Application**
   ```bash
   # Start backend server
   cd backend
   uvicorn app.main:app --reload

   # Start frontend development server
   cd frontend
   npm run dev
   ```

## 📊 System Architecture

```
UTM Course Assistant
├── Frontend (React + TypeScript)
│   ├── Course Search Component
│   ├── Course Detail View
│   └── Interactive Graph Visualization
│
└── Backend (FastAPI)
    ├── DSPy Integration
    │   ├── Query Processing
    │   └── Context Understanding
    ├── Course Graph Engine
    │   ├── Prerequisite Analysis
    │   └── Relationship Mapping
    └── Semantic Search
        ├── BM25 Indexing
        └── Result Ranking
```

## 🔍 Core Functionalities

### Course Search
- Semantic understanding of search queries
- Real-time search suggestions
- Relevance-based result ranking

### Course Graph
- Interactive node exploration
- Zoom and pan capabilities
- Prerequisite chain visualization
- Dynamic relationship highlighting

### Smart Assistant
- Natural language understanding
- Context-aware responses
- Course recommendation system
- Program requirement analysis



