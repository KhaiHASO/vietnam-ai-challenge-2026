# Project Rules & Design Guidelines

Tài liệu này định nghĩa các quy tắc bắt buộc mà mọi AI Agent khi làm việc trên repository này phải tuân thủ.

## 1. Quy tắc giao diện (UI & Template Guidelines)
* **Bắt buộc tuân thủ template**: Dự án sử dụng template **Velzon (Next.js & Bootstrap/Reactstrap)**. Không được tự ý chế, tự bịa hoặc viết đè các class CSS ad-hoc.
* **Hỗ trợ theme sáng/tối (Light/Dark Mode)**:
  * Tuyệt đối **không gán cứng** các class màu sắc tối/sáng như `bg-dark`, `bg-light`, `text-white`, `text-black` vào các cấu trúc layout chung (ví dụ: `Col`, `Card`, `Container`).
  * Sử dụng các class mặc định của Bootstrap/Reactstrap hoặc Velzon như `card`, `text-muted`, `bg-light` để giao diện tự động co giãn tone màu theo theme của hệ thống.
  * Chỉ dùng các nút bấm có màu sắc tiêu chuẩn (`primary`, `secondary`, `success`, `danger`, `warning`, `info`, `light`, `dark`).

## 2. Quy tắc mã nguồn Python (Python & PyTorch Engine)
* **Import an toàn (Optional Imports)**: 
  * Mô hình PyTorch `ImpactTriageNet` và các module liên quan phải hỗ trợ chế độ chạy không cần PyTorch (ví dụ: trong môi trường không có GPU hoặc chưa chạy `pip install`).
  * Tất cả các import `import torch` và `from torch.utils.data import Dataset` phải được bọc trong block `try...except ImportError` và định nghĩa sẵn các lớp mock dự phòng.
  * Nếu không có PyTorch, hệ thống tự động chuyển sang cơ chế suy luận rule-based fallback (`run_rule_based_fallback`).

## 3. Quy tắc liên kết tệp tin (File Link Conventions)
* Tất cả các tham chiếu đến tệp tin trong tài liệu hoặc phản hồi phải sử dụng liên kết markdown có thể click được (clickable links) với giao thức `file://` và đường dẫn tuyệt đối (sử dụng dấu gạch chéo `/` ngay cả trên Windows).
  * Ví dụ đúng: `[page.tsx](file:///C:/Users/Admin/Desktop/github/vietnam-ai-challenge-2026/frontend/src/app/%28with-layout%29/diagnosis/page.tsx)`
