# 📁 Danh mục Bộ Dữ Liệu Kiểm Thử 200 Ảnh (Lab + In-the-wild)

Thư mục này chứa **200** tệp ảnh thực tế được chia làm hai tập con để phục vụ đánh giá đầy đủ năng lực AI:
1.  **Tập ảnh phòng thí nghiệm (`leaf_001.jpg` đến `leaf_100.jpg`):** Ảnh lá cây trên nền trơn sạch (dữ liệu **PlantVillage** gốc).
2.  **Tập ảnh thực địa phức tạp (`complex_leaf_001.jpg` đến `complex_leaf_100.jpg`):** Ảnh chụp lá cây trong điều kiện thực tế nông trại (dữ liệu **PlantDoc**). Ảnh có bối cảnh phức tạp: đất, cỏ dại, bàn tay nâng lá, ánh sáng dông nắng hoặc bóng râm gắt, đốm bệnh mờ hoặc lá bị chồng chéo.

---

## 📋 Danh Sách Nhãn Đối Chiếu (Ground Truth Catalog)

| Tên File | Nhãn Tiếng Anh (Model Class) | Chẩn Đoán Việt Hóa (Ground Truth) | Nguồn Dữ Liệu & Ghi Chú |
| :--- | :--- | :--- | :--- |
| **`complex_leaf_001.jpg`** | `Apple___Apple_scab` | [Ảnh thực địa] Táo - Bệnh ghẻ (Apple scab) | PlantDoc (In-the-wild) - Labeled as 'Apple Scab Leaf' |
| **`complex_leaf_002.jpg`** | `Apple___Apple_scab` | [Ảnh thực địa] Táo - Bệnh ghẻ (Apple scab) | PlantDoc (In-the-wild) - Labeled as 'Apple Scab Leaf' |
| **`complex_leaf_003.jpg`** | `Apple___Apple_scab` | [Ảnh thực địa] Táo - Bệnh ghẻ (Apple scab) | PlantDoc (In-the-wild) - Labeled as 'Apple Scab Leaf' |
| **`complex_leaf_004.jpg`** | `Apple___Apple_scab` | [Ảnh thực địa] Táo - Bệnh ghẻ (Apple scab) | PlantDoc (In-the-wild) - Labeled as 'Apple Scab Leaf' |
| **`complex_leaf_005.jpg`** | `Apple___Apple_scab` | [Ảnh thực địa] Táo - Bệnh ghẻ (Apple scab) | PlantDoc (In-the-wild) - Labeled as 'Apple Scab Leaf' |
| **`complex_leaf_006.jpg`** | `Apple___Apple_scab` | [Ảnh thực địa] Táo - Bệnh ghẻ (Apple scab) | PlantDoc (In-the-wild) - Labeled as 'Apple Scab Leaf' |
| **`complex_leaf_007.jpg`** | `Apple___healthy` | [Ảnh thực địa] Táo - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Apple leaf' |
| **`complex_leaf_008.jpg`** | `Apple___healthy` | [Ảnh thực địa] Táo - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Apple leaf' |
| **`complex_leaf_009.jpg`** | `Apple___healthy` | [Ảnh thực địa] Táo - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Apple leaf' |
| **`complex_leaf_010.jpg`** | `Apple___healthy` | [Ảnh thực địa] Táo - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Apple leaf' |
| **`complex_leaf_011.jpg`** | `Apple___healthy` | [Ảnh thực địa] Táo - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Apple leaf' |
| **`complex_leaf_012.jpg`** | `Apple___healthy` | [Ảnh thực địa] Táo - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Apple leaf' |
| **`complex_leaf_013.jpg`** | `Apple___Cedar_apple_rust` | [Ảnh thực địa] Táo - Bệnh rỉ sắt táo Cedar | PlantDoc (In-the-wild) - Labeled as 'Apple rust leaf' |
| **`complex_leaf_014.jpg`** | `Apple___Cedar_apple_rust` | [Ảnh thực địa] Táo - Bệnh rỉ sắt táo Cedar | PlantDoc (In-the-wild) - Labeled as 'Apple rust leaf' |
| **`complex_leaf_015.jpg`** | `Apple___Cedar_apple_rust` | [Ảnh thực địa] Táo - Bệnh rỉ sắt táo Cedar | PlantDoc (In-the-wild) - Labeled as 'Apple rust leaf' |
| **`complex_leaf_016.jpg`** | `Apple___Cedar_apple_rust` | [Ảnh thực địa] Táo - Bệnh rỉ sắt táo Cedar | PlantDoc (In-the-wild) - Labeled as 'Apple rust leaf' |
| **`complex_leaf_017.jpg`** | `Apple___Cedar_apple_rust` | [Ảnh thực địa] Táo - Bệnh rỉ sắt táo Cedar | PlantDoc (In-the-wild) - Labeled as 'Apple rust leaf' |
| **`complex_leaf_018.jpg`** | `Apple___Cedar_apple_rust` | [Ảnh thực địa] Táo - Bệnh rỉ sắt táo Cedar | PlantDoc (In-the-wild) - Labeled as 'Apple rust leaf' |
| **`complex_leaf_019.jpg`** | `Pepper,_bell___healthy` | [Ảnh thực địa] Ớt chuông - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Bell_pepper leaf' |
| **`complex_leaf_020.jpg`** | `Pepper,_bell___healthy` | [Ảnh thực địa] Ớt chuông - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Bell_pepper leaf' |
| **`complex_leaf_021.jpg`** | `Pepper,_bell___healthy` | [Ảnh thực địa] Ớt chuông - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Bell_pepper leaf' |
| **`complex_leaf_022.jpg`** | `Pepper,_bell___healthy` | [Ảnh thực địa] Ớt chuông - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Bell_pepper leaf' |
| **`complex_leaf_023.jpg`** | `Pepper,_bell___healthy` | [Ảnh thực địa] Ớt chuông - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Bell_pepper leaf' |
| **`complex_leaf_024.jpg`** | `Pepper,_bell___healthy` | [Ảnh thực địa] Ớt chuông - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Bell_pepper leaf' |
| **`complex_leaf_025.jpg`** | `Cherry_(including_sour)___healthy` | [Ảnh thực địa] Anh đào - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Cherry leaf' |
| **`complex_leaf_026.jpg`** | `Cherry_(including_sour)___healthy` | [Ảnh thực địa] Anh đào - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Cherry leaf' |
| **`complex_leaf_027.jpg`** | `Cherry_(including_sour)___healthy` | [Ảnh thực địa] Anh đào - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Cherry leaf' |
| **`complex_leaf_028.jpg`** | `Cherry_(including_sour)___healthy` | [Ảnh thực địa] Anh đào - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Cherry leaf' |
| **`complex_leaf_029.jpg`** | `Cherry_(including_sour)___healthy` | [Ảnh thực địa] Anh đào - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Cherry leaf' |
| **`complex_leaf_030.jpg`** | `Cherry_(including_sour)___healthy` | [Ảnh thực địa] Anh đào - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Cherry leaf' |
| **`complex_leaf_031.jpg`** | `Corn_(maize)___healthy` | [Ảnh thực địa] Ngô - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Corn leaf blight' |
| **`complex_leaf_032.jpg`** | `Corn_(maize)___healthy` | [Ảnh thực địa] Ngô - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Corn leaf blight' |
| **`complex_leaf_033.jpg`** | `Corn_(maize)___healthy` | [Ảnh thực địa] Ngô - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Corn leaf blight' |
| **`complex_leaf_034.jpg`** | `Corn_(maize)___healthy` | [Ảnh thực địa] Ngô - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Corn leaf blight' |
| **`complex_leaf_035.jpg`** | `Corn_(maize)___healthy` | [Ảnh thực địa] Ngô - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Corn leaf blight' |
| **`complex_leaf_036.jpg`** | `Corn_(maize)___healthy` | [Ảnh thực địa] Ngô - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Corn leaf blight' |
| **`complex_leaf_037.jpg`** | `Corn_(maize)___Common_rust_` | [Ảnh thực địa] Ngô - Bệnh rỉ sắt thông thường | PlantDoc (In-the-wild) - Labeled as 'Corn rust leaf' |
| **`complex_leaf_038.jpg`** | `Corn_(maize)___Common_rust_` | [Ảnh thực địa] Ngô - Bệnh rỉ sắt thông thường | PlantDoc (In-the-wild) - Labeled as 'Corn rust leaf' |
| **`complex_leaf_039.jpg`** | `Corn_(maize)___Common_rust_` | [Ảnh thực địa] Ngô - Bệnh rỉ sắt thông thường | PlantDoc (In-the-wild) - Labeled as 'Corn rust leaf' |
| **`complex_leaf_040.jpg`** | `Corn_(maize)___Common_rust_` | [Ảnh thực địa] Ngô - Bệnh rỉ sắt thông thường | PlantDoc (In-the-wild) - Labeled as 'Corn rust leaf' |
| **`complex_leaf_041.jpg`** | `Corn_(maize)___Common_rust_` | [Ảnh thực địa] Ngô - Bệnh rỉ sắt thông thường | PlantDoc (In-the-wild) - Labeled as 'Corn rust leaf' |
| **`complex_leaf_042.jpg`** | `Corn_(maize)___Common_rust_` | [Ảnh thực địa] Ngô - Bệnh rỉ sắt thông thường | PlantDoc (In-the-wild) - Labeled as 'Corn rust leaf' |
| **`complex_leaf_043.jpg`** | `Peach___healthy` | [Ảnh thực địa] Đào - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Peach leaf' |
| **`complex_leaf_044.jpg`** | `Peach___healthy` | [Ảnh thực địa] Đào - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Peach leaf' |
| **`complex_leaf_045.jpg`** | `Peach___healthy` | [Ảnh thực địa] Đào - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Peach leaf' |
| **`complex_leaf_046.jpg`** | `Peach___healthy` | [Ảnh thực địa] Đào - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Peach leaf' |
| **`complex_leaf_047.jpg`** | `Peach___healthy` | [Ảnh thực địa] Đào - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Peach leaf' |
| **`complex_leaf_048.jpg`** | `Peach___healthy` | [Ảnh thực địa] Đào - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Peach leaf' |
| **`complex_leaf_049.jpg`** | `Potato___Early_blight` | [Ảnh thực địa] Khoai tây - Bệnh úa sớm (Early blight) | PlantDoc (In-the-wild) - Labeled as 'Potato leaf early blight' |
| **`complex_leaf_050.jpg`** | `Potato___Early_blight` | [Ảnh thực địa] Khoai tây - Bệnh úa sớm (Early blight) | PlantDoc (In-the-wild) - Labeled as 'Potato leaf early blight' |
| **`complex_leaf_051.jpg`** | `Potato___Early_blight` | [Ảnh thực địa] Khoai tây - Bệnh úa sớm (Early blight) | PlantDoc (In-the-wild) - Labeled as 'Potato leaf early blight' |
| **`complex_leaf_052.jpg`** | `Potato___Early_blight` | [Ảnh thực địa] Khoai tây - Bệnh úa sớm (Early blight) | PlantDoc (In-the-wild) - Labeled as 'Potato leaf early blight' |
| **`complex_leaf_053.jpg`** | `Potato___Early_blight` | [Ảnh thực địa] Khoai tây - Bệnh úa sớm (Early blight) | PlantDoc (In-the-wild) - Labeled as 'Potato leaf early blight' |
| **`complex_leaf_054.jpg`** | `Potato___Early_blight` | [Ảnh thực địa] Khoai tây - Bệnh úa sớm (Early blight) | PlantDoc (In-the-wild) - Labeled as 'Potato leaf early blight' |
| **`complex_leaf_055.jpg`** | `Potato___Late_blight` | [Ảnh thực địa] Khoai tây - Bệnh mốc sương (Late blight) | PlantDoc (In-the-wild) - Labeled as 'Potato leaf late blight' |
| **`complex_leaf_056.jpg`** | `Potato___Late_blight` | [Ảnh thực địa] Khoai tây - Bệnh mốc sương (Late blight) | PlantDoc (In-the-wild) - Labeled as 'Potato leaf late blight' |
| **`complex_leaf_057.jpg`** | `Potato___Late_blight` | [Ảnh thực địa] Khoai tây - Bệnh mốc sương (Late blight) | PlantDoc (In-the-wild) - Labeled as 'Potato leaf late blight' |
| **`complex_leaf_058.jpg`** | `Potato___Late_blight` | [Ảnh thực địa] Khoai tây - Bệnh mốc sương (Late blight) | PlantDoc (In-the-wild) - Labeled as 'Potato leaf late blight' |
| **`complex_leaf_059.jpg`** | `Potato___Late_blight` | [Ảnh thực địa] Khoai tây - Bệnh mốc sương (Late blight) | PlantDoc (In-the-wild) - Labeled as 'Potato leaf late blight' |
| **`complex_leaf_060.jpg`** | `Potato___Late_blight` | [Ảnh thực địa] Khoai tây - Bệnh mốc sương (Late blight) | PlantDoc (In-the-wild) - Labeled as 'Potato leaf late blight' |
| **`complex_leaf_061.jpg`** | `Squash___Powdery_mildew` | [Ảnh thực địa] Bí ngòi/Bí đỏ - Bệnh phấn trắng | PlantDoc (In-the-wild) - Labeled as 'Squash Powdery mildew leaf' |
| **`complex_leaf_062.jpg`** | `Squash___Powdery_mildew` | [Ảnh thực địa] Bí ngòi/Bí đỏ - Bệnh phấn trắng | PlantDoc (In-the-wild) - Labeled as 'Squash Powdery mildew leaf' |
| **`complex_leaf_063.jpg`** | `Squash___Powdery_mildew` | [Ảnh thực địa] Bí ngòi/Bí đỏ - Bệnh phấn trắng | PlantDoc (In-the-wild) - Labeled as 'Squash Powdery mildew leaf' |
| **`complex_leaf_064.jpg`** | `Squash___Powdery_mildew` | [Ảnh thực địa] Bí ngòi/Bí đỏ - Bệnh phấn trắng | PlantDoc (In-the-wild) - Labeled as 'Squash Powdery mildew leaf' |
| **`complex_leaf_065.jpg`** | `Squash___Powdery_mildew` | [Ảnh thực địa] Bí ngòi/Bí đỏ - Bệnh phấn trắng | PlantDoc (In-the-wild) - Labeled as 'Squash Powdery mildew leaf' |
| **`complex_leaf_066.jpg`** | `Squash___Powdery_mildew` | [Ảnh thực địa] Bí ngòi/Bí đỏ - Bệnh phấn trắng | PlantDoc (In-the-wild) - Labeled as 'Squash Powdery mildew leaf' |
| **`complex_leaf_067.jpg`** | `Tomato___Early_blight` | [Ảnh thực địa] Cà chua - Bệnh úa sớm (Early blight) | PlantDoc (In-the-wild) - Labeled as 'Tomato Early blight leaf' |
| **`complex_leaf_068.jpg`** | `Tomato___Early_blight` | [Ảnh thực địa] Cà chua - Bệnh úa sớm (Early blight) | PlantDoc (In-the-wild) - Labeled as 'Tomato Early blight leaf' |
| **`complex_leaf_069.jpg`** | `Tomato___Early_blight` | [Ảnh thực địa] Cà chua - Bệnh úa sớm (Early blight) | PlantDoc (In-the-wild) - Labeled as 'Tomato Early blight leaf' |
| **`complex_leaf_070.jpg`** | `Tomato___Early_blight` | [Ảnh thực địa] Cà chua - Bệnh úa sớm (Early blight) | PlantDoc (In-the-wild) - Labeled as 'Tomato Early blight leaf' |
| **`complex_leaf_071.jpg`** | `Tomato___Early_blight` | [Ảnh thực địa] Cà chua - Bệnh úa sớm (Early blight) | PlantDoc (In-the-wild) - Labeled as 'Tomato Early blight leaf' |
| **`complex_leaf_072.jpg`** | `Tomato___Early_blight` | [Ảnh thực địa] Cà chua - Bệnh úa sớm (Early blight) | PlantDoc (In-the-wild) - Labeled as 'Tomato Early blight leaf' |
| **`complex_leaf_073.jpg`** | `Tomato___healthy` | [Ảnh thực địa] Cà chua - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf' |
| **`complex_leaf_074.jpg`** | `Tomato___healthy` | [Ảnh thực địa] Cà chua - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf' |
| **`complex_leaf_075.jpg`** | `Tomato___healthy` | [Ảnh thực địa] Cà chua - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf' |
| **`complex_leaf_076.jpg`** | `Tomato___healthy` | [Ảnh thực địa] Cà chua - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf' |
| **`complex_leaf_077.jpg`** | `Tomato___healthy` | [Ảnh thực địa] Cà chua - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf' |
| **`complex_leaf_078.jpg`** | `Tomato___healthy` | [Ảnh thực địa] Cà chua - Khỏe mạnh | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf' |
| **`complex_leaf_079.jpg`** | `Tomato___Bacterial_spot` | [Ảnh thực địa] Cà chua - Bệnh đốm vi khuẩn | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf bacterial spot' |
| **`complex_leaf_080.jpg`** | `Tomato___Bacterial_spot` | [Ảnh thực địa] Cà chua - Bệnh đốm vi khuẩn | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf bacterial spot' |
| **`complex_leaf_081.jpg`** | `Tomato___Bacterial_spot` | [Ảnh thực địa] Cà chua - Bệnh đốm vi khuẩn | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf bacterial spot' |
| **`complex_leaf_082.jpg`** | `Tomato___Bacterial_spot` | [Ảnh thực địa] Cà chua - Bệnh đốm vi khuẩn | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf bacterial spot' |
| **`complex_leaf_083.jpg`** | `Tomato___Bacterial_spot` | [Ảnh thực địa] Cà chua - Bệnh đốm vi khuẩn | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf bacterial spot' |
| **`complex_leaf_084.jpg`** | `Tomato___Bacterial_spot` | [Ảnh thực địa] Cà chua - Bệnh đốm vi khuẩn | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf bacterial spot' |
| **`complex_leaf_085.jpg`** | `Tomato___Late_blight` | [Ảnh thực địa] Cà chua - Bệnh mốc sương (Late blight) | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf late blight' |
| **`complex_leaf_086.jpg`** | `Tomato___Late_blight` | [Ảnh thực địa] Cà chua - Bệnh mốc sương (Late blight) | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf late blight' |
| **`complex_leaf_087.jpg`** | `Tomato___Late_blight` | [Ảnh thực địa] Cà chua - Bệnh mốc sương (Late blight) | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf late blight' |
| **`complex_leaf_088.jpg`** | `Tomato___Late_blight` | [Ảnh thực địa] Cà chua - Bệnh mốc sương (Late blight) | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf late blight' |
| **`complex_leaf_089.jpg`** | `Tomato___Late_blight` | [Ảnh thực địa] Cà chua - Bệnh mốc sương (Late blight) | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf late blight' |
| **`complex_leaf_090.jpg`** | `Tomato___Late_blight` | [Ảnh thực địa] Cà chua - Bệnh mốc sương (Late blight) | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf late blight' |
| **`complex_leaf_091.jpg`** | `Tomato___Tomato_mosaic_virus` | [Ảnh thực địa] Cà chua - Bệnh virus khảm cà chua | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf mosaic virus' |
| **`complex_leaf_092.jpg`** | `Tomato___Tomato_mosaic_virus` | [Ảnh thực địa] Cà chua - Bệnh virus khảm cà chua | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf mosaic virus' |
| **`complex_leaf_093.jpg`** | `Tomato___Tomato_mosaic_virus` | [Ảnh thực địa] Cà chua - Bệnh virus khảm cà chua | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf mosaic virus' |
| **`complex_leaf_094.jpg`** | `Tomato___Tomato_mosaic_virus` | [Ảnh thực địa] Cà chua - Bệnh virus khảm cà chua | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf mosaic virus' |
| **`complex_leaf_095.jpg`** | `Tomato___Tomato_mosaic_virus` | [Ảnh thực địa] Cà chua - Bệnh virus khảm cà chua | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf mosaic virus' |
| **`complex_leaf_096.jpg`** | `Tomato___Tomato_mosaic_virus` | [Ảnh thực địa] Cà chua - Bệnh virus khảm cà chua | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf mosaic virus' |
| **`complex_leaf_097.jpg`** | `Tomato___Tomato_Yellow_Leaf_Curl_Virus` | [Ảnh thực địa] Cà chua - Bệnh virus xoăn lùn lá vàng | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf yellow virus' |
| **`complex_leaf_098.jpg`** | `Tomato___Tomato_Yellow_Leaf_Curl_Virus` | [Ảnh thực địa] Cà chua - Bệnh virus xoăn lùn lá vàng | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf yellow virus' |
| **`complex_leaf_099.jpg`** | `Tomato___Tomato_Yellow_Leaf_Curl_Virus` | [Ảnh thực địa] Cà chua - Bệnh virus xoăn lùn lá vàng | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf yellow virus' |
| **`complex_leaf_100.jpg`** | `Tomato___Tomato_Yellow_Leaf_Curl_Virus` | [Ảnh thực địa] Cà chua - Bệnh virus xoăn lùn lá vàng | PlantDoc (In-the-wild) - Labeled as 'Tomato leaf yellow virus' |
| **`leaf_001.jpg`** | `Apple___Apple_scab` | Táo - Bệnh ghẻ (Apple scab) | PlantVillage (Lab control) |
| **`leaf_002.jpg`** | `Apple___Apple_scab` | Táo - Bệnh ghẻ (Apple scab) | PlantVillage (Lab control) |
| **`leaf_003.jpg`** | `Apple___Apple_scab` | Táo - Bệnh ghẻ (Apple scab) | PlantVillage (Lab control) |
| **`leaf_004.jpg`** | `Apple___Apple_scab` | Táo - Bệnh ghẻ (Apple scab) | PlantVillage (Lab control) |
| **`leaf_005.jpg`** | `Apple___Apple_scab` | Táo - Bệnh ghẻ (Apple scab) | PlantVillage (Lab control) |
| **`leaf_006.jpg`** | `Apple___Black_rot` | Táo - Bệnh thối đen (Black rot) | PlantVillage (Lab control) |
| **`leaf_007.jpg`** | `Apple___Black_rot` | Táo - Bệnh thối đen (Black rot) | PlantVillage (Lab control) |
| **`leaf_008.jpg`** | `Apple___Black_rot` | Táo - Bệnh thối đen (Black rot) | PlantVillage (Lab control) |
| **`leaf_009.jpg`** | `Apple___Black_rot` | Táo - Bệnh thối đen (Black rot) | PlantVillage (Lab control) |
| **`leaf_010.jpg`** | `Apple___Black_rot` | Táo - Bệnh thối đen (Black rot) | PlantVillage (Lab control) |
| **`leaf_011.jpg`** | `Apple___Cedar_apple_rust` | Táo - Bệnh rỉ sắt táo Cedar | PlantVillage (Lab control) |
| **`leaf_012.jpg`** | `Apple___Cedar_apple_rust` | Táo - Bệnh rỉ sắt táo Cedar | PlantVillage (Lab control) |
| **`leaf_013.jpg`** | `Apple___Cedar_apple_rust` | Táo - Bệnh rỉ sắt táo Cedar | PlantVillage (Lab control) |
| **`leaf_014.jpg`** | `Apple___Cedar_apple_rust` | Táo - Bệnh rỉ sắt táo Cedar | PlantVillage (Lab control) |
| **`leaf_015.jpg`** | `Apple___Cedar_apple_rust` | Táo - Bệnh rỉ sắt táo Cedar | PlantVillage (Lab control) |
| **`leaf_016.jpg`** | `Apple___healthy` | Táo - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_017.jpg`** | `Apple___healthy` | Táo - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_018.jpg`** | `Apple___healthy` | Táo - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_019.jpg`** | `Apple___healthy` | Táo - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_020.jpg`** | `Apple___healthy` | Táo - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_021.jpg`** | `Blueberry___healthy` | Việt quất - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_022.jpg`** | `Blueberry___healthy` | Việt quất - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_023.jpg`** | `Blueberry___healthy` | Việt quất - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_024.jpg`** | `Blueberry___healthy` | Việt quất - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_025.jpg`** | `Blueberry___healthy` | Việt quất - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_026.jpg`** | `Cherry_(including_sour)___Powdery_mildew` | Anh đào - Bệnh phấn trắng | PlantVillage (Lab control) |
| **`leaf_027.jpg`** | `Cherry_(including_sour)___Powdery_mildew` | Anh đào - Bệnh phấn trắng | PlantVillage (Lab control) |
| **`leaf_028.jpg`** | `Cherry_(including_sour)___Powdery_mildew` | Anh đào - Bệnh phấn trắng | PlantVillage (Lab control) |
| **`leaf_029.jpg`** | `Cherry_(including_sour)___Powdery_mildew` | Anh đào - Bệnh phấn trắng | PlantVillage (Lab control) |
| **`leaf_030.jpg`** | `Cherry_(including_sour)___Powdery_mildew` | Anh đào - Bệnh phấn trắng | PlantVillage (Lab control) |
| **`leaf_031.jpg`** | `Cherry_(including_sour)___healthy` | Anh đào - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_032.jpg`** | `Cherry_(including_sour)___healthy` | Anh đào - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_033.jpg`** | `Cherry_(including_sour)___healthy` | Anh đào - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_034.jpg`** | `Cherry_(including_sour)___healthy` | Anh đào - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_035.jpg`** | `Cherry_(including_sour)___healthy` | Anh đào - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_036.jpg`** | `Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot` | Ngô - Bệnh đốm lá xám (Cercospora) | PlantVillage (Lab control) |
| **`leaf_037.jpg`** | `Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot` | Ngô - Bệnh đốm lá xám (Cercospora) | PlantVillage (Lab control) |
| **`leaf_038.jpg`** | `Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot` | Ngô - Bệnh đốm lá xám (Cercospora) | PlantVillage (Lab control) |
| **`leaf_039.jpg`** | `Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot` | Ngô - Bệnh đốm lá xám (Cercospora) | PlantVillage (Lab control) |
| **`leaf_040.jpg`** | `Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot` | Ngô - Bệnh đốm lá xám (Cercospora) | PlantVillage (Lab control) |
| **`leaf_041.jpg`** | `Corn_(maize)___Common_rust_` | Ngô - Bệnh rỉ sắt thông thường | PlantVillage (Lab control) |
| **`leaf_042.jpg`** | `Corn_(maize)___Common_rust_` | Ngô - Bệnh rỉ sắt thông thường | PlantVillage (Lab control) |
| **`leaf_043.jpg`** | `Corn_(maize)___Common_rust_` | Ngô - Bệnh rỉ sắt thông thường | PlantVillage (Lab control) |
| **`leaf_044.jpg`** | `Corn_(maize)___Common_rust_` | Ngô - Bệnh rỉ sắt thông thường | PlantVillage (Lab control) |
| **`leaf_045.jpg`** | `Corn_(maize)___Common_rust_` | Ngô - Bệnh rỉ sắt thông thường | PlantVillage (Lab control) |
| **`leaf_046.jpg`** | `Corn_(maize)___Northern_Leaf_Blight` | Ngô - Bệnh cháy lá muộn (Northern Leaf Blight) | PlantVillage (Lab control) |
| **`leaf_047.jpg`** | `Corn_(maize)___Northern_Leaf_Blight` | Ngô - Bệnh cháy lá muộn (Northern Leaf Blight) | PlantVillage (Lab control) |
| **`leaf_048.jpg`** | `Corn_(maize)___Northern_Leaf_Blight` | Ngô - Bệnh cháy lá muộn (Northern Leaf Blight) | PlantVillage (Lab control) |
| **`leaf_049.jpg`** | `Corn_(maize)___Northern_Leaf_Blight` | Ngô - Bệnh cháy lá muộn (Northern Leaf Blight) | PlantVillage (Lab control) |
| **`leaf_050.jpg`** | `Corn_(maize)___Northern_Leaf_Blight` | Ngô - Bệnh cháy lá muộn (Northern Leaf Blight) | PlantVillage (Lab control) |
| **`leaf_051.jpg`** | `Corn_(maize)___healthy` | Ngô - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_052.jpg`** | `Corn_(maize)___healthy` | Ngô - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_053.jpg`** | `Corn_(maize)___healthy` | Ngô - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_054.jpg`** | `Corn_(maize)___healthy` | Ngô - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_055.jpg`** | `Corn_(maize)___healthy` | Ngô - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_056.jpg`** | `Grape___Black_rot` | Nho - Bệnh thối đen (Black rot) | PlantVillage (Lab control) |
| **`leaf_057.jpg`** | `Grape___Black_rot` | Nho - Bệnh thối đen (Black rot) | PlantVillage (Lab control) |
| **`leaf_058.jpg`** | `Grape___Black_rot` | Nho - Bệnh thối đen (Black rot) | PlantVillage (Lab control) |
| **`leaf_059.jpg`** | `Grape___Black_rot` | Nho - Bệnh thối đen (Black rot) | PlantVillage (Lab control) |
| **`leaf_060.jpg`** | `Grape___Black_rot` | Nho - Bệnh thối đen (Black rot) | PlantVillage (Lab control) |
| **`leaf_061.jpg`** | `Grape___Esca_(Black_Measles)` | Nho - Bệnh Esca (Lốm đốm đen) | PlantVillage (Lab control) |
| **`leaf_062.jpg`** | `Grape___Esca_(Black_Measles)` | Nho - Bệnh Esca (Lốm đốm đen) | PlantVillage (Lab control) |
| **`leaf_063.jpg`** | `Grape___Esca_(Black_Measles)` | Nho - Bệnh Esca (Lốm đốm đen) | PlantVillage (Lab control) |
| **`leaf_064.jpg`** | `Grape___Esca_(Black_Measles)` | Nho - Bệnh Esca (Lốm đốm đen) | PlantVillage (Lab control) |
| **`leaf_065.jpg`** | `Grape___Esca_(Black_Measles)` | Nho - Bệnh Esca (Lốm đốm đen) | PlantVillage (Lab control) |
| **`leaf_066.jpg`** | `Grape___Leaf_blight_(Isariopsis_Leaf_Spot)` | Nho - Bệnh cháy lá (Isariopsis) | PlantVillage (Lab control) |
| **`leaf_067.jpg`** | `Grape___Leaf_blight_(Isariopsis_Leaf_Spot)` | Nho - Bệnh cháy lá (Isariopsis) | PlantVillage (Lab control) |
| **`leaf_068.jpg`** | `Grape___Leaf_blight_(Isariopsis_Leaf_Spot)` | Nho - Bệnh cháy lá (Isariopsis) | PlantVillage (Lab control) |
| **`leaf_069.jpg`** | `Grape___Leaf_blight_(Isariopsis_Leaf_Spot)` | Nho - Bệnh cháy lá (Isariopsis) | PlantVillage (Lab control) |
| **`leaf_070.jpg`** | `Grape___Leaf_blight_(Isariopsis_Leaf_Spot)` | Nho - Bệnh cháy lá (Isariopsis) | PlantVillage (Lab control) |
| **`leaf_071.jpg`** | `Grape___healthy` | Nho - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_072.jpg`** | `Grape___healthy` | Nho - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_073.jpg`** | `Grape___healthy` | Nho - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_074.jpg`** | `Grape___healthy` | Nho - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_075.jpg`** | `Grape___healthy` | Nho - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_076.jpg`** | `Orange___Haunglongbing_(Citrus_greening)` | Cam - Bệnh vàng lá gân xanh (Citrus greening) | PlantVillage (Lab control) |
| **`leaf_077.jpg`** | `Orange___Haunglongbing_(Citrus_greening)` | Cam - Bệnh vàng lá gân xanh (Citrus greening) | PlantVillage (Lab control) |
| **`leaf_078.jpg`** | `Orange___Haunglongbing_(Citrus_greening)` | Cam - Bệnh vàng lá gân xanh (Citrus greening) | PlantVillage (Lab control) |
| **`leaf_079.jpg`** | `Orange___Haunglongbing_(Citrus_greening)` | Cam - Bệnh vàng lá gân xanh (Citrus greening) | PlantVillage (Lab control) |
| **`leaf_080.jpg`** | `Orange___Haunglongbing_(Citrus_greening)` | Cam - Bệnh vàng lá gân xanh (Citrus greening) | PlantVillage (Lab control) |
| **`leaf_081.jpg`** | `Peach___Bacterial_spot` | Đào - Bệnh đốm vi khuẩn | PlantVillage (Lab control) |
| **`leaf_082.jpg`** | `Peach___Bacterial_spot` | Đào - Bệnh đốm vi khuẩn | PlantVillage (Lab control) |
| **`leaf_083.jpg`** | `Peach___Bacterial_spot` | Đào - Bệnh đốm vi khuẩn | PlantVillage (Lab control) |
| **`leaf_084.jpg`** | `Peach___Bacterial_spot` | Đào - Bệnh đốm vi khuẩn | PlantVillage (Lab control) |
| **`leaf_085.jpg`** | `Peach___Bacterial_spot` | Đào - Bệnh đốm vi khuẩn | PlantVillage (Lab control) |
| **`leaf_086.jpg`** | `Peach___healthy` | Đào - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_087.jpg`** | `Peach___healthy` | Đào - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_088.jpg`** | `Peach___healthy` | Đào - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_089.jpg`** | `Peach___healthy` | Đào - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_090.jpg`** | `Peach___healthy` | Đào - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_091.jpg`** | `Pepper,_bell___Bacterial_spot` | Ớt chuông - Bệnh đốm vi khuẩn | PlantVillage (Lab control) |
| **`leaf_092.jpg`** | `Pepper,_bell___Bacterial_spot` | Ớt chuông - Bệnh đốm vi khuẩn | PlantVillage (Lab control) |
| **`leaf_093.jpg`** | `Pepper,_bell___Bacterial_spot` | Ớt chuông - Bệnh đốm vi khuẩn | PlantVillage (Lab control) |
| **`leaf_094.jpg`** | `Pepper,_bell___Bacterial_spot` | Ớt chuông - Bệnh đốm vi khuẩn | PlantVillage (Lab control) |
| **`leaf_095.jpg`** | `Pepper,_bell___Bacterial_spot` | Ớt chuông - Bệnh đốm vi khuẩn | PlantVillage (Lab control) |
| **`leaf_096.jpg`** | `Pepper,_bell___healthy` | Ớt chuông - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_097.jpg`** | `Pepper,_bell___healthy` | Ớt chuông - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_098.jpg`** | `Pepper,_bell___healthy` | Ớt chuông - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_099.jpg`** | `Pepper,_bell___healthy` | Ớt chuông - Khỏe mạnh | PlantVillage (Lab control) |
| **`leaf_100.jpg`** | `Pepper,_bell___healthy` | Ớt chuông - Khỏe mạnh | PlantVillage (Lab control) |

---

## 🚀 Hướng dẫn Chạy Kiểm Thử (How to Test)

1. Mở trình duyệt: **http://localhost:8501**
2. Chọn **"Tải ảnh lên từ thiết bị"** ở cột trái.
3. Tải lên ảnh phòng thí nghiệm `leaf_xxx.jpg` (dễ) hoặc ảnh thực địa `complex_leaf_xxx.jpg` (khó) lên giao diện.
4. Bấm **"Phân Tích Và Chẩn Đoán Ngay"** để xem AI nhận diện bệnh thực địa tốt đến mức nào so với ảnh tiêu chuẩn!
