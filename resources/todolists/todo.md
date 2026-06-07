# To-Do List: Document Automation & Image Extraction

## Prerequisites
- **Python Libraries**: `pandas`, `opencv-python` (`cv2`), `matplotlib`, `docxtpl`, `python-docx`, `jinja2`.
- **Input Data Structure**: 
  - **CSV File**: `WPL_02_Final_Dataset.csv` (must contain student data, ELO scores, and a `Page No.` column).
  - **Raw Scans Directory**: `raw_scans/` filled with physical forms named sequentially (e.g., `001.png`, `002.jpg`).
  - **Word Template**: `WPL 02_Rubric for GA12_Workplace Practices.docx` with Jinja2 tags (e.g., `{{ student_name }}`, `{{ comment_block }}`).

## Tasks
- [ ] **1. Setup & Environment**
  - Import required libraries.
  - Define global variables and paths.
  - Create necessary output directories (`outputs/comments/`, `outputs/signatures/`, `outputs/dates/`, `outputs/docs/`, `logs/process_logs/`).
- [x] **2. Core Function Implementation**
  - Use `cv2.ORB_create` and Homography (`cv2.findHomography`, `cv2.warpPerspective`) to align the raw scan to `WPL_02_ELO_Original_Template.png`.
  - Write `extract_image_blocks(image_path, student_number)` using percentage-based cropping on the aligned output for Comment, Signature, and Date blocks.
- [ ] **3. Preview Mode (Interactive)**
  - Select a random row from the CSV.
  - Process the image, show `matplotlib` subplots of the 3 cropped regions.
  - Implement interactive input prompt (`y/n`) to confirm before proceeding.
- [ ] **4. Batch Execution Loop**
  - Iterate through the CSV.
  - Process Page No., handle missing files gracefully with warnings.
  - Extract image blocks, perform `docxtpl` injection (text and InlineImage).
  - Save output `.docx` sequentially.
- [ ] **5. Changelog Generation**
  - Create and document changes in `/logs/changelogs/2026-06-04-refactor.md`.