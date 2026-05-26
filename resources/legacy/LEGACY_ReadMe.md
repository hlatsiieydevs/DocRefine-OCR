# crazyOCR
This is simply a mini project that I am working on that aims to digitise scanned documents into text files effectively and efficiently.

## Prerequisites
A system with Ubuntu and Anaconda preinstalled

## Setup
### Install required packages
Update local repository
``` bash
sudo apt update && sudo apt upgrade
```

Install required packages
``` bash
sudo apt install -y build-essential pkg-config \
    tesseract-ocr tesseract-ocr-eng tesseract-ocr-osd tesseract-ocr-script-latn \
    poppler-utils
```

### Verify Tesseract
Confirm Tesseract is installed
``` bash
tesseract --version
```

Confirm the required Tesseract packages are installed
``` bash
tesseract --list-langs
```
If `eng`(and `Latin` or `script-latn`) appears, you're all good homie. If not, install the missing language packages.

### Launch into your Conda environment 
Create a Conda environment. Enter a name of your choosing.
``` bash
conda create -n <name-of-environment> python=3.10 -y
```

Launch into the environment
``` bash
conda activate <name-of-environment>
```

### Install necessary packages in the environment
``` bash
conda install -c conda-forge pytorch torchvision torchaudio nvidia pytorch-cuda opencv pillow matplotlib numpy pytesseract notebook -y
```

### For crazyOCR v2.0
```bash
pip install psutils
```

## How to Use
### Loading the images
For the best results, make sure your scans are high quality (+300 dpi) and that it is a single page. The more preprocessed the image, the better the chances of a good result.

For books, create a folder in `data/raw` with the name of your book (e.g. Demonstration_Works)
(e.g. `data/raw/Demonstration_Works`)

Rename the individual images to the following format, `Demonstration_Works_1.png`, `Demonstration_Works_2.png` and so forth. You can make use of Bulk Rename Utility on Windows or IfranView to achieve this process without wasting time.

Run Jupyter Notebook and open the `crazyOCR.iypnb`, do tweak the parameter in Cell #2 to your preference thereafter click on `Restart Kernal and Run All Cells`.

 
