"""Compatibility stub — seed_mock() delegates to the new vector store."""
from .vector_db import LocalVectorDB

_db = LocalVectorDB()


def seed_knowledge_base():
    _db.add_documents([
        {
            "id": "policy-001",
            "knowledge_item_id": "KI-RICE",
            "content": "Nấm đạo ôn (Magnaporthe oryzae) trên lúa: phòng ngừa bằng giống kháng bệnh, bón cân đối NPK, không thụ động nhiều.",
            "metadata": {"source_type": "policy", "crop": "lúa", "topic": "nấm đạo ôn"},
        },
        {
            "id": "policy-002",
            "knowledge_item_id": "KI-DURIAN",
            "content": "Tưới sầu riêng: lượng nước 30-40mm/ngày, tránh ngập úng gây thối rễ, tưới sáng sớm.",
            "metadata": {"source_type": "policy", "crop": "sầu riêng", "topic": "tưới tiêu"},
        },
        {
            "id": "policy-003",
            "knowledge_item_id": "KI-RICE",
            "content": "Bón phân lúa: 45kgN/ha đợt sinh trưởng, 15kgP2O5/ha đợt đẻ nhánh, sau đó bổ kali.",
            "metadata": {"source_type": "policy", "crop": "lúa", "topic": "bón phân"},
        },
    ])
