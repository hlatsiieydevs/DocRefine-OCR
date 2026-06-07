# Implementation Plan - PDF Refinement, Conversion & Reporting System

We will implement a Python script (`run_pipeline.py`) that automates the generation of cover pages and rubrics for both `WPL_02` and `WPL_04` configurations, converts them to PDF using LibreOffice, and generates a post-process verification report.

## Proposed Changes

### 1. New Standalone Script: `run_pipeline.py`
We will create a clean, standalone Python script [run_pipeline.py](file:///home/hlatsiieyhax/DevBlock/personal_projects/DocRefine-OCR/run_pipeline.py) that implements the pipeline logic, mathematical rules, and the final reporting system.

#### [NEW] [run_pipeline.py](file:///home/hlatsiieyhax/DevBlock/personal_projects/DocRefine-OCR/run_pipeline.py)
- **Data Loading**: Loads student data from `data/tables/WPL_02_Final_Dataset.csv` and marks from `data/tables/totals/MIP360S_Results.csv`.
- **Date Generation**: Generates `r_date` as a random date between Nov 25 and Dec 1 of the student's respective year.
- **WPL_02 ELO Score Distribution**:
  - Combined Total: $TotalCombined = \text{round}(T2\% \times 56)$
  - Generates random integers $Q1T \in [10, 28]$ and $Q2T = TotalCombined - Q1T$.
  - Enforces $Q2T > Q1T$ when $T2 \ge 50\%$.
  - For $T2 < 50\%$: relaxes the $Q2T > Q1T$ constraint. ELO variables range from $0$ to $3$ instead of $2$ to $4$.
  - Distributes $Q1T$ and $Q2T$ randomly among 7 ELO scores ($Q1_1 \dots Q1_7$ and $Q2_1 \dots Q2_7$).
- **WPL_04 ELO Score Distribution**:
  - Total: $XT = \text{round}(T4\% \times 28)$
  - If $T4 \ge 50\%$, distributes $XT$ among 7 variables $X_1 \dots X_7$ in range $[2, 4]$.
  - If $T4 < 50\%$, distributes $XT$ among 7 variables $X_1 \dots X_7$ in range $[0, 3]$.
- **N/A and Omission Handling**:
  - If a student has no entry or a 0/NaN score in the Results CSV, leaves ELO scores, total scores, final score, and achievement status blank (`""`).
  - Omits `N/A` fields from the student table (e.g. mentor name, year, comments).
- **Signature Routing**:
  - Checks if mentor signature is registered at `data/signature/mentor_signatures/{page_no_int}.png`.
  - If present: uses it and skips processing raw scans.
  - If missing: falls back to locating the raw scan in `data/raw_scans/{page_no_3_digits}.png` to align, crop, and save it.
- **Docx rendering & PDF conversion**:
  - Renders all 4 templates.
  - Converts them to PDF using `libreoffice --headless --convert-to pdf`.
  - Saves them as:
    * `page_###_WPL_02_Cover_Page.pdf`
    * `page_###_WPL_02.pdf`
    * `page_###_WPL_04_Cover_Page.pdf`
    * `page_###_WPL_04.pdf`
    where `###` is a three-digit zero-padded page number (e.g., `013`).
- **Reporting System**:
  Tracks and counts:
  - **Successfully Completed**: Generated successfully with valid scores and no warnings/comments.
  - **Empty/Missing Scores**: Generated successfully but student had no entry or a 0/NaN score in Results CSV.
  - **Missing Information**: Missing crucial fields (e.g., Student Name, Student Number, or Year) in the dataset.
  - **Need to be Reviewed**: Records flagged with issues in `AI Comments` (e.g. "Missing Mentor Name"), invalid student numbers, missing signatures, or compile errors.
  - Outputs a detailed markdown report summary at the end of execution and saves it to `logs/process_logs/`.

---

### 2. Jupyter Notebook Integration
We will update [Automation_Pipeline.ipynb](file:///home/hlatsiieyhax/DevBlock/personal_projects/DocRefine-OCR/Automation_Pipeline.ipynb) to import the refactored logic from `run_pipeline.py` or run it directly so you can trigger the batch process from your notebook.

#### [MODIFY] [Automation_Pipeline.ipynb](file:///home/hlatsiieyhax/DevBlock/personal_projects/DocRefine-OCR/Automation_Pipeline.ipynb)
- Replaces legacy cells with clean wrapper code that runs the standalone script and prints the execution report inline.

---

## Verification Plan

### Automated Verification
- We will run a validation command on a single row/subset to verify:
  1. No template tags remain unrendered (warnings from docxtpl).
  2. PDF conversions succeed and create valid, openable `.pdf` files.
  3. Score sums mathematically match the target percentages.
  4. The reporting script correctly classifies student statuses.

### Manual Verification
- We will inspect the generated PDFs inside `data/output/docs/` to confirm that:
  - Portrait and landscape orientations are preserved appropriately.
  - Images (WIL coordinator signature and mentor signatures) render inline correctly.
  - Text fields containing `N/A` are omitted (blank).
