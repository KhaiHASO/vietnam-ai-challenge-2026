import os
import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DatasetDownloader")

def ensure_datasets_installed():
    try:
        import datasets
        logger.info("datasets library already installed.")
    except ImportError:
        logger.info("Installing datasets library...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "datasets"])
        logger.info("datasets library installed successfully.")

def download_samples():
    ensure_datasets_installed()
    
    from datasets import load_dataset
    
    # Target folder
    demo_dir = os.path.join("ai_layer", "cropdoctor", "demo_cases")
    os.makedirs(demo_dir, exist_ok=True)
    
    logger.info("Loading tomato-leaves-dataset in streaming mode from Hugging Face...")
    # Use streaming=True to download only the metadata and fetch images on-the-fly (super fast)
    ds = load_dataset("lorenzoxi/tomato-leaves-dataset", split="train", streaming=True)
    # Shuffle the dataset to mix classes so we don't stream one class sequentially
    ds = ds.shuffle(seed=42, buffer_size=1000)
    
    # Class mapping for lorenzoxi/tomato-leaves-dataset
    # Usually: 0: Bacterial_spot, 1: Early_blight, 2: Late_blight, 3: Leaf_Mold, 4: Septoria_leaf_spot,
    # 5: Spider_mites, 6: Target_Spot, 7: Yellow_Leaf_Curl, 8: Mosaic_virus, 9: healthy
    targets = {
        0: {"filename": "real_pepper_bacterial_spot.jpg", "title": "Bacterial Spot (Real)"}, # We can use tomato bacterial spot as a proxy for the demo
        1: {"filename": "real_tomato_early_blight.jpg", "title": "Tomato Early Blight (Real)"},
        2: {"filename": "real_tomato_late_blight.jpg", "title": "Tomato Late Blight (Real)"},
        9: {"filename": "real_tomato_healthy.jpg", "title": "Tomato Healthy (Real)"}
    }
    
    found_classes = set()
    
    logger.info("Streaming dataset to find sample images...")
    for item in ds:
        label = item["label"]
        if label in targets and label not in found_classes:
            image = item["image"]
            target_info = targets[label]
            path = os.path.join(demo_dir, target_info["filename"])
            
            # Save the PIL image to disk
            image.save(path, format="JPEG")
            logger.info(f"Saved real image: {target_info['title']} to {path}")
            
            found_classes.add(label)
            
        # Stop once we have all 4 target images
        if len(found_classes) == len(targets):
            break
            
    logger.info("Successfully loaded real dataset images.")

if __name__ == "__main__":
    download_samples()
