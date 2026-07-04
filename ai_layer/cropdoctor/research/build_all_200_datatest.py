import os
import json
import logging
from datasets import load_dataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("UnifiedDatatestBuilder")

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

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    datatest_dir = os.path.join(root_dir, "datatest")
    os.makedirs(datatest_dir, exist_ok=True)
    
    logger.info(f"Target directory for 200 images: {datatest_dir}")
    
    catalog = {}
    
    # 1. Collect 100 Laboratory Images (PlantVillage)
    logger.info("Part 1: Loading PlantVillage (Lab) Dataset...")
    ds_pv = load_dataset("BrandonFors/Plant-Diseases-PlantVillage-Dataset", split="train", streaming=True)
    class_names = list(PLANT_VILLAGE_CLASSES_VI.keys())
    pv_counts = {name: 0 for name in class_names}
    max_pv_per_class = 5
    pv_collected = []
    
    for item in ds_pv:
        label_idx = item["label"]
        if 0 <= label_idx < len(class_names):
            class_name = class_names[label_idx]
            if pv_counts[class_name] < max_pv_per_class:
                pv_counts[class_name] += 1
                pv_collected.append({
                    "image": item["image"],
                    "class_name": class_name,
                    "label_vi": PLANT_VILLAGE_CLASSES_VI[class_name]
                })
                if len(pv_collected) >= 100:
                    break
                    
    logger.info(f"Part 1: Saving {len(pv_collected)} laboratory images...")
    for idx, data in enumerate(pv_collected):
        filename = f"leaf_{idx+1:03d}.jpg"
        path = os.path.join(datatest_dir, filename)
        data["image"].save(path, format="JPEG")
        catalog[filename] = {
            "class_name": data["class_name"],
            "label_vi": data["label_vi"],
            "source": "PlantVillage (Lab control)"
        }
        
    # 2. Collect 100 Complex Field Images (PlantDoc)
    logger.info("Part 2: Loading PlantDoc (Complex/In-the-wild) Dataset...")
    ds_pd = load_dataset("geraldmc/plantdoc-full", split="train", streaming=True)
    pd_counts = {}
    max_pd_per_class = 6
    pd_collected = []
    
    for item in ds_pd:
        class_label = item.get("class_label", "").strip()
        label_lower = class_label.lower()
        
        pv_key = PLANTDOC_TO_PLANTVILLAGE.get(label_lower)
        if not pv_key:
            for k, v in PLANTDOC_TO_PLANTVILLAGE.items():
                if k in label_lower:
                    pv_key = v
                    break
                    
        if pv_key:
            pd_counts[pv_key] = pd_counts.get(pv_key, 0)
            if pd_counts[pv_key] < max_pd_per_class:
                pd_counts[pv_key] += 1
                pd_collected.append({
                    "image": item["image"],
                    "class_name": pv_key,
                    "label_vi": PLANT_VILLAGE_CLASSES_VI[pv_key],
                    "original_label": class_label
                })
                if len(pd_collected) >= 100:
                    break
                    
    logger.info(f"Part 2: Saving {len(pd_collected)} complex field images...")
    for idx, data in enumerate(pd_collected):
        filename = f"complex_leaf_{idx+1:03d}.jpg"
        path = os.path.join(datatest_dir, filename)
        data["image"].save(path, format="JPEG")
        catalog[filename] = {
            "class_name": data["class_name"],
            "label_vi": "[Ảnh thực địa] " + data["label_vi"],
            "source": f"PlantDoc (In-the-wild) - Labeled as '{data['original_label']}'"
        }
        
    # 3. Save labels.json catalog
    json_path = os.path.join(datatest_dir, "labels.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved total {len(catalog)} labels to {json_path}")
    
    # 4. Save README.md guide
    readme_path = os.path.join(datatest_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(f"""# 📁 Danh mục Bộ Dữ Liệu Kiểm Thử 200 Ảnh (Lab + In-the-wild)

Thư mục này chứa **{len(catalog)}** tệp ảnh thực tế được chia làm hai tập con để phục vụ đánh giá đầy đủ năng lực AI:
1.  **Tập ảnh phòng thí nghiệm (`leaf_001.jpg` đến `leaf_100.jpg`):** Ảnh lá cây trên nền trơn sạch (dữ liệu **PlantVillage** gốc).
2.  **Tập ảnh thực địa phức tạp (`complex_leaf_001.jpg` đến `complex_leaf_100.jpg`):** Ảnh chụp lá cây trong điều kiện thực tế nông trại (dữ liệu **PlantDoc**). Ảnh có bối cảnh phức tạp: đất, cỏ dại, bàn tay nâng lá, ánh sáng dông nắng hoặc bóng râm gắt, đốm bệnh mờ hoặc lá bị chồng chéo.

---

## 📋 Danh Sách Nhãn Đối Chiếu (Ground Truth Catalog)

| Tên File | Nhãn Tiếng Anh (Model Class) | Chẩn Đoán Việt Hóa (Ground Truth) | Nguồn Dữ Liệu & Ghi Chú |
| :--- | :--- | :--- | :--- |
""")
        for filename, info in sorted(catalog.items()):
            f.write(f"| **`{filename}`** | `{info['class_name']}` | {info['label_vi']} | {info['source']} |\n")
            
        f.write("""
---

## 🚀 Hướng dẫn Chạy Kiểm Thử (How to Test)

1. Mở trình duyệt: **http://localhost:8501**
2. Chọn **"Tải ảnh lên từ thiết bị"** ở cột trái.
3. Tải lên ảnh phòng thí nghiệm `leaf_xxx.jpg` (dễ) hoặc ảnh thực địa `complex_leaf_xxx.jpg` (khó) lên giao diện.
4. Bấm **"Phân Tích Và Chẩn Đoán Ngay"** để xem AI nhận diện bệnh thực địa tốt đến mức nào so với ảnh tiêu chuẩn!
""")
        
    logger.info("Done building unified 200 datatest!")
    print("\n" + "="*50)
    print("SUCCESS: 200 IMAGES (100 LAB + 100 COMPLEX) GENERATED!")
    print(f"Path: {datatest_dir}")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
