# **Role and Objective**

You are an expert Python developer specializing in document automation, computer vision (OpenCV), and templating.

Your objective is to write a complete, robust, and well-commented Jupyter Notebook script that automates the generation of assessment documents. The script will read structured data from a CSV, extract three specific image regions (Comment block, Signature block, Date block) from corresponding raw scanned images, and inject both the text data and the images into a .docx template.

# **Input Data**

1. **CSV File (WPL\_02\_Final\_Dataset.csv)**: Contains student data, ELO scores, and a Page No. column.  
2. **Raw Scans Directory (raw\_scans/)**: Contains scanned physical forms. The files are named sequentially based on the page number, padded to three digits (e.g., Page No. 1 corresponds to 001.png or 001.jpg). Note: Some scans may have slightly different dimensions.  
3. **Word Template (WPL 02\_Rubric for GA12\_Workplace Practices.docx)**: A Jinja2-tagged Word document using docxtpl formatting (e.g., {{ student\_name }}, {{ student\_number }}, {{ comment\_block }}, {{ signature\_block }}, {{ date\_block }}).

# **Workflow Requirements**

Please write a Python script that executes the following workflow:

### **1\. Setup & Initialization**

* Import necessary libraries: pandas, cv2, os, matplotlib.pyplot, random, docxtpl (specifically DocxTemplate and InlineImage), docx.shared.Mm, logging, and datetime.  
* Define global variables for file paths (CSV\_PATH, SCANS\_DIR, TEMPLATE\_PATH, OUTPUT\_DOCS\_DIR, and LOG\_DIR mapped to logs/process\_logs/).  
* Define global variables for the image extraction outputs:  
  * OUTPUT\_COMMENTS\_DIR \= "outputs/comments/"  
  * OUTPUT\_SIGNATURES\_DIR \= "outputs/signatures/"  
  * OUTPUT\_DATES\_DIR \= "outputs/dates/"  
* Ensure all necessary directories are created if they do not exist.

### **2\. Helper Function: Image Cropping**

* Write a function extract\_image\_blocks(image\_path, student\_number).  
* The function should load the image using OpenCV.  
* **Crucial Step:** Because some scans have different dimensions, do not use absolute hardcoded pixel values. Instead, calculate the crops based on relative percentages or relative bounding boxes to capture three separate sections:  
  1. The "Comments" block  
  2. The "Mentor Signature" block  
  3. The "Date" block  
* Save the three cropped snippets to their respective output directories using the student number as the filename (e.g., outputs/signatures/{student\_number}.png).  
* Return a dictionary of the successful file paths (e.g., {'comment': path1, 'signature': path2, 'date': path3}) or None if it fails.

### **3\. Preview Mode (Interactive)**

* Before batch processing, the script must load the CSV and pick one random row.  
* Format the Page No. from that row into a 3-digit zero-padded string (e.g., 1 \-\> 001). Look for 001.png or 001.jpg in the raw\_scans directory.  
* Run the extract\_image\_blocks function on this file.  
* Use matplotlib.pyplot.subplots to display all three cropped images side-by-side in the Jupyter cell so the user can verify the crops are accurate.  
* Use Python's input() function to pause execution: "Do the crops look correct? Proceed with batch? \[y/n\]: ". If 'n', gracefully exit the script.

### **4\. Batch Processing Loop**

* If the user approves the preview, iterate through every row in the CSV file.  
* **Step A: File Mapping:** Read Page No., zero-pad it to 3 digits, and locate the raw scan file. Handle both .png and .jpg extensions. If a file is missing, log a warning and skip the image portion but still generate the document.  
* **Step B: Cropping:** Call extract\_image\_blocks(image\_path, student\_number).  
* **Step C: Template Injection:**  
  * Initialize DocxTemplate(TEMPLATE\_PATH).  
  * Create a context dictionary mapping the CSV row headers to the {{ tags }} in the Word document. (e.g., {'student\_name': row\['Student Name'\], 'year': row\['Year'\], ...}).  
  * Check if the crops were successful. If they were, instantiate an InlineImage for the comment\_block, signature\_block, and date\_block tags, appropriately restricting their width using Mm() to prevent breaking the document layout. If an image is missing, pass a fallback string like "IMAGE MISSING" to the context instead.  
* **Step D: Export:** Render the document and save it to the OUTPUT\_DOCS\_DIR named as WPL02\_{student\_number}.docx.

### **5\. Error Handling & Logging**

* Configure Python's built-in logging module to output to a file inside the logs/process\_logs/ directory.  
* The log file should be named using the current timestamp formatted as YYYY-MM-DD-HH-MM-SS.log (e.g., 2024-05-24-15-30-00.log).  
* Use logging to track the execution state:  
  * Log the initialisation of the script.  
  * Log a debug/info message whenever a file begins processing.  
  * Log warnings if an expected image file (e.g., 004.png) is missing.  
  * Wrap all file loading/saving operations in try/except blocks and log the exception tracebacks (logger.error()) if issues are encountered.  
* Keep a tally of successful generations versus errors.  
* Print a final summary at the end of the script (e.g., "Processed 90 files. 1 missing image.") and record this same summary into the log file.

# **Technical Constraints**

* The script must be structured to run smoothly in a Jupyter Notebook environment.  
* Do not use multithreading for the docxtpl generation unless necessary, as saving .docx files sequentially in a simple for loop is usually fast enough and easier to debug.