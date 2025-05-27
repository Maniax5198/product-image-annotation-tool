import os
import cv2
import pandas as pd
import threading

from tkinter import *
from tkinter import ttk, filedialog, messagebox, colorchooser

from dimension_gen import *
from resize_img import shrink_and_pad_image
from getpic import process_folders
from dimension_manu import get_dimension_points, detect_product_and_draw_bounds_manual
from miniphotoshop import manual_overlay_selector, manual_overlay_select_pair, preview_dimension_lines, manual_overlay_select_point


cv2_font_dict = {
    "FONT_HERSHEY_SIMPLEX": cv2.FONT_HERSHEY_SIMPLEX,
    "FONT_HERSHEY_PLAIN": cv2.FONT_HERSHEY_PLAIN,
    "FONT_HERSHEY_DUPLEX": cv2.FONT_HERSHEY_DUPLEX,
    "FONT_HERSHEY_COMPLEX": cv2.FONT_HERSHEY_COMPLEX,
    "FONT_HERSHEY_TRIPLEX": cv2.FONT_HERSHEY_TRIPLEX,
    "FONT_HERSHEY_COMPLEX_SMALL": cv2.FONT_HERSHEY_COMPLEX_SMALL,
    "FONT_HERSHEY_SCRIPT_SIMPLEX": cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
    "FONT_HERSHEY_SCRIPT_COMPLEX": cv2.FONT_HERSHEY_SCRIPT_COMPLEX,
}


# =========================
#    MAIN APP CLASS
# =========================

class PikeeGeneratorApp:
    def __init__(self):
        # Core config
        self.data_excel = None
        self.font_scale = 1.2
        self.line_thickness = 5
        self.line_color = (96, 96, 96)
        self.text_color = (0, 0, 0)
        self.max_files = 200
        self.actual_input_file_paths = []
        self.stop_processing = False 
        

        
        

        # Tk root
        self.window = Tk()
        self.window.title("Pikee Generator")
        self.window.geometry('600x690')
        self.window.resizable(False, False)

        self.cv2_font = StringVar(value="FONT_HERSHEY_SIMPLEX")
        self.source_image_folder = StringVar()

        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True)

        # Tabs
        self.tab1 = Frame(self.notebook)
        self.tab2 = Frame(self.notebook)
        self.tab3 = Frame(self.notebook)
        self.tab_organize = Frame(self.notebook)
        self.tab4 = Frame(self.notebook)
        self.notebook.add(self.tab1, text="Pikee Generator")
        self.notebook.add(self.tab2, text="Manually Sizing")
        self.notebook.add(self.tab3, text="Image Extractor")
        self.notebook.add(self.tab_organize,text="Organize Pictures")
        self.notebook.add(self.tab4, text="Settings")

        # Setup tabs
        self.setup_tab1()
        self.setup_tab2()
        self.setup_tab3()
        self.setup_tab_organize()
        self.setup_tab4()


        
        self.window.mainloop()

    # =========================
    #         TAB 1
    # =========================

    def setup_tab1(self):
        tab = self.tab1

        # Input
        Label(tab, text="Input Paths: ", anchor="w", font=("Arial", 10)).place(x=10, y=30)
        frame1 = Frame(tab, bd=2, relief="groove", bg="white")
        frame1.place(x=10, y=50, width=580, height=120)
        scrollbar2 = Scrollbar(frame1)
        scrollbar2.pack(side=RIGHT, fill=Y)

        self.label_file_paths_input = Text(frame1, wrap="word", yscrollcommand=scrollbar2.set, bg="white", state="disabled")
        self.label_file_paths_input.pack(fill="both", expand=True)
        scrollbar2.config(command=self.label_file_paths_input.yview)

        Button(tab, text="Browse", command=self.browse_file_input).place(x=10, y=180)

        self.num_files_label = Label(tab, text="Selected Files: 0", anchor="w", font=("Arial", 10), fg="black")
        self.num_files_label.place(x=420, y=190)

        # Output
        Label(tab, text="Output Path: ", anchor="w", font=("Arial", 10)).place(x=10, y=210)
        frame2 = Frame(tab, bd=2, relief="groove", bg="white")
        frame2.place(x=10, y=230, width=580, height=20)
        default_output_path = r"C:\Users\hoang\OneDrive\Desktop\PikeeGenerator\result"

        self.label_file_path_output = Label(frame2, anchor="w", bg="white")
        self.label_file_path_output.pack(fill="both", expand=True)

        Button(tab, text="Browse", command=self.browse_directory_output).place(x=10, y=260)

        # Execute
        self.btn_generate_tab1 = Button(tab, text="Generate dimensions", command=self.execute_action_threaded, height=2, width=17)
        self.btn_generate_tab1.place(x=320, y=580)


        #Stop processsing 
        Button(tab, text="Stop Processing", command=self.stop_action,height=2,width=17,fg="red").place(x = 120,y = 580)

        # Status Textbox
        frame_status = Frame(tab, bd=2, relief="groove")
        frame_status.place(x=10, y=390, width=580, height=160)
        scrollbar = Scrollbar(frame_status)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.text_execution_status = Text(frame_status, wrap="word", yscrollcommand=scrollbar.set, bg="white", fg="black", state="disabled")
        self.text_execution_status.pack(fill="both", expand=True)
        scrollbar.config(command=self.text_execution_status.yview)
        self.text_execution_status.tag_config("success", foreground="green")
        self.text_execution_status.tag_config("error", foreground="red")

        # Progress bar
        self.progress_bar = ttk.Progressbar(tab, orient="horizontal", length=580, mode="determinate")
        self.progress_bar.place(x=10, y=340)
        self.progress_label = Label(tab, text="", anchor="center", font=("Arial", 10))
        self.progress_label.place(x=280, y=365)

    def browse_file_input(self):
        file_paths = filedialog.askopenfilenames(title="Select files")
        if file_paths:
            self.label_file_paths_input.config(state="normal")
            self.label_file_paths_input.delete(1.0, END)
            filenames_only = "\n".join(os.path.basename(path) for path in file_paths)
            self.label_file_paths_input.insert(END, filenames_only)
            self.label_file_paths_input.config(state="disabled")
            self.num_files_label.config(text=f"Selected Files: {len(file_paths)}")
            self.actual_input_file_paths = list(file_paths)

    def browse_directory_output(self):
        directory_path = filedialog.askdirectory(title="Select folder")
        if directory_path:
            self.label_file_path_output.config(text=f"{directory_path}")

    def update_bar(self, progress, total):
        percentage = ((progress / total) * 100)
        self.progress_bar['value'] = percentage
        self.progress_label.config(text=f"{percentage:.0f}%")
        self.window.update_idletasks()

    def execute_action_threaded(self):
        self.btn_generate_tab1.config(state=DISABLED)
        threading.Thread(target=self.execute_action).start()

    def execute_action(self):
        selected_font = cv2_font_dict.get(self.cv2_font.get(), cv2.FONT_HERSHEY_SIMPLEX)

        try:
            file_paths_text = self.label_file_paths_input.get(1.0, END).strip()
            output_directory = self.label_file_path_output.cget("text")
            self.progress_label.config(text="0%")
            self.progress_bar['value'] = 0
            if file_paths_text and output_directory:
                self.label_file_paths_input.config(state="disabled")
                self.text_execution_status.config(state="normal")
                self.text_execution_status.delete(1.0, END)
                file_paths = self.actual_input_file_paths
                errors, successes = [], []
                total_files = len(file_paths)
                if (total_files > self.max_files):
                    errors.append(f"Amount of chosen Files should not exceed {self.max_files} !")
                    self.text_execution_status.insert(END, "ERRORS:\n" + "\n".join(errors) + "\n", "error")
                    self.text_execution_status.config(state="disabled")
                    return  # Không cần enable ở đây, sẽ enable ở finally
                self.stop_processing = False
                for i, file_path in enumerate(file_paths, 1):
                    if self.stop_processing:
                        self.text_execution_status.insert(END,f"Stopped by user at file {i}\n", "error")
                        break
                    input_filename = os.path.basename(file_path)
                    temp_path = os.path.join(output_directory, f"temp_{input_filename}")
                    output_filename = os.path.splitext(input_filename)[0] + "_size.jpg"
                    output_path = os.path.join(output_directory, output_filename)
                    try:
                        shrink_and_pad_image(file_path, temp_path, shrink_percent=30)
                        detect_product_and_draw_bounds(temp_path, output_path, self.data_excel, input_filename,
                                                       self.line_color, self.text_color,
                                                       font_scale=float(self.font_scale_entry.get()),
                                                       thickness=int(self.line_thickness_entry.get()),
                                                       cv2_font=selected_font)
                        os.remove(temp_path)
                        successes.append(f"{output_filename}")
                    except Exception as e:
                        errors.append(f"Error for {input_filename}: {e}")
                    self.update_bar(i, total_files)
                if successes:
                    self.text_execution_status.insert(END, "SUCCESS:\n" + "\n".join(successes) + "\n\n", "success")
                if errors:
                    self.text_execution_status.insert(END, "ERRORS:\n" + "\n".join(errors) + "\n", "error")
                self.text_execution_status.config(state="disabled")
            else:
                self.text_execution_status.config(state="normal")
                self.text_execution_status.delete(1.0, END)
                self.text_execution_status.insert(END, "Select input files and output folder!\n", "error")
                self.text_execution_status.config(state="disabled")
        finally:
            self.btn_generate_tab1.config(state=NORMAL)

    
    def stop_action(self):
        self.stop_processing = True




    # =========================
    #         TAB 2
    # =========================

    def setup_tab2(self):
        tab = self.tab2
        self.input_path_tab2 = StringVar()
        self.output_path_tab2 = StringVar()
        self.status_label_tab2 = Label(tab, text="", fg="green", font=("Arial", 10))
        self.status_label_tab2.place(x=10, y=570)

        # Frame nhập mã sản phẩm
        frame_code = Frame(tab, bd=2, relief="groove")
        frame_code.place(x=10, y=10, width=580, height=40)
        Label(frame_code, text="Product Code to Edit: ", font=("Arial", 10)).place(x=10, y=8)
        self.code_tab2 = StringVar()
        Entry(frame_code, textvariable=self.code_tab2, width=25).place(x=170, y=10)
        Button(frame_code, text="Load Image", command=self.load_image_by_code_tab2).place(x=420, y=8)

        base_y = 60  # Tăng mọi thành phần phía dưới lên 50px so với cũ

        # Input
        Label(tab, text="Input Image: ").place(x=10, y=base_y)
        self.frame_tab2_input = Label(tab, text="", bg="white", bd=2, relief="groove")
        self.frame_tab2_input.place(x=100, y=base_y, width=490, height=20)
        Button(tab, text="Browse", command=self.browse_file_tab2).place(x=10, y=base_y+25)
        self.num_files_label_2 = Label(tab, text="Selected Files: 0")
        self.num_files_label_2.place(x=400, y=base_y+30)

        # Output
        Label(tab, text="Output Folder: ").place(x=10, y=base_y+60)
        self.frame_tab2_output = Label(tab, text="", bg="white", bd=2, relief="groove")
        self.frame_tab2_output.place(x=100, y=base_y+60, width=490, height=20)
        Button(tab, text="Browse", command=self.browse_output_tab2).place(x=10, y=base_y+85)

        # Manual Dimensions
        Label(tab, text="Manual Dimensions (x, y)", font=("Arial", 10, "bold")).place(x=10, y=base_y+120)
        self.entry_fields = {}
        labels = ["Height", "Width", "Depth"]
        for i, label in enumerate(labels):
            y_offset = base_y+150 + i * 40
            Label(tab, text=f"{label} Start:").place(x=10, y=y_offset)
            self.entry_fields[label] = {}
            self.entry_fields[label]['start_x'] = Entry(tab, width=6)
            self.entry_fields[label]['start_x'].place(x=110, y=y_offset)
            self.entry_fields[label]['start_y'] = Entry(tab, width=6)
            self.entry_fields[label]['start_y'].place(x=160, y=y_offset)
            Label(tab, text=f"{label} End:").place(x=240, y=y_offset)
            self.entry_fields[label]['end_x'] = Entry(tab, width=6)
            self.entry_fields[label]['end_x'].place(x=310, y=y_offset)
            self.entry_fields[label]['end_y'] = Entry(tab, width=6)
            self.entry_fields[label]['end_y'].place(x=360, y=y_offset)
            # Nút Edit
            Button(tab, text=f"Edit {label}", command=lambda l=label: self.update_points(l), width=10).place(x=430, y=y_offset-2)
        
        
        self.entry_height_x = self.entry_fields['Height']['start_x']
        self.entry_height_y = self.entry_fields['Height']['start_y']
        self.exit_height_x = self.entry_fields['Height']['end_x']
        self.exit_height_y = self.entry_fields['Height']['end_y']
        
        self.entry_width_x = self.entry_fields['Width']['start_x']
        self.entry_width_y = self.entry_fields['Width']['start_y']
        self.exit_width_x = self.entry_fields['Width']['end_x']
        self.exit_width_y = self.entry_fields['Width']['end_y']
        
        self.entry_depth_x = self.entry_fields['Depth']['start_x']
        self.entry_depth_y = self.entry_fields['Depth']['start_y']
        self.exit_depth_x = self.entry_fields['Depth']['end_x']
        self.exit_depth_y = self.entry_fields['Depth']['end_y']
        # Text Position & Size of Product
        move_down = 0
        Label(tab, text="Text Position (x, y)", font=("Arial", 10, "bold")).place(x=10, y=base_y+270 + move_down)
        Label(tab, text="Height:").place(x=10, y=base_y+300 + move_down)
        self.text1_x = Entry(tab, width=6)
        self.text1_x.place(x=110, y=base_y+300 + move_down)
        self.text1_y = Entry(tab, width=6)
        self.text1_y.place(x=160, y=base_y+300 + move_down)
        Button(tab, text="Edit", command=lambda: self.update_text_point("Height"), width=9).place(x=215, y=base_y+299 + move_down)
        Label(tab, text="Width:").place(x=10, y=base_y+330 + move_down)
        self.text2_x = Entry(tab, width=6)
        self.text2_x.place(x=110, y=base_y+330 + move_down)
        self.text2_y = Entry(tab, width=6)
        self.text2_y.place(x=160, y=base_y+330 + move_down)
        Button(tab, text="Edit", command=lambda: self.update_text_point("Width"), width=9).place(x=215, y=base_y+329 + move_down)
        Label(tab, text="Depth:").place(x=10, y=base_y+360 + move_down)
        self.text3_x = Entry(tab, width=6)
        self.text3_x.place(x=110, y=base_y+360 + move_down)
        self.text3_y = Entry(tab, width=6)
        self.text3_y.place(x=160, y=base_y+360 + move_down)
        Button(tab, text="Edit", command=lambda: self.update_text_point("Depth"), width=9).place(x=215, y=base_y+359 + move_down)

        Label(tab, text="Size of Product :", font=("Arial", 10, "bold")).place(x=305, y=base_y+270 + move_down)
        self.number_text1 = Entry(tab, width=15)
        self.number_text1.place(x=310, y=base_y+300 + move_down)
        self.number_text2 = Entry(tab, width=15)
        self.number_text2.place(x=310, y=base_y+330 + move_down)
        self.number_text3 = Entry(tab, width=15)
        self.number_text3.place(x=310, y=base_y+360 + move_down)

        Button(tab, text=" Preview ", command=self.select_points_gui_tab2, width=12, height=6).place(x=430, y=base_y+290)
        Button(tab, text="Generate dimensions", command=self.execute_manual_dimensions, height=2).place(x=220, y=base_y+420)
        
        #apply tick
        self.apply_for_all_color_tab2 = IntVar()
        Checkbutton(tab, text="Apply for all color", variable=self.apply_for_all_color_tab2).place(x=360  , y=base_y + 428)


        frame_note = Frame(tab, bd=2, relief="groove", bg="#fffbe7")
        frame_note.place(x=10, y=610, width=580, height=38)
        Label(
            frame_note,
            text="Note : Insert Excel Tabel and Folder of origin Products in TAB Settings before editing",
            fg="black", bg="#fffbe7", font=("Arial", 10, "bold")
        ).place(x=10, y=7)


    def browse_file_tab2(self):
        file_path = filedialog.askopenfilename(title="Select image file")
        if file_path:
            self.load_image_data_tab2(file_path)


    def browse_output_tab2(self):
        path = filedialog.askdirectory(title="Select output folder")
        if path:
            self.output_path_tab2.set(path)
            self.frame_tab2_output.config(text=path)

    def execute_manual_dimensions(self):
        try:
            input_file = self.input_path_tab2.get()
            output_dir = self.output_path_tab2.get()
            if not input_file or not output_dir:
                messagebox.showerror("Error", "Missing input or output path.")
                return

            # Lấy các toạ độ điểm và text như bình thường
            selected_points = []
            if self.entry_height_x.get() and self.exit_height_x.get():
                selected_points.append((int(self.entry_height_x.get()), int(self.entry_height_y.get())))
                selected_points.append((int(self.exit_height_x.get()), int(self.exit_height_y.get())))
            if self.entry_width_x.get() and self.exit_width_x.get():
                selected_points.append((int(self.entry_width_x.get()), int(self.entry_width_y.get())))
                selected_points.append((int(self.exit_width_x.get()), int(self.exit_width_y.get())))
            if self.entry_depth_x.get() and self.exit_depth_x.get():
                selected_points.append((int(self.entry_depth_x.get()), int(self.entry_depth_y.get())))
                selected_points.append((int(self.exit_depth_x.get()), int(self.exit_depth_y.get())))
            text_positions = []
            if self.text1_x.get() and self.text1_y.get():
                text_positions.append((int(self.text1_x.get()), int(self.text1_y.get())))
            if self.text2_x.get() and self.text2_y.get():
                text_positions.append((int(self.text2_x.get()), int(self.text2_y.get())))
            if self.text3_x.get() and self.text3_y.get():
                text_positions.append((int(self.text3_x.get()), int(self.text3_y.get())))
            text1 = self.number_text1.get().strip() or "(choose) cm"
            text2 = self.number_text2.get().strip() or "(choose) cm"
            text3 = self.number_text3.get().strip() or "(choose) cm"

            
            selected_font = cv2_font_dict.get(self.cv2_font.get(), cv2.FONT_HERSHEY_SIMPLEX)


            # Nếu chọn "Apply for all color"
            if hasattr(self, "apply_for_all_color_tab2") and self.apply_for_all_color_tab2.get():
                product_code = os.path.basename(input_file)[:6]
                # Đảm bảo đã chọn thư mục gốc ảnh ở Tab 4
                folder_origin = self.source_image_folder.get() if hasattr(self, "source_image_folder") else ""
                if not folder_origin or not os.path.isdir(folder_origin):
                    messagebox.showerror("Error", "Please select the source image folder in Tab 4 first!")
                    return
                files_to_process = [
                    os.path.join(folder_origin, f) for f in os.listdir(folder_origin)
                    if f.startswith(product_code) and f.lower().endswith(('.jpg', '.jpeg', '.png'))
                ]
                if not files_to_process:
                    messagebox.showerror("Error", f"No images found for {product_code} in {folder_origin}")
                    return
            else:
                files_to_process = [input_file]

            count = 0
            for img_path in files_to_process:
                filename = os.path.basename(img_path)
                temp_path = os.path.join(output_dir, f"temp_{filename}")
                output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + "_size.jpg")
                shrink_and_pad_image(img_path, temp_path, shrink_percent=30)
                detect_product_and_draw_bounds_manual(
                    temp_path,
                    output_path,
                    filename,
                    self.data_excel,
                    selected_points,
                    text_positions=text_positions,
                    line_color=self.line_color, text_color=self.text_color,
                    text1=text1, text2=text2, text3=text3,
                    font_scale=float(self.font_scale_entry.get()),
                    thickness=int(self.line_thickness_entry.get()),
                    cv2_font=selected_font 

                )
                os.remove(temp_path)
                count += 1

            self.status_label_tab2.config(text=f"Done ({count} images)", fg="green")
        except Exception as e:
            self.status_label_tab2.config(text=f"Error: {e}", fg="red")

    def select_points_gui_tab2(self):
        try:
            image_path = self.input_path_tab2.get()
            if not image_path:
                messagebox.showerror("Error", "Select Input Image")
                return
            existing_points = []
            def fetch_pair(x1, y1, x2, y2):
                if x1.get() and y1.get() and x2.get() and y2.get():
                    return [(int(x1.get()), int(y1.get())), (int(x2.get()), int(y2.get()))]
                return []
            existing_points += fetch_pair(self.entry_height_x, self.entry_height_y, self.exit_height_x, self.exit_height_y)
            existing_points += fetch_pair(self.entry_width_x, self.entry_width_y, self.exit_width_x, self.exit_width_y)
            existing_points += fetch_pair(self.entry_depth_x, self.entry_depth_y, self.exit_depth_x, self.exit_depth_y)

            # Lấy điểm text positions (nếu có)
            text_points = []
            if self.text1_x.get() and self.text1_y.get():
                text_points.append((int(self.text1_x.get()), int(self.text1_y.get())))
            else:
                text_points.append(None)
            if self.text2_x.get() and self.text2_y.get():
                text_points.append((int(self.text2_x.get()), int(self.text2_y.get())))
            else:
                text_points.append(None)
            if self.text3_x.get() and self.text3_y.get():
                text_points.append((int(self.text3_x.get()), int(self.text3_y.get())))
            else:
                text_points.append(None)

            selected_points = manual_overlay_selector(image_path, existing_points=existing_points, text_points=text_points)
            # Cập nhật lại entry như cũ
            if len(selected_points) >= 2:
                self.entry_height_x.delete(0, END)
                self.entry_height_x.insert(0, selected_points[0][0])
                self.entry_height_y.delete(0, END)
                self.entry_height_y.insert(0, selected_points[0][1])
                self.exit_height_x.delete(0, END)
                self.exit_height_x.insert(0, selected_points[1][0])
                self.exit_height_y.delete(0, END)
                self.exit_height_y.insert(0, selected_points[1][1])
            if len(selected_points) >= 4:
                self.entry_width_x.delete(0, END)
                self.entry_width_x.insert(0, selected_points[2][0])
                self.entry_width_y.delete(0, END)
                self.entry_width_y.insert(0, selected_points[2][1])
                self.exit_width_x.delete(0, END)
                self.exit_width_x.insert(0, selected_points[3][0])
                self.exit_width_y.delete(0, END)
                self.exit_width_y.insert(0, selected_points[3][1])
            if len(selected_points) >= 6:
                self.entry_depth_x.delete(0, END)
                self.entry_depth_x.insert(0, selected_points[4][0])
                self.entry_depth_y.delete(0, END)
                self.entry_depth_y.insert(0, selected_points[4][1])
                self.exit_depth_x.delete(0, END)
                self.exit_depth_x.insert(0, selected_points[5][0])
                self.exit_depth_y.delete(0, END)
                self.exit_depth_y.insert(0, selected_points[5][1])
            self.status_label_tab2.config(text=f"Selected {len(selected_points)} Points", fg="green")
        except Exception as e:
            self.status_label_tab2.config(text=f"Error: {e}", fg="red")


    def update_points(self, kind):
        entry_dict = {
            "Height": (self.entry_height_x, self.entry_height_y, self.exit_height_x, self.exit_height_y),
            "Width": (self.entry_width_x, self.entry_width_y, self.exit_width_x, self.exit_width_y),
            "Depth": (self.entry_depth_x, self.entry_depth_y, self.exit_depth_x, self.exit_depth_y)
        }
        path = self.input_path_tab2.get()
        if not path:
            messagebox.showerror("Error", "Select Input Image")
            return
        try:
            existing = None
            x1, y1, x2, y2 = entry_dict[kind]
            if x1.get() and x2.get():
                existing = [(int(x1.get()), int(y1.get())), (int(x2.get()), int(y2.get()))]

            # Lấy tất cả các lines Height, Width, Depth (có thể có hoặc None)
            all_lines = self.get_all_lines()
            # Loại line hiện tại đang edit để tránh trùng (OPTIONAL, hoặc cứ truyền cả 3 cũng được)
            # Dùng hết cả 3 line (để overlay tự nhận diện)
            background_lines = [line for line in all_lines if line is not None]

            pts = manual_overlay_select_pair(
                path,
                f"{kind} ",
                existing_pair=existing,
                background_lines=background_lines  # truyền vào overlay để hiện đủ 3 đường
            )
            if len(pts) == 2:
                x1.delete(0, END)
                y1.delete(0, END)
                x2.delete(0, END)
                y2.delete(0, END)
                x1.insert(0, pts[0][0])
                y1.insert(0, pts[0][1])
                x2.insert(0, pts[1][0])
                y2.insert(0, pts[1][1])
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def update_text_point(self, kind):
        path = self.input_path_tab2.get()
        if not path:
            messagebox.showerror("Error", "Select input image")
            return
        entry_xy = {
            "Height": (self.text1_x, self.text1_y, self.entry_height_x, self.entry_height_y, self.exit_height_x, self.exit_height_y),
            "Width": (self.text2_x, self.text2_y, self.entry_width_x, self.entry_width_y, self.exit_width_x, self.exit_width_y),
            "Depth": (self.text3_x, self.text3_y, self.entry_depth_x, self.entry_depth_y, self.exit_depth_x, self.exit_depth_y)
        }
        txt_x, txt_y, l_x1, l_y1, l_x2, l_y2 = entry_xy[kind]
        try:
            existing = (int(txt_x.get()), int(txt_y.get())) if txt_x.get() and txt_y.get() else None
            if l_x1.get() and l_x2.get():
                line_pts = [(int(l_x1.get()), int(l_y1.get())), (int(l_x2.get()), int(l_y2.get()))]
            else:
                line_pts = None
            pt = manual_overlay_select_point(path, f"Select Text {kind}", existing_point=existing, line_points=[line_pts] if line_pts else None)
            if pt:
                txt_x.delete(0, END); txt_x.insert(0, pt[0])
                txt_y.delete(0, END); txt_y.insert(0, pt[1])
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def get_all_lines(self):
        lines = []
        # Height
        if self.entry_height_x.get() and self.exit_height_x.get():
            lines.append([
                (int(self.entry_height_x.get()), int(self.entry_height_y.get())),
                (int(self.exit_height_x.get()), int(self.exit_height_y.get()))
            ])
        else:
            lines.append(None)
        # Width
        if self.entry_width_x.get() and self.exit_width_x.get():
            lines.append([
                (int(self.entry_width_x.get()), int(self.entry_width_y.get())),
                (int(self.exit_width_x.get()), int(self.exit_width_y.get()))
            ])
        else:
            lines.append(None)
        # Depth
        if self.entry_depth_x.get() and self.exit_depth_x.get():
            lines.append([
                (int(self.entry_depth_x.get()), int(self.entry_depth_y.get())),
                (int(self.exit_depth_x.get()), int(self.exit_depth_y.get()))
            ])
        else:
            lines.append(None)
        return lines

    def load_image_by_code_tab2(self):
        code = self.code_tab2.get().strip()
        folder = self.source_image_folder.get().strip() if hasattr(self, 'source_image_folder') else ""
        if not code or not folder:
            messagebox.showerror("Error", "Please enter product code and select source image folder in Settings (Tab 4)!")
            return
        found_image = None
        for ext in [".jpg", ".png", ".jpeg"]:
            path = os.path.join(folder, f"{code}{ext}")
            if os.path.isfile(path):
                found_image = path
                break
        if found_image:
            self.load_image_data_tab2(found_image)
        else:
            messagebox.showerror("Not found", f"Cannot find image for code: {code} in {folder}")

    def load_image_data_tab2(self, file_path):
        self.input_path_tab2.set(file_path)
        self.frame_tab2_input.config(text=os.path.basename(file_path))
        self.num_files_label_2.config(text="Selected Files: 1")
        try:
            start_v, end_v, start_h, end_h, start_diag, end_diag, text1_pos, text2_pos, text3_pos, temp_path = get_dimension_points(file_path)
            # Height line
            self.entry_height_x.delete(0, END)
            self.entry_height_x.insert(0, start_v[0])
            self.entry_height_y.delete(0, END)
            self.entry_height_y.insert(0, start_v[1])
            self.exit_height_x.delete(0, END)
            self.exit_height_x.insert(0, end_v[0])
            self.exit_height_y.delete(0, END)
            self.exit_height_y.insert(0, end_v[1])
            # Width line
            self.entry_width_x.delete(0, END)
            self.entry_width_x.insert(0, start_h[0])
            self.entry_width_y.delete(0, END)
            self.entry_width_y.insert(0, start_h[1])
            self.exit_width_x.delete(0, END)
            self.exit_width_x.insert(0, end_h[0])
            self.exit_width_y.delete(0, END)
            self.exit_width_y.insert(0, end_h[1])
            # Depth line
            self.entry_depth_x.delete(0, END)
            self.entry_depth_x.insert(0, start_diag[0])
            self.entry_depth_y.delete(0, END)
            self.entry_depth_y.insert(0, start_diag[1])
            self.exit_depth_x.delete(0, END)
            self.exit_depth_x.insert(0, end_diag[0])
            self.exit_depth_y.delete(0, END)
            self.exit_depth_y.insert(0, end_diag[1])
            # Text positions
            if text1_pos:
                self.text1_x.delete(0, END)
                self.text1_x.insert(0, text1_pos[0])
                self.text1_y.delete(0, END)
                self.text1_y.insert(0, text1_pos[1])
            if text2_pos:
                self.text2_x.delete(0, END)
                self.text2_x.insert(0, text2_pos[0])
                self.text2_y.delete(0, END)
                self.text2_y.insert(0, text2_pos[1])
            if text3_pos:
                self.text3_x.delete(0, END)
                self.text3_x.insert(0, text3_pos[0])
                self.text3_y.delete(0, END)
                self.text3_y.insert(0, text3_pos[1])
            # Load sizes from Excel
            if self.data_excel is not None:
                try:
                    product_code = os.path.basename(file_path)[:6]
                    number_text1_val, number_text2_val, number_text3_val = "", "", ""
                    matched = self.data_excel[self.data_excel.iloc[:, 1].astype(str) == product_code]
                    if not matched.empty:
                        number_text1_val, number_text2_val, number_text3_val = matched.iloc[0, 2:5].astype(str).tolist()
                    self.number_text1.delete(0, END)
                    self.number_text1.insert(0, number_text1_val)
                    self.number_text2.delete(0, END)
                    self.number_text2.insert(0, number_text2_val)
                    self.number_text3.delete(0, END)
                    self.number_text3.insert(0, number_text3_val)
                except Exception as e:
                    self.number_text1.delete(0, END)
                    self.number_text2.delete(0, END)
                    self.number_text3.delete(0, END)
            os.remove(temp_path)
        except Exception as e:
            messagebox.showerror("Error", str(e))



    # =========================
    #         TAB 3
    # =========================

    def setup_tab3(self):
        tab = self.tab3

        # Input Folder
        Label(tab, text="Input Folder:").place(x=10, y=20)
        self.input_entry_tab3 = Entry(tab, width=50)
        self.input_entry_tab3.insert(0,"P:\\")
        self.input_entry_tab3.place(x=140, y=20)
        Button(tab, text="Browse", command=self.browse_input_tab3).place(x=470, y=18)

        # Output Folder
        Label(tab, text="Source Image Folder:").place(x=10, y=60)
        self.output_label_tab3 = Label(tab, textvariable=self.source_image_folder, anchor="w", bg="white",relief="groove", width=43)
        self.output_label_tab3.place(x=140, y=60)
        Button(tab, text="Browse", command=self.browse_output_tab3).place(x=470, y=58)

        # Start Product Code
        Label(tab, text="Start Product Code:").place(x=10, y=100)
        self.start_code_entry = Entry(tab, width=10)
        self.start_code_entry.place(x=140, y=100)

        # End Product Code
        Label(tab, text="End Product Code:").place(x=10, y=140)
        self.end_code_entry = Entry(tab, width=10)
        self.end_code_entry.place(x=140, y=140)

        # Start Button
        Button(tab, text="Start", command=self.run_image_extraction_threaded).place(x=250, y=180, width=100, height=30)

        # Progress Bar & Label
        self.progress_bar_tab3 = ttk.Progressbar(tab, length=400, mode="determinate")
        self.progress_bar_tab3.place(x=100, y=230)
        self.progress_label_tab3 = Label(tab, text="")
        self.progress_label_tab3.place(x=510, y=230)

        default_bg = tab.cget("background")
        text_frame = Frame(tab, bd=2, relief="groove", background=default_bg)
        text_frame.place(x=50, y=270, width=500, height=200)

        instruction = (
            "GUIDE : TO EXTRACT PICTURE FROM DATABASE \n\n"
            "1. Input Folder : to select the parent directory containing product code folders.( Here is P:) \n"
            "2. Output Folder : to select the folder where the images will be saved.\n"
            "3. Enter the Start Product Code and End Product Code to filter images by product code (start 000000 to 999999 to extract all).\n\n"
            "Note:\n Selected Images in Input Folder must be located inside a '_shops' folder within each product code folder."
        )

        # Chỉ tạo 1 Text widget và cho vừa trong frame
        text_widget = Text(
            text_frame,
            wrap="word",
            width=60,        # vừa với frame width=500, Arial 10
            height=11,       # đủ với frame height=200
            font=("Arial", 10),
            bg=default_bg,
            bd=0,
            padx=4,
            pady=4
        )
        text_widget.place(x=1, y=1, width=490, height=195)  # phủ kín text_frame
        text_widget.insert("1.0", instruction)
        text_widget.config(state="disabled")


    def browse_input_tab3(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_entry_tab3.delete(0, END)
            self.input_entry_tab3.insert(0, folder)

    def browse_output_tab3(self):
        folder = filedialog.askdirectory()
        if folder:
            self.source_image_folder.set(folder)

    def update_progress_tab3(self, progress, total):
        percent = (progress / total) * 100
        self.progress_bar_tab3["value"] = percent
        self.progress_label_tab3.config(text=f"{percent:.0f}%")
        self.window.update_idletasks()

    def run_image_extraction_threaded(self):
        threading.Thread(target=self.run_image_extraction).start()

    def run_image_extraction(self):
        parent_folder = self.input_entry_tab3.get()
        output_folder = self.source_image_folder.get()

        start_code = self.start_code_entry.get().strip()
        end_code = self.end_code_entry.get().strip()
        if not os.path.isdir(parent_folder) or not os.path.isdir(output_folder):
            messagebox.showerror("Error", "Wrong input path or output path.")
            return
        if not (start_code.isdigit() and end_code.isdigit()):
            messagebox.showerror("Error", "Start and end product codes must be numeric.")
            return
        try:
            copied_files = process_folders(parent_folder, output_folder, self.update_progress_tab3, start_code=start_code, end_code=end_code)
            messagebox.showinfo("SUCCESS", f"{len(copied_files)} files copied.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =========================
    #         TAB ORGANIZE
    # =========================
    def setup_tab_organize(self):
        tab = self.tab_organize
        default_bg = tab.cget("background")

        # Input Images
        Label(tab, text="Input Images: ", anchor="w", font=("Arial", 10)).place(x=10, y=20)
        frame_input = Frame(tab, bd=2, relief="groove", bg="white")
        frame_input.place(x=10, y=40, width=580, height=100)
        scrollbar = Scrollbar(frame_input)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.organize_input_text = Text(frame_input, wrap="word", yscrollcommand=scrollbar.set, bg="white", state="disabled")
        self.organize_input_text.pack(fill="both", expand=True)
        scrollbar.config(command=self.organize_input_text.yview)
        Button(tab, text="Browse", command=self.organize_browse_input).place(x=10, y=150)
        self.organize_num_files = Label(tab, text="Selected Files: 0", font=("Arial", 10))
        self.organize_num_files.place(x=400, y=155)

        # Output Folder
        Label(tab, text="Output Folder: ", anchor="w", font=("Arial", 10)).place(x=10, y=190)
        self.organize_output_path = StringVar()
        self.organize_output_path.set("P:\\")

        frame_output = Frame(tab, bd=2, relief="groove", bg="white")
        frame_output.place(x=10, y=210, width=580, height=20)

        self.organize_output_label = Label(frame_output,  textvariable=self.organize_output_path, anchor="w", bg="white")
        self.organize_output_label.pack(fill="both", expand=True)
        Button(tab, text="Browse", command=self.organize_browse_output).place(x=10, y=240)

        # Checkbox options
        self.organize_var_shops = IntVar(value=1)
        self.organize_var_vangraafde = IntVar()
        Checkbutton(tab, text="To '_shops'", variable=self.organize_var_shops).place(x=30, y=280)
        Checkbutton(tab, text="To 'vangraafde'", variable=self.organize_var_vangraafde).place(x=180, y=280)
        self.organize_var_delete = IntVar()
        Checkbutton(tab, text="Delete pictures after Transfering", variable=self.organize_var_delete).place(x=350, y=280)

        # Start button
        Button(tab, text="Start", command=self.organize_start, width=15, height=2).place(x=230, y=330)

        # Status label
        self.organize_status = Label(tab, text="", font=("Arial", 10), fg="green")
        self.organize_status.place(x=10, y=390)

        default_bg = tab.cget("background")
        text_frame = Frame(tab, bd=2, relief="groove", background=default_bg)
        text_frame.place(x=50, y=430, width=500, height=200)

        instruction = (
            "GUIDE : TO PLACE IMAGES BACK INTO DATABASE \n\n"
            "1. Input Images: pictures has '_size.jpg' \n"
            "2. Output Folder: Folder contains all Products's Folder ( here is P:). \n"
            "3. Tick on Folder that Images should be placed.  \n\n"
            "Note:\n "
            "    - All different color will be placed in same 1 product folder\n"
            
        )

        # Chỉ tạo 1 Text widget và cho vừa trong frame
        text_widget = Text(
            text_frame,
            wrap="word",
            width=60,        # vừa với frame width=500, Arial 10
            height=11,       # đủ với frame height=200
            font=("Arial", 10),
            bg=default_bg,
            bd=0,
            padx=4,
            pady=4
        )
        text_widget.place(x=1, y=1, width=490, height=195)  # phủ kín text_frame
        text_widget.insert("1.0", instruction)
        text_widget.config(state="disabled")
    
    def organize_browse_input(self):
        files = filedialog.askopenfilenames(title="Select picture ", filetypes=[
        ("Image Files", "*.jpg;*.jpeg;*.png;*.bmp;*.gif"),
        ("All Files", "*.*")
    ])
        if files:
            self.organize_input_files = list(files)
            self.organize_input_text.config(state="normal")
            self.organize_input_text.delete(1.0, END)
            filenames_only = "\n".join(os.path.basename(path) for path in files)
            self.organize_input_text.insert(END, filenames_only)
            self.organize_input_text.config(state="disabled")
            self.organize_num_files.config(text=f"Selected Files: {len(files)}")
        else:
            self.organize_input_files = []
            self.organize_num_files.config(text="Selected Files: 0")

    def organize_browse_output(self):
        path = filedialog.askdirectory(title="Select Destination Folder")
        if path:
            self.organize_output_path.set(path)
            self.organize_output_label.config(text=path)

    def organize_start(self):
        try:
            files = getattr(self, "organize_input_files", [])
            out_folder = self.organize_output_path.get()
            add_shops = self.organize_var_shops.get()
            add_vangraafde = self.organize_var_vangraafde.get()
            if not files or not out_folder:
                self.organize_status.config(text="Select Input and Output", fg="red")
                return
            if not (add_shops or add_vangraafde):
                self.organize_status.config(text="Select at least one destination", fg="red")
                return
            import shutil
            success, error = [], []
            for f in files:
                basename = os.path.basename(f)
                #if not basename.endswith("_size.jpg"):
                #    continue
                product_code = basename[:6]  # Chỉ lấy 6 ký tự đầu
                base_folder = os.path.join(out_folder, product_code)
                shops_folder = os.path.join(base_folder, f"{product_code}_shops")
                if add_shops:
                    os.makedirs(shops_folder, exist_ok=True)
                    dest_path = os.path.join(shops_folder, basename)  # Giữ nguyên tên _size.jpg
                    try:
                        shutil.copy(f, dest_path)
                        success.append(dest_path)
                    except Exception as ex:
                        error.append(str(ex))

                if add_vangraafde:
                    vangraafde_folder = os.path.join(shops_folder, "vangraafde")
                    os.makedirs(vangraafde_folder, exist_ok=True)
                    dest_path = os.path.join(vangraafde_folder, basename)
                    try:
                        shutil.copy(f, dest_path)
                        success.append(dest_path)
                    except Exception as ex:
                        error.append(str(ex))

                if self.organize_var_delete.get() and (add_shops or add_vangraafde) and os.path.isfile(f):
                    try:
                        os.remove(f)
                    except Exception as ex:
                        error.append(f"Error {f}: {ex}")

            self.organize_status.config(
                text=f"Organized {len(success)} Pictures. {len(error)} Error.", fg="green" if not error else "orange"
            )
        except Exception as e:
            self.organize_status.config(text=str(e), fg="red")





    # =========================
    #         TAB 4 - Settings
    # =========================

    def setup_tab4(self):
        tab = self.tab4
        default_bg = tab.cget("background")

        #Folder Browse 
        frame_source_img= Frame(tab,bd=2,relief="groove",bg=default_bg)
        frame_source_img.place(x=10,y=370,width=580,height=80)
        Label(frame_source_img,text= "Source Image Folder: ",anchor="w",font=("Arial", 10)).place(x=10, y=10)
        Label(frame_source_img, textvariable=self.source_image_folder, bg="white", bd=2, relief="groove", width=55, anchor="w").place(x=150, y=10)
        Button(frame_source_img, text="Browse", command=self.browse_source_image_folder).place(x=260, y=40)

        
        # Excel
        frame_excel = Frame(tab, bd=2, relief="groove", bg=default_bg)
        frame_excel.place(x=10, y=10, width=580, height=100)
        label_excel_title = Label(frame_excel, text="Excel Path: ", anchor="w", font=("Arial", 10))
        label_excel_title.place(x=10, y=10)
        self.label_excel_path = Label(frame_excel, bd=2, relief="groove", bg="white")
        self.label_excel_path.place(x=10, y=30, width=560, height=20)
        browse_excel_button = Button(frame_excel, text="Browse", command=self.browse_excel_file)
        browse_excel_button.place(x=10, y=60)
        # Color
        frame_colors = Frame(tab, bd=2, relief="groove", bg=default_bg)
        frame_colors.place(x=10, y=120, width=580, height=100)
        Label(frame_colors, text="Line Color:", font=("Arial", 10)).place(x=10, y=10)
        self.label_line_preview = Label(frame_colors, bg="#606060", width=10)
        self.label_line_preview.place(x=100, y=10)
        Label(frame_colors, text="Text Color:", font=("Arial", 10)).place(x=10, y=50)
        self.label_text_preview = Label(frame_colors, bg="#000000", width=10)
        self.label_text_preview.place(x=100, y=50)
        Button(frame_colors, text="Choose", command=self.choose_line_color).place(x=190, y=7)
        Button(frame_colors, text="Choose", command=self.choose_text_color).place(x=190, y=47)
        
        # Font/Line
        frame_font_line = Frame(tab, bd=2, relief="groove", bg=default_bg)
        frame_font_line.place(x=10, y=230, width=580, height=130)
        Label(frame_font_line, text="Font Scale:", font=("Arial", 10)).place(x=10, y=10)
        self.font_scale_entry = Entry(frame_font_line, width=10)
        self.font_scale_entry.insert(0, str(self.font_scale))
        self.font_scale_entry.place(x=110, y=10)
        Label(frame_font_line, text="( Recommend : 1.2 )", font=("Arial", 7, "bold")).place(x=190, y=10)
        Label(frame_font_line, text="Line Thickness:", font=("Arial", 10)).place(x=10, y=50)
        self.line_thickness_entry = Entry(frame_font_line, width=10)
        self.line_thickness_entry.insert(0, str(self.line_thickness))
        self.line_thickness_entry.place(x=110, y=50)
        Label(frame_font_line, text="( Recommend : 5 )", font=("Arial", 7, "bold")).place(x=190, y=50)
        Button(frame_font_line, text="Apply", command=self.update_font_and_thickness, width=6).place(x=260, y=90)

        frame_note = Frame(tab, bd=2, relief="groove", bg="#fffbe7")
        frame_note.place(x=10, y=610, width=580, height=38)
        Label(
            frame_note,
            text="Note : 'Source Image Folder' is where contains all the Original Pictures got extracted ",
            fg="black", bg="#fffbe7", font=("Arial", 10, "bold")
        ).place(x=10, y=7)

        # Font
        Label(frame_font_line, text="CV2 Font:", font=("Arial", 10)).place(x=320, y=10)

        cv2_font_list = [
            "FONT_HERSHEY_SIMPLEX",
            "FONT_HERSHEY_PLAIN",
            "FONT_HERSHEY_DUPLEX",
            "FONT_HERSHEY_COMPLEX",
            "FONT_HERSHEY_TRIPLEX",
            "FONT_HERSHEY_COMPLEX_SMALL",
            "FONT_HERSHEY_SCRIPT_SIMPLEX",
            "FONT_HERSHEY_SCRIPT_COMPLEX"
        ]
        self.cv2_font_menu = ttk.Combobox(
            frame_font_line, textvariable=self.cv2_font, values=cv2_font_list, state="readonly", width=24
        )
        self.cv2_font_menu.place(x=400, y=10)
        self.cv2_font_menu.set(self.cv2_font.get())



    def browse_source_image_folder(self):
        folder = filedialog.askdirectory(title="Select Source Image Folder")
        if folder:
            self.source_image_folder.set(folder)

    def browse_excel_file(self):
        file_path = filedialog.askopenfilename(title="Select Excel file", filetypes=[("Excel Files", "*.xlsx *.xls")])
        if file_path:
            try:
                self.data_excel = pd.read_excel(file_path)
                self.label_excel_path.config(text=f"Loaded: {os.path.basename(file_path)}")
            except Exception as e:
                self.label_excel_path.config(text=f"Error loading Excel: {e}")

    def choose_line_color(self):
        rgb, hex_color = colorchooser.askcolor(title="Choose Line Color")
        if rgb:
            r, g, b = [int(v) for v in rgb]
            self.line_color = (b, g, r)
            self.label_line_preview.config(bg=hex_color)

    def choose_text_color(self):
        rgb, hex_color = colorchooser.askcolor(title="Choose Text Color")
        if rgb:
            r, g, b = [int(v) for v in rgb]
            self.text_color = (b, g, r)
            self.label_text_preview.config(bg=hex_color)

    def update_font_and_thickness(self):
        try:
            self.font_scale = float(self.font_scale_entry.get())
            self.line_thickness = int(self.line_thickness_entry.get())
            messagebox.showinfo("Success", "Font scale,Thickness and Font Style updated.")
        except:
            messagebox.showerror("Error", "Invalid number format!")


if __name__ == "__main__":
    PikeeGeneratorApp()
