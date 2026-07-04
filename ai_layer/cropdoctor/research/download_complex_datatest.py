import os
import json
import logging
from datasets import load_dataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ComplexDatatestBuilder")

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

PLANTDOC_TO_PLANTVILLAGE = {
    "apple scab leaf": "Apple___Apple_scab",
    "apple leaf": "Apple___healthy",
    "apple rust leaf": "Apple___Cedar_apple_rust",
    "squash powdery mildew leaf": "Squash___Powdery_mildew",
    "cherry leaf": "Cherry_(including_sour)___healthy",
    "grape leaf": "Grape___healthy",
    "grape black rot leaf": "Grape___Black_rot",
    "peach leaf": "Peach___healthy",
    "peach bacterial spot leaf": "Peach___Bacterial_spot",
    "potato leaf": "Potato___healthy",
    "potato early blight leaf": "Potato___Early_blight",
    "potato late blight leaf": "Potato___Late_blight",
    "tomato early blight leaf": "Tomato___Early_blight",
    "tomato late blight leaf": "Tomato___Late_blight",
    "tomato leaf": "Tomato___healthy",
    "tomato mold leaf": "Tomato___Leaf_Mold",
    "tomato septoria leaf spot leaf": "Tomato___Septoria_leaf_spot",
    "tomato yellow leaf curl virus leaf": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "tomato mosaic virus leaf": "Tomato___Tomato_mosaic_virus",
    "corn leaf blight leaf": "Corn_(maize)___Northern_Leaf_Blight",
    "corn rust leaf": "Corn_(maize)___Common_rust_",
    "corn leaf": "Corn_(maize)___healthy",
    "pepper leaf": "Pepper,_bell___healthy",
    "pepper bacterial spot leaf": "Pepper,_bell___Bacterial_spot",
    "bell pepper leaf": "Pepper,_bell___healthy",
    "bell pepper leaf spot": "Pepper,_bell___Bacterial_spot",
    "potato leaf late blight": "Potato___Late_blight",
    "potato leaf early blight": "Potato___Early_blight",
    "tomato leaf late blight": "Tomato___Late_blight",
    "tomato leaf early blight": "Tomato___Early_blight",
    "tomato leaf yellow virus": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "tomato leaf mosaic virus": "Tomato___Tomato_mosaic_virus",
    "tomato leaf bacterial spot": "Tomato___Bacterial_spot",
    "tomato leaf spot": "Tomato___Septoria_leaf_spot"
}

def build_complex_datatest():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    datatest_dir = os.path.join(base_dir, "datatest")
    os.makedirs(datatest_dir, exist_ok=True)
    
    logger.info(f"Target directory for complex datatest: {datatest_dir}")
    
    # Load existing labels if present
    catalog = {}
    json_path = os.path.join(datatest_dir, "labels.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                catalog = json.load(f)
            logger.info(f"Loaded existing {len(catalog)} laboratory test cases from labels.json.")
        except Exception as e:
            logger.error(f"Error loading existing labels.json: {e}")
            
    # Load PlantDoc dataset
    logger.info("Loading PlantDoc in-the-wild dataset...")
    ds = load_dataset("geraldmc/plantdoc-full", split="train", streaming=True)
    
    # Keep track of class counts to balance classes
    class_counts = {}
    max_per_class = 6
    target_total = 100
    collected = []
    
    logger.info("Streaming PlantDoc to collect 100 in-the-wild complex images...")
    for item in ds:
        class_label = item.get("class_label", "").strip()
        label_lower = class_label.lower()
        
        # Map class label to PlantVillage standard key
        pv_key = PLANTDOC_TO_PLANTVILLAGE.get(label_lower)
        
        # If no exact match, try matching by substring
        if not pv_key:
            for k, v in PLANTDOC_TO_PLANTVILLAGE.items():
                if k in label_lower:
                    pv_key = v
                    break
                    
        if pv_key:
            class_counts[pv_key] = class_counts.get(pv_key, 0)
            if class_counts[pv_key] < max_per_class:
                class_counts[pv_key] += 1
                collected.append({
                    "image": item["image"],
                    "class_name": pv_key,
                    "label_vi": PLANT_VILLAGE_CLASSES_VI.get(pv_key, pv_key),
                    "original_label": class_label
                })
                
                if len(collected) >= target_total:
                    break
                    
    logger.info(f"Collected {len(collected)} complex in-the-wild images. Saving...")
    
    for idx, data in enumerate(collected):
        file_number = idx + 1
        filename = f"complex_leaf_{file_number:03d}.jpg"
        path = os.path.join(datatest_dir, filename)
        
        # Save image
        data["image"].save(path, format="JPEG")
        
        # Add to catalog
        catalog[filename] = {
            "class_name": data["class_name"],
            "label_vi": "[Ảnh thực địa phức tạp] " + data["label_vi"],
            "note_en": f"Originally labeled as '{data['original_label']}' in PlantDoc"
        }
        
    # Save the updated labels.json containing both lab and complex leaves
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    logger.info(f"Updated labels catalog written to {json_path}. Total images: {len(catalog)}")
    
    # Save a comprehensive README.md file listing all images
    readme_path = os.path.join(datatest_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(f"""# 📁 Danh mục Bộ Dữ Liệu Kiểm Thử 200 Ảnh (Lab + In-the-wild)

Thư mục này chứa **{len(catalog)}** tệp ảnh thực tế được chia làm hai tập con để phục vụ đánh giá đầy đủ năng lực AI:
1.  **Tập ảnh phòng thí nghiệm (`leaf_001.jpg` đến `leaf_100.jpg`):** Ảnh lá cây trên nền trơn sạch (dữ liệu **PlantVillage** gốc).
2.  **Tập ảnh thực địa phức tạp (`complex_leaf_001.jpg` đến `complex_leaf_100.jpg`):** Ảnh chụp lá cây trong điều kiện thực tế nông trại (dữ liệu **PlantDoc**). Ảnh có bối cảnh phức tạp: đất, cỏ dại, bàn tay nâng lá, ánh sáng dông nắng hoặc bóng râm gắt, đốm bệnh mờ hoặc lá bị chồng chéo.

---

## 📋 Danh Sách Nhãn Đối Chiếu (Ground Truth Catalog)

| Tên File | Nhãn Tiếng Anh (Model Class) | Chẩn Đoán Việt Hóa (Ground Truth) | Ghi Chú / Nguồn Dữ Liệu |
| :--- | :--- | :--- | :--- |
""")
        for filename, info in sorted(catalog.items()):
            note = info.get("note_en", "Dữ liệu phòng thí nghiệm (PlantVillage)")
            f.write(f"| **`{filename}`** | `{info['class_name']}` | {info['label_vi']} | {note} |\n")
            
        f.write("""
---

## 🚀 Hướng dẫn Chạy Kiểm Thử (How to Test)

1. Mở trình duyệt: **http://localhost:8501**
2. Chọn **"Tải ảnh lên từ thiết bị"** ở cột trái.
3. Tải lên ảnh phòng thí nghiệm `leaf_xxx.jpg` (dễ) hoặc ảnh thực địa `complex_leaf_xxx.jpg` (khó) lên giao diện.
4. Bấm **"Phân Tích Và Chẩn Đoán Ngay"** để xem AI nhận diện bệnh thực địa tốt đến mức nào so với ảnh tiêu chuẩn!
""")
        
    logger.info("Done building complex dataset!")
    print("\n" + "="*50)
    print("SUCCESS: 100 COMPLEX FIELD TEST IMAGES ADDED!")
    print(f"Total images in folder: {len(catalog)}")
    print(f"Path: {datatest_dir}")
    print("="*50 + "\n")

if __name__ == "__main__":
    build_complex_datatest()
