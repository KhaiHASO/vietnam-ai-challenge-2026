from ai_layer.rag.vector_db import LocalVectorDB

def seed_knowledge_base():
    """Seeds the Vector DB with default SME policy guidelines."""
    db = LocalVectorDB()
    
    # If DB is already seeded, don't seed again
    if len(db.documents) > 0:
        print("[RAG] Vector DB already has documents. Skipping seed.")
        return
        
    mock_docs = [
        {
            "id": "policy_refund_01",
            "content": "Chính sách hoàn tiền: Khách hàng được hoàn trả 100% số tiền nếu yêu cầu hủy dịch vụ được thực hiện ít nhất 6 tiếng trước giờ bắt đầu. Nếu hủy từ 2 đến 6 tiếng, hoàn 50%. Hủy dưới 2 tiếng không được hoàn tiền.",
            "metadata": {"category": "finance", "tags": ["refund", "cancellation"]}
        },
        {
            "id": "policy_refund_momo",
            "content": "Đối với các thanh toán qua Ví điện tử Momo, việc hoàn tiền tự động chỉ được thực hiện cho các giao dịch dưới 500,000 VND. Các giao dịch từ 500,000 VND trở lên yêu cầu người quản trị (Admin) phê duyệt thủ công (Human-in-the-loop) để phòng tránh gian lận.",
            "metadata": {"category": "payment", "tags": ["momo", "approval", "limits"]}
        },
        {
            "id": "policy_booking_01",
            "content": "Quy định đặt sân: Sân Pickleball hoạt động từ 6:00 đến 22:00 hàng ngày. Khách hàng phải thanh toán trong vòng 15 phút sau khi giữ chỗ trực tuyến, nếu không hệ thống sẽ tự động hủy booking và giải phóng sân.",
            "metadata": {"category": "booking", "tags": ["pickleball", "hours", "payment_limit"]}
        },
        {
            "id": "policy_support_ticket",
            "content": "Chính sách tạo ticket hỗ trợ: Khi khách hàng khiếu nại về lỗi trừ tiền mà không có mã booking, nhân viên hoặc AI Agent phải lập tức tạo Ticket hỗ trợ. Mức độ ưu tiên của ticket liên quan đến giao dịch tài chính bị lỗi luôn được đặt là High (Cao).",
            "metadata": {"category": "support", "tags": ["ticket", "priority", "finance"]}
        }
    ]
    
    print("[RAG] Seeding default knowledge base documents...")
    db.add_documents(mock_docs)
    print(f"[RAG] Successfully seeded {len(mock_docs)} documents.")

if __name__ == "__main__":
    seed_knowledge_base()
