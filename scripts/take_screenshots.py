import os
import time
from playwright.sync_api import sync_playwright
from PIL import Image

def take_screenshots_and_make_pdf():
    # 1. Setup output directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(project_dir, "screenshots")
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"[Screenshot] Output directory set to: {output_dir}")
    
    # 2. Run Playwright
    with sync_playwright() as p:
        print("[Playwright] Launching Chromium browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        
        # Step 1: Login Page
        print("[Playwright] Navigating to login page...")
        page.goto("http://localhost:3000/auth/login")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        print("[Playwright] Logging in with default admin credentials...")
        page.fill("input[name='email']", "admin@themesbrand.com")
        page.fill("input[name='password']", "123456")
        
        # Click login button
        page.click("button[type='submit']", force=True)
        page.wait_for_load_state("networkidle")
        time.sleep(5) # Allow redirect and page load
        
        # Take Dashboard Screenshot
        dashboard_path = os.path.join(output_dir, "1_Dashboard.png")
        page.screenshot(path=dashboard_path)
        print(f"[Screenshot] Saved: {dashboard_path}")
        
        # Step 2: Navigate to AI Copilot page
        print("[Playwright] Navigating to AI Copilot cockpit...")
        page.goto("http://localhost:3000/ai-copilot")
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        
        # SME Domain Default
        print("[Playwright] Switching to SME Domain...")
        page.locator("button:has-text('SME')").first.click(force=True)
        time.sleep(2)
        sme_default_path = os.path.join(output_dir, "2_SME_Default.png")
        page.screenshot(path=sme_default_path)
        print(f"[Screenshot] Saved: {sme_default_path}")
        
        # SME Interacted (Hủy đặt sân & Hoàn tiền)
        print("[Playwright] Triggering SME interactive scenario...")
        page.locator("button:has-text('Hủy đặt sân & Hoàn tiền')").first.click(force=True)
        time.sleep(1)
        # Click parent button of the feather-send SVG icon
        page.locator("svg.feather-send").first.locator("xpath=..").click(force=True)
        print("[Playwright] Waiting 6 seconds for 9-step trace flow...")
        time.sleep(6)
        sme_interacted_path = os.path.join(output_dir, "3_SME_Interacted.png")
        page.screenshot(path=sme_interacted_path)
        print(f"[Screenshot] Saved: {sme_interacted_path}")
        
        # Education Domain Default
        print("[Playwright] Switching to Education Domain...")
        page.locator("button:has-text('Education')").first.click(force=True)
        time.sleep(2)
        edu_default_path = os.path.join(output_dir, "4_Education_Default.png")
        page.screenshot(path=edu_default_path)
        print(f"[Screenshot] Saved: {edu_default_path}")
        
        # Education Interacted
        print("[Playwright] Triggering Education interactive scenario...")
        page.locator("button:has-text('Phát hiện nguy cơ & Can thiệp')").first.click(force=True)
        time.sleep(1)
        page.locator("svg.feather-send").first.locator("xpath=..").click(force=True)
        print("[Playwright] Waiting 6 seconds for 9-step trace flow...")
        time.sleep(6)
        edu_interacted_path = os.path.join(output_dir, "5_Education_Interacted.png")
        page.screenshot(path=edu_interacted_path)
        print(f"[Screenshot] Saved: {edu_interacted_path}")
        
        # Agriculture Domain Default
        print("[Playwright] Switching to Agriculture Domain...")
        page.locator("button:has-text('Agriculture')").first.click(force=True)
        time.sleep(2)
        agri_default_path = os.path.join(output_dir, "6_Agriculture_Default.png")
        page.screenshot(path=agri_default_path)
        print(f"[Screenshot] Saved: {agri_default_path}")
        
        # Agriculture Interacted
        print("[Playwright] Triggering Agriculture interactive scenario...")
        page.locator("button:has-text('Chẩn đoán bệnh hại & Đơn thuốc')").first.click(force=True)
        time.sleep(1)
        page.locator("svg.feather-send").first.locator("xpath=..").click(force=True)
        print("[Playwright] Waiting 6 seconds for 9-step trace flow...")
        time.sleep(6)
        agri_interacted_path = os.path.join(output_dir, "7_Agriculture_Interacted.png")
        page.screenshot(path=agri_interacted_path)
        print(f"[Screenshot] Saved: {agri_interacted_path}")
        
        browser.close()
        print("[Playwright] Finished browser session.")

    # 3. Compile images into PDF using Pillow
    print("[PDF] Compiling PNG screenshots into a single PDF document...")
    images_list = [
        "1_Dashboard.png",
        "2_SME_Default.png",
        "3_SME_Interacted.png",
        "4_Education_Default.png",
        "5_Education_Interacted.png",
        "6_Agriculture_Default.png",
        "7_Agriculture_Interacted.png"
    ]
    
    pil_images = []
    for img_name in images_list:
        img_path = os.path.join(output_dir, img_name)
        if os.path.exists(img_path):
            img = Image.open(img_path)
            # Convert to RGB mode because PNG can have RGBA, but PDF requires RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
            pil_images.append(img)
            
    if pil_images:
        pdf_path = os.path.join(output_dir, "Project_Screenshots.pdf")
        # Save as PDF
        pil_images[0].save(pdf_path, save_all=True, append_images=pil_images[1:])
        print(f"[PDF] Compilation complete! Output saved to: {pdf_path}")
    else:
        print("[PDF] Error: No images found to compile.")

if __name__ == "__main__":
    take_screenshots_and_make_pdf()
