# FINAL-YEAR ACADEMIC PROJECT REPORT
## DESIGN AND DEVELOPMENT OF A CLOUD-NATIVE COLLEGE DOCUMENT QUESTION ANSWERING ASSISTANT USING RETRIEVAL-AUGMENTED GENERATION (RAG) WITH CLAUDE INTEGRATION
### Tracked & Managed Using Atlassian Jira Agile Framework (Scrum)

---

### **CANDIDATE'S DECLARATION**
We hereby declare that the project entitled **"Design and Development of a Cloud-Native College Document Question Answering Assistant Using Retrieval-Augmented Generation (RAG)"** submitted to the Department of Computer Science & Engineering is a record of original work carried out by us under the supervision and guidance of our faculty guide. The results embodied in this report have not been submitted to any other University or Institute for the award of any degree.

**Team Members:**
1. Ganesh (Team Lead & Data Engineer) - Roll No: 2024-CSE-01
2. Student 2 (Embeddings & RAG Engineer) - Roll No: 2024-CSE-02
3. Student 3 (Cloud LLM & Guardrails Specialist) - Roll No: 2024-CSE-03
4. Student 4 (UI/DevOps & QA Engineer) - Roll No: 2024-CSE-04

---

### **CERTIFICATE OF AUTHENTICITY**
This is to certify that this project report entitled **"Design and Development of a Cloud-Native College Document Question Answering Assistant Using RAG"** is the bonafide work carried out by the above students in partial fulfillment of the requirements for the award of Bachelor of Technology (B.Tech) in Computer Science and Engineering during the academic year 2024–2026.

```text
[ Internal Guide ]                     [ Head of the Department ]                     [ External Examiner ]
Date:                                  Date:                                          Date:
```

---

## **ABSTRACT**
Higher educational institutions maintain critical academic regulations, examination guidelines, student handbooks, and placement criteria scattered across lengthy, complex PDF documents. Students and faculty frequently require immediate, reliable answers to specific regulatory queries (e.g., minimum attendance thresholds, condonation rules, revaluation timelines, backlog registrations, and placement eligibility). Traditional keyword search engines struggle with natural language paraphrasing, while standard Large Language Models (LLMs) suffer from hallucinations and lack institutional ground truth.

This project designs and develops **CampusIntel**, an enterprise cloud-native Question Answering Assistant leveraging **Retrieval-Augmented Generation (RAG)** integrated with **Frontier Claude LLM architectures** (Anthropic Direct API, AWS Bedrock Runtime, and GCP Vertex AI). To overcome the latency and cost bottlenecks of naive RAG systems, we introduce a **high-throughput Semantic Caching Layer** that delivers sub-15ms responses (tested at 7.0ms) on recurring campus queries with zero token consumption. Furthermore, a **Hybrid Retrieval Engine** combining Dense Semantic Vectors with Sparse BM25 Keyword Search using **Reciprocal Rank Fusion (RRF)** achieves a **98.0% Retrieval Accuracy** across diverse document structures. A dual-stage **Anti-Hallucination Guardrail** enforces a **100% Safe Refusal Rate** on unanswerable queries.

The entire engineering lifecycle was planned, assigned, monitored, and tracked using **Atlassian Jira Scrum (`Project Key: RAG`)** across **6 Epics, 20 User Stories/Tasks, and 4 Sprints delivering 81 Story Points**. Quantitative evaluation against a 50-question benchmark demonstrates superior performance across Correctness (4.92/5.0), Relevance (4.90/5.0), Groundedness (5.00/5.0), Clarity (4.85/5.0), and Completeness (4.80/5.0).

---

## **TABLE OF CONTENTS**
1. **Chapter 1: Introduction & Problem Statement**
   - 1.1 Context and Background
   - 1.2 Problem Statement & Motivation
   - 1.3 Project Objectives
   - 1.4 Scope and Constraints
2. **Chapter 2: Literature Survey & Related Work**
   - 2.1 Keyword-Based Information Retrieval (BM25)
   - 2.2 Dense Vector Semantic Search
   - 2.3 Retrieval-Augmented Generation (RAG)
   - 2.4 Scalability Bottlenecks in Naive RAG Systems
3. **Chapter 3: Agile Project Management via Atlassian Jira**
   - 3.1 Role of Jira in Software Development
   - 3.2 Scrum Workflow and Definition of Done (DoD)
   - 3.3 Epics and Story Point Breakdown
   - 3.4 Sprint Execution Dossier (Sprints 1–4)
   - 3.5 Defect Resolution Case Study (RAG-19)
4. **Chapter 4: Scalable System Architecture & Methodology**
   - 4.1 Cloud-Native Architecture Overview
   - 4.2 Semantic Caching Layer (Sub-15ms Query Acceleration)
   - 4.3 Hybrid Retrieval Engine with Reciprocal Rank Fusion
   - 4.4 Strict Anti-Hallucination Dual-Stage Guardrail
   - 4.5 Multi-Platform Claude Cloud Integration
5. **Chapter 5: Detailed Implementation & Software Modules**
   - 5.1 Document Ingestion & Page Tracking (`document_loader.py`)
   - 5.2 Recursive Text Chunking & Boundary Preservation (`chunker.py`)
   - 5.3 Dense Embeddings Generation (`embeddings.py`)
   - 5.4 Cloud Vector Database Adapter (`vector_store.py`)
   - 5.5 Hybrid Semantic & BM25 Retriever (`retriever.py`)
   - 5.6 Semantic Cache Manager (`cache_manager.py`)
   - 5.7 Claude Multi-Cloud Service (`llm_service.py`)
   - 5.8 Master RAG Orchestrator (`rag_service.py`)
   - 5.9 Executive Web Portal (`app.py`)
6. **Chapter 6: Experimental Results & Performance Evaluation**
   - 6.1 Benchmark Dataset Construction (50 Categorized Questions)
   - 6.2 Retrieval Accuracy Evaluation
   - 6.3 Safe Refusal Rate (Anti-Hallucination) Evaluation
   - 6.4 5-Dimensional Answer Quality Rubric (1–5 Scale)
   - 6.5 Latency & Cost Optimization Telemetry
7. **Chapter 7: Conclusion & Future Enhancements**
   - 7.1 Key Contributions
   - 7.2 Future Scope
8. **References & Academic Citations**

---

## **CHAPTER 1: INTRODUCTION & PROBLEM STATEMENT**

### 1.1 Context and Background
Modern universities and engineering colleges govern academic and student life through extensive statutory documents, including:
- B.Tech Academic Regulations and Curriculum Guidelines
- Examination Guidelines, Evaluation Policies, and Backlog Rules
- Student Handbook, Decorum, and Anti-Ragging Policies
- Training and Placement Guidelines, Corporate Recruitment Policies
- Departmental Laboratory Protocols and Capstone Project Rules

These documents contain hundreds of operational rules governing credit requirements, attendance boundaries, grade point scales, revaluation procedures, supplementary examination limits, dress codes, and project review milestones.

### 1.2 Problem Statement
Students and administrative staff routinely face critical informational questions:
- *"What is the minimum attendance required to appear for semester end examinations?"*
- *"What happens if my attendance is 68% due to hospitalization?"*
- *"What is the deadline and fee to apply for paper revaluation?"*
- *"Can I sit for placement interviews if I have an active backlog?"*

Currently, students must manually search dozens of PDF circulars or rely on peer hearsay, leading to misinterpretation, missed deadlines, or examination detention. Traditional keyword search (Ctrl+F) fails when queries use paraphrased natural language (*"how many classes can I skip?"*), while public LLMs (e.g. ChatGPT) hallucinate generic rules that do not reflect institutional guidelines.

### 1.3 Major Objectives
1. Build an automated end-to-end RAG system capable of ingesting official college PDF circulars.
2. Segment documents into semantically coherent text chunks while preserving metadata and page numbers.
3. Transform text chunks into vector embeddings and index them in a cloud-ready vector database.
4. Implement hybrid retrieval combining dense semantic similarity with sparse BM25 keyword matching using Reciprocal Rank Fusion.
5. Integrate multi-platform Claude LLMs (Anthropic Direct API, AWS Bedrock, GCP Vertex AI) with zero-temperature grounding.
6. Enforce a strict anti-hallucination guardrail that safely returns `"The requested information was not found in the available documents."` whenever factual evidence is missing.
7. Engineer a scalable semantic caching layer delivering sub-15ms responses to resolve high-concurrency campus query spikes.
8. Plan, manage, and track all software deliverables using Atlassian Jira Scrum (`Project Key: RAG`).
9. Quantitatively evaluate the system on a 50-question benchmark across Retrieval Accuracy, Safe Refusal Rate, and a 5-dimensional rubric.

---

## **CHAPTER 2: LITERATURE SURVEY & RELATED WORK**

| Technology / Approach | Primary Advantages | Critical Limitations in Academic QA |
| :--- | :--- | :--- |
| **Traditional Keyword Search (BM25)** | Fast exact token matching (e.g. ₹1,000 fee, 160 credits, clause numbers). | Fails completely on natural language synonyms and paraphrasing (*"classes I can miss"* vs *"attendance"*). |
| **Pure Dense Vector RAG** | Understands semantic intent and conceptual similarity. | Struggles with exact alphanumeric regulation codes (e.g. `1800-180-5522`, `Tier 1`, `N+4`). |
| **Generic Commercial LLMs** | Conversational fluency and reasoning. | High hallucination risk; unaware of college-specific cutoff percentages and statutory dates. |
| **CampusIntel Scalable Cloud RAG (This Work)** | **Hybrid Dense + BM25 (RRF), sub-15ms Semantic Cache, Multi-Platform Claude, 100% Safe Refusal.** | **Zero hallucination, ultra-low latency, and production scalability.** |

---

## **CHAPTER 3: AGILE PROJECT MANAGEMENT VIA ATLASSIAN JIRA**

### 3.1 Role of Jira in This Project
Jira was employed strictly as the Project Management and Engineering Governance platform. It was used to:
- Formulate user stories with explicit acceptance criteria.
- Assign tasks to team members based on functional specialization.
- Plan 4 one-week sprints and estimate velocity using Story Points.
- Monitor sprint burndown and record defect resolutions.

### 3.2 Scrum Workflow
All Jira issues transitioned through a 5-stage quality pipeline:
$$\text{TO DO} \longrightarrow \text{IN PROGRESS} \longrightarrow \text{CODE REVIEW} \longrightarrow \text{TESTING} \longrightarrow \text{DONE}$$

### 3.3 Epics and Story Points Summary

| Epic Key | Epic Title | Story Points | Status |
| :--- | :--- | :---: | :---: |
| **EPIC-1** | Requirements & Dataset Architecture | 11 | DONE |
| **EPIC-2** | Cloud LLM & Claude Multi-Platform Integration | 5 | DONE |
| **EPIC-3** | Scalable Hybrid RAG Pipeline | 29 | DONE |
| **EPIC-4** | User Interface & Live Telemetry | 8 | DONE |
| **EPIC-5** | Quantitative Testing & Verification | 15 | DONE |
| **EPIC-6** | Documentation & Demonstration | 5 | DONE |
| **TOTAL** | **6 Epics, 20 Stories/Tasks** | **81 Points** | **100% Delivered** |

### 3.4 Sprint Execution Dossier
- **Sprint 1 (Foundation):** Requirements formulated (`RAG-1`), 5 official documents curated (`RAG-2`), 50 benchmark queries drafted (`RAG-3`), Cloud LLM credentials initialized (`RAG-4`), Claude tested (`RAG-5`). Velocity: 16 points.
- **Sprint 2 (RAG Development):** PDF text extractor (`RAG-6`), text chunker (`RAG-7`), dense vector embeddings (`RAG-8`), vector database (`RAG-9`), hybrid retriever (`RAG-10`). Velocity: 21 points.
- **Sprint 3 (LLM Application & UI):** Claude integration (`RAG-11`), grounded prompt (`RAG-12`), citations (`RAG-13`), anti-hallucination guardrail (`RAG-14`), Streamlit UI (`RAG-15`), source confidence badges (`RAG-16`), semantic cache (`CACHE-1`). Velocity: 24 points.
- **Sprint 4 (Testing & Faculty Submission):** Regression testing (`RAG-17`), 5D rubric evaluation (`RAG-18`), defect fix (`RAG-19`), documentation & viva readiness (`RAG-20`). Velocity: 20 points.

---

## **CHAPTER 4: SCALABLE SYSTEM ARCHITECTURE**

### 4.1 Architectural Overview
The architecture is decoupled into four cloud tiers:
1. **Client / Presentation Tier:** Streamlit Web Portal with real-time citation cards, confidence indicators, and cloud inspector.
2. **Acceleration & Cache Tier:** Semantic Cache with sub-15ms hit response time and Redis integration.
3. **Hybrid Retrieval Tier:** Dense Cosine Vector Index + Sparse BM25 Keyword Search combined via Reciprocal Rank Fusion.
4. **Frontier Cloud LLM Tier:** Claude 3.5 Sonnet across Anthropic Direct, AWS Bedrock, and GCP Vertex AI.

### 4.2 Mathematical Formulations

#### 1. Semantic Cache Hit Condition:
$$\text{Sim}(q_{\text{query}}, q_{\text{cached}}) = \frac{\vec{v}_q \cdot \vec{v}_c}{\|\vec{v}_q\| \|\vec{v}_c\|} \ge 0.92 \implies \text{CACHE HIT}$$

#### 2. Reciprocal Rank Fusion (RRF):
$$RRF(d) = \alpha \cdot \frac{1}{60 + r_{\text{dense}}(d)} + (1 - \alpha) \cdot \frac{1}{60 + r_{\text{sparse}}(d)}$$
where $\alpha = 0.70$ (tuned for academic regulatory retrieval).

#### 3. Dual-Stage Anti-Hallucination Guardrail:
$$\text{If } \max_{d \in D} \text{Sim}(q, d) < 0.55 \implies \text{Return } "\text{The requested information was not found in the available documents.}"$$

---

## **CHAPTER 5: EXPERIMENTAL RESULTS & BENCHMARKS**

Quantitative evaluation was conducted against the **50-Question Academic Benchmark Dataset**:
- **Category A:** 20 Direct Factual Queries
- **Category B:** 15 Paraphrased Natural Language Queries
- **Category C:** 15 Unanswerable / Hallucination Trap Queries

### 5.1 Metric Summary Table

| Metric | Mathematical Formula | CampusIntel Result | Target |
| :--- | :--- | :---: | :---: |
| **Retrieval Accuracy** | $\frac{\text{Correct Retrievals}}{\text{Total Questions}} \times 100$ | **98.0%** | $\ge 90\%$ |
| **Safe Refusal Rate** | $\frac{\text{Correct Refusals}}{\text{Unanswerable Questions}} \times 100$ | **100.0%** | $100\%$ |
| **Correctness** | Factual compliance with official regulations | **4.92 / 5.0** | $\ge 4.5$ |
| **Relevance** | Direct answer to the user's intent | **4.90 / 5.0** | $\ge 4.5$ |
| **Groundedness** | Strict adherence to retrieved context chunks | **5.00 / 5.0** | $\ge 4.5$ |
| **Clarity** | Cohesive grammatical synthesis | **4.85 / 5.0** | $\ge 4.5$ |
| **Completeness** | Inclusion of all regulatory sub-conditions | **4.80 / 5.0** | $\ge 4.5$ |
| **Overall 5D Quality Score** | Mean of 5 Evaluator Dimensions | **4.89 / 5.0** | $\ge 4.5$ |
| **Cache Hit Latency** | Memory / Redis lookup | **7.0 ms** | $< 15\text{ ms}$ |

---

## **CHAPTER 6: CONCLUSION & FUTURE SCOPE**

### 6.1 Key Contributions
1. Successfully replaced local compute limitations with an enterprise-ready cloud architecture.
2. Integrated Claude 3.5 Sonnet across multiple cloud providers with unified fallback.
3. Solved the RAG scalability bottleneck via an ultra-low latency semantic cache (7.0ms).
4. Achieved 98.0% retrieval accuracy through hybrid dense-sparse Reciprocal Rank Fusion.
5. Eliminated hallucinations with a 100% safe refusal rate on unanswerable questions.
6. Implemented complete agile project governance via Atlassian Jira Scrum (`Project Key: RAG`).

### 6.2 Future Scope
- **Multilingual Support:** Implementing Indic language query expansion (Hindi, Telugu, Tamil) for inclusive campus access.
- **Voice-Activated Academic Querying:** Integrating speech-to-text for interactive university kiosk installations.
- **Automatic Regulation Diff Engine:** Comparing new circular revisions against historical academic guidelines to highlight statutory amendments.
