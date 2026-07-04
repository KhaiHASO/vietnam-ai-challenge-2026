import os
import json
import logging
from datasets import load_dataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DatatestBuilder")

def build_datatest():
    # Folder paths
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    datatest_dir = os.path.join(base_dir, "datatest")
    os.makedirs(datatest_dir, exist_ok=True)
    
    logger.info(f"Target directory for datatest: {datatest_dir}")
    
    # Load dataset
    logger.info("Loading PlantVillage dataset features to extract class labels...")
    # Loading dataset split train to check names
    ds = load_dataset("BrandonFors/Plant-Diseases-PlantVillage-Dataset", split="train", streaming=True)
    
    # Extract class names
    # BrandonFors/Plant-Diseases-PlantVillage-Dataset classes (usually the 38 classes of PlantVillage)
    class_names = [
        "Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust", "Apple___healthy",
        "Blueberry___healthy", "Cherry_(including_sour)___Powdery_mildew", "Cherry_(including_sour)___healthy",
        "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot", "Corn_(maize)___Common_rust_",
        "Corn_(maize)___Northern_Leaf_Blight", "Corn_(maize)___healthy", "Grape___Black_rot",
        "Grape___Esca_(Black_Measles)", "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)", "Grape___healthy",
        "Orange___Haunglongbing_(Citrus_greening)", "Peach___Bacterial_spot", "Peach___healthy",
        "Pepper,_bell___Bacterial_spot", "Pepper,_bell___healthy", "Potato___Early_blight",
        "Potato___Late_blight", "Potato___healthy", "Raspberry___healthy", "Soybean___healthy",
        "Squash___Powdery_mildew", "Strawberry___Leaf_scorch", "Strawberry___healthy",
        "Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___Late_blight", "Tomato___Leaf_Mold",
        "Tomato___Septoria_leaf_spot", "Tomato___Spider_mites Two-spotted_spider_mite",
        "Tomato___Target_Spot", "Tomato___Tomato_Yellow_Leaf_Curl_Virus", "Tomato___Tomato_mosaic_virus",
        "Tomato___healthy"
    ]
    
    # Mapping of target classes we want to collect
    targets = {
        "Tomato___Early_blight": {
            "filename": "tomato_early_blight.jpg",
            "title": "Cà chua - Bệnh úa sớm (Early Blight)",
            "description": "Các vết đốm màu nâu đen vòng tròn đồng tâm, thường xuất hiện ở các lá già sát đất."
        },
        "Tomato___Late_blight": {
            "filename": "tomato_late_blight.jpg",
            "title": "Cà chua - Bệnh mốc sương (Late Blight)",
            "description": "Vết thâm thối loang rộng mép lá như vết bỏng nước, khi ẩm ướt có tơ trắng dưới mặt lá."
        },
        "Tomato___healthy": {
            "filename": "tomato_healthy.jpg",
            "title": "Cà chua - Lá khỏe mạnh (Healthy)",
            "description": "Phiến lá màu xanh đều màu, không bị đốm hay rỉ sét."
        },
        "Potato___Early_blight": {
            "filename": "potato_early_blight.jpg",
            "title": "Khoai tây - Bệnh úa sớm (Early Blight)",
            "description": "Đốm đen có vòng đồng tâm khô ráp trên lá khoai tây."
        },
        "Potato___Late_blight": {
            "filename": "potato_late_blight.jpg",
            "title": "Khoai tây - Bệnh mốc sương (Late Blight)",
            "description": "Bệnh thối nhũn lá và thân khoai tây lan rất nhanh trong điều kiện ẩm ướt."
        },
        "Pepper,_bell___Bacterial_spot": {
            "filename": "pepper_bacterial_spot.jpg",
            "title": "Ớt chuông - Bệnh đốm vi khuẩn (Bacterial Spot)",
            "description": "Các đốm nhỏ ngậm nước li ti có viền vàng nhạt trên lá ớt chuông."
        }
    }
    
    # Find matching labels indices
    label_to_key = {}
    for idx, name in enumerate(class_names):
        if name in targets:
            label_to_key[idx] = name
            
    logger.info(f"Target label mapping: {label_to_key}")
    
    collected = {}
    
    logger.info("Streaming dataset to collect target images...")
    for item in ds:
        label_idx = item["label"]
        if label_idx in label_to_key:
            class_name = label_to_key[label_idx]
            if class_name not in collected:
                image = item["image"]
                target_info = targets[class_name]
                path = os.path.join(datatest_dir, target_info["filename"])
                
                # Save as JPEG
                image.save(path, format="JPEG")
                logger.info(f"Saved real image for class {class_name} to {path}")
                
                collected[class_name] = {
                    "filename": target_info["filename"],
                    "class_name": class_name,
                    "title": target_info["title"],
                    "description": target_info["description"]
                }
                
        # Stop once we have all targets
        if len(collected) == len(targets):
            break
            
    # Save labels.json in datatest directory
    json_path = os.path.join(datatest_dir, "labels.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(collected, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved labels catalog to {json_path}")
    
    # Save README.md guide in datatest directory
    readme_path = os.path.join(datatest_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(f"""# 📁 Danh mục Dữ liệu Kiểm thử (Datatest Catalog)

Thư mục này chứa **{len(collected)}** tệp ảnh thực tế được trích xuất từ tập dữ liệu học thuật **PlantVillage** gốc. 
Bạn có thể sử dụng các ảnh này để kiểm tra độ chính xác của mô hình chẩn đoán **CropDoctor AI** qua giao diện Streamlit hoặc các API Backend.

## 📋 Danh sách nhãn đối chiếu (Ground Truth Labels)

| Tên File | Cây Trồng & Bệnh Lý | Nhãn Tiếng Anh (Model Class) | Đặc Điểm Nhận Biết Lâm Sàng |
| :--- | :--- | :--- | :--- |
""")
        for class_name, info in collected.items():
            f.write(f"| **`{info['filename']}`** | {info['title']} | `{info['class_name']}` | {info['description']} |\n")
            
        f.write("""
---

## 🚀 Hướng dẫn Kiểm Thử (Testing Guide)

1. Mở trình duyệt truy cập giao diện tại: **http://localhost:8501**
2. Ở cột bên trái, chọn phần nguồn ảnh là **"Tải ảnh lên từ thiết bị"**.
3. Nhấp chọn và tải lên một tệp ảnh bất kỳ trong thư mục `datatest` này.
4. Đảm bảo chọn đúng gợi ý **"Bạn đang chụp cây gì? (Crop Hint)"** tương ứng ở mục số 1:
   - Chọn `tomato` cho ảnh cà chua (`tomato_early_blight.jpg`, `tomato_late_blight.jpg`, `tomato_healthy.jpg`).
   - Chọn `potato` cho ảnh khoai tây (`potato_early_blight.jpg`, `potato_late_blight.jpg`).
   - Chọn `pepper` cho ảnh ớt chuông (`pepper_bacterial_spot.jpg`).
5. Bấm **"Phân Tích Và Chẩn Đoán Ngay"** và đối chiếu kết quả trong tab **"Chi Tiết Kỹ Thuật (Consensus)"** với cột **Nhãn Tiếng Anh (Model Class)** ở bảng phía trên để xác minh tính chính xác của hệ thống.
""")
    logger.info(f"Saved README.md guide to {readme_path}")
    print("\n" + "="*50)
    print("DATATEST FOLDER CONSTRUCTED SUCCESSFULLY!")
    print(f"Path: {datatest_dir}")
    print(f"Files saved: {len(collected)} real images, labels.json, README.md")
    print("="*50 + "\n")

if __name__ == "__main__":
    build_datatest()
