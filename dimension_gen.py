import cv2
import numpy as np
import math

COLOUR_1 = (96, 96, 96)
COLOUR_RED = (0, 0, 255)

def compute_tip_length(start, end, desired_tip_px):
    dx, dy = end[0] - start[0], end[1] - start[1]
    arrow_length = math.hypot(dx, dy)
    return 0.0 if arrow_length == 0 else desired_tip_px / arrow_length

def calculate_ratio_white_and_nonwhite(gray, x, y, w, h, axis='vertical'):
    ratios = []
    for i in range((y if axis == 'vertical' else x), (y + h if axis == 'vertical' else x + w)):
        count_white = 0
        count_non_white = 0
        for j in range((x if axis == 'vertical' else y), (x + w if axis == 'vertical' else y + h)):
            pixel = gray[i, j] if axis == 'vertical' else gray[j, i]
            if pixel < 255:
                count_non_white += 1
            else:
                count_white += 1
        ratio = count_non_white / count_white if count_white else float('inf')
        ratios.append(ratio)
    return ratios

def detect_product_and_draw_bounds(image_path, output_path, data_excel,
                                    input_filename,line_color=(96, 96, 96),
                                    text_color=(0, 0, 0), font_scale=1.2, thickness=5):
    
    img = cv2.imread(image_path)
    
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




# Dọc
    start_v = (x + w + 70, y_new)
    #print(f"Dọc_start_x = {x+w+70}")
    #print(f"Dọc_start_y = {y_new}")
    end_v = (x + w + 70, y_bottom_2)
    #print(f"Dọc_end_x = {x+w+70}")
    #print(f"Dọc_end_y = {y_bottom_2}")

    cv2.arrowedLine(img, start_v, end_v, line_color, thickness, tipLength=compute_tip_length(start_v, end_v, 20))
    cv2.arrowedLine(img, end_v, start_v, line_color, thickness, tipLength=compute_tip_length(start_v, end_v, 20))
# Ngang
    start_h = (x_left, y + h + 70)
    #print(f"Ngang_start_x = {x_left}")
    #print(f"Ngang_start_y = {y+h+70}")
    end_h = (x_right, y_bottom_strong + 70)
    #print(f"ngang_end_x = {x_right}")
    #print(f"ngang_end_y = {y_bottom_strong+70}")
    cv2.arrowedLine(img, start_h, end_h, line_color, thickness, tipLength=compute_tip_length(start_h, end_h, 20))
    cv2.arrowedLine(img, end_h, start_h, line_color, thickness, tipLength=compute_tip_length(start_h, end_h, 20))

#Chéo
    start_diag = (x_left - 50, y + h + 70)
    #print(f"chéo_start_x = {x_left-50}")
    #print(f"chéo_start_y = {y+h+70}")
    end_diag = (x - 120, int((y + h) * 0.99))
    #print(f"chéo_end_x = {x-120}")
    #print(f"chéo_end_y = { int((y + h) * 0.99)}")
    cv2.arrowedLine(img, start_diag, end_diag, line_color, thickness, tipLength=compute_tip_length(start_diag, end_diag, 20))
    cv2.arrowedLine(img, end_diag, start_diag, line_color, thickness, tipLength=compute_tip_length(start_diag, end_diag, 20))

    product_code = input_filename[:6]
    text1, text2, text3 = "(choose) cm", "(choose) cm", "(choose) cm"
    if data_excel is not None:
        matched = data_excel[data_excel.iloc[:, 1].astype(str) == product_code]
        if not matched.empty:
            text1, text2, text3 = matched.iloc[0, 2:5].astype(str).tolist()



    cv2.putText(img, text1, (x + w + 80, int(y_new + (y_bottom_2 - y_new) / 2)), cv2.FONT_ITALIC, font_scale, text_color, 2)
    cv2.putText(img, text2, (int(x_left + w / 2), y_bottom_1 + 120), cv2.FONT_ITALIC, font_scale, text_color, 2)
    cv2.putText(img, text3, (int((start_diag[0] + end_diag[0]) / 2 - 110 - 40), int((start_diag[1] + end_diag[1]) / 2 + 10 + 20)), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, 2)

   # print(f"x_text1 = {x + w + 80}")
    #print(f"y_text1 = {int(y_new + (y_bottom_2 - y_new) / 2)}")
    #print(f"-------------")
    #print(f"x_text2 = {int(x_left + w / 2)}")
    #print(f"y_text2 = {y_bottom_1 + 120}")
    #print(f"-------------")
    #print(f"x_text3 = {int((start_diag[0] + end_diag[0]) / 2 - 110)}")
    #Sprint(f"y_text4 = {int((start_diag[1] + end_diag[1]) / 2 + 10)}")
    cv2.imwrite(output_path, img)