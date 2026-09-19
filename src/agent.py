from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        chunks = self.store.search(question, top_k=top_k)
        if not chunks:
            return "Không tìm thấy thông tin phù hợp trong cơ sở tri thức để trả lời câu hỏi."

        context_parts = []
        for idx, chunk in enumerate(chunks, start=1):
            source = chunk.get("metadata", {}).get("doc_id", chunk.get("id", f"doc_{idx}"))
            context_parts.append(f"[{idx}] (Nguồn: {source}): {chunk['content']}")

        context_str = "\n\n".join(context_parts)
        prompt = (
            f"Dưới đây là thông tin tham khảo từ cơ sở tri thức:\n\n"
            f"{context_str}\n\n"
            f"Câu hỏi: {question}\n\n"
            f"Hãy trả lời câu hỏi trên dựa trên các đoạn thông tin được cung cấp. "
            f"Trích dẫn nguồn [1], [2],... tương ứng. Nếu ngữ cảnh không có thông tin, hãy nói rõ không tìm thấy."
        )
        return self.llm_fn(prompt)
