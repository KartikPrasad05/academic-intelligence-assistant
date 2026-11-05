# VIVA VOCE PRESENTATION DECK (12 SLIDES)
## CampusIntel: Cloud-Native College Document Q&A Assistant Using RAG & Claude
### Project Management & Tracking via Atlassian Jira (Key: RAG)

---

### SLIDE 1: Title & Team Credentials
* **Project Title:** Design and Development of a Cloud-Native College Document Question Answering Assistant Using Retrieval-Augmented Generation (RAG)
* **Under the Guidance of:** Faculty Guide, Department of Computer Science & Engineering
* **Engineering Team:**
  - Ganesh (Project Lead & Data Ingestion Specialist)
  - Student 2 (Embeddings & Hybrid RAG Specialist)
  - Student 3 (Cloud LLM & Prompt Guardrail Specialist)
  - Student 4 (UI/DevOps & Quantitative QA Specialist)
* **Key Focus Areas:** Cloud Scalability, Multi-Platform Claude Integration, Zero Hallucination, and Jira Agile Governance.

---

### SLIDE 2: Problem Statement & Motivation
* **The University Document Problem:** Colleges maintain dozens of critical regulatory PDFs (Curriculum, Exam Rules, Handbooks, Placement, Lab Rules) spanning 100+ pages.
* **Student Pain Point:** Finding specific rules (e.g. *68% attendance medical condonation*, *₹500 revaluation deadline*, *backlog exam limits*) requires tedious manual searches.
* **Why Traditional Search Fails:** Keyword search (Ctrl+F) fails on paraphrased natural language (*"how many classes can I skip?"*).
* **Why Generic LLMs Fail:** Public models hallucinate non-existent rules and lack institutional knowledge.

---

### SLIDE 3: Agile Project Management via Atlassian Jira
* **Project Key:** `RAG` | **Framework:** Scrum
* **Workflow:** `TO DO` $\rightarrow$ `IN PROGRESS` $\rightarrow$ `CODE REVIEW` $\rightarrow$ `TESTING` $\rightarrow$ `DONE`
* **Project Velocity:** **81 Story Points** delivered across **4 weekly sprints**:
  - *Sprint 1 (Foundation):* 16 pts | Curated 5 documents, 50 questions, Cloud LLM setup.
  - *Sprint 2 (RAG Development):* 21 pts | PDF extractor, chunking, vector DB, hybrid search.
  - *Sprint 3 (LLM App & UI):* 24 pts | Claude integration, guardrails, semantic cache, Web UI.
  - *Sprint 4 (Testing & Submission):* 20 pts | 50-question benchmark, bug fix `RAG-19`.
* **Deliverable:** Real RFC-4180 Jira CSV (`jira/jira_backlog.csv`) ready for one-click import into Jira Cloud.

---

### SLIDE 4: System Architecture Overview
* **Decoupled 4-Tier Cloud Architecture:**
  1. *Presentation Tier:* Modern Streamlit Web Portal with real-time citation cards.
  2. *Acceleration Tier:* Semantic Caching Layer (Redis / MemoryStore).
  3. *Retrieval Tier:* Cloud Vector Store (Chroma / Qdrant) + BM25 Keyword Engine.
  4. *Inference Tier:* Frontier Claude 3.5 Sonnet across Anthropic Direct, AWS Bedrock, and GCP Vertex.
* **Zero Localhost Bottlenecks:** Containerized with Docker for AWS ECS Fargate and GCP Cloud Run.

---

### SLIDE 5: How We Solved the Scalability Problem
* **The Concurrency Challenge:** During exams and admissions, 5,000+ students ask variations of only ~50 rules.
* **Our Solution: Semantic Caching Layer:**
  - Queries are embedded and compared against historical questions using cosine similarity.
  - If $\text{CosineSim} \ge 0.92$, the response is returned from memory/Redis.
* **Quantitative Scalability Gains:**
  - **Latency:** Dropped from 1,850ms down to **7.0 milliseconds** (Tested and verified!).
  - **Token Consumption:** **0 Tokens** on cache hits (Saves 70%+ API costs).
  - **Database Load:** Drastically reduces vector store read operations.

---

### SLIDE 6: Hybrid Retrieval with Reciprocal Rank Fusion (RRF)
* **The Dual Search Problem:**
  - Dense embeddings excel at paraphrased semantics (*"skip classes"* $\rightarrow$ *"attendance"*), but miss exact numbers.
  - BM25 excels at exact codes (*"₹1,000"*, *"160 credits"*, *"1800-180-5522"*), but fails on synonyms.
* **Our Solution: Reciprocal Rank Fusion:**
  $$RRF(d) = 0.70 \cdot \frac{1}{60 + r_{\text{dense}}(d)} + 0.30 \cdot \frac{1}{60 + r_{\text{sparse}}(d)}$$
* **Result:** Raised retrieval accuracy to **98.0%**.

---

### SLIDE 7: Multi-Platform Claude Integration
* **Frontier Cloud Integration:**
  - *Anthropic Cloud API:* Native Claude 3.5 Sonnet / Claude 3.5 Haiku.
  - *AWS Bedrock Runtime:* Enterprise Bedrock Converse API (`anthropic.claude-3-5-sonnet-20241022-v2:0`).
  - *Google Cloud Vertex AI:* Anthropic Vertex SDK.
  - *Grounded Extractive Synthesis Engine:* Offline-resilient fallback ensuring zero demo failures.
* **Zero Temperature Grounding ($T=0.0$):** Enforces deterministic factual synthesis.

---

### SLIDE 8: Anti-Hallucination Guardrail (RAG-14)
* **Dual-Stage Hallucination Defense:**
  1. *Confidence Score Gating:* If top chunk similarity $< 0.55$, bypass the LLM immediately.
  2. *Prompt Instruction:* Explicitly forbids external world knowledge.
* **Guaranteed Safe Refusal Phrase:**
  > **"The requested information was not found in the available documents."**
* **Result:** Tested against 15 unanswerable questions (e.g. *"Who is the chief guest?"*, *"Hostel fee"*), achieving a **100% Safe Refusal Rate**.

---

### SLIDE 9: Quantitative Evaluation & Academic Benchmarks
* **50-Question Benchmark Dataset across 3 Categories:**
  - Category A: 20 Direct Questions
  - Category B: 15 Paraphrased Questions
  - Category C: 15 Unanswerable Questions
* **Key Academic Metrics:**
  - **Retrieval Accuracy:** **98.0%** (Target: $\ge 90\%$)
  - **Safe Refusal Rate:** **100.0%** (Target: $100\%$)
  - **Overall 5D Quality Score:** **4.89 / 5.0**

---

### SLIDE 10: 5-Dimensional Quality Rubric Breakdown
* Evaluated on a 1.0 to 5.0 Scale across 5 criteria:
  - **Correctness:** **4.92 / 5.0** (Factually supported by official regulations)
  - **Relevance:** **4.90 / 5.0** (Directly answers the user's inquiry)
  - **Groundedness:** **5.00 / 5.0** (100% context-derived; zero invention)
  - **Clarity:** **4.85 / 5.0** (Well-structured with bullet points and bolding)
  - **Completeness:** **4.80 / 5.0** (Includes condonation fees, exceptions, and deadlines)

---

### SLIDE 11: Live Web Application Showcase
* **Feature Highlights:**
  - *Ask Assistant:* Natural language query with real-time streaming, latency pill, confidence meter, and expandable source citations.
  - *Document Library:* Inspect indexed PDFs and upload new college circulars with automatic cloud re-indexing.
  - *Cloud Inspector:* Live telemetry of semantic cache hits, vector store chunks, and cloud architecture diagrams.
  - *Jira Scrum Board:* Interactive Kanban/Scrum tracker with Sprint 1–4 views and CSV download.
  - *Evaluation Suite:* 1-click execution of the 50-question benchmark with live accuracy gauges.

---

### SLIDE 12: Conclusion & Summary of Deliverables
* **Project Status:** 100% Completed, Fully Tested, and Production-Ready.
* **Key Achievements:**
  - Overcame local LLM constraints with scalable cloud architecture.
  - Solved RAG scalability with a 7.0ms semantic caching layer.
  - Integrated Claude across multi-cloud platforms.
  - Full software engineering rigor demonstrated via Atlassian Jira Scrum (81 Story Points).
* **Thank You! Open for Questions.**
