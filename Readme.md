# ResearchMate AI

## Real-Time Multi-Agent Research Assistant for Evidence-Based Academic Literature Analysis

ResearchMate AI is an AI-powered research assistant that helps users quickly investigate academic and technical topics. It searches multiple information sources, collects relevant research material, extracts evidence, detects conflicting findings, and generates a citation-grounded research summary.

The system uses a multi-agent workflow with LangGraph and a locally running Ollama LLM.

---

## 🚀 Features

* 🔎 **Multi-Source Research**

  * Web Search
  * arXiv
  * Semantic Scholar

* 🤖 **Multi-Agent Architecture**

  * Web Research Agent
  * arXiv Research Agent
  * Semantic Scholar Agent
  * Source Reader Agent
  * Evidence Extraction Agent
  * Conflict Detection Agent
  * Research Writer Agent

* 📚 **Evidence-Based Analysis**

  * Extracts factual claims from retrieved sources
  * Links evidence to source citation IDs
  * Reduces unsupported AI-generated claims

* ⚔️ **Conflict Detection**

  * Identifies disagreements between research sources
  * Compares different findings, conclusions, or recommendations

* 📝 **Citation-Grounded Report**

  * Generates a structured research report
  * Includes numbered citations such as `[1]`, `[2]`
  * Provides a references section

* ⚡ **Real-Time Processing**

  * WebSocket-based communication
  * Displays agent progress while research is running

* 💾 **Research History**

  * Stores completed research results using SQLite

* 🖥️ **Interactive Dashboard**

  * Modern web interface
  * Live agent activity
  * Source statistics
  * Evidence and conflict visualization

---

## 🏗️ System Architecture

```text
                         ┌──────────────────┐
                         │      User        │
                         │  Research Topic  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   FastAPI API    │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   LangGraph      │
                         │ Research Workflow│
                         └────────┬─────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
       ┌─────────────┐     ┌─────────────┐     ┌──────────────┐
       │ Web Search  │     │    arXiv    │     │  Semantic    │
       │    Agent    │     │    Agent    │     │ Scholar Agent│
       └──────┬──────┘     └──────┬──────┘     └──────┬───────┘
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  ▼
                         ┌──────────────────┐
                         │  Source Reader   │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Evidence Agent   │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Conflict Agent   │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  Writer Agent    │
                         │  Ollama / Qwen   │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Research Report  │
                         │ + Citations      │
                         └──────────────────┘
```

---

## 🛠️ Technology Stack

### Frontend

* HTML5
* CSS3
* JavaScript
* WebSocket

### Backend

* Python
* FastAPI
* Uvicorn

### AI / Agent Framework

* LangGraph
* LangChain
* Ollama
* Qwen2.5

### Research Sources

* Web Search
* arXiv
* Semantic Scholar

### Data Processing

* BeautifulSoup
* PyMuPDF
* Feedparser

### Database

* SQLite

---

## 📁 Project Structure

```text
ResearchMate-AI/
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── research_graph.py
│   ├── agents.py
│   ├── arxiv_client.py
│   ├── semantic_scholar.py
│   ├── web_search.py
│   ├── source_reader.py
│   ├── conflict_detector.py
│   └── database.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── data/
│   └── research.db
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Requirements

Make sure the following are installed:

* Python 3.10+
* Git
* Ollama
* Qwen2.5 model

---

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/nnagasrinivas03/ResearchMate-AI.git
```

```bash
cd ResearchMate-AI
```

### 2. Create Virtual Environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## 🤖 Ollama Setup

Install Ollama and make sure the Ollama service is running.

Check installed models:

```powershell
ollama list
```

Pull Qwen2.5:

```powershell
ollama pull qwen2.5:7b
```

For systems with limited RAM, a smaller model can be used:

```powershell
ollama pull qwen2.5:3b
```

---

## 🔐 Environment Configuration

Create a `.env` file in the project root:

```env
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b

SEMANTIC_SCHOLAR_API_KEY=
WEB_SEARCH_API_KEY=
```

### API Keys

The Semantic Scholar API key is optional.

The Web Search API key is used for the configured web-search provider.

**Never commit your `.env` file to GitHub.**

The project `.gitignore` already excludes:

```text
.env
```

---

## ▶️ Running the Project

From the project root:

```powershell
python -m uvicorn backend.main:app --reload
```

The application will start at:

```text
http://127.0.0.1:8000
```

Open the address in your browser.

---

## 🔬 How ResearchMate AI Works

### Step 1 — User Input

The user enters a research topic.

Example:

```text
Artificial Intelligence in Education
```

### Step 2 — Multi-Source Retrieval

The system searches:

```text
Web
arXiv
Semantic Scholar
```

Relevant sources are collected and assigned citation IDs.

### Step 3 — Source Reading

ResearchMate AI attempts to read publicly accessible web pages and open-access PDFs.

If full content cannot be retrieved, the system can fall back to available metadata or abstracts.

### Step 4 — Evidence Extraction

The Evidence Agent analyzes the retrieved material and extracts supported claims.

Example:

```json
{
  "claim": "AI-based tutoring systems can provide personalized learning support.",
  "source_ids": [1],
  "support": "supports",
  "confidence": "high"
}
```

### Step 5 — Conflict Detection

The Conflict Agent compares evidence from different sources.

It identifies genuine disagreements involving:

* Different conclusions
* Different measurements
* Different findings
* Different recommendations

### Step 6 — Research Writing

The Writer Agent generates a structured research report containing:

```text
Research Summary
    ↓
Overview
    ↓
Key Findings
    ↓
Evidence
    ↓
Conflicting Findings
    ↓
Research Gaps
    ↓
Conclusion
    ↓
References
```

---

## 📊 Example Workflow

Input:

```text
Retrieval Augmented Generation
```

Possible processing:

```text
12 Sources Retrieved
        ↓
10 Evidence Items
        ↓
3 Conflicts Detected
        ↓
AI Research Report Generated
```

The dashboard displays this process in real time.

---

## 🎯 Problem Statement

Researchers often spend significant time searching multiple information sources, reading research papers, comparing different findings, and preparing properly cited literature summaries.

Existing AI assistants may provide useful answers but can struggle with source traceability, conflicting evidence, and citation reliability.

ResearchMate AI addresses this problem by combining multi-source retrieval, evidence extraction, conflict detection, and citation-grounded report generation in a single real-time research workflow.

---

## 💡 Key Innovation

The main innovation of ResearchMate AI is the combination of:

```text
Multi-Source Retrieval
        +
Multi-Agent Reasoning
        +
Evidence Extraction
        +
Conflict Detection
        +
Citation-Grounded Generation
        +
Real-Time Visualization
```

This allows the system to provide not just an answer, but a transparent research process showing **where the information came from and how different sources compare**.

---

## 📈 Advantages

* Reduces manual research effort
* Searches multiple sources automatically
* Provides source-linked evidence
* Detects conflicting findings
* Generates structured research summaries
* Provides real-time processing updates
* Uses a local LLM through Ollama
* Maintains research history
* Can be extended with additional research tools

---

## 🔮 Future Enhancements

* Research gap detection
* Source credibility scoring
* Duplicate paper detection
* Citation network visualization
* Automatic PDF report generation
* IEEE-format references
* Research paper comparison tables
* Vector database integration
* Semantic similarity search
* Voice-based research queries
* More academic databases
* Export to PDF and DOCX
* Advanced research history and analytics

---

## 🔒 Security Considerations

* API keys are stored in `.env`
* `.env` is excluded from Git
* The system does not bypass paywalls
* Only publicly accessible source content is processed
* Restricted source content is not downloaded without access
* API credentials should never be committed to the repository

---

## 🧪 Testing

Example research topics:

```text
Artificial Intelligence in Education
```

```text
Retrieval Augmented Generation
```

```text
Large Language Models in Healthcare
```

```text
AI Based Skin Cancer Detection
```

```text
Multi-Agent AI Systems
```

---

## 📌 Project Status

**Status: Working Prototype**

The current implementation successfully supports:

* Multi-source retrieval
* Source processing
* Evidence extraction
* Conflict detection
* AI report generation
* Citation-based reporting
* Real-time WebSocket updates
* SQLite research history

---

## 👨‍💻 Author

**Naga Srinivas**

B.E. Computer Science and Engineering

---

## ⭐ Project Goal

ResearchMate AI aims to make academic research faster, more transparent, and evidence-driven by combining modern AI agents with real-time research retrieval and citation-grounded generation.
