# Walkthrough: Batch Document Generation & PDF Conversion

We have successfully implemented and executed the batch document generation, PDF conversion, and reporting pipeline. All 344 PDF documents (both WPL_02 and WPL_04 cover pages and rubrics) have been compiled successfully.

---

## 🛠️ Changes Made

1. **Standalone Automation Script (`run_pipeline.py`)**:
   - Creates a modular process using `pandas`, `docxtpl`, and `docx`.
   - Incorporates student scores from `MIP360S_Results.csv` (using split-based matching to support multiple student numbers like `218288891/220163103`).
   - Evaluates random variables for `WPL_02` ($Q1T, Q2T \in [10, 28]$ and $Q2T \ge Q1T$ when $T2 \ge 50\%$) and `WPL_04` ($XT \le 28$).
   - Decomposes combined scores into random ELO ratings in the $[2, 4]$ range (high scores) or the $[0, 3]$ range (low scores < 50%).
   - Generates random registration dates (`r_date`) between November 25 and December 1 of the respective year.
   - Cleans and formats all data fields, omitting `N/A` or empty entries from the Word layout.
   
2. **Signature Verification & Fallback Routing**:
   - Searches `data/signature/mentor_signatures/{page_no}.png` for pre-registered signatures.
   - Bypasses raw scan processing if found, improving batch performance significantly.
   - Automatically falls back to alignment (`align_images` via SIFT homography) and crop extraction if a registered signature is missing (e.g. Page 33).

3. **LibreOffice Headless PDF Conversion**:
   - Renders output `.docx` files temporarily.
   - Performs command line conversions to `.pdf` format.
   - Deletes intermediate `.docx` templates to maintain a clean workspace.

4. **Process Reporting System**:
   - Compiles metrics for the run, tracking completed items, blank records, missing data, and flagged files.
   - Saves a detailed markdown report inside `logs/process_logs/`.

---

## 🧪 What Was Tested & Validation Results

We executed the batch pipeline logic on the entire dataset:

* **Trial Test Run**:
  - Ran a subset of the first 5 records generating 20 PDF files.
  - Verified that landscape (cover page) and portrait (rubric) orientations were preserved.
  - Confirmed the correct rendering of embedded signatures and text mappings.

* **Full Run Statistics**:
  - Ran the script on the entire dataset of **86 records**, generating **344 PDF files** in the `data/output/docs/` folder:
    - **Total PDF Files Generated**: 344 files
    - **Successfully Fully Completed**: 32 records
    - **Empty / Missing Scores (Left Blank)**: 4 records
    - **Missing Crucial Information**: 9 records
    - **Needs Review (Flagged)**: 41 records

### Generated Output files:
- Cover Pages: `page_###_WPL_02_Cover_Page.pdf` & `page_###_WPL_04_Cover_Page.pdf` (saved in landscape format).
- Rubric Pages: `page_###_WPL_02.pdf` & `page_###_WPL_04.pdf` (saved in portrait format).

### Log & Report Location:
- Process Log: [run_pipeline.log](file:///home/hlatsiieyhax/DevBlock/personal_projects/DocRefine-OCR/logs/process_logs/)
- Full Markdown Report: [report_20260607_161422.md](file:///home/hlatsiieyhax/DevBlock/personal_projects/DocRefine-OCR/logs/process_logs/report_20260607_161422.md)
