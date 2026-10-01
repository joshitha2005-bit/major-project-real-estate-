import os
import zipfile

zip_files = [
    r"c:\major real estate\backend\datasets\BANGALORE-HOUSE-PRICE-PREDICTION-main.zip",
    r"c:\major real estate\backend\datasets\Houses-dataset-master.zip",
    r"c:\major real estate\backend\datasets\mhpp-master.zip"
]

for zpath in zip_files:
    print(f"\n=================== {os.path.basename(zpath)} ===================")
    if not os.path.exists(zpath):
        print("File does not exist.")
        continue
    try:
        with zipfile.ZipFile(zpath, 'r') as zf:
            infolist = zf.infolist()
            print(f"Total files in zip: {len(infolist)}")
            file_types = {}
            for item in infolist:
                ext = os.path.splitext(item.filename)[1].lower()
                file_types[ext] = file_types.get(ext, 0) + 1
            print(f"File extensions breakdown: {file_types}")
            
            # Print any csv or image filenames
            csvs = [i.filename for i in infolist if i.filename.endswith('.csv')]
            print(f"CSVs: {csvs}")
            images = [i.filename for i in infolist if any(i.filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp'])]
            print(f"Image count: {len(images)}")
            if images[:5]:
                print(f"Sample images: {images[:5]}")
    except Exception as e:
        print(f"Error inspecting zip: {e}")
