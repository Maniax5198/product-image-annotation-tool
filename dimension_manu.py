import cv2
import numpy as np
import math
from dimension_gen import calculate_ratio_white_and_nonwhite  # Reuse from dimension_gen
from resize_img import shrink_and_pad_image
import os

COLOUR_1 = (96, 96, 96)
COLOUR_RED = (0, 0, 255)

def compute_tip_length(start, end, desired_tip_px):
    dx, dy = end[0] - start[0], end[1] - start[1]
    arrow_length = math.hypot(dx, dy)
    return 0.0 if arrow_length == 0 else desired_tip_px / arrow_length

def get_dimension_points(original_image_path):
    temp_path = os.path.splitext(original_image_path)[0] + "_temp.jpg"
    shrink_and_pad_image(original_image_path, temp_path, shrink_percent=30)

    img = cv2.imread(temp_path)
    if img is None:
        raise ValueError("Could not load the image. Please check the path.")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("Product not found, background must be clear!")

    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)

    vertical_ratios = calculate_ratio_white_and_nonwhite(gray, x, y, w, h, axis='vertical')
    vertical_ratios_full = [0] * y + vertical_ratios

    y_new = next((i for i, r in enumerate(vertical_ratios_full) if r > 1), y)
    y_bottom_1 = next((i for i, r in reversed(list(enumerate(vertical_ratios_full))) if r >= 0.9), y + h)
    y_bottom_2 = next((i for i, r in reversed(list(enumerate(vertical_ratios_full))) if r >= 5), y + h)
    y_bottom_strong = next((i for i, r in reversed(list(enumerate(vertical_ratios_full))) if r >= 3), y + h)

    horizontal_ratios = calculate_ratio_white_and_nonwhite(gray, x, y, w, h, axis='horizontal')
    horizontal_ratios_full = [0] * x + horizontal_ratios

    x_left = next((i for i, r in enumerate(horizontal_ratios_full) if r >= 1.2), x)
    x_right = next((i for i, r in reversed(list(enumerate(horizontal_ratios_full))) if r > 0.8), x + w)

    start_v = (x + w + 70, y_new)
    end_v = (x + w + 70, y_bottom_2)
    start_h = (x_left, y + h + 70)
    end_h = (x_right, y_bottom_strong + 70)
    start_diag = (x_left - 50, y + h + 70)
    end_diag = (x - 120, int((y + h) * 0.99))

    #os.remove(temp_path)

    # Tính vị trí gợi ý cho text
    text1_pos = (start_v[0] + 10, int((start_v[1] + end_v[1]) / 2))
    text2_pos = (int((start_h[0] + end_h[0]) / 2), max(start_h[1], end_h[1]) + 10)
    text3_pos = (min(start_diag[0], end_diag[0]) - 50, int((start_diag[1] + end_diag[1]) / 2))

    return start_v, end_v, start_h, end_h, start_diag, end_diag, text1_pos, text2_pos, text3_pos, temp_path

def detect_product_and_draw_bounds_manual(image_path, output_path, input_filename, data_excel,
                                           selected_points,text_positions=None,
                                           line_color=(96,96,96), text_color=(0,0,0),
                                            text1="(choose) cm", text2="(choose) cm",
                                            text3="(choose) cm",
                                            font_scale=1.2, thickness=5):
    
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Không đọc được ảnh.")


    # Vẽ  chiều cao
    if len(selected_points) >= 2:
        start_v = selected_points[0]
        end_v = selected_points[1]
        cv2.arrowedLine(img, start_v, end_v, line_color, thickness, tipLength=compute_tip_length(start_v, end_v, 20))
        cv2.arrowedLine(img, end_v, start_v, line_color, thickness, tipLength=compute_tip_length(start_v, end_v, 20))
    # Vẽ  chiều rộng
    if len(selected_points) >= 4:
        start_h = selected_points[2]
        end_h = selected_points[3]
        cv2.arrowedLine(img, start_h, end_h, line_color, thickness, tipLength=compute_tip_length(start_h, end_h, 20))
        cv2.arrowedLine(img,end_h, start_h, line_color, thickness, tipLength=compute_tip_length(start_h, end_h, 20))

    # Vẽ  chéo
    if len(selected_points) >= 6:
        start_diag = selected_points[4]
        end_diag = selected_points[5]
        cv2.arrowedLine(img, start_diag, end_diag, line_color, thickness, tipLength=compute_tip_length(start_diag, end_diag, 20))
        cv2.arrowedLine(img, end_diag, start_diag, line_color, thickness, tipLength=compute_tip_length(start_diag, end_diag, 20))

    if len(selected_points) >= 2:
        start_v = selected_points[0]
        end_v = selected_points[1]
        mid_y = int((start_v[1] + end_v[1]) / 2)
        text1_pos = (start_v[0] + 10, mid_y)
    else:
        text1_pos = None
    
    
    if len(selected_points) >= 4:
        start_h = selected_points[2]
        end_h = selected_points[3]
        mid_x = int((start_h[0] + end_h[0]) / 2)
        max_y = max(start_h[1], end_h[1])
        text2_pos = (mid_x, max_y + 10)
    else:
        text2_pos = None
    
  
    if len(selected_points) >= 6:
        start_diag = selected_points[4]
        end_diag = selected_points[5]
        text3_pos = (min(start_diag[0], end_diag[0]) - 50, int((start_diag[1] + end_diag[1]) / 2))
    else:
        text3_pos = None
    
   
    if text_positions:
        if len(text_positions) >= 1:
            text1_pos = text_positions[0]
        if len(text_positions) >= 2:
            text2_pos = text_positions[1]
        if len(text_positions) >= 3:
            text3_pos = text_positions[2]
            
    if text_positions and len(text_positions) >= 1:
        cv2.putText(img, text1, text_positions[0], cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, 2)

    if text_positions and len(text_positions) >= 2:
        cv2.putText(img, text2, text_positions[1], cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, 2)

    if text_positions and len(text_positions) >= 3:
        cv2.putText(img, text3, text_positions[2], cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, 2)

    cv2.imwrite(output_path, img)

