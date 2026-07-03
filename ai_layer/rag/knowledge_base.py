from ai_layer.config import settings
from ai_layer.rag.vector_db import LocalVectorDB

def seed_knowledge_base():
    """Seeds the Vector DB with dynamic domain policy guidelines."""
    db = LocalVectorDB()
    
    # If DB is already seeded, don't seed again
    if len(db.documents) > 0:
        print(f"[RAG] Vector DB for domain '{settings.ACTIVE_DOMAIN}' already has documents. Skipping seed.")
        return
        
    domain = settings.ACTIVE_DOMAIN
    
    if domain == "education":
        mock_docs = [
            {
                "id": "policy_attendance",
                "content": "Quy chế chuyên cần: Sinh viên nghỉ học quá 20% tổng số giờ học phần (vắng quá 3 buổi học đối với môn 3 tín chỉ) sẽ bị đình chỉ thi và nhận điểm F học phần.",
                "metadata": {"category": "academic", "tags": ["attendance", "failing"]}
            },
            {
                "id": "policy_scholarship",
                "content": "Quy định xét học bổng khuyến khích học tập: Sinh viên có GPA tích lũy từ 3.20 đến 3.59 đạt học bổng loại Khá; GPA từ 3.60 trở lên đạt học bổng Xuất sắc. Không có môn nào dưới điểm C và điểm rèn luyện trên 80.",
                "metadata": {"category": "scholarship", "tags": ["gpa", "reward"]}
            },
            {
                "id": "policy_warning",
                "content": "Chính sách cảnh cáo học vụ: Sinh viên bị cảnh cáo học vụ lần 1 nếu GPA học kỳ dưới 1.6. Cảnh cáo học vụ lần 2 nếu GPA dưới 1.8 trong hai học kỳ liên tiếp. Nhận cảnh cáo lần 3 sẽ bị buộc thôi học tự động.",
                "metadata": {"category": "rules", "tags": ["warning", "dismissal"]}
            }
        ]
    elif domain == "agriculture":
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
    else: # Default: SME
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
        
    print(f"[RAG] Seeding default knowledge base documents for '{domain}'...")
    db.add_documents(mock_docs)
    print(f"[RAG] Successfully seeded {len(mock_docs)} documents.")

if __name__ == "__main__":
    seed_knowledge_base()
