# DocRefine-OCR

An end-to-end PDF refinement tool built on legacy `crazyOCR`. Extacts unstructured text from raw scans using OCR, parses data with Python and programmatically populates polished, widget-enabled PDF templates. We use machine learning and image processing to achieve optimal digitisation results!

## Pre-requisites & Foundation
This guide assumes you are on **Windows 10/11**.
Before continuing with this project, you must have Windows Subsystem for Linux (WSL2), Ubuntu, and Anaconda installed. 
👉 **[Please follow the Foundation Setup Guide here](resources/guides/Foundation_Setup.md)** to get your base environment ready.
👉 **[New to programming or Linux? Read our Guide to Code and CLI here](resources/guides/guide_to_code.md)**.

## Setup Guide

### 1. Install System Dependencies (Ubuntu/WSL2)
Open your Ubuntu terminal and update your system, then install the required text-recognition tools:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential pkg-config tesseract-ocr tesseract-ocr-eng tesseract-ocr-osd tesseract-ocr-script-latn poppler-utils
```
Verify Tesseract is successfully installed:
```bash
tesseract --version
tesseract --list-langs
```
*(If `eng` and `osd` appear, you are good to go!)*

### 2. Identify your Hardware (Do you have a dGPU?)
DocRefine-OCR uses PyTorch. PyTorch runs much faster if you have a **Dedicated Graphics Processing Unit (dGPU)** specifically made by **NVIDIA**.

**How to check:**
1. On Windows, press `Ctrl + Shift + Esc` to open Task Manager.
2. Click on the **Performance** tab on the left.
3. Look for **GPU 0** or **GPU 1** at the bottom of the list. 
4. Click on it. If you see **NVIDIA** listed in the top right corner (e.g., NVIDIA GeForce RTX 3060), you have an NVIDIA dGPU! Follow the **A (GPU Setup)** below.
5. If you see Intel, AMD Radeon Graphics, or no GPU, follow the **B (CPU Setup)** below.

### 3. Setup Python Environment

#### Option A: I have an NVIDIA dGPU (GPU Setup)
Create a new contained environment and install packages with CUDA (GPU acceleration) support:
```bash
conda create -n docrefine python=3.10 -y
conda activate docrefine
conda install -y pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
conda install -y -c conda-forge opencv pillow matplotlib numpy pytesseract notebook psutil
```

#### Option B: I don't have an NVIDIA dGPU (CPU Setup)
Create a new contained environment and install standard CPU-only packages:
```bash
conda create -n docrefine python=3.10 -y
conda activate docrefine
conda install -y pytorch torchvision torchaudio cpuonly -c pytorch
conda install -y -c conda-forge opencv pillow matplotlib numpy pytesseract notebook psutil
```

## How to Use
1. For the best results, make sure your scans are high quality (300+ dpi). Single pages work best.
2. Create a folder inside `data/raw_scans/` with the name of your document (e.g., `data/raw_scans/Demonstration_Works`).
3. Rename your images sequentially inside that folder: `Demonstration_Works_1.png`, `Demonstration_Works_2.png`, etc. 
   *(Tip: Use a tool like Bulk Rename Utility on Windows for large batches)*.
4. Activate your environment and launch Jupyter Notebook:
   ```bash
   conda activate docrefine
   jupyter notebook
   ```
5. Navigate to the `resources/crazyOCR-v2.ipynb` notebook in the web browser window that opens.
6. Scroll to the bottom **Cell #11** (Main Execution) and update the `BOOK_NAME` parameter exactly to match your folder name.
7. Click **Restart Kernel and Run All Cells** at the top. The processed output will be saved into `data/output/` when complete!
