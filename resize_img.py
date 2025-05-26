import cv2
import numpy as np

def shrink_and_pad_image(image_path,output_path, shrink_percent=15):
    # Tính tỉ lệ scale
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Cannot open file from : {image_path}")
    
    scale = 1 - shrink_percent / 100.0
    height, width = image.shape[:2]

    # Tính kích thước ảnh sau khi thu nhỏ
    new_width = int(width * scale)
    new_height = int(height * scale)

    # Resize (thu nhỏ) ảnh
    resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

    # Tạo ảnh mới màu trắng với kích thước gốc
    padded_image = np.ones_like(image) * 255  # 255: pixel trắng

    # Tính toán vị trí để dán ảnh đã thu nhỏ vào giữa
    x_offset = (width - new_width) // 2
    y_offset = (height - new_height) // 2

    # Dán ảnh nhỏ vào trung tâm ảnh trắng
    padded_image[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = resized_image

    cv2.imwrite(output_path, padded_image)

