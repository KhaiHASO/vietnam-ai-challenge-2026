# Design: Thiết Kế Hệ Thống Chẩn Đoán Lâm Sàng CropDoctor AI

Tài liệu thiết kế cấu trúc lớp xử lý của backend.

## 1. Thiết kế kiểm tra ảnh lâm sàng (Vision Guardrail)

```text
Upload ảnh ──► PIL (Convert to Grayscale)
                ├──► Mean Pixel < 45  ──► Từ chối (too_dark)
                └──► Std Dev < 15     ──► Từ chối (blurry)
```

## 2. Thiết kế logic chẩn đoán phân biệt & IPM 3 tầng

Trong `SafetyIpmService` và `ReasoningService`:
- Nếu `risk_level == "high"` hoặc có từ khóa thuốc hóa học mạnh: Đánh dấu `needs_approval = True`.
- Kế hoạch IPM tự động bọc các thuốc hóa học mạnh như `Ridomil Gold`, `Mancozeb` vào hàng đợi duyệt của chuyên gia.

## 3. Thiết kế phát hiện ổ dịch cấp hợp tác xã (Cooperative Outbreak Signal)

FastAPI endpoint `/api/cooperative/outbreaks`:
- Tìm kiếm các ca bệnh trong cùng khu vực (bán kính 5km) và có cùng chuẩn đoán trong vòng 7 ngày gần nhất.
- Nếu số ca bệnh vượt quá ngưỡng (ví dụ $\ge 3$ ca), hệ thống sẽ kích hoạt tín hiệu cảnh báo ổ dịch.
