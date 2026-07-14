import os
import numpy as np
import pandas as pd
try:
    import torch
    from torch.utils.data import Dataset
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    class Dataset:
        def __init__(self, *args, **kwargs):
            pass
from ai_layer.config import settings
from ai_layer.rag.vector_db import LocalVectorDB

class OperationsTriageDataset(Dataset):
    """
    PyTorch Dataset for AI-Native Operations Triage.
    Loads tabular metrics and embeds description text for training.
    """
    def __init__(self, domain: str = "agriculture", csv_path: str = None, num_samples: int = 200):
        self.domain = domain
        self.vector_db = LocalVectorDB() # Helper to get text embeddings
        
        # If no CSV path provided, try the default domain path, or generate synthetic data
        if not csv_path:
            csv_path = settings.data_path(self.domain) / "pytorch_dataset.csv"
            
        if not os.path.exists(csv_path):
            print(f"[PyTorch Dataset] CSV not found at {csv_path}. Generating synthetic data...")
            df = self.generate_synthetic_df(self.domain, num_samples)
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            df.to_csv(csv_path, index=False, encoding="utf-8")
        else:
            df = pd.read_csv(csv_path)

        self.df = df
        
        # Process Tabular Features (10 dimensions)
        self.tabular_features = self._extract_tabular_features(self.df, self.domain)
        
        # Process Text Embeddings
        print("[PyTorch Dataset] Encoding text descriptions. Please wait...")
        self.text_embeddings = self._encode_text_descriptions(self.df["description"].tolist())
        
        # Process Labels
        # Risk level: low (0), medium (1), high (2)
        self.risk_labels = self.df["risk_level"].map({"low": 0, "medium": 1, "high": 2}).fillna(0).values.astype(np.int64)
        # Priority score: float [0, 1]
        self.priority_scores = self.df["priority_score"].values.astype(np.float32)
        # Needs human review: bool -> float/int
        self.needs_review = self.df["needs_human_review"].astype(np.float32).values
        # Confidence score: float [0, 1]
        self.confidence_scores = self.df["confidence_score"].values.astype(np.float32)

    def _extract_tabular_features(self, df: pd.DataFrame, domain: str) -> np.ndarray:
        # Standardize features to 10 dims
        features = np.zeros((len(df), 10), dtype=np.float32)
        
        if domain == "sme":
            # Features: order_value (scaled), loyalty_tier, pending_tickets, is_payment_error, day_of_week, etc.
            features[:, 0] = df["order_value"] / 1000000.0  # Normalize value
            features[:, 1] = df["customer_loyalty_tier"] / 5.0 # Normalize tier
            features[:, 2] = df["pending_tickets_count"] / 10.0
            features[:, 3] = df["is_financial_transaction"].astype(np.float32)
        elif domain == "education":
            # Features: prior_gpa, attendance_rate, late_submissions, lms_activity_score, midterm_grade, etc.
            features[:, 0] = df["prior_gpa"] / 4.0
            features[:, 1] = df["attendance_rate"]
            features[:, 2] = df["late_submissions_count"] / 10.0
            features[:, 3] = df["lms_activity_score"] / 100.0
            features[:, 4] = df["midterm_grade"] / 10.0
        elif domain == "agriculture":
            # Features: leaf_damage_percentage, temperature, humidity, soil_moisture, rainfall, etc.
            features[:, 0] = df["leaf_damage_percent"] / 100.0
            features[:, 1] = (df["temperature"] - 15.0) / 30.0  # Min-Max approx
            features[:, 2] = df["humidity"] / 100.0
            features[:, 3] = df["soil_moisture"] / 100.0
            features[:, 4] = df["days_since_last_treatment"] / 30.0
            
        # Add random noise/padding to make up 10 dims if some are unused
        np.random.seed(42)
        noise = np.random.normal(0, 0.05, (len(df), 10))
        features = features + noise
        return features

    def _encode_text_descriptions(self, texts: list) -> np.ndarray:
        embeddings = []
        for text in texts:
            emb = self.vector_db.get_embedding(text)
            embeddings.append(emb)
        return np.array(embeddings, dtype=np.float32)

    def generate_synthetic_df(self, domain: str, num_samples: int) -> pd.DataFrame:
        np.random.seed(42)
        data = []
        
        sme_descriptions = [
            "Khách khiếu nại tài khoản bị trừ 220,000 VND qua ví Momo nhưng không xuất vé.",
            "Lịch hoạt động sân Pickleball bị xung đột vào lúc 18h tối nay.",
            "Yêu cầu hoàn tiền dịch vụ đặt trước do hệ thống bị lỗi thanh toán.",
            "Khách hàng hỏi thông tin về giờ mở cửa và phí thuê vợt.",
            "Báo cáo giao dịch thanh toán thành công, gửi hóa đơn điện tử.",
            "Yêu cầu hủy đặt sân trước 12 tiếng vì lý do gia đình.",
            "Khiếu nại về chất lượng dịch vụ bảo vệ tại bãi giữ xe sân bóng."
        ]
        
        edu_descriptions = [
            "Sinh viên vắng mặt liên tiếp 3 tuần học phần Lập trình Python ứng dụng.",
            "Sinh viên nộp bài tập muộn và có điểm thi giữa kỳ dưới trung bình.",
            "Yêu cầu tư vấn định hướng ngành học và hỗ trợ học bổng học tập.",
            "Sinh viên hỏi về thủ tục đăng ký học phần tự chọn và thời gian đóng học phí.",
            "Học viên tích cực phát biểu trên lớp và hoàn thành xuất sắc bài tập lớn.",
            "Sinh viên vi phạm quy chế thi cử lần đầu, cần xem xét cảnh cáo học vụ.",
            "Yêu cầu rút bớt môn học trong thời gian quy định do trùng lịch."
        ]
        
        agri_descriptions = [
            "Phát hiện vệt đốm nâu diện rộng trên lá lúa nghi ngờ do nấm đạo ôn.",
            "Đất bị khô hạn cục bộ do hệ thống tưới nhỏ giọt gặp sự cố rò rỉ nước.",
            "Đăng ký lịch bón phân hữu cơ NPK định kỳ cho vườn sầu riêng diện tích 2ha.",
            "Hỏi ý kiến chuyên gia nông nghiệp về kỹ thuật tỉa cành cho bưởi da xanh.",
            "Thời tiết nắng nóng kéo dài, độ ẩm không khí giảm mạnh dưới 45%.",
            "Ứng dụng phân bón lá và thuốc trừ sâu sinh học định kỳ hàng tháng.",
            "Báo cáo nông sản thu hoạch đạt chất lượng VietGAP xuất khẩu."
        ]
        
        for i in range(num_samples):
            if domain == "sme":
                desc = np.random.choice(sme_descriptions)
                order_value = float(np.random.choice([0, 150000, 220000, 450000, 600000, 1200000]))
                loyalty = int(np.random.randint(1, 5))
                pending = int(np.random.randint(0, 5))
                is_fin = 1.0 if order_value >= 220000 or "momo" in desc.lower() or "hoàn tiền" in desc.lower() else 0.0
                
                # Logic outputs
                if is_fin == 1.0 or "trừ" in desc or "hủy" in desc:
                    risk = "high" if order_value >= 500000 else "medium"
                    priority = np.random.uniform(0.7, 0.98)
                    review = True
                    conf = np.random.uniform(0.8, 0.95)
                else:
                    risk = "low"
                    priority = np.random.uniform(0.1, 0.4)
                    review = False
                    conf = np.random.uniform(0.85, 0.99)
                    
                data.append({
                    "description": desc,
                    "order_value": order_value,
                    "customer_loyalty_tier": loyalty,
                    "pending_tickets_count": pending,
                    "is_financial_transaction": is_fin,
                    "risk_level": risk,
                    "priority_score": priority,
                    "needs_human_review": review,
                    "confidence_score": conf
                })
                
            elif domain == "education":
                desc = np.random.choice(edu_descriptions)
                gpa = float(np.random.uniform(1.8, 3.9))
                attendance = float(np.random.uniform(0.6, 1.0))
                late = int(np.random.randint(0, 8))
                lms = float(np.random.uniform(20, 100))
                midterm = float(np.random.uniform(3, 10))
                
                # Logic outputs
                is_danger = attendance < 0.8 or midterm < 5.0 or "vắng" in desc or "vi phạm" in desc
                if is_danger:
                    risk = "high" if attendance < 0.7 else "medium"
                    priority = np.random.uniform(0.65, 0.95)
                    review = True
                    conf = np.random.uniform(0.75, 0.9)
                else:
                    risk = "low"
                    priority = np.random.uniform(0.1, 0.45)
                    review = False
                    conf = np.random.uniform(0.85, 0.98)
                    
                data.append({
                    "description": desc,
                    "prior_gpa": gpa,
                    "attendance_rate": attendance,
                    "late_submissions_count": late,
                    "lms_activity_score": lms,
                    "midterm_grade": midterm,
                    "risk_level": risk,
                    "priority_score": priority,
                    "needs_human_review": review,
                    "confidence_score": conf
                })
                
            elif domain == "agriculture":
                desc = np.random.choice(agri_descriptions)
                damage = float(np.random.uniform(0.0, 70.0))
                temp = float(np.random.uniform(20.0, 38.0))
                hum = float(np.random.uniform(40.0, 95.0))
                soil = float(np.random.uniform(30.0, 85.0))
                days_since = int(np.random.randint(0, 25))
                
                # Logic outputs
                is_risk = damage > 20.0 or "sâu bệnh" in desc or "hạn" in desc or "nấm" in desc
                if is_risk:
                    risk = "high" if damage > 40.0 else "medium"
                    priority = np.random.uniform(0.7, 0.99)
                    review = True
                    conf = np.random.uniform(0.8, 0.95)
                else:
                    risk = "low"
                    priority = np.random.uniform(0.15, 0.5)
                    review = False
                    conf = np.random.uniform(0.8, 0.99)
                    
                data.append({
                    "description": desc,
                    "leaf_damage_percent": damage,
                    "temperature": temp,
                    "humidity": hum,
                    "soil_moisture": soil,
                    "days_since_last_treatment": days_since,
                    "risk_level": risk,
                    "priority_score": priority,
                    "needs_human_review": review,
                    "confidence_score": conf
                })
                
        return pd.DataFrame(data)

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        return {
            "tab_features": torch.tensor(self.tabular_features[idx], dtype=torch.float32),
            "text_emb": torch.tensor(self.text_embeddings[idx], dtype=torch.float32),
            "risk_label": torch.tensor(self.risk_labels[idx], dtype=torch.long),
            "priority_score": torch.tensor(self.priority_scores[idx], dtype=torch.float32),
            "needs_review": torch.tensor(self.needs_review[idx], dtype=torch.float32),
            "confidence_score": torch.tensor(self.confidence_scores[idx], dtype=torch.float32)
        }
