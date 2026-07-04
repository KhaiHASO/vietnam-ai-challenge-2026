import os
import shutil
import time
from playwright.sync_api import sync_playwright
from PIL import Image

def take_screenshots_and_make_pdf():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(project_dir, "screenshots")
    
    # 1. Clear old screenshots
    if os.path.exists(output_dir):
        print(f"[Screenshot] Deleting old screenshots from: {output_dir}")
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # 2. Run Playwright
    routes_to_screenshot = [
        ("dashboard", "1_TongQuan.png"),
        ("diagnosis/new", "2_ChanDoanMoi.png"),
        ("diagnosis/history", "3_LichSuChanDoan.png"),
        ("diagnosis/follow-up", "4_CaCanTheoDoi.png"),
        ("farms", "5_VuonCuaToi.png"),
        ("farm-logs", "6_NhatKyMuaVu.png"),
        ("reminders", "7_LichNhacChamSoc.png"),
        ("knowledge/diseases", "8_ThuVienBenhCay.png"),
        ("knowledge/ipm", "9_KhuyenNghiIPM.png"),
        ("cooperative/map", "10_BanDoCaBenh.png"),
        ("expert/review", "11_ChuyenGiaXacNhan.png"),
        ("ai/model-report", "12_ModelPyTorch.png"),
        ("ai/agent-logs", "13_NhatKyAgent.png")
    ]
    
    with sync_playwright() as p:
        print("[Playwright] Launching Chromium browser...")
        browser = p.chromium.launch(headless=True)
        # 1440x900 viewport gives a good view of sidebar + content
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        
        # Step 1: Login
        print("[Playwright] Logging in...")
        page.goto("http://localhost:3000/auth/login")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        page.fill("input[name='email']", "admin@themesbrand.com")
        page.fill("input[name='password']", "123456")
        page.click("button[type='submit']", force=True)
        page.wait_for_load_state("networkidle")
        time.sleep(4)
        
        # Step 2: Visit each page in the new layout
        for route, img_name in routes_to_screenshot:
            url = f"http://localhost:3000/{route}"
            print(f"[Playwright] Visiting page: {url}")
            try:
                page.goto(url)
                page.wait_for_load_state("networkidle")
                time.sleep(3) # Wait for page load/animations
                path = os.path.join(output_dir, img_name)
                page.screenshot(path=path)
                print(f"[Screenshot] Saved: {path}")
            except Exception as e:
                print(f"[Screenshot] Error visiting {url}: {e}")
                
        browser.close()
        print("[Playwright] Finished browser session.")
        
    # 3. Compile PDF using Pillow
    print("[PDF] Compiling new screenshots into PDF document...")
    pil_images = []
    for _, img_name in routes_to_screenshot:
        img_path = os.path.join(output_dir, img_name)
        if os.path.exists(img_path):
            img = Image.open(img_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            pil_images.append(img)
            
    if pil_images:
        pdf_path = os.path.join(output_dir, "Project_Screenshots.pdf")
        pil_images[0].save(pdf_path, save_all=True, append_images=pil_images[1:])
        print(f"[PDF] Compilation complete! Output saved to: {pdf_path}")
    else:
        print("[PDF] Error: No images found to compile.")

if __name__ == "__main__":
    take_screenshots_and_make_pdf()
