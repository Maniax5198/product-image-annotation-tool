import os
import shutil

def filter_image(file_name):
    file_lower = file_name.lower()
    return (
        file_lower.endswith((".jpg","png")) and
        "a" in file_lower and
        "model" not in file_lower and
        "edoute" not in file_lower and
        "_size" not in file_lower
    )

def process_folders(parent_folder, output_folder, update_callback=None,start_code = None, end_code=None):
    copied_files = []

    subfolder = [
        f for f in os.listdir(parent_folder)
        if os.path.isdir(os.path.join(parent_folder, f)) and f.isdigit() and 5 <= len(f) <=6
        and(start_code is None or start_code <= f <= end_code )
    ]

    total = len(subfolder)
    for idx , subfolder in enumerate(subfolder, 1):
        subfolder_path = os.path.join(parent_folder,subfolder)
        shop_folder = [
            sf for sf in os.listdir(subfolder_path)
            if os.path.isdir(os.path.join(subfolder_path,sf)) and "_shops" in sf
        ]

        for shop_folder in shop_folder:
            shop_folder_path = os.path.join(subfolder_path, shop_folder)
            for file in os.listdir(shop_folder_path):
                if filter_image(file) :
                    src_path = os.path.join(shop_folder_path,file)
                    dest_path = os.path.join(output_folder, f"{file}")
                    shutil.copy(src_path,dest_path)
                    copied_files.append(file)
        
        if update_callback:
            update_callback(idx, total)
            
    return copied_files