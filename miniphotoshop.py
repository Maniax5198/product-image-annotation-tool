import cv2
import os
from resize_img import shrink_and_pad_image
import tempfile

def manual_overlay_selector(image_path, existing_points=None, text_points=None):
    temp_path = os.path.splitext(image_path)[0] + "_temp_for_click.jpg"
    shrink_and_pad_image(image_path, temp_path, shrink_percent=30)

    img_original = cv2.imread(temp_path)
    if img_original is None:
        raise ValueError("Không đọc được ảnh.")

    screen_max_width = 900
    screen_max_height = 800
    scale_w = screen_max_width / img_original.shape[1]
    scale_h = screen_max_height / img_original.shape[0]
    scale = min(scale_w, scale_h, 1.0)
    img_display = cv2.resize(img_original, (int(img_original.shape[1] * scale), int(img_original.shape[0] * scale)))

    points = []
    window_name = "Select : Height, Width, Diagonal"
    instructions = [
        "1.",
        "2.",
        "3.",
        "4.",
        "5.",
        "6."
    ]

    def draw_all():
        preview = img_display.copy()

        # Vẽ line cũ nếu có
        if existing_points:
            color = (10, 213, 1)
            def scaled(pt): return int(pt[0] * scale), int(pt[1] * scale)
            if len(existing_points) >= 2:
                cv2.line(preview, scaled(existing_points[0]), scaled(existing_points[1]), color, 2)
            if len(existing_points) >= 4:
                cv2.line(preview, scaled(existing_points[2]), scaled(existing_points[3]), color, 2)
            if len(existing_points) >= 6:
                cv2.line(preview, scaled(existing_points[4]), scaled(existing_points[5]), color, 2)

        # Vẽ các điểm text (nếu có)
        if text_points:
            text_labels = ['H', 'W', 'D']
            for i, pt in enumerate(text_points):
                if pt:
                    sx, sy = int(pt[0] * scale), int(pt[1] * scale)
                    cv2.circle(preview, (sx, sy), 7, (50, 200, 50), -1)
                    cv2.putText(preview, text_labels[i], (sx + 8, sy - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (50, 200, 50), 2)

        # Vẽ các điểm mới
        for i, pt in enumerate(points):
            sx, sy = int(pt[0] * scale), int(pt[1] * scale)
            cv2.circle(preview, (sx, sy), 5, (0, 0, 255), -1)
            cv2.putText(preview, str(i+1), (sx + 5, sy - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        if len(points) < 6:
            cv2.putText(preview, instructions[len(points)], (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (50, 50, 50), 2)

        return preview

    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(points) < 6:
            original_x = int(x / scale)
            original_y = int(y / scale)
            points.append((original_x, original_y))
            cv2.imshow(window_name, draw_all())

    cv2.imshow(window_name, draw_all())
    cv2.setMouseCallback(window_name, mouse_callback)

    while True:
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break
        key = cv2.waitKey(1) & 0xFF
        if len(points) >= 6 or key in [13, 27]:
            break

    cv2.destroyAllWindows()
    os.remove(temp_path)
    return points


def manual_overlay_select_pair(image_path, instruction_text="Chọn 2 điểm", existing_pair=None, background_lines=None):
    temp_path = os.path.splitext(image_path)[0] + "_temp_for_edit.jpg"
    shrink_and_pad_image(image_path, temp_path, shrink_percent=30)

    img = cv2.imread(temp_path)
    if img is None:
        raise ValueError("Không đọc được ảnh.")

    screen_max_width = 800
    screen_max_height = 800
    scale_w = screen_max_width / img.shape[1]
    scale_h = screen_max_height / img.shape[0]
    scale = min(scale_w, scale_h, 1.0)
    img_display = cv2.resize(img, (int(img.shape[1] * scale), int(img.shape[0] * scale)))

    points = []
    window_name = "Sửa điểm - " + instruction_text

    def draw_all():
        preview = img_display.copy()
        # Vẽ các line nền (height/width/depth)
        if background_lines:
            for line in background_lines:
                if line:
                    p1 = (int(line[0][0] * scale), int(line[0][1] * scale))
                    p2 = (int(line[1][0] * scale), int(line[1][1] * scale))
                    cv2.line(preview, p1, p2, (180,180,180), 2)  # màu nhạt
        # Vẽ line đang chỉnh
        if existing_pair:
            p1 = (int(existing_pair[0][0] * scale), int(existing_pair[0][1] * scale))
            p2 = (int(existing_pair[1][0] * scale), int(existing_pair[1][1] * scale))
            cv2.line(preview, p1, p2, (0, 200, 200), 2)
        for i, pt in enumerate(points):
            px = int(pt[0] * scale)
            py = int(pt[1] * scale)
            cv2.circle(preview, (px, py), 5, (0, 0, 255), -1)
            cv2.putText(preview, str(i+1), (px + 5, py - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        return preview

    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(points) < 2:
            orig_x = int(x / scale)
            orig_y = int(y / scale)
            points.append((orig_x, orig_y))
            cv2.imshow(window_name, draw_all())

    preview_img = draw_all()
    cv2.putText(preview_img, instruction_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (80, 80, 80), 2)
    cv2.imshow(window_name, preview_img)
    cv2.setMouseCallback(window_name, mouse_callback)

    while True:
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break
        key = cv2.waitKey(1) & 0xFF
        if len(points) >= 2 or key in [13, 27]:
            break

    cv2.destroyAllWindows()
    os.remove(temp_path)
    return points


def preview_dimension_lines(image_path, points, text_points=None):
    temp_path = os.path.splitext(image_path)[0] + "_temp_preview.jpg"
    shrink_and_pad_image(image_path, temp_path, shrink_percent=30)

    img = cv2.imread(temp_path)
    if img is None:
        raise ValueError("Không đọc được ảnh preview.")

    screen_max_width = 800
    scale = min(screen_max_width / img.shape[1], 1.0)
    img_display = cv2.resize(img, (int(img.shape[1] * scale), int(img.shape[0] * scale)))

    color = (0, 0, 255)
    thickness = max(1, int(min(img_display.shape[1], img_display.shape[0]) * 0.003))

    def scaled(pt): return int(pt[0] * scale), int(pt[1] * scale)

    # Vẽ các đường đo
    if len(points) >= 2:
        cv2.line(img_display, scaled(points[0]), scaled(points[1]), color, thickness)
    if len(points) >= 4:
        cv2.line(img_display, scaled(points[2]), scaled(points[3]), color, thickness)
    if len(points) >= 6:
        cv2.line(img_display, scaled(points[4]), scaled(points[5]), color, thickness)

    # Vẽ các vị trí text nếu có
    if text_points:
        text_labels = ['H', 'W', 'D']  # hoặc 'Height', 'Width', 'Depth'
        for i, pt in enumerate(text_points):
            if pt:
                sx, sy = scaled(pt)
                cv2.circle(img_display, (sx, sy), 7, (50, 200, 50), -1)
                cv2.putText(img_display, text_labels[i], (sx + 5, sy - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (50, 200, 50), 2)

    cv2.imshow("Preview đường đo", img_display)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    os.remove(temp_path)

def manual_overlay_select_point(image_path, title="Pick Point", existing_point=None,line_points=None):
    import cv2
    import os
    import tempfile
    from resize_img import shrink_and_pad_image

    # Tạo ảnh tạm đã shrink
    temp_fd, temp_path = tempfile.mkstemp(suffix=".jpg")
    os.close(temp_fd)
    shrink_and_pad_image(image_path, temp_path, shrink_percent=30)

    img = cv2.imread(temp_path)
    if img is None:
        raise ValueError("Cannot open image.")

    # Giới hạn kích thước preview
    screen_max_width = 900
    screen_max_height = 800
    scale_w = screen_max_width / img.shape[1]
    scale_h = screen_max_height / img.shape[0]
    scale = min(scale_w, scale_h, 1.0)

    img_display = cv2.resize(img, (int(img.shape[1] * scale), int(img.shape[0] * scale)))
    clone = img_display.copy()
    selected_point = []

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            selected_point.clear()
            original_x = int(x / scale)
            original_y = int(y / scale)
            selected_point.append((original_x, original_y))
            temp = clone.copy()
            cv2.circle(temp, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow(title, temp)
            cv2.waitKey(500)  # Hiển thị 0.5 giây rồi tự động đóng
            cv2.destroyWindow(title)

    if existing_point:
        disp_x = int(existing_point[0] * scale)
        disp_y = int(existing_point[1] * scale)
        cv2.circle(img_display, (disp_x, disp_y), 5, (128, 128, 128), -1)

    if line_points:
        for pt1, pt2 in line_points:
            x1, y1 = int(pt1[0] * scale), int(pt1[1] * scale)
            x2, y2 = int(pt2[0] * scale), int(pt2[1] * scale)
            cv2.line(img_display, (x1, y1), (x2, y2), (10, 213, 1), 2)

    cv2.imshow(title, img_display)
    cv2.setMouseCallback(title, click_event)

    while True:
        if cv2.getWindowProperty(title, cv2.WND_PROP_VISIBLE) < 1:
            break
        key = cv2.waitKey(1) & 0xFF
        if key in [13, 32]:  # Enter or Space
            break
        elif key == 27:
            selected_point = []
            break

    cv2.destroyAllWindows()
    os.remove(temp_path)
    return selected_point[0] if selected_point else None


