import pandas as pd
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import os

# 1. Setup Paths
TEMPLATE_PATH = "WPL 02_Rubric for GA12_Workplace Practices.docx"
CSV_PATH = "WPL_02_Final_Dataset.csv"
SIGNATURE_DIR = "signatures_crop/"
OUTPUT_DIR = "completed_forms/"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 2. Load the Dataset
df = pd.read_csv(CSV_PATH)

# 3. Process Each Student
for index, row in df.iterrows():
    student_no = str(row['Student Number'])
    
    # Initialize the Word Template
    doc = DocxTemplate(TEMPLATE_PATH)
    
    # Locate the combined signature/comment crop for this student
    image_path = os.path.join(SIGNATURE_DIR, f"{student_no}.png")
    
    if os.path.exists(image_path):
        # Create an InlineImage object. 
        # width=Mm(150) restricts the image to 150 millimeters wide so it doesn't break the page margins.
        signature_img = InlineImage(doc, image_path, width=Mm(150))
    else:
        signature_img = "SIGNATURE MISSING"
        print(f"Warning: No signature image found for {student_no}")

    # 4. Map the Data to the {{ tags }} in the Word Document
    context = {
        'student_name': row['Student Name'],
        'student_number': student_no,
        'mentor_name': row['Mentor Name'],
        'signature_block': signature_img
    }
    
    # 5. Render and Save
    doc.render(context)
    output_filename = os.path.join(OUTPUT_DIR, f"WPL02_{student_no}.docx")
    doc.save(output_filename)
    print(f"Generated: {output_filename}")