# Product Image Annotation Tool

_A Python application for automatic annotation of product images for e-commerce, designed for high-volume and batch processing (10,000+ images). Developed independently for real-world business needs._

---

## Overview

This tool automates the process of annotating product images (e.g., handbags) by drawing measurement lines and adding dimension labels directly onto the images.  
Originally developed to optimize image processing for an Amazon shop (Samantha Look), it supports both batch and manual annotation modes via an intuitive desktop GUI.

- **Automatic bag body & handle detection:** Uses pixel ratio analysis for robust identification.
- **GUI for manual adjustments and previewing.**
- **Excel integration for size data and product mapping.**
- **Scalable:** Handles thousands of images efficiently.

---

## Features

- **Automatic Dimension Detection:**  
  The tool analyzes image pixel ratios to distinguish the main bag body from the handle, allowing for precise placement of measurement lines—without manual labeling.
- **Batch Processing:**  
  Select hundreds or thousands of product images to annotate automatically.
- **Manual Editing:**  
  Use the GUI to manually adjust measurement points or labels for individual images if needed.
- **Excel Data Integration:**  
  Import product size data from Excel files to automatically add accurate labels.
- **Customizable Output:**  
  Change colors, font size, line thickness, and export location directly from the GUI.

---

## About this project
This project was independently developed based on real e-commerce workflow challenges.  
It enables automated, large-scale annotation of product images, reducing manual workload and increasing accuracy.

- **Data-driven automation:**  
  Custom algorithm detects the transition between handle and bag body by analyzing the proportion of non-white pixels along horizontal lines—an insight discovered from the image set's consistent product arrangement.
- **End-to-end workflow:**  
  From Excel data input to automatic or manual annotation, all in one application.
- **Scalable for real e-commerce needs:**  
  Designed to process 10,000+ images used for Amazon product listings.

---

## Sample result
![Sample Image](https://github.com/Maniax5198/product-image-annotation-tool/blob/main/020323-17a_size.jpg)
![Sample Image](https://github.com/Maniax5198/product-image-annotation-tool/blob/main/020331-17a_size.jpg)

---
## Technology Stack

- **Python 3.x**
- **OpenCV** (image processing)
- **Tkinter** (GUI)
- **Pandas** (Excel/data integration)
- **Threading** (for smooth GUI operation during batch processing)

---


## Installation

1. **Clone this repository**
    ```bash
    git clone https://github.com/Maniax5198/product-image-annotation-tool.git
    cd product-image-annotation-tool
    ```
2. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```
3. **(Optional) Prepare Excel size data**  
   Prepare your Excel file according to the template (product code in column 2, sizes in columns 3–5).

---

## Usage

### **Batch Mode**
1. Launch the app:
    ```bash
    python main_new.py
    ```
2. In the GUI, go to "Pikee Generator" tab:
   - Select input image files (supports multi-selection)
   - Select output folder
   - Import Excel size file (in Settings tab)
   - Click **Generate dimensions**
   - Progress and errors are shown in the status box

### **Manual Mode**
- Go to "Manually Sizing" tab
- Choose input image and output folder
- Edit measurement points or label positions as needed
- Click **Generate dimensions** or preview/edit individual points

### **Image Extractor**
- Bulk copy product images based on code ranges

### **Settings**
- Customize line/text color, font size, thickness, and Excel integration

---

## Project Background

This project was independently initiated and implemented during my student job at [Pikee GmbH], after identifying a repetitive bottleneck in the image processing workflow for Amazon product listings.  
All algorithm design, code, and optimization were done individually, using both my programming knowledge and modern AI tools (such as ChatGPT) for rapid prototyping and troubleshooting.

---
## Example Workflow

1. The tool automatically detects the boundary between bag handle and body based on horizontal pixel ratio statistics.
2. Measurement lines (height, width, diagonal) and size labels are drawn on the image.
3. Results are exported as new image files ready for Amazon/e-commerce listing.
---

## Contact

**Author:** [Doan Minh Hoang]  
**Email:** [hoanga050998@gmail.com]  
**LinkedIn:** [linkedin.com/in/yourprofile](https://linkedin.com/in/yourprofile)

---
## License

This project is released under the MIT License.  
You are welcome to use, modify, and learn from it.  
For commercial use or custom adaptations, please contact me.
