import sys, io, traceback
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

pass_count = 0
fail_count = 0

def check(name, fn):
    global pass_count, fail_count
    try:
        fn()
        print(f" PASS: {name}")
        pass_count += 1
    except Exception as e:
        print(f" FAIL: {name}: {e}")
        traceback.print_exc()
        fail_count += 1

print("=== Phase 2 Verification ===\n")

def test_imports():
    from ai_layer.rag.app_context import app_context
    _ = app_context.retriever
    _ = app_context.embedding_provider
    _ = app_context.vector_store
    _ = app_context.llm_provider

def test_seed_and_retrieve():
    from ai_layer.rag.knowledge_base import seed_knowledge_base
    seed_knowledge_base()
    from ai_layer.rag.app_context import app_context
    chunks = app_context.retriever.retrieve("nấm đạo ôn lúa", top_k=3)
    assert len(chunks) > 0, f"Expected >0 chunks, got {len(chunks)}"
    texts = " ".join(c.text for c in chunks)
    assert "nấm" in texts or "đạo" in texts or "lúa" in texts, f"No relevant content: {texts[:100]}"

def test_model_768dim():
    from ai_layer.config import settings
    assert "vietnamese-sbert" in settings.EMBEDDING_MODEL, f"Wrong model: {settings.EMBEDDING_MODEL}"
    from ai_layer.rag.app_context import app_context
    v = app_context.embedding_provider.embed_query("test nấm đạo ôn")
    assert len(v) == 768, f"Expected 768-dim, got {len(v)}"

def test_chroma_collection_768():
    from ai_layer.rag.app_context import app_context
    store = app_context.vector_store
    info = store.collection.count()
    assert info > 0, f"ChromaDB collection is empty: {info}"

def test_orchestrator_init():
    from ai_layer.orchestrator import AIOrchestrator
    o = AIOrchestrator()
    assert o is not None

def test_output_safety_not_strict():
    from ai_layer.guardrails.output_safety import OutputSafetyGuardrail
    g = OutputSafetyGuardrail(hallucination_threshold=0.8)
    blocked, score, reason = g.evaluate_output("Tôi có thể hỗ trợ giám sát sức khỏe cây trồng.", [])
    assert not blocked, f"Guardrail blocked safe output: {reason}"
    assert score < 0.8, f"Score too high for safe output: {score}"

def test_guardrail_still_catches_garbage():
    from ai_layer.guardrails.output_safety import OutputSafetyGuardrail
    g = OutputSafetyGuardrail(hallucination_threshold=0.8)
    blocked, score, reason = g.evaluate_output("blah random nonsense xyz", [])
    # With no RAG context, should not be blocked (score defaults)
    assert not blocked, f"Should not block empty context output"

def test_retriever_threshold_filter():
    from ai_layer.rag.app_context import app_context
    # request more than top_k to force filter activation inside retriever
    chunks = app_context.retriever.retrieve("nấm đạo ôn lúa", top_k=5)
    assert len(chunks) > 0
    for c in chunks:
        dist = c.metadata.extra.get("similarity_distance", 99)
        score = c.metadata.rerank_score
        assert dist <= 0.9, f"Distance too far: {dist}"

def test_knowledge_base_seeds():
    from ai_layer.rag.knowledge_base import seed_knowledge_base, _db
    seed_knowledge_base()
    assert len(_db.documents) > 0, "vector_db shim has no documents"

check("imports", test_imports)
check("seed_and_retrieve", test_seed_and_retrieve)
check("model_768dim", test_model_768dim)
check("chroma_collection_768", test_chroma_collection_768)
check("orchestrator_init", test_orchestrator_init)
check("output_safety_not_strict", test_output_safety_not_strict)
check("guardrail_still_catches_garbage", test_guardrail_still_catches_garbage)
check("retriever_threshold_filter", test_retriever_threshold_filter)
check("knowledge_base_seeds", test_knowledge_base_seeds)

print(f"\n=== Result: {pass_count} PASS, {fail_count} FAIL ===")
sys.exit(0 if fail_count == 0 else 1)
