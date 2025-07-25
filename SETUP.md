# Setup Instructions for Vacation Calculator

This document explains how to set up and run the vacation calculation script from scratch on a machine without Python.

## Prerequisites

You'll need to install the following software:

### 1. Python 3.8+
- **Windows**: Download from [python.org](https://www.python.org/downloads/windows/)
- **macOS**: Use Homebrew: `brew install python3` or download from [python.org](https://www.python.org/downloads/mac-osx/)
- **Linux**: `sudo apt install python3 python3-pip python3-venv` (Ubuntu/Debian) or equivalent for your distribution

### 2. Ghostscript (required for PDF processing)
- **Windows**: Download from [ghostscript.com](https://www.ghostscript.com/download/gsdnld.html)
- **macOS**: `brew install ghostscript`
- **Linux**: `sudo apt install ghostscript` (Ubuntu/Debian)

### 3. System Dependencies for PDF processing
- **Windows**: Usually included with Ghostscript
- **macOS**: `brew install poppler` (optional but recommended)
- **Linux**: `sudo apt install poppler-utils` (Ubuntu/Debian)

## Installation Steps

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd sespa
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment**
   ```bash
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

4. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Scripts

### Main extraction script:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
python extract.py
```

### Test suite:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
python test_vacation_calculation.py
```

## Expected Output

- The script will process the PDF file in `data/vida_laboral (2).pdf`
- It will create output files in the `output/` directory
- The console will show the total non-overlapping vacation days
- The test suite will run 10 test cases and show pass/fail results

## Troubleshooting

### Common Issues:

1. **"camelot not found" error**
   - Make sure ghostscript is installed
   - Try: `pip install "camelot-py[cv]"` manually

2. **PDF processing errors**
   - Ensure the PDF file exists in `data/vida_laboral (2).pdf`
   - Check that ghostscript is properly installed and in PATH

3. **Permission errors on Windows**
   - Run command prompt as Administrator
   - Or use: `python -m pip install -r requirements.txt`

4. **Virtual environment issues**
   - Delete the `venv` folder and recreate it
   - Use `python -m venv venv` instead of `python3`

## File Structure
```
sespa/
├── extract.py                          # Main extraction script
├── test_vacation_calculation.py        # Test suite
├── requirements.txt                    # Python dependencies
├── data/
│   └── vida_laboral (2).pdf           # Input PDF file
└── output/                            # Generated output files
    ├── py_output.json
    └── py_output_with_calculation.json
```

## What the Script Does

1. Extracts vacation and contract data from the PDF
2. Identifies vacation periods (`isVacaciones: true`) and contract periods (`isVacaciones: false`)
3. Calculates vacation days that don't overlap with any contract period
4. Outputs the total non-overlapping vacation days

The calculation handles edge cases like:
- Partial overlaps between vacations and contracts
- Multiple overlapping contracts
- Active contracts with no end date
- Invalid or missing dates