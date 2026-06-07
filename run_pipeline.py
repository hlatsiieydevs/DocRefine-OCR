import os
import random
import subprocess
import logging
import pandas as pd
from datetime import datetime, timedelta
from docxtpl import DocxTemplate, InlineImage
from docx import Document
from docx.shared import Mm
from docx.enum.section import WD_ORIENT

# Initialize Logging
LOG_DIR = 'logs/process_logs/'
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, f"run_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    filename=log_file, 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Global Paths
CSV_PATH = "data/tables/WPL_02_Final_Dataset.csv"
RESULTS_PATH = "data/tables/totals/MIP360S_Results.csv"
TEMPLATE_WPL02_COVER = "data/templates/injection/WPL_02_Cover_Page.docx"
TEMPLATE_WPL02_RUBRIC = "data/templates/injection/WPL_02.docx"
TEMPLATE_WPL04_COVER = "data/templates/injection/WPL_04_Cover_Page.docx"
TEMPLATE_WPL04_RUBRIC = "data/templates/injection/WPL_04.docx"

WIL_SIG_PATH = "data/signature/wil_signature.jpeg"
MENTOR_SIG_DIR = "data/signature/mentor_signatures/"
SCANS_DIR = "data/raw_scans/"
OUTPUT_DIR = "data/output/docs/"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs("scratch", exist_ok=True)

# ROI configuration for raw scan extraction fallback (legacy template matching)
DYNAMIC_ANCHOR_MAP = {
    'signature': {
        'anchor_path': 'data/templates/extraction/signature_anchor.png',
        'offset_x': 256,
        'offset_y': 20,
        'crop_w': 885,
        'crop_h': 71,
        'threshold': 0.55
    }
}
FULL_PAGE_TEMPLATE_PATH = "data/templates/extraction/full_page_template.png"

def is_homography_valid(H):
    if H is None:
        return False
    det = H[0, 0] * H[1, 1] - H[0, 1] * H[1, 0]
    if det <= 0.1 or det >= 10.0:
        return False
    if abs(H[2, 0]) > 0.002 or abs(H[2, 1]) > 0.002:
        return False
    return True

def align_images(img, template_img, max_features=5000):
    import cv2
    import numpy as np
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template_img, cv2.COLOR_BGR2GRAY)
    
    sift = cv2.SIFT_create(max_features)
    kpsA, descsA = sift.detectAndCompute(img_gray, None)
    kpsB, descsB = sift.detectAndCompute(template_gray, None)
    
    if descsA is None or descsB is None:
        return cv2.resize(img, (template_img.shape[1], template_img.shape[0]))

    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(descsA, descsB, k=2)
    
    good_matches = []
    for m_n in matches:
        if len(m_n) != 2:
            continue
        m, n = m_n
        if m.distance < 0.7 * n.distance:
            good_matches.append(m)
            
    if len(good_matches) < 10:
        return cv2.resize(img, (template_img.shape[1], template_img.shape[0]))
        
    ptsA = np.zeros((len(good_matches), 2), dtype="float32")
    ptsB = np.zeros((len(good_matches), 2), dtype="float32")
    for (i, m) in enumerate(good_matches):
        ptsA[i] = kpsA[m.queryIdx].pt
        ptsB[i] = kpsB[m.trainIdx].pt
        
    H, mask = cv2.findHomography(ptsA, ptsB, cv2.RANSAC, 5.0)
    if is_homography_valid(H):
        h, w = template_img.shape[:2]
        return cv2.warpPerspective(img, H, (w, h))
    else:
        return cv2.resize(img, (template_img.shape[1], template_img.shape[0]))

def crop_dynamic_region(aligned_img, anchor_img_path, offset_x, offset_y, crop_w, crop_h, threshold=0.55):
    import cv2
    gray_img = cv2.cvtColor(aligned_img, cv2.COLOR_BGR2GRAY)
    if not os.path.exists(anchor_img_path):
        return None
    anchor_img = cv2.imread(anchor_img_path, cv2.IMREAD_GRAYSCALE)
    if anchor_img is None:
        return None
        
    res = cv2.matchTemplate(gray_img, anchor_img, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    if max_val < threshold:
        return None
        
    anchor_x, anchor_y = max_loc
    start_x = anchor_x + offset_x
    start_y = anchor_y + offset_y
    end_x = start_x + crop_w
    end_y = start_y + crop_h
    
    img_h, img_w = aligned_img.shape[:2]
    crop_x_start = max(0, min(img_w, start_x))
    crop_x_end = max(0, min(img_w, end_x))
    crop_y_start = max(0, min(img_h, start_y))
    crop_y_end = max(0, min(img_h, end_y))
    
    if (crop_x_end - crop_x_start) <= 0 or (crop_y_end - crop_y_start) <= 0:
        return None
        
    return aligned_img[crop_y_start:crop_y_end, crop_x_start:crop_x_end]

def extract_signature_fallback(page_no):
    """
    Tries to locate the raw scan, aligns it, crops the signature, and registers it.
    """
    import cv2
    page_no_3d = str(page_no).zfill(3)
    img_path_png = os.path.join(SCANS_DIR, f"{page_no_3d}.png")
    img_path_jpg = os.path.join(SCANS_DIR, f"{page_no_3d}.jpg")
    image_path = img_path_png if os.path.exists(img_path_png) else img_path_jpg
    
    if not os.path.exists(image_path):
        logging.warning(f"Raw scan not found for page {page_no} at {image_path}")
        return None
        
    img = cv2.imread(image_path)
    template_img = cv2.imread(FULL_PAGE_TEMPLATE_PATH)
    if img is None or template_img is None:
        return None
        
    if img.shape == template_img.shape:
        aligned = img
    else:
        aligned = align_images(img, template_img)
        
    config = DYNAMIC_ANCHOR_MAP['signature']
    crop_img = crop_dynamic_region(
        aligned,
        config['anchor_path'],
        config['offset_x'],
        config['offset_y'],
        config['crop_w'],
        config['crop_h'],
        config['threshold']
    )
    
    if crop_img is not None:
        out_path = os.path.join(MENTOR_SIG_DIR, f"{page_no}.png")
        os.makedirs(MENTOR_SIG_DIR, exist_ok=True)
        cv2.imwrite(out_path, crop_img)
        logging.info(f"Extracted and registered mentor signature to {out_path}")
        return out_path
        
    return None

# Date Generator
def get_random_r_date(year_val):
    if pd.isna(year_val) or str(year_val).strip() in ('', 'N/A', 'nan', 'NaN'):
        return ''
    try:
        year = int(float(year_val))
    except ValueError:
        return ''
    start_date = datetime(year, 11, 25)
    random_days = random.randint(0, 6)
    r_date_obj = start_date + timedelta(days=random_days)
    return r_date_obj.strftime("%d/%m/%Y")

# Data cleaning
def clean_val(val):
    if pd.isna(val):
        return ""
    s = str(val).strip()
    if s.upper() in ("N/A", "NAN", ""):
        return ""
    # Remove trailing .0 if integer float
    if s.endswith('.0'):
        try:
            return str(int(float(s)))
        except ValueError:
            pass
    return s

# Look up T2 and T4
def lookup_scores(student_no_raw, results_df):
    if pd.isna(student_no_raw):
        return 0.0, 0.0
    s_raw = str(student_no_raw).strip()
    if s_raw.upper() in ("N/A", "NAN", ""):
        return 0.0, 0.0
    # Split by / or comma in case of multiple student numbers
    parts = [p.strip() for p in s_raw.replace('/', ',').split(',') if p.strip()]
    for part in parts:
        res_row = results_df[results_df['Student Number'].astype(str).str.strip() == part]
        if not res_row.empty:
            t2_val = res_row.iloc[0]['T2']
            t4_val = res_row.iloc[0]['T4']
            t2 = float(t2_val) if not pd.isna(t2_val) else 0.0
            t4 = float(t4_val) if not pd.isna(t4_val) else 0.0
            return t2, t4
    return 0.0, 0.0

# Decompiling sums into 7 ELO scores
def decompose_high_score(target_sum):
    # Sum is in [14, 28], variables in [2, 4]
    scores = [2] * 7
    remaining = target_sum - 14
    indices = list(range(7))
    random.shuffle(indices)
    for idx in indices:
        add = min(2, remaining)
        scores[idx] += add
        remaining -= add
        if remaining == 0:
            break
    return scores

def decompose_low_score(target_sum):
    # Sum is in [0, 21], variables in [0, 3]
    scores = [0] * 7
    remaining = target_sum
    indices = list(range(7))
    random.shuffle(indices)
    for idx in indices:
        add = min(3, remaining)
        scores[idx] += add
        remaining -= add
        if remaining == 0:
            break
    return scores

def generate_wpl02_scores(t2_val):
    if t2_val == 0.0:
        return {f'Q1_{i}': '' for i in range(1, 8)} | {f'Q2_{i}': '' for i in range(1, 8)} | {'Q1T': '', 'Q2T': ''}
    
    total_combined = int(round((t2_val / 100) * 56))
    
    # Low-score case check: if total combined score is below 29, ELO variables range 0-3
    if total_combined < 29:
        # Range of Q1T must be [0, min(21, total_combined)]
        min_q1 = max(0, total_combined - 21)
        max_q1 = min(21, total_combined)
        q1_total = random.randint(min_q1, max_q1)
        q2_total = total_combined - q1_total
        
        q1_scores = decompose_low_score(q1_total)
        q2_scores = decompose_low_score(q2_total)
    else:
        # High-score case: Q2T > Q1T, ELO variables range 2-4
        min_q1 = max(14, total_combined - 28)
        max_q1 = min(28, total_combined - 14, total_combined // 2)
        
        q1_total = random.randint(min_q1, max_q1)
        q2_total = total_combined - q1_total
        
        q1_scores = decompose_high_score(q1_total)
        q2_scores = decompose_high_score(q2_total)
        
    result = {}
    for i in range(1, 8):
        result[f'Q1_{i}'] = q1_scores[i-1]
        result[f'Q2_{i}'] = q2_scores[i-1]
    result['Q1T'] = q1_total
    result['Q2T'] = q2_total
    return result

def generate_wpl04_scores(t4_val):
    if t4_val == 0.0:
        return {f'X{i}': '' for i in range(1, 8)} | {'XT': ''}
        
    xt_val = int(round((t4_val / 100) * 28))
    
    if xt_val < 14:
        # Low score: range 0-3
        xt_val = max(0, min(21, xt_val))
        scores = decompose_low_score(xt_val)
    else:
        # High score: range 2-4
        xt_val = max(14, min(28, xt_val))
        scores = decompose_high_score(xt_val)
        
    result = {}
    for i in range(1, 8):
        result[f'X{i}'] = scores[i-1]
    result['XT'] = xt_val
    return result

# Conversion to PDF
def convert_docx_to_pdf(docx_path):
    try:
        # libreoffice --headless --convert-to pdf --outdir <out_dir> <docx_path>
        cmd = ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", OUTPUT_DIR, docx_path]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        logging.error(f"LibreOffice conversion failed for {docx_path}: {e}")
        return False

# Main batch process
def execute_batch():
    print("Starting document automation pipeline...")
    logging.info("Batch execution started.")
    
    try:
        df1 = pd.read_csv(CSV_PATH)
        df2 = pd.read_csv(RESULTS_PATH)
    except Exception as e:
        print(f"Error loading tables: {e}")
        logging.error(f"Error loading CSV files: {e}")
        return
        
    # Metrics
    total_records = len(df1)
    completed_wpl02 = 0
    completed_wpl04 = 0
    empty_scores_count = 0
    missing_info_count = 0
    review_needed_count = 0
    
    review_details = []
    missing_info_details = []
    empty_score_details = []
    
    # Check for WIL signature
    has_wil_sig = os.path.exists(WIL_SIG_PATH)
    if not has_wil_sig:
        print(f"WARNING: WIL Coordinator signature not found at {WIL_SIG_PATH}")
        logging.warning("WIL signature file missing.")

    for idx, row in df1.iterrows():
        student_name_raw = row.get('Student Name')
        student_name = clean_val(student_name_raw)
        student_number_raw = row.get('Student Number')
        student_number = clean_val(student_number_raw)
        year_raw = row.get('Year')
        year = clean_val(year_raw)
        
        page_no_raw = row.get('Page No.')
        if pd.isna(page_no_raw):
            logging.error(f"Missing page number for row {idx}")
            continue
        page_no = int(page_no_raw)
        page_no_str = str(page_no).zfill(3)
        
        mentor_name = clean_val(row.get('Mentor Name'))
        comment = clean_val(row.get('Comments'))
        ai_comments = clean_val(row.get('AI Comments'))
        
        # Determine Status flags
        is_missing_info = not student_name or not student_number or not year
        is_review_needed = (ai_comments != "" and ai_comments.upper() != "N/A" and ai_comments != "-")
        
        # Lookup Scores
        t2_val, t4_val = lookup_scores(student_number_raw, df2)
        is_empty_scores = (t2_val == 0.0 and t4_val == 0.0)
        
        # Build report logs
        student_id = f"{student_name} ({student_number})" if student_name else f"Row {idx} (Page {page_no})"
        if is_missing_info:
            missing_fields = []
            if not student_name: missing_fields.append("Student Name")
            if not student_number: missing_fields.append("Student Number")
            if not year: missing_fields.append("Year")
            missing_info_details.append(f"Page {page_no}: {student_id} - Missing {', '.join(missing_fields)}")
            missing_info_count += 1
        elif is_review_needed:
            review_details.append(f"Page {page_no}: {student_id} - Flagged: '{ai_comments}'")
            review_needed_count += 1
        elif is_empty_scores:
            empty_score_details.append(f"Page {page_no}: {student_id} - No matching score in Results table.")
            empty_scores_count += 1
            
        # Get signatures
        mentor_sig_path = f"{MENTOR_SIG_DIR}{page_no}.png"
        mentor_sig_exists = os.path.exists(mentor_sig_path)
        
        if not mentor_sig_exists and not is_missing_info:
            # Fallback to crop signature from scan
            extracted_path = extract_signature_fallback(page_no)
            if extracted_path:
                mentor_sig_path = extracted_path
                mentor_sig_exists = True
            else:
                logging.warning(f"Signature missing for page {page_no} and fallback extraction failed.")
                if not is_missing_info and not is_review_needed and not is_empty_scores:
                    review_details.append(f"Page {page_no}: {student_id} - Mentor signature missing.")
                    review_needed_count += 1
                    
        # Generate r_date
        r_date = get_random_r_date(year_raw)
        
        # Generate Scores
        scores_wpl02 = generate_wpl02_scores(t2_val)
        scores_wpl04 = generate_wpl04_scores(t4_val)
        
        # Cover page variables
        ach_stat_02 = ""
        ach_stat_04 = ""
        final_score_02 = ""
        final_score_04 = ""
        
        if t2_val > 0.0:
            ach_stat_02 = "Achieved" if t2_val >= 50.0 else "Not Achieved"
            final_score_02 = f"{int(t2_val)}%"
        if t4_val > 0.0:
            ach_stat_04 = "Achieved" if t4_val >= 50.0 else "Not achieved"
            final_score_04 = f"{int(t4_val)}%"
            
        # Context building
        context_wpl02_cover = {
            'student_name': student_name,
            'student_number': student_number,
            'final_score': final_score_02,
            'ach_state': ach_stat_02,
            'r_date': r_date
        }
        
        context_wpl02_rubric = {
            'student_name': student_name,
            'student_number': student_number,
            'year': year,
            'mentor_name': mentor_name,
            'comment': comment,
            'r_date': r_date
        }
        context_wpl02_rubric.update(scores_wpl02)
        
        context_wpl04_cover = {
            'student_name': student_name,
            'student_number': student_number,
            'final_score': final_score_04,
            'ach_state': ach_stat_04,
            'r_date': r_date
        }
        
        context_wpl04_rubric = {
            'student_name': student_name,
            'student_number': student_number,
            'year': year,
            'comment': comment
        }
        context_wpl04_rubric.update(scores_wpl04)
        
        # RENDER WPL_02
        try:
            # WPL_02 Cover
            tpl_02_cover = DocxTemplate(TEMPLATE_WPL02_COVER)
            tpl_02_cover.render(context_wpl02_cover)
            docx_02_cover_path = f"scratch/page_{page_no_str}_WPL_02_Cover_Page.docx"
            tpl_02_cover.save(docx_02_cover_path)
            

            
            # WPL_02 Rubric
            tpl_02_rubric = DocxTemplate(TEMPLATE_WPL02_RUBRIC)
            if has_wil_sig:
                context_wpl02_rubric['wil_signature'] = InlineImage(tpl_02_rubric, WIL_SIG_PATH, width=Mm(60))
            if mentor_sig_exists:
                context_wpl02_rubric['mentor_signature'] = InlineImage(tpl_02_rubric, mentor_sig_path, width=Mm(60))
            else:
                context_wpl02_rubric['mentor_signature'] = "SIGNATURE MISSING"
            tpl_02_rubric.render(context_wpl02_rubric)
            docx_02_rubric_path = f"scratch/page_{page_no_str}_WPL_02.docx"
            tpl_02_rubric.save(docx_02_rubric_path)
            
            # Convert both WPL_02 files to PDF
            conv_1 = convert_docx_to_pdf(docx_02_cover_path)
            conv_2 = convert_docx_to_pdf(docx_02_rubric_path)
            
            # Clean up temp docx
            os.remove(docx_02_cover_path)
            os.remove(docx_02_rubric_path)
            
            if conv_1 and conv_2:
                completed_wpl02 += 1
                logging.info(f"Page {page_no_str}: Successfully generated WPL_02 cover page and rubric PDFs.")
            else:
                logging.error(f"Page {page_no_str}: Failed to convert WPL_02 docx to PDF.")
                
        except Exception as e:
            logging.error(f"Page {page_no_str}: WPL_02 generation failed: {e}")
            
        # RENDER WPL_04
        try:
            # WPL_04 Cover
            tpl_04_cover = DocxTemplate(TEMPLATE_WPL04_COVER)
            tpl_04_cover.render(context_wpl04_cover)
            docx_04_cover_path = f"scratch/page_{page_no_str}_WPL_04_Cover_Page.docx"
            tpl_04_cover.save(docx_04_cover_path)
            

            
            # WPL_04 Rubric
            tpl_04_rubric = DocxTemplate(TEMPLATE_WPL04_RUBRIC)
            if has_wil_sig:
                context_wpl04_rubric['wil_signature'] = InlineImage(tpl_04_rubric, WIL_SIG_PATH, width=Mm(60))
            tpl_04_rubric.render(context_wpl04_rubric)
            docx_04_rubric_path = f"scratch/page_{page_no_str}_WPL_04.docx"
            tpl_04_rubric.save(docx_04_rubric_path)
            
            # Convert both WPL_04 files to PDF
            conv_3 = convert_docx_to_pdf(docx_04_cover_path)
            conv_4 = convert_docx_to_pdf(docx_04_rubric_path)
            
            # Clean up temp docx
            os.remove(docx_04_cover_path)
            os.remove(docx_04_rubric_path)
            
            if conv_3 and conv_4:
                completed_wpl04 += 1
                logging.info(f"Page {page_no_str}: Successfully generated WPL_04 cover page and rubric PDFs.")
            else:
                logging.error(f"Page {page_no_str}: Failed to convert WPL_04 docx to PDF.")
                
        except Exception as e:
            logging.error(f"Page {page_no_str}: WPL_04 generation failed: {e}")
            
    # Clean up empty temp cover/rubric files if any exist
    for p in ['scratch/temp_cover.docx', 'scratch/temp_rubric.docx', 'scratch/temp_cover_wpl04.docx', 'scratch/temp_rubric_wpl04.docx']:
        if os.path.exists(p):
            os.remove(p)

    # Compute successful fully completed count (records with no missing info, no empty scores, and not needing review)
    successful_fully_completed = total_records - (empty_scores_count + missing_info_count + review_needed_count)

    # Output Report Summary
    report_md = f"""# Document Automation Process Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Process Metrics
- **Total Student Records in Dataset**: {total_records}
- **Successfully Fully Completed**: {successful_fully_completed}
- **Empty / Missing Scores (Left Blank)**: {empty_scores_count}
- **Missing Crucial Information**: {missing_info_count}
- **Needs Review (AI Comments / Missing Signature)**: {review_needed_count}

- **Total WPL_02 Cover Page PDFs Generated**: {completed_wpl02}
- **Total WPL_02 Rubric PDFs Generated**: {completed_wpl02}
- **Total WPL_04 Cover Page PDFs Generated**: {completed_wpl04}
- **Total WPL_04 Rubric PDFs Generated**: {completed_wpl04}

---

## Details of Records with Missing Crucial Information
"""
    if missing_info_details:
        for d in missing_info_details:
            report_md += f"- {d}\n"
    else:
        report_md += "*None*\n"
        
    report_md += "\n## Details of Records Left with Blank Scores\n"
    if empty_score_details:
        for d in empty_score_details:
            report_md += f"- {d}\n"
    else:
        report_md += "*None*\n"
        
    report_md += "\n## Details of Records Flagged for Review\n"
    if review_details:
        for d in review_details:
            report_md += f"- {d}\n"
    else:
        report_md += "*None*\n"
        
    # Write Report File
    report_file_path = os.path.join(LOG_DIR, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    with open(report_file_path, "w") as f:
        f.write(report_md)
        
    print("\n" + "="*40)
    print("      DOCUMENT AUTOMATION PROCESS REPORT")
    print("="*40)
    print(f"Total Student Records:                {total_records}")
    print(f"Successfully Fully Completed:         {successful_fully_completed}")
    print(f"Empty/Missing Scores (Left Blank):    {empty_scores_count}")
    print(f"Missing Crucial Information:          {missing_info_count}")
    print(f"Needs Review (AI Flagged / Sig Miss): {review_needed_count}")
    print("-"*40)
    print(f"Total PDF Files Generated:            {completed_wpl02 + completed_wpl02 + completed_wpl04 + completed_wpl04}")
    print(f"Report saved to: {report_file_path}")
    print("="*40)
    
if __name__ == "__main__":
    execute_batch()
