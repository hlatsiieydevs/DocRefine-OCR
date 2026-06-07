# DocRefine-OCR

An end-to-end PDF refinement, score distribution, and PDF generation tool. Resolves unstructured student workplace practical records, maps registered signatures (with fallback SIFT alignment/crop on raw scans), distributes ELO marks dynamically, and generates formatted landscape/portrait PDFs.

## Pre-requisites & Foundation
This guide assumes you are on **Windows 10/11** with **WSL2 (Ubuntu)**.
Before continuing, you must have WSL2, Ubuntu, Anaconda, and LibreOffice installed.

### 1. Install System Dependencies (Ubuntu/WSL2)
Open your Ubuntu terminal and install the required text-recognition and headless document conversion packages:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential pkg-config tesseract-ocr tesseract-ocr-eng tesseract-ocr-osd tesseract-ocr-script-latn poppler-utils libreoffice-writer libreoffice-java-common --no-install-recommends
```

👉 **[Please follow the Foundation Setup Guide here](resources/guides/Foundation_Setup.md)** to configure your base environment.

---

## Setup Guide

### 1. Setup Python Environment
Create a new conda environment and install the required libraries:
```bash
conda create -n docrefine python=3.10 -y
conda activate docrefine
conda install -y -c conda-forge opencv pillow matplotlib numpy pytesseract notebook psutil docxtpl python-docx
pip install docxcompose
```

---

## How to Use

1. **Place Scans**: Place raw PDF rubric scans inside `data/raw_scans/` named as `001.png`, `002.png`, etc.
2. **Place Pre-captured Signatures**: Place pre-cropped mentor signatures inside `data/signature/mentor_signatures/` named as `1.png`, `2.png`, etc., and the WIL coordinator signature at `data/signature/wil_signature.jpeg`.
3. **Execute Pipeline**: Run the batch execution script from the command line:
   ```bash
   conda activate docrefine
   python run_pipeline.py
   ```
4. **Review Outputs**:
   - PDF documents are generated and saved inside `data/output/docs/`.
   - Process metrics and review reports are saved at `logs/process_logs/report_*.md`.
