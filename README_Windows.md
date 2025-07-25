# SESPA Document Processor - Windows User Guide

## 📋 Overview
This tool processes Spanish labor documents ("INFORME DE VIDA LABORAL") to extract vacation and contract information, calculating non-overlapping vacation days.

## 🚀 Quick Start for Non-Technical Users

### Step 1: Install Requirements
1. **Download and install Python 3.8+** from https://python.org
   - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation
2. **Download and install Ghostscript** from https://www.ghostscript.com/download/gsdnld.html
   - Required for PDF processing only

### Step 2: Setup the Application
1. Double-click `setup_windows.bat`
2. Wait for installation to complete
3. Press any key when finished

### Step 3: Prepare Your Documents

#### For PDF Processing:
- Place your PDF file in the `data` folder
- Rename it to: `vida_laboral (2).pdf`

#### For Image/OCR Processing:
- Place your document images in the `data/imagenes` folder
- Supported formats: .jpg, .jpeg, .png

### Step 4: Run Processing

#### Process PDF Documents:
1. Double-click `run_pdf_processing.bat`
2. Choose whether to filter records before 2008 (y/n)
3. Wait for processing to complete

#### Process Image Documents:
1. Double-click `run_ocr_processing.bat`
2. Choose whether to filter records before 2008 (y/n)
3. Wait for processing to complete (may take several minutes)

### Step 5: View Results
Results are saved in the `output` folder:
- **vacation_report.xlsx** - Excel report with summary and detailed periods
- **py_output.json** - Raw extracted data
- **py_output_with_calculation.json** - Data with calculations
- **situaciones.csv** - CSV export (PDF processing only)

## 📁 Folder Structure
```
sespa/
├── data/
│   ├── vida_laboral (2).pdf        # Your PDF file goes here
│   └── imagenes/                   # Your image files go here
├── output/                         # Results appear here
├── setup_windows.bat               # Run this first
├── run_pdf_processing.bat          # For PDF files
├── run_ocr_processing.bat          # For image files
└── README_Windows.md               # This guide
```

## 🔧 Troubleshooting

### "Python is not installed or not in PATH"
- Reinstall Python from https://python.org
- Make sure to check "Add Python to PATH" during installation

### "Ghostscript not found"
- Download and install from https://www.ghostscript.com/download/gsdnld.html
- Only needed for PDF processing

### "PDF file not found"
- Make sure your PDF is named exactly: `vida_laboral (2).pdf`
- Place it in the `data` folder

### "No image files found"
- Place your images in `data/imagenes` folder
- Supported formats: .jpg, .jpeg, .png

### OCR Processing is Slow
- This is normal - OCR processing can take several minutes per image
- Higher quality images process faster and more accurately

## 📊 Understanding Results

### Excel Report (vacation_report.xlsx)
- **Summary sheet**: Total non-overlapping vacation days
- **Detailed periods sheet**: Each vacation period with dates and duration

### What the Tool Does
1. Extracts vacation records ("VACACIONES RETRIBUIDAS Y NO DISFRUTADAS")
2. Extracts contract records ("SERVICIO DE SALUD DEL PRINCIPADO")
3. Calculates vacation days that don't overlap with active contracts
4. Generates detailed reports

## 🆘 Need Help?
If you encounter issues:
1. Make sure all installation steps were completed
2. Check that your documents are in the correct folders
3. Verify file names match exactly as specified
4. Try running `setup_windows.bat` again if needed

## 📝 Notes
- OCR processing requires internet connection (uses AI service)
- PDF processing works offline after initial setup
- Results are automatically saved with timestamps
- All processing is done locally on your computer (except OCR AI calls)