from ai_layer.config import settings
from ai_layer.rag.vector_db import LocalVectorDB

def seed_knowledge_base():
    """Seeds the Vector DB with dynamic domain policy guidelines."""
    db = LocalVectorDB()
    
    # If DB is already seeded, don't seed again
    if len(db.documents) > 0:
        print(f"[RAG] Vector DB for domain '{settings.ACTIVE_DOMAIN}' already has documents. Skipping seed.")
        return
        
    mock_docs = [
        {
            "id": "policy_rice_disease",
            "content": "Triệu chứng và điều trị nấm đạo ôn lúa: Bệnh do nấm Pyricularia oryzae gây ra đốm hình quả trám màu xám nâu trên lá. Nếu diện tích lá bị hại vượt quá 10%, cần phun thuốc trừ nấm gốc Tricyclazole. Việc phun hóa chất này yêu cầu chuyên gia xác nhận.",
            "metadata": {"category": "disease", "tags": ["rice", "fungus", "pesticide"]}
        },
        {
            "id": "policy_durian_watering",
            "content": "Lịch tưới nước cho sầu riêng Monthong: Cần giữ độ ẩm đất ổn định từ 60-70% ở giai đoạn nuôi trái. Nếu độ ẩm giảm xuống dưới 40%, lá sẽ héo và rụng quả non. Khuyến nghị tưới 80-100 lít/gốc mỗi 2 ngày.",
            "metadata": {"category": "irrigation", "tags": ["durian", "water", "moisture"]}
        },
        {
            "id": "policy_fertilizer_rule",
            "content": "Chính sách bón phân hữu cơ: Bón lót phân chuồng hoai mục kết hợp NPK tỉ lệ 15-15-15 vào đầu mùa mưa. Tuyệt đối không bón phân hóa học đậm đặc trực tiếp vào sát gốc cây để tránh hiện tượng xót rễ.",
            "metadata": {"category": "fertilizer", "tags": ["NPK", "soil"]}
        }
    ]
        
    print(f"[RAG] Seeding default knowledge base documents for '{settings.ACTIVE_DOMAIN}'...")
    db.add_documents(mock_docs)
    print(f"[RAG] Successfully seeded {len(mock_docs)} documents.")

if __name__ == "__main__":
    seed_knowledge_base()
