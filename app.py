import os
import tempfile
from flask import Flask, request, jsonify, render_template
import camelot
import pandas as pd
import datetime

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def extract_situaciones(pdf_path, pages="2-5"):
    """
    Extract situations from PDF labor life report.
    """
    tablas = camelot.read_pdf(pdf_path, pages=pages, flavor="stream")
    registros, corriente = [], None

    for tabla in tablas:
        df = tabla.df

        for _, fila_raw in df.iterrows():
            # Normalize: remove line breaks and extra spaces
            fila = [" ".join(str(c).split()) for c in fila_raw.tolist()]

            # Filter headers and separators
            if (fila[0].upper().startswith(("RÉGIMEN", "SITUACIÓN"))
                or fila[0] == "" and not fila[1].isdigit()):
                continue

            # Continuation rows (cell 0 is empty)
            if fila[0] == "":
                if corriente and fila[2]:
                    corriente["Empresa"] += " " + fila[2]
                continue

            # Fill missing cells to avoid index errors
            while len(fila) < 10:
                fila.append("")

            corriente = {
                "Regimen":           fila[0],
                "Codigo_Empresa":    fila[1],
                "Empresa":           fila[2],
                "Fecha_Alta":        fila[3],
                "Fecha_Efecto_Alta": fila[4],
                "Fecha_Baja":        fila[5],
                "C.T.":              fila[6],
                "CTP_%":             fila[7],
                "G.C.":              fila[8],
                "Dias":              fila[9],
            }
            registros.append(corriente)

    return pd.DataFrame(registros)

def format_date(date_str):
    """Format date from DD.MM.YYYY to DD/MM/YYYY"""
    try:
        d = datetime.datetime.strptime(date_str, "%d.%m.%Y")
        return d.strftime("%d/%m/%Y")
    except Exception:
        return ""

def calculate_non_overlapping_vacation_days(data):
    """
    Calculate vacation days that don't overlap with contract periods.
    Returns both the total days and the specific non-overlapping periods.
    """
    vacations = [item for item in data if item["isVacaciones"]]
    contracts = [item for item in data if not item["isVacaciones"]]
    
    total_non_overlapping_days = 0
    non_overlapping_periods = []
    
    for vacation in vacations:
        if not vacation["fechaAlta"] or not vacation["fechaBaja"]:
            continue
            
        try:
            vac_start = datetime.datetime.strptime(vacation["fechaAlta"], "%d/%m/%Y")
            vac_end = datetime.datetime.strptime(vacation["fechaBaja"], "%d/%m/%Y")
        except ValueError:
            continue
            
        # Find overlapping contracts
        overlapping_periods = []
        
        for contract in contracts:
            if not contract["fechaAlta"]:
                continue
                
            try:
                contract_start = datetime.datetime.strptime(contract["fechaAlta"], "%d/%m/%Y")
                # If contract has no end date, assume it's still active (use today)
                if contract["fechaBaja"]:
                    contract_end = datetime.datetime.strptime(contract["fechaBaja"], "%d/%m/%Y")
                else:
                    contract_end = datetime.datetime.now()
                    
                # Check if vacation overlaps with contract
                if vac_start <= contract_end and vac_end >= contract_start:
                    # Calculate overlapping period
                    overlap_start = max(vac_start, contract_start)
                    overlap_end = min(vac_end, contract_end)
                    overlapping_periods.append((overlap_start, overlap_end))
                    
            except ValueError:
                continue
        
        # Calculate non-overlapping periods for this vacation
        if not overlapping_periods:
            # No overlap, count all vacation days
            vacation_days = (vac_end - vac_start).days + 1
            total_non_overlapping_days += vacation_days
            non_overlapping_periods.append({
                "start": vac_start.strftime("%d/%m/%Y"),
                "end": vac_end.strftime("%d/%m/%Y"),
                "days": vacation_days
            })
        else:
            # Merge overlapping periods and calculate non-overlapping segments
            overlapping_periods.sort()
            merged_overlaps = []
            
            for overlap in overlapping_periods:
                if not merged_overlaps or merged_overlaps[-1][1] < overlap[0]:
                    merged_overlaps.append(overlap)
                else:
                    merged_overlaps[-1] = (merged_overlaps[-1][0], max(merged_overlaps[-1][1], overlap[1]))
            
            # Find non-overlapping segments within this vacation
            current_pos = vac_start
            
            for overlap_start, overlap_end in merged_overlaps:
                # Add period before this overlap (if any)
                if current_pos < overlap_start:
                    segment_end = overlap_start - datetime.timedelta(days=1)
                    segment_days = (segment_end - current_pos).days + 1
                    if segment_days > 0:
                        total_non_overlapping_days += segment_days
                        non_overlapping_periods.append({
                            "start": current_pos.strftime("%d/%m/%Y"),
                            "end": segment_end.strftime("%d/%m/%Y"),
                            "days": segment_days
                        })
                
                # Move current position past this overlap
                current_pos = overlap_end + datetime.timedelta(days=1)
            
            # Add remaining period after all overlaps (if any)
            if current_pos <= vac_end:
                segment_days = (vac_end - current_pos).days + 1
                if segment_days > 0:
                    total_non_overlapping_days += segment_days
                    non_overlapping_periods.append({
                        "start": current_pos.strftime("%d/%m/%Y"),
                        "end": vac_end.strftime("%d/%m/%Y"),
                        "days": segment_days
                    })
    
    return total_non_overlapping_days, non_overlapping_periods

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_pdf():
    try:
        if 'pdf' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['pdf']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'File must be a PDF'}), 400
        
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Extract data from PDF
            df = extract_situaciones(temp_path, pages="2-5")
            
            # Convert Fecha_Alta to datetime for filtering
            def parse_date(date_str):
                try:
                    return datetime.datetime.strptime(date_str, "%d.%m.%Y")
                except Exception:
                    return None

            df["Fecha_Alta_dt"] = df["Fecha_Alta"].apply(parse_date)
            
            # Extract only relevant records
            output_data = []
            for _, row in df.iterrows():
                empresa = row["Empresa"]
                
                # Check if it's a vacation record
                if empresa.startswith("VACACIONES RETRIBUIDAS Y NO"):
                    output_data.append({
                        "isVacaciones": True,
                        "fechaAlta": format_date(row["Fecha_Alta"]),
                        "fechaBaja": format_date(row["Fecha_Baja"])
                    })
                # Check if it's a health service contract
                elif empresa == "SERVICIO DE SALUD DEL PRINCIPADO":
                    output_data.append({
                        "isVacaciones": False,
                        "fechaAlta": format_date(row["Fecha_Alta"]),
                        "fechaBaja": format_date(row["Fecha_Baja"])
                    })
            
            # Calculate non-overlapping vacation days
            non_overlapping_vacation_days, vacation_periods = calculate_non_overlapping_vacation_days(output_data)
            
            # Prepare response
            results = {
                "data": output_data,
                "total_non_overlapping_vacation_days": non_overlapping_vacation_days,
                "non_overlapping_vacation_periods": vacation_periods
            }
            
            return jsonify(results)
            
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)