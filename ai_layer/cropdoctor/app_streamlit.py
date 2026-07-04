import os
import requests
import json
import logging
from PIL import Image, ImageDraw
import streamlit as st

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CropDoctorUI")

# API URL
API_URL = "http://localhost:8000/api/cropdoctor"

# Set up page configurations
st.set_page_config(
    page_title="CropDoctor AI - Chẩn Đoán Bệnh Cây Trồng",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium CSS injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Gradient */
    .header-container {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 2.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(56, 239, 125, 0.15);
    }
    .header-container h1 {
        color: white !important;
        font-weight: 700;
        margin: 0;
        font-size: 2.5rem;
    }
    .header-container p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
        margin-bottom: 0;
    }
    
    /* Sleek Cards */
    .premium-card {
        background-color: var(--secondary-background-color, #ffffff);
        color: var(--text-color, #212529);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid rgba(128, 128, 128, 0.15);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
        margin-bottom: 1.5rem;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .premium-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.04);
    }
    .premium-card h1, .premium-card h2, .premium-card h3, .premium-card h4, .premium-card p, .premium-card span {
        color: var(--text-color, #212529) !important;
    }
    
    /* Timeline styling */
    .timeline-item {
        border-left: 3px solid #38ef7d;
        padding-left: 1.5rem;
        position: relative;
        margin-bottom: 1.5rem;
    }
    .timeline-item::before {
        content: '';
        width: 12px;
        height: 12px;
        background-color: #11998e;
        border: 2px solid white;
        border-radius: 50%;
        position: absolute;
        left: -8px;
        top: 4px;
    }
    
    /* Confidence Badge styles */
    .badge {
        display: inline-block;
        padding: 0.35em 0.65em;
        font-size: 0.85em;
        font-weight: 600;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 50rem;
        text-transform: uppercase;
    }
    .badge-high {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .badge-medium {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeeba;
    }
    .badge-low {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# Real PlantVillage dataset image resources
REAL_DATASET_IMAGES = {
    "real_tomato_early_blight.jpg": {
        "title": "Cà chua - Bệnh úa sớm (Real Tomato Early Blight)",
        "url": "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Tomato__Early_blight/0012b70f-15de-4d70-b731-5097deab2057___RS_Erly.B%209427.JPG",
        "crop": "tomato"
    },
    "real_tomato_late_blight.jpg": {
        "title": "Cà chua - Bệnh mốc sương (Real Tomato Late Blight)",
        "url": "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Tomato__Late_blight/0003faa9-ad6a-4372-87a5-99b99f128e48___RS_Late.B%204946.JPG",
        "crop": "tomato"
    },
    "real_pepper_bacterial_spot.jpg": {
        "title": "Ớt chuông - Đốm vi khuẩn (Real Pepper Bacterial Spot)",
        "url": "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Pepper%2C_bell___Bacterial_spot/0022d6c7-c6dd-484b-9d4d-db22bf4d6ef1___JR_B.Spot%203106.JPG",
        "crop": "pepper"
    },
    "real_potato_early_blight.jpg": {
        "title": "Khoai tây - Bệnh úa sớm (Real Potato Early Blight)",
        "url": "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Potato___Early_blight/001187b0-85ab-4329-bda0-b9967733f39a___RS_Erly.B%208168.JPG",
        "crop": "potato"
    },
    "real_potato_late_blight.jpg": {
        "title": "Khoai tây - Bệnh mốc sương (Real Potato Late Blight)",
        "url": "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Potato___Late_blight/00695906-a189-4af7-90a1-a7d3c224840f___RS_HL%201943.JPG",
        "crop": "potato"
    },
    "real_tomato_healthy.jpg": {
        "title": "Cà chua - Khỏe mạnh (Real Tomato Healthy)",
        "url": "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/raw/color/Tomato___healthy/00bce074-961b-4dd8-bc23-a6b2d28f33f4___RS_HL%206173.JPG",
        "crop": "tomato"
    }
}

# Helper function to generate mockup images for demo cases
def generate_demo_images():
    demo_dir = os.path.join("ai_layer", "cropdoctor", "demo_cases")
    os.makedirs(demo_dir, exist_ok=True)
    
    cases = {
        "tomato_early_blight_demo.jpg": {
            "title": "Tomato Early Blight",
            "bg_color": (34, 139, 34), # Forest Green
            "spots": [(150, 150, 20, (139, 69, 19)), (165, 145, 15, (139, 69, 19)), (220, 250, 25, (100, 50, 10))]
        },
        "tomato_late_blight_demo.jpg": {
            "title": "Tomato Late Blight",
            "bg_color": (46, 125, 50), # Darker Green
            "spots": [(100, 120, 45, (60, 40, 20)), (250, 200, 60, (70, 45, 15))]
        },
        "pepper_bacterial_spot_demo.jpg": {
            "title": "Pepper Bacterial Spot",
            "bg_color": (100, 180, 80), # Lighter Green
            "spots": [(110, 100, 5, (0, 0, 0)), (115, 110, 6, (0, 0, 0)), (130, 150, 5, (0, 0, 0)), 
                      (180, 220, 8, (0, 0, 0)), (210, 140, 7, (0, 0, 0)), (240, 190, 6, (0, 0, 0))]
        },
        "healthy_leaf_demo.jpg": {
            "title": "Healthy Leaf",
            "bg_color": (40, 167, 69), # Vibrant Green
            "spots": []
        }
    }
    
    generated_paths = {}
    for filename, details in cases.items():
        path = os.path.join(demo_dir, filename)
        if not os.path.exists(path):
            try:
                # Create a 400x400 image of a stylized leaf
                img = Image.new("RGB", (400, 400), color=(240, 245, 240))
                draw = ImageDraw.Draw(img)
                
                # Draw main leaf shape (ellipse/polygon)
                draw.ellipse([50, 80, 350, 320], fill=details["bg_color"], outline=(30, 90, 30), width=3)
                
                # Draw leaf stem
                draw.line([50, 200, 20, 200], fill=(101, 67, 33), width=8)
                # Draw main leaf vein
                draw.line([50, 200, 350, 200], fill=(130, 210, 130), width=3)
                # Side veins
                draw.line([150, 200, 100, 120], fill=(130, 210, 130), width=2)
                draw.line([150, 200, 100, 280], fill=(130, 210, 130), width=2)
                draw.line([250, 200, 200, 120], fill=(130, 210, 130), width=2)
                draw.line([250, 200, 200, 280], fill=(130, 210, 130), width=2)
                
                # Draw spots representing the disease
                for cx, cy, radius, color in details["spots"]:
                    # Draw central lesion
                    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=color, outline=(0,0,0))
                    # Draw a yellow halo if it's early blight
                    if "early" in filename:
                        draw.ellipse([cx - radius - 5, cy - radius - 5, cx + radius + 5, cy + radius + 5], outline=(230, 230, 0), width=2)
                
                # Overlay demo text badge
                draw.rectangle([10, 10, 390, 45], fill=(255, 255, 255), outline=(200, 200, 200))
                draw.text((20, 18), f"Demo Case: {details['title']}", fill=(50, 50, 50))
                
                img.save(path)
                logger.info(f"Generated demo image at {path}")
            except Exception as e:
                logger.error(f"Error generating demo image {filename}: {e}")
        
        generated_paths[details["title"]] = path
        
    return generated_paths

def load_local_datatest_images():
    datatest_dir = "datatest"
    labels_path = os.path.join(datatest_dir, "labels.json")
    real_paths = {}
    if os.path.exists(labels_path):
        try:
            import json
            with open(labels_path, "r", encoding="utf-8") as f:
                catalog = json.load(f)
            for filename, info in sorted(catalog.items()):
                path = os.path.join(datatest_dir, filename)
                if os.path.exists(path):
                    # Title containing file name and Vietnamese diagnostic label
                    title = f"[{filename}] {info['label_vi']}"
                    real_paths[title] = path
        except Exception as e:
            logger.error(f"Error loading local datatest: {e}")
    return real_paths

# Automatically generate and load demo cases on app startup
demo_paths = generate_demo_images()
real_paths = load_local_datatest_images()

# Merge all demo cases (real ones first)
all_demo_paths = {}
all_demo_paths.update(real_paths)
all_demo_paths.update(demo_paths)


# Render Header
st.markdown("""
<div class="header-container">
    <h1>🌱 CropDoctor AI</h1>
    <p>Hệ thống chẩn đoán bệnh cây trồng thông minh (MVP không Training: Vision Consensus + DeepSeek Agentic Reasoning)</p>
</div>
""", unsafe_allow_html=True)

# Layout columns
col_inputs, col_results = st.columns([1, 2])

with col_inputs:
    with st.container(border=True):
        st.subheader("🔍 Đầu Vào Chẩn Đoán")
        
        symptoms = st.text_area(
            "1. Triệu chứng quan sát thêm (Không bắt buộc)",
            placeholder="Ví dụ: lá có đốm nâu đen đồng tâm xuất hiện trên lá già bên dưới sau đợt mưa dông...",
            help="Lập luận DeepSeek Reasoning Agent sẽ sử dụng thông tin này để kiểm chứng chẩn đoán."
        )
        
        # Choose between uploading an image or choosing a demo case
        input_source = st.radio(
            "2. Chọn nguồn hình ảnh:",
            ["Tải ảnh lên từ thiết bị", "Sử dụng ảnh Demo có sẵn (Khuyên Dùng)"]
        )
        
        image_to_diagnose = None
        demo_selected = None
        
        if input_source == "Tải ảnh lên từ thiết bị":
            uploaded_file = st.file_uploader(
                "Tải lên ảnh lá/quả/thân nghi bị bệnh",
                type=["jpg", "jpeg", "png", "webp"]
            )
            if uploaded_file:
                try:
                    # Open with PIL to verify and display safely
                    img = Image.open(uploaded_file)
                    st.image(img, caption="Ảnh bạn tải lên", use_container_width=True)
                    image_to_diagnose = uploaded_file
                except Exception as e:
                    st.error(f"❌ Không thể nhận diện định dạng ảnh này. Vui lòng tải lên một ảnh hợp lệ (.jpg, .png, .webp). Chi tiết: {e}")
                    image_to_diagnose = None
        else:
            # Load demo cases
            demo_choice = st.selectbox(
                "Chọn một ảnh demo bệnh cây trồng:",
                list(all_demo_paths.keys())
            )
            if demo_choice:
                demo_path = all_demo_paths[demo_choice]
                try:
                    # Load image to display in Streamlit
                    img = Image.open(demo_path)
                    st.image(img, caption=f"Demo: {demo_choice}", use_container_width=True)
                    
                    # We will read this file path during prediction
                    image_to_diagnose = demo_path
                    demo_selected = demo_choice
                except Exception as e:
                    st.error(f"Không thể tải ảnh demo: {e}")
    
    # Diagnostic Trigger Button
    diagnose_btn = st.button("🚀 PHÂN TÍCH VÀ CHẨN ĐOÁN NGAY", use_container_width=True)

with col_results:
    if diagnose_btn and image_to_diagnose:
        with st.spinner("⏳ Đang xử lý... Lớp thị giác đồng thuận (Vision Consensus) kết hợp Lập luận thông minh (DeepSeek Agent)..."):
            
            try:
                # Prepare payload
                data = {
                    "crop_hint": "",
                    "symptoms": symptoms
                }
                
                # Call backend API
                if isinstance(image_to_diagnose, str):
                    # It's a file path of a demo case
                    with open(image_to_diagnose, "rb") as f:
                        files = {"image": (os.path.basename(image_to_diagnose), f.read(), "image/jpeg")}
                        resp = requests.post(f"{API_URL}/diagnose", data=data, files=files, timeout=40)
                else:
                    # It's an uploaded file
                    files = {"image": (image_to_diagnose.name, image_to_diagnose.getvalue(), image_to_diagnose.type)}
                    resp = requests.post(f"{API_URL}/diagnose", data=data, files=files, timeout=40)
                
                if resp.status_code == 200:
                    result = resp.json()
                    st.balloons()
                    
                    # Extract variables
                    vision_res = result.get("vision", {})
                    reasoning_res = result.get("reasoning", {})
                    agent_logs = result.get("agent_logs", [])
                    
                    confidence = vision_res.get("confidence", 0.0)
                    decision_status = vision_res.get("decision_status", "uncertain")
                    disease_vi = vision_res.get("final_disease_vi", "Không xác định")
                    
                    # Create custom layout for results
                    st.markdown("### 📊 KẾT QUẢ CHẨN ĐOÁN AGENTIC")
                    
                    # 1. Show diagnostic status badge & confidence
                    conf_percentage = f"{round(confidence * 100, 1)}%"
                    if decision_status == "confident_preliminary_diagnosis":
                        status_html = f'<span class="badge badge-high">Tự tin sơ bộ ({conf_percentage})</span>'
                    elif decision_status == "need_more_symptoms":
                        status_html = f'<span class="badge badge-medium">Cần xác minh triệu chứng ({conf_percentage})</span>'
                    else:
                        status_html = f'<span class="badge badge-low">Độ tin cậy thấp ({conf_percentage})</span>'
                        
                    st.markdown(f"""
                    <div class="premium-card" style="border-left: 5px solid #11998e;">
                        <h4 style="margin: 0 0 0.5rem 0;">🔬 Nhận diện lớp thị giác: <b>{disease_vi}</b></h4>
                        <p style="margin:0;">Độ tin cậy: {status_html} | Động cơ chính: <code>{vision_res.get('primary_engine')}</code></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 2. Render Tabs
                    tab_diagnosis, tab_logs, tab_config = st.tabs([
                        "📋 Phân Tích & Khuyến Nghị (DeepSeek)", 
                        "🤖 Tiến Trình Agent Logs", 
                        "🧬 Chi Tiết Kỹ Thuật (Consensus)"
                    ])
                    
                    with tab_diagnosis:
                        # DeepSeek Reasoning Content
                        content = reasoning_res.get("content", {})
                        if isinstance(content, str):
                            try:
                                content = json.loads(content)
                            except Exception:
                                pass
                                
                        if isinstance(content, dict):
                            # Beautiful layout for the parsed JSON response
                            st.markdown(f"#### 🏷️ Chẩn đoán sơ bộ: **{content.get('short_diagnosis', disease_vi)}**")
                            
                            # Possibilities
                            st.markdown("##### 🧬 Khả năng xảy ra cao nhất:")
                            for pos in content.get("top_possibilities", []):
                                st.markdown(f"- {pos}")
                                
                            # Why
                            st.markdown("##### 🔍 Cơ sở chẩn đoán (Lập luận):")
                            for reason in content.get("why", []):
                                st.markdown(f"- {reason}")
                                
                            # Questions to confirm
                            st.markdown("##### ❓ Câu hỏi kiểm chứng tại thực địa (Nông dân tự kiểm tra):")
                            for q in content.get("questions_to_confirm", []):
                                st.markdown(f"- **[ ]** {q}")
                                
                            # Safe Recommendations (Split or layout)
                            st.markdown("##### 🛡️ Khuyến nghị Quản lý Dịch hại Tổng hợp (IPM) An Toàn:")
                            for rec in content.get("safe_recommendations", []):
                                if "hóa học" in rec.lower() or "thuốc" in rec.lower():
                                    st.warning(rec)
                                else:
                                    st.success(rec)
                                    
                            # When to call expert
                            st.markdown("##### ⚠️ Khi nào cần liên hệ chuyên gia bảo vệ thực vật:")
                            for exp in content.get("when_to_call_expert", []):
                                st.markdown(f"🚨 {exp}")
                                
                            # Disclaimer
                            st.markdown(f"<small style='color: #6c757d; display: block; margin-top: 1.5rem;'>*Miễn trừ trách nhiệm: {content.get('disclaimer', '')}</small>", unsafe_allow_html=True)
                        else:
                            # If content is a plain string (deepseek outputted raw markdown text)
                            st.markdown("##### 📝 Chi tiết phân tích từ DeepSeek Reasoning Agent:")
                            st.write(content)
                            
                    with tab_logs:
                        st.markdown("#### 🪵 Nhật ký hoạt động của các Tác nhân (Agent Logs)")
                        st.markdown("Quy trình xử lý tuần tự qua các Agent chuyên biệt:")
                        
                        for idx, log in enumerate(agent_logs):
                            agent_name = log.get("agent", "UnknownAgent")
                            status = log.get("status", "pending")
                            details = log.get("details", "")
                            
                            status_badge = "✅ Hoàn thành" if status == "done" else "🛡️ Áp dụng Guardrail" if status == "guardrail_applied" else "❌ Lỗi"
                            color = "#28a745" if status == "done" else "#17a2b8" if status == "guardrail_applied" else "#dc3545"
                            
                            st.markdown(f"""
                            <div class="timeline-item">
                                <strong style="font-size: 1.1rem; color: #11998e;">Bước {idx+1}: {agent_name}</strong><br/>
                                <span style="color: {color}; font-weight: 600; font-size: 0.9rem;">Trạng thái: {status_badge}</span><br/>
                                <span style="color: #6c757d; font-size: 0.9rem;">Chi tiết: {details}</span>
                            </div>
                            """, unsafe_allow_html=True)
                            
                    with tab_config:
                        st.markdown("#### 🧬 Chi tiết Đồng thuận Phân loại (Consensus Details)")
                        
                        col_hf, col_ch = st.columns(2)
                        with col_hf:
                            st.markdown("##### 🟢 Kết quả PyTorch Local Classifier")
                            hf_data = vision_res.get("engines", {}).get("hf_vision", {})
                            st.write(f"Mô hình: `{hf_data.get('model')}`")
                            st.write(f"Fallback đã dùng: `{hf_data.get('fallback_used')}`")
                            st.write("Top 3 dự đoán của mô hình:")
                            for idx, pred in enumerate(hf_data.get("top_predictions", [])):
                                st.write(f"{idx+1}. **{pred.get('label_vi')}** (`{pred.get('label')}`) - **{round(pred.get('score', 0.0)*100, 1)}%**")
                                
                        with col_ch:
                            st.markdown("##### 🔵 Kết quả Expert API (Kindwise / Plant.id)")
                            ch_data = vision_res.get("engines", {}).get("crop_health", {})
                            st.write(f"Moteur: `{ch_data.get('engine')}`")
                            
                            diagnosis = ch_data.get("diagnosis", {})
                            if diagnosis:
                                st.write(f"Bệnh dự đoán: **{diagnosis.get('disease')}**")
                                st.write(f"Độ tin cậy API: **{round(diagnosis.get('confidence', 0.0)*100, 1)}%**")
                                st.write(f"Mức độ nghiêm trọng: `{diagnosis.get('severity')}`")
                            elif ch_data.get("error"):
                                st.warning(f"Lỗi API: {ch_data.get('error')}")
                            else:
                                st.write("Không có thông tin chẩn đoán từ API.")
                                
                else:
                    st.error(f"Lỗi phản hồi từ backend API (Mã lỗi {resp.status_code}): {resp.text}")
                    
            except Exception as e:
                st.error(f"Không thể kết nối đến backend API. Hãy đảm bảo FastAPI đã được khởi chạy trên cổng 8000. Chi tiết: {e}")
                
    elif diagnose_btn:
        st.warning("⚠️ Vui lòng tải ảnh lên hoặc chọn một ảnh demo có sẵn trước khi nhấn nút chẩn đoán.")
    else:
        # Default placeholder visual when no analysis has run
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem; color: var(--text-color); border: 2px dashed rgba(128,128,128,0.2); border-radius: 12px; background-color: var(--secondary-background-color, #fafbfc);">
            <span style="font-size: 4rem;">🌱</span>
            <h3 style="margin-top: 1rem; color: var(--text-color, #495057);">Sẵn sàng Chẩn Đoán</h3>
            <p style="color: var(--text-color, #6c757d);">Chọn ảnh demo hoặc tải ảnh lên ở cột bên trái và nhấn nút "Phân Tích Và Chẩn Đoán Ngay" để xem kết quả hoạt động của các Agent.</p>
        </div>
        """, unsafe_allow_html=True)

# Sidebar Info Panel
st.sidebar.markdown("""
### 🛠️ Trạng Thái Hệ Thống
""")

# Check API health
try:
    health_resp = requests.get(f"{API_URL}/health", timeout=3)
    if health_resp.status_code == 200:
        health_data = health_resp.json()
        st.sidebar.success("● FastAPI Backend: Đang chạy")
        st.sidebar.markdown(f"**Vision Engine:** `{health_data.get('vision_engine')}`")
        st.sidebar.markdown(f"**Reasoning Agent:** `{health_data.get('reasoning_engine')}`")
        st.sidebar.markdown(f"**Fallback Mode:** `{health_data.get('fallback_active')}`")
    else:
        st.sidebar.error("● FastAPI Backend: Phản hồi lỗi")
except Exception:
    st.sidebar.error("● FastAPI Backend: Không hoạt động (Chưa chạy uvicorn)")

st.sidebar.markdown("""
---
### 🧬 Kiến trúc MVP không Training
Hệ thống kết hợp sức mạnh của:
1. **Lớp Thị Giác Đồng Thuận (Vision Consensus):**
   - **Local Model:** Pretrained PyTorch ResNet50 (38 lớp PlantVillage) chạy trên FastAPI.
   - **Expert APIs:** Kết nối Kindwise crop.health & Plant.id.
2. **Lớp Lập Luận Tác Nhân (DeepSeek Reasoning Agent):**
   - Phân tích chéo giữa ảnh và mô tả lâm sàng của nông dân.
   - Trực tiếp đặt câu hỏi thực địa kiểm chứng.
   - Sinh khuyến nghị phòng trừ tổng hợp (IPM) an toàn.
""")
