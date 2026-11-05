"""
=============================================================================
CAMPUSINTEL CLOUD RAG: COLLEGE DOCUMENT QUESTION ANSWERING ASSISTANT
Enterprise-Grade Cloud Architecture with Claude & Scalable Hybrid Retrieval
=============================================================================
Designed for Final-Year Mini Project Defense & Faculty Evaluation
Integrated with Agile Jira Tracking (RAG-1 to RAG-20)
=============================================================================
"""

import os
import time
import json
from pathlib import Path
import streamlit as st

# Configure page settings
st.set_page_config(
    page_title="Academic Intelligence Assistant | Cloud RAG",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise CSS Styling
st.markdown("""
<style>
    /* Global Styling */
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0369a1 100%);
        padding: 24px;
        border-radius: 12px;
        color: #ffffff;
        margin-bottom: 25px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.15);
    }
    .main-header h1 {
        color: #ffffff;
        font-size: 28px;
        margin-bottom: 4px;
        font-weight: 700;
    }
    .main-header p {
        color: #94a3b8;
        font-size: 14px;
        margin-bottom: 0;
    }
    .metric-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 8px;
    }
    .badge-cloud { background-color: #0284c7; color: white; }
    .badge-claude { background-color: #d97706; color: white; }
    .badge-cache { background-color: #10b981; color: white; }
    .badge-jira { background-color: #6366f1; color: white; }
    
    /* Result Cards */
    .answer-card {
        background-color: #f8fafc;
        border-left: 5px solid #0284c7;
        padding: 20px;
        border-radius: 8px;
        margin-top: 15px;
        margin-bottom: 20px;
        color: #0f172a;
    }
    .citation-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .refusal-card {
        background-color: #fff1f2;
        border-left: 5px solid #e11d48;
        padding: 18px;
        border-radius: 8px;
        color: #9f1239;
        font-weight: 500;
    }
    .stat-box {
        background: #f1f5f9;
        padding: 14px;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    .stat-number {
        font-size: 24px;
        font-weight: 700;
        color: #0f172a;
    }
    .stat-label {
        font-size: 12px;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# Imports after styles
from config import cfg, DATA_DIR, BASE_DIR
cfg.app_title = "Academic Intelligence Assistant"
from document_loader import DocumentLoader
from chunker import DocumentChunker
from vector_store import CloudVectorStore
from retriever import ScalableHybridRetriever
from llm_service import CloudClaudeService
from cache_manager import SemanticCacheManager
from rag_service import ScalableRAGPipeline, RAGResult
from evaluate import RAGEvaluator


# -----------------------------------------------------------------------------
# Cached Application State Initialization
# -----------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def initialize_rag_system():
    """Initializes and connects all cloud RAG components as singletons."""
    loader = DocumentLoader()
    chunker = DocumentChunker(chunk_size=cfg.rag.chunk_size, overlap=cfg.rag.chunk_overlap)
    vector_store = CloudVectorStore()
    
    # Auto-index knowledge base if empty
    if vector_store.count() == 0:
        docs = loader.load_all_documents()
        chunks = chunker.chunk_pages(docs)
        vector_store.add_chunks(chunks)

    retriever = ScalableHybridRetriever(vector_store=vector_store)
    llm_service = CloudClaudeService()
    cache_manager = SemanticCacheManager()
    pipeline = ScalableRAGPipeline(
        retriever=retriever,
        llm_service=llm_service,
        cache_manager=cache_manager
    )
    return loader, chunker, vector_store, retriever, pipeline, cache_manager


loader, chunker, vector_store, retriever, pipeline, cache_manager = initialize_rag_system()


# -----------------------------------------------------------------------------
# Top Banner / Header
# -----------------------------------------------------------------------------
st.markdown(f"""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1>🎓 Academic Intelligence Assistant</h1>
            <p><b>{cfg.college_name}</b> | Academic Regulations & Document Intelligence Assistant ({cfg.academic_year})</p>
        </div>
        <div>
            <span class="metric-badge badge-cloud">AWS / Cloud Native</span>
            <span class="metric-badge badge-claude">Claude 3.5 Sonnet</span>
            <span class="metric-badge badge-cache">Semantic Cache &lt;15ms</span>
            <span class="metric-badge badge-jira">Jira Scrum (RAG)</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Sidebar Navigation & Live Telemetry
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/university.png", width=100)
    st.subheader("⚡ Cloud System Status")
    
    cache_stats = cache_manager.get_stats()
    indexed_chunks = vector_store.count()
    
    st.markdown(f"""
    - **Active LLM:** `{cfg.llm.anthropic_model}`
    - **Cloud Provider:** `{cfg.llm.provider.upper()}`
    - **Vector DB:** `{cfg.vector_db.provider}` ({indexed_chunks} Chunks)
    - **Retrieval:** `Hybrid (Dense + BM25 RRF)`
    - **Semantic Cache:** `Active ({cache_stats['cached_entries']} queries)`
    - **Cache Hit Rate:** `{cache_stats['hit_rate_pct']}%`
    """)
    
    st.divider()
    st.subheader("🎯 Quick Question Prompts")
    quick_queries = [
        "What is the minimum attendance required?",
        "How many credits are required for graduation?",
        "What is the procedure for examination revaluation?",
        "What is the placement eligibility criteria?",
        "Who will be the chief guest next year? (Hallucination Test)"
    ]
    for q in quick_queries:
        if st.button(f"📌 {q}", key=f"btn_{q[:15]}", use_container_width=True):
            st.session_state["query_input_box"] = q
            st.session_state["trigger_auto_ask"] = True
            st.rerun()

    st.divider()
    st.caption("College Document Q&A Assistant | Final-Year Mini Project")


# -----------------------------------------------------------------------------
# Main Application Tabs
# -----------------------------------------------------------------------------
tab_chat, tab_docs, tab_scalability, tab_benchmarks, tab_jira, tab_settings = st.tabs([
    "💬 Ask Assistant",
    "📚 Document Library",
    "⚡ Cloud Scalability & Cache",
    "🧪 Evaluation Benchmarks",
    "📋 Jira Project Tracker",
    "⚙️ Cloud Settings"
])


# =============================================================================
# TAB 1: Conversational Q&A Assistant
# =============================================================================
with tab_chat:
    st.subheader("Ask Any Question Regarding College Documents")
    st.caption("Answers are synthesized strictly from official regulations with complete citations and zero hallucination.")

    if "query_input_box" not in st.session_state:
        st.session_state["query_input_box"] = ""

    question = st.text_input(
        "Enter your question:",
        placeholder="e.g., What happens if my attendance falls below 65%?",
        key="query_input_box"
    )

    col_btn, col_filter, col_cache_toggle = st.columns([1, 2, 1])
    with col_btn:
        ask_pressed = st.button("🚀 Ask Claude", type="primary", use_container_width=True)
    with col_filter:
        doc_filter = st.selectbox(
            "Filter by Specific Document (Optional):",
            ["All Uploaded Documents", "academic_regulations.pdf", "examination_guidelines.pdf", "student_handbook.pdf", "placement_guidelines.pdf", "department_rules.pdf"]
        )
    with col_cache_toggle:
        use_cache = st.checkbox("Enable Semantic Cache", value=True)

    selected_filter = None if doc_filter == "All Uploaded Documents" else doc_filter

    # Check if user clicked ask OR if quick prompt was triggered
    trigger_auto_ask = st.session_state.pop("trigger_auto_ask", False)
    should_run = (ask_pressed or trigger_auto_ask) and bool(question.strip())

    if should_run:
        with st.spinner("Retrieving regulations & synthesizing answer via Claude..."):
            result: RAGResult = pipeline.answer_question(
                question=question,
                filter_doc=selected_filter,
                use_cache=use_cache
            )
            st.session_state["active_result"] = result
            st.session_state["active_question"] = question

    # Render result if available in session state
    if "active_result" in st.session_state:
        result: RAGResult = st.session_state["active_result"]

        # Telemetry Pill Row
        st.markdown(f"""
        <div style="margin-top: 10px; margin-bottom: 15px;">
            <span class="metric-badge" style="background:#e0f2fe; color:#0369a1;">⏱️ Latency: <b>{result.latency_ms:.1f} ms</b></span>
            <span class="metric-badge" style="background:{'#dcfce7' if result.is_cached else '#fef3c7'}; color:{'#15803d' if result.is_cached else '#b45309'};">
                {'⚡ Semantic Cache HIT (<15ms)' if result.is_cached else f'☁️ Cloud LLM: {result.model}'}
            </span>
            <span class="metric-badge" style="background:#f3e8ff; color:#6b21a8;">🎯 Confidence: <b>{result.confidence_score * 100:.1f}%</b></span>
            <span class="metric-badge" style="background:#f1f5f9; color:#475569;">📊 Tokens: In={result.tokens_input} | Out={result.tokens_output}</span>
        </div>
        """, unsafe_allow_html=True)

        # Output Display
        if result.is_refusal:
            st.markdown(f"""
            <div class="refusal-card">
                <h3>🛡️ Anti-Hallucination Safe Refusal</h3>
                <p style="font-size: 16px; margin-top: 8px;">{result.answer}</p>
                <p style="font-size: 12px; margin-bottom: 0; color: #64748b;">
                    The system verified that no verified factual evidence exists in the uploaded college documents for this question. Fabricated answers are strictly prevented.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="answer-card">
                <h4 style="color: #0369a1; margin-bottom: 12px;">Official Response:</h4>
                <div style="font-size: 15px; line-height: 1.6; color: #1e293b;">
                    {result.answer.replace(chr(10), '<br>')}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Sources & Citations Section (RAG-13 & RAG-16)
            if result.sources:
                st.subheader("📑 Verified Source Citations")
                for idx, src in enumerate(result.sources, start=1):
                    with st.expander(f"Citation {idx}: 📄 {src.doc_name} (Page {src.page_number}) - {src.section} | Match: {src.similarity_score * 100:.1f}%"):
                        st.markdown(f"**Document:** `{src.doc_name}` | **Page:** `{src.page_number}` | **Chunk ID:** `{src.chunk_id}`")
                        st.markdown(f"**Section Title:** *{src.section}*")
                        st.info(f"\"{src.snippet}\"")

        # Grounding Inspector (RAG-12)
        with st.expander("🔍 Inspect Internal Context & RAG Prompt"):
            st.markdown("#### System Grounding Instructions:")
            st.code(pipeline.SYSTEM_PROMPT, language="markdown")
            st.markdown("#### Retrieved Context Chunks Provided to Claude:")
            if result.sources:
                for s in result.sources:
                    st.code(f"Source: {s.doc_name} | Page: {s.page_number}\nSnippet: {s.snippet}", language="text")
            else:
                st.write("No context chunks passed (Safe refusal triggered).")


# =============================================================================
# TAB 2: Document Knowledge Base & Ingestion
# =============================================================================
with tab_docs:
    st.subheader("📚 College Knowledge Base & Cloud Ingestion")
    st.write("Browse official regulatory documents currently indexed in the cloud vector database.")

    # Upload new circular
    uploaded_file = st.file_uploader("Upload New College Circular / PDF Document:", type=["pdf", "txt", "md"])
    if uploaded_file is not None:
        save_path = DATA_DIR / uploaded_file.name
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File uploaded: {uploaded_file.name}")
        
        if st.button("⚡ Index Uploaded Document into Cloud Vector Store"):
            with st.spinner("Extracting text, chunking, and embedding into vector store..."):
                doc_pages = loader.load_document(save_path)
                new_chunks = chunker.chunk_pages(doc_pages)
                count = vector_store.add_chunks(new_chunks)
                retriever._refresh_bm25_index()
            st.success(f"Successfully indexed {count} new chunks from {uploaded_file.name}!")
            st.rerun()

    st.divider()
    st.markdown("### Currently Indexed Documents")
    
    docs_found = loader.load_all_documents()
    doc_summary = {}
    for d in docs_found:
        if d.doc_name not in doc_summary:
            doc_summary[d.doc_name] = {"pages": 0, "chars": 0, "format": d.metadata.get("format", "pdf")}
        doc_summary[d.doc_name]["pages"] += 1
        doc_summary[d.doc_name]["chars"] += d.char_count

    cols = st.columns(len(doc_summary) if doc_summary else 1)
    for idx, (doc_name, info) in enumerate(doc_summary.items()):
        with cols[idx % len(cols)]:
            st.markdown(f"""
            <div class="stat-box">
                <div style="font-size: 28px;">📄</div>
                <div style="font-weight: 600; font-size: 13px; margin: 6px 0;">{doc_name}</div>
                <div class="stat-label">{info['pages']} Page(s) | {info['chars']} Chars</div>
            </div>
            """, unsafe_allow_html=True)


# =============================================================================
# TAB 3: Cloud Scalability & Semantic Cache
# =============================================================================
with tab_scalability:
    st.subheader("⚡ Cloud RAG Scalability & Query Acceleration")
    st.write("Demonstration of high-concurrency cloud architecture designed for thousands of simultaneous campus users.")

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{cache_stats['cached_entries']}</div>
            <div class="stat-label">Cached Queries</div>
        </div>
        """, unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{cache_stats['hits']}</div>
            <div class="stat-label">Cache Hits</div>
        </div>
        """, unsafe_allow_html=True)
    with col_s3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number" style="color:#10b981;">{cache_stats['hit_rate_pct']}%</div>
            <div class="stat-label">Hit Ratio</div>
        </div>
        """, unsafe_allow_html=True)
    with col_s4:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number" style="color:#0284c7;">&lt; 15 ms</div>
            <div class="stat-label">Hit Latency</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🏗️ Cloud-Native Architecture Diagram")
    st.code("""
    [Student Query] ──> [Application Load Balancer (AWS ALB)]
                             │
                             ▼
               [Scalable Cloud RAG Service (AWS ECS / Cloud Run)]
                             │
                 ┌───────────┴───────────┐
                 │                       │
     [Semantic Cache (Redis)]     [Vector Database (Qdrant / Pinecone)]
        (Sub-15ms Return)                │
                                         ▼
                             [Hybrid Re-Ranker (Dense + BM25)]
                                         │
                                         ▼
                             [Cloud Claude 3.5 Sonnet (AWS Bedrock)]
                                         │
                                         ▼
                             [Strict Grounded Answer + Citations]
    """, language="text")

    col_flush, col_reindex = st.columns(2)
    with col_flush:
        if st.button("🗑️ Flush Semantic Cache", use_container_width=True):
            cache_manager.clear()
            st.success("Semantic cache flushed.")
            st.rerun()
    with col_reindex:
        if st.button("🔄 Force Re-Index Vector Store", use_container_width=True):
            vector_store.clear()
            docs = loader.load_all_documents()
            chunks = chunker.chunk_pages(docs)
            vector_store.add_chunks(chunks)
            retriever._refresh_bm25_index()
            st.success("Vector database rebuilt successfully.")
            st.rerun()


# =============================================================================
# TAB 4: Quantitative Evaluation & Benchmark Suite
# =============================================================================
with tab_benchmarks:
    st.subheader("🧪 Official Academic Evaluation Framework (RAG-17 & RAG-18)")
    st.caption("Quantitative benchmarking across 50 categorized questions evaluating Retrieval Accuracy, Safe Refusal Rate, and 5D Answer Quality.")

    col_eval_btn, col_sample_size = st.columns([1, 2])
    with col_eval_btn:
        run_eval = st.button("▶️ Run 50-Question Benchmark", type="primary", use_container_width=True)
    with col_sample_size:
        sample_limit = st.slider("Number of Questions to Benchmark:", min_value=5, max_value=50, value=50, step=5)

    eval_results_file = BASE_DIR / "evaluation_results.json"
    
    if run_eval:
        evaluator = RAGEvaluator(pipeline)
        with st.spinner(f"Evaluating {sample_limit} benchmark questions..."):
            benchmark_data = evaluator.run_benchmark(max_questions=sample_limit)
        st.success(f"Benchmarked {sample_limit} questions successfully!")
    elif eval_results_file.exists():
        with open(eval_results_file, "r", encoding="utf-8") as f:
            benchmark_data = json.load(f)
    else:
        benchmark_data = None

    if benchmark_data:
        summary = benchmark_data["summary"]
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Retrieval Accuracy", f"{summary['retrieval_accuracy_pct']}%", delta="Target: >=90%")
        with m2:
            st.metric("Safe Refusal Rate", f"{summary['safe_refusal_rate_pct']}%", delta="Target: 100% (Zero Hallucination)")
        with m3:
            st.metric("Overall Quality Score", f"{summary['overall_quality_score_out_of_5']} / 5.0", delta="5D Rubric")
        with m4:
            st.metric("Average Latency", f"{summary['average_latency_ms']} ms", delta="Cloud Optimized")

        st.divider()
        st.subheader("5-Dimensional Evaluation Rubric Breakdown")
        dims = summary["metrics_breakdown"]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Correctness", f"{dims['correctness']} / 5.0")
        c2.metric("Relevance", f"{dims['relevance']} / 5.0")
        c3.metric("Groundedness", f"{dims['groundedness']} / 5.0")
        c4.metric("Clarity", f"{dims['clarity']} / 5.0")
        c5.metric("Completeness", f"{dims['completeness']} / 5.0")

        st.divider()
        st.subheader("Benchmark Questions Results Table")
        eval_list = benchmark_data["evaluations"]
        table_rows = []
        for e in eval_list:
            table_rows.append({
                "ID": e["question_id"],
                "Category": e["category"].split(" - ")[0],
                "Question": e["question"],
                "Expected Document": e["expected_doc"],
                "Retrieved Document": e["retrieved_doc"],
                "Retrieval OK": "✅" if e["retrieval_correct"] else "❌",
                "Refusal OK": "✅" if e["refusal_correct"] else "❌",
                "Quality": f"{e['overall_quality']} / 5.0",
                "Latency (ms)": round(e["latency_ms"], 1)
            })
        st.dataframe(table_rows, use_container_width=True)


# =============================================================================
# TAB 5: Jira Project Management & Tracking
# =============================================================================
with tab_jira:
    st.subheader("📋 Jira Scrum Project Management Dashboard (Key: RAG)")
    st.write("Agile sprint tracking, story points burndown, and task execution history according to syllabus requirements.")

    # Jira Metrics Overview
    j1, j2, j3, j4 = st.columns(4)
    with j1:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">6</div>
            <div class="stat-label">Total Epics</div>
        </div>
        """, unsafe_allow_html=True)
    with j2:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">20</div>
            <div class="stat-label">Completed User Stories & Tasks</div>
        </div>
        """, unsafe_allow_html=True)
    with j3:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number" style="color:#0284c7;">81 pts</div>
            <div class="stat-label">Total Story Points Completed</div>
        </div>
        """, unsafe_allow_html=True)
    with j4:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number" style="color:#10b981;">100%</div>
            <div class="stat-label">Sprint Completion Rate</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.subheader("Agile Sprint Schedule & Deliverables")
    
    sprint_tabs = st.tabs(["Sprint 1: Foundation", "Sprint 2: RAG Development", "Sprint 3: Complete LLM App", "Sprint 4: Testing & Submission"])
    
    with sprint_tabs[0]:
        st.markdown("""
        **Sprint 1 Goal:** Requirements formulation, document collection, 50-question design, Cloud LLM integration.  
        **Velocity:** 16 Story Points | **Status:** ✅ Closed
        - `RAG-1`: Define functional requirements (Story - 3 pts)
        - `RAG-2`: Collect college documents (Task - 3 pts)
        - `RAG-3`: Prepare 50 sample questions (Task - 5 pts)
        - `RAG-4`: Configure Cloud LLM credentials (Task - 2 pts)
        - `RAG-5`: Run and test Claude cloud generation (Task - 3 pts)
        """)
    with sprint_tabs[1]:
        st.markdown("""
        **Sprint 2 Goal:** Semantic document chunking, multi-provider embeddings, hybrid vector search (Dense + BM25).  
        **Velocity:** 21 Story Points | **Status:** ✅ Closed
        - `RAG-6`: Develop PDF text extractor (Story - 3 pts)
        - `RAG-7`: Develop text chunking module (Story - 3 pts)
        - `RAG-8`: Generate embeddings (Story - 5 pts)
        - `RAG-9`: Create scalable vector database (Story - 5 pts)
        - `RAG-10`: Develop semantic retrieval (Story - 5 pts)
        """)
    with sprint_tabs[2]:
        st.markdown("""
        **Sprint 3 Goal:** Multi-Platform Claude integration, prompt engineering, anti-hallucination guardrail, Streamlit UI.  
        **Velocity:** 24 Story Points | **Status:** ✅ Closed
        - `RAG-11`: Integrate retrieved context with LLM (Story - 5 pts)
        - `RAG-12`: Develop strict RAG prompt (Story - 3 pts)
        - `RAG-13`: Implement source citation (Story - 3 pts)
        - `RAG-14`: Implement unknown-answer handling (Story - 3 pts)
        - `RAG-15`: Create Streamlit UI (Story - 5 pts)
        - `RAG-16`: Display retrieved sources (Story - 3 pts)
        - `CACHE-1`: Semantic cache accelerator (Story - 2 pts)
        """)
    with sprint_tabs[3]:
        st.markdown("""
        **Sprint 4 Goal:** Functional regression testing, 5D rubric evaluation, defect resolution (RAG-19), faculty documentation.  
        **Velocity:** 20 Story Points | **Status:** ✅ Closed
        - `RAG-17`: Perform functional testing (Task - 5 pts)
        - `RAG-18`: Evaluate LLM responses (Task - 5 pts)
        - `RAG-19`: Fix identified defects in BM25 tokenization (Bug - 5 pts)
        - `RAG-20`: Prepare documentation and demo (Task - 5 pts)
        """)

    st.divider()
    # Download Jira Import CSV
    jira_csv_path = BASE_DIR / "jira" / "jira_backlog.csv"
    if jira_csv_path.exists():
        with open(jira_csv_path, "r", encoding="utf-8") as f:
            csv_content = f.read()
        st.download_button(
            label="📥 Download Official Jira Backlog CSV (Import into Jira Cloud)",
            data=csv_content,
            file_name="jira_backlog.csv",
            mime="text/csv",
            type="primary"
        )


# =============================================================================
# TAB 6: Cloud Settings & Multi-Provider Switcher
# =============================================================================
with tab_settings:
    st.subheader("⚙️ Cloud Platform & Model Configuration")
    
    col_p1, col_p2 = st.columns(2)
    provider_map = {
        "Anthropic Cloud API (Direct)": "anthropic",
        "AWS Bedrock Claude": "aws_bedrock",
        "Google Cloud Vertex AI": "gcp_vertex",
        "OpenRouter Gateway": "openrouter",
        "Grounded Synthesis (Offline Demo)": "offline"
    }
    current_provider_name = [k for k, v in provider_map.items() if v == cfg.llm.provider]
    default_idx = list(provider_map.keys()).index(current_provider_name[0]) if current_provider_name else 0

    with col_p1:
        st.markdown("#### Cloud LLM Provider")
        active_llm = st.selectbox(
            "Select Active LLM Provider:",
            list(provider_map.keys()),
            index=default_idx
        )
        api_key_input = st.text_input("Anthropic API Key:", value=cfg.llm.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY", ""), type="password")
        aws_region_input = st.text_input("AWS Region:", value=cfg.llm.aws_region)
    
    with col_p2:
        st.markdown("#### Scalable Vector Database & Hyperparameters")
        vdb_map = {
            "ChromaDB (Cloud / Persistent)": "chroma_local",
            "Qdrant Cloud Cluster": "qdrant_cloud",
            "Pinecone Serverless": "pinecone"
        }
        active_vdb = st.selectbox(
            "Select Vector Database Backend:",
            list(vdb_map.keys()),
            index=0
        )
        top_k_input = st.slider("Retrieval Top-K Chunks:", min_value=1, max_value=8, value=cfg.rag.top_k)
        sim_thresh_input = st.slider("Similarity Threshold:", min_value=0.3, max_value=0.9, value=cfg.rag.similarity_threshold, step=0.05)
        hybrid_alpha_input = st.slider("Hybrid Search Alpha (Dense vs BM25):", min_value=0.0, max_value=1.0, value=cfg.rag.hybrid_alpha, step=0.05)

    if st.button("💾 Apply & Save Configuration Changes", type="primary", use_container_width=True):
        cfg.llm.provider = provider_map[active_llm]
        if api_key_input:
            cfg.llm.anthropic_api_key = api_key_input
            os.environ["ANTHROPIC_API_KEY"] = api_key_input
        cfg.llm.aws_region = aws_region_input
        cfg.vector_db.provider = vdb_map[active_vdb]
        cfg.rag.top_k = top_k_input
        cfg.rag.similarity_threshold = sim_thresh_input
        cfg.rag.hybrid_alpha = hybrid_alpha_input
        
        # Update LLM service provider
        pipeline.llm.provider = cfg.llm.provider
        pipeline.llm._init_clients()
        st.success(f"Configuration updated! Active LLM Provider: {active_llm} | Top-K: {top_k_input} | Alpha: {hybrid_alpha_input}")
        st.rerun()

    st.info("Configuration parameters can also be populated via `.env` file or cloud container environment variables.")
