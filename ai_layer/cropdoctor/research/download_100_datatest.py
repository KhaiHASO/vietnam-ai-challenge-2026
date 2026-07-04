import os
import json
import logging
from datasets import load_dataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("100DatatestBuilder")

PLANT_VILLAGE_CLASSES_VI = {
    "Apple___Apple_scab": "Táo - Bệnh ghẻ (Apple scab)",
    "Apple___Black_rot": "Táo - Bệnh thối đen (Black rot)",
    "Apple___Cedar_apple_rust": "Táo - Bệnh rỉ sắt táo Cedar",
    "Apple___healthy": "Táo - Khỏe mạnh",
    "Blueberry___healthy": "Việt quất - Khỏe mạnh",
    "Cherry_(including_sour)___Powdery_mildew": "Anh đào - Bệnh phấn trắng",
    "Cherry_(including_sour)___healthy": "Anh đào - Khỏe mạnh",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "Ngô - Bệnh đốm lá xám (Cercospora)",
    "Corn_(maize)___Common_rust_": "Ngô - Bệnh rỉ sắt thông thường",
    "Corn_(maize)___Northern_Leaf_Blight": "Ngô - Bệnh cháy lá muộn (Northern Leaf Blight)",
    "Corn_(maize)___healthy": "Ngô - Khỏe mạnh",
    "Grape___Black_rot": "Nho - Bệnh thối đen (Black rot)",
    "Grape___Esca_(Black_Measles)": "Nho - Bệnh Esca (Lốm đốm đen)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "Nho - Bệnh cháy lá (Isariopsis)",
    "Grape___healthy": "Nho - Khỏe mạnh",
    "Orange___Haunglongbing_(Citrus_greening)": "Cam - Bệnh vàng lá gân xanh (Citrus greening)",
    "Peach___Bacterial_spot": "Đào - Bệnh đốm vi khuẩn",
    "Peach___healthy": "Đào - Khỏe mạnh",
    "Pepper,_bell___Bacterial_spot": "Ớt chuông - Bệnh đốm vi khuẩn",
    "Pepper,_bell___healthy": "Ớt chuông - Khỏe mạnh",
    "Potato___Early_blight": "Khoai tây - Bệnh úa sớm (Early blight)",
    "Potato___Late_blight": "Khoai tây - Bệnh mốc sương (Late blight)",
    "Potato___healthy": "Khoai tây - Khỏe mạnh",
    "Raspberry___healthy": "Mâm xôi - Khỏe mạnh",
    "Soybean___healthy": "Đậu nành - Khỏe mạnh",
    "Squash___Powdery_mildew": "Bí ngòi/Bí đỏ - Bệnh phấn trắng",
    "Strawberry___Leaf_scorch": "Dâu tây - Bệnh cháy lá (Leaf scorch)",
    "Strawberry___healthy": "Dâu tây - Khỏe mạnh",
    "Tomato___Bacterial_spot": "Cà chua - Bệnh đốm vi khuẩn",
    "Tomato___Early_blight": "Cà chua - Bệnh úa sớm (Early blight)",
    "Tomato___Late_blight": "Cà chua - Bệnh mốc sương (Late blight)",
    "Tomato___Leaf_Mold": "Cà chua - Bệnh mốc lá (Leaf mold)",
    "Tomato___Septoria_leaf_spot": "Cà chua - Bệnh đốm lá Septoria",
    "Tomato___Spider_mites Two-spotted_spider_mite": "Cà chua - Bệnh nhện đỏ hai chấm",
    "Tomato___Target_Spot": "Cà chua - Bệnh đốm vòng (Target Spot)",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "Cà chua - Bệnh virus xoăn lùn lá vàng",
    "Tomato___Tomato_mosaic_virus": "Cà chua - Bệnh virus khảm cà chua",
    "Tomato___healthy": "Cà chua - Khỏe mạnh"
}

def build_100_datatest():
    # Target path C:\Users\Admin\Desktop\github\VisionAgricultureDemo\datatest
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    datatest_dir = os.path.join(base_dir, "datatest")
    os.makedirs(datatest_dir, exist_ok=True)
    
    logger.info(f"Target directory: {datatest_dir}")
    
    # Class list
    class_names = list(PLANT_VILLAGE_CLASSES_VI.keys())
    
    # Load dataset
    logger.info("Loading PlantVillage dataset...")
    ds = load_dataset("BrandonFors/Plant-Diseases-PlantVillage-Dataset", split="train", streaming=True)
    
    # To keep it balanced, we allow at most 5 images per class
    class_counts = {name: 0 for name in class_names}
    max_per_class = 5
    target_total = 100
    
    collected_images = []
    
    logger.info("Streaming dataset and collecting 100 balanced images...")
    for item in ds:
        label_idx = item["label"]
        if 0 <= label_idx < len(class_names):
            class_name = class_names[label_idx]
            if class_counts[class_name] < max_per_class:
                class_counts[class_name] += 1
                collected_images.append({
                    "image": item["image"],
                    "class_name": class_name,
                    "label_vi": PLANT_VILLAGE_CLASSES_VI.get(class_name, class_name)
                })
                
                if len(collected_images) >= target_total:
                    break
                    
    logger.info(f"Collected {len(collected_images)} images. Saving them...")
    
    catalog = {}
    
    # Write files
    for idx, data in enumerate(collected_images):
        file_number = idx + 1
        filename = f"leaf_{file_number:03d}.jpg"
        path = os.path.join(datatest_dir, filename)
        
        # Save image
        data["image"].save(path, format="JPEG")
        
        # Add to catalog
        catalog[filename] = {
            "class_name": data["class_name"],
            "label_vi": data["label_vi"]
        }
        
    # Save labels.json (overwriting with all 100 + original ones)
    json_path = os.path.join(datatest_dir, "labels.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
        
    # Update README.md with the table of 100 files
    readme_path = os.path.join(datatest_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(f"""# 📁 Danh mục Bộ Dữ Liệu Kiểm Thử 100 Ảnh (Blind Test Suite)

Thư mục này chứa **{len(catalog)}** tệp ảnh thực tế được trích xuất từ tập dữ liệu học thuật **PlantVillage** gốc. 
Các tệp ảnh được đặt tên từ `leaf_001.jpg` đến `leaf_100.jpg` để bạn dễ dàng làm bài test "mù" (blind test) cho hệ thống chẩn đoán **CropDoctor AI**.

## 📋 Bảng Nhãn Đối Chiếu (Ground Truth Catalog)

| Tên File | Nhãn Tiếng Anh (Model Class) | Chẩn Đoán Việt Hóa (Ground Truth) |
| :--- | :--- | :--- |
""")
        for filename, info in sorted(catalog.items()):
            f.write(f"| **`{filename}`** | `{info['class_name']}` | {info['label_vi']} |\n")
            
        f.write("""
---

## 🚀 Hướng dẫn Chạy Kiểm Thử (How to Test)

1. Truy cập giao diện tại: **http://localhost:8501**
2. Chọn **"Tải ảnh lên từ thiết bị"** ở cột trái.
3. Kéo thả bất kỳ tệp ảnh nào từ `leaf_001.jpg` đến `leaf_100.jpg` từ thư mục này lên giao diện.
4. Bấm nút **"Phân Tích Và Chẩn Đoán Ngay"**.
5. Xem kết quả chẩn đoán ở cột bên phải, đối chiếu với **Bảng Nhãn Đối Chiếu** ở phía trên để chấm điểm độ chính xác cho mô hình!
""")

    logger.info("Done building 100 image dataset!")
    print("\n" + "="*50)
    print("SUCCESS: 100 REAL TEST IMAGES AND LABELS GENERATED!")
    print(f"Path: {datatest_dir}")
    print("="*50 + "\n")

if __name__ == "__main__":
    build_100_datatest()
