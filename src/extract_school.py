
import pandas as pd
import os

def extract_school_data():
    input_file = 'data/raw/IMC FEDERAL.xlsx'
    sheet_name = 'Hoja1'
    
    print(f"Reading {input_file}...")
    try:
        df = pd.read_excel(input_file, sheet_name=sheet_name)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Filter for Nuevo Ideal and Amado Nervo
    locality = 'NUEVO IDEAL'
    school_name = 'AMADO NERVO'
    
    print(f"Filtering for Localidad: '{locality}' and Escuela: '{school_name}'...")
    
    # Normalize strings for comparison just in case
    df['LOCALIDAD'] = df['LOCALIDAD'].astype(str).str.strip().str.upper()
    df['ESCUELA'] = df['ESCUELA'].astype(str).str.strip().str.upper()
    
    filtered_df = df[
        (df['LOCALIDAD'] == locality) & 
        (df['ESCUELA'] == school_name)
    ]
    
    print(f"Found {len(filtered_df)} records.")
    
    if len(filtered_df) == 0:
        print("No records found. Check spelling or data.")
        return

    output_dir = 'data/processed/NUEVO_IDEAL'
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'AMADO_NERVO.xlsx')
    
    print(f"Saving to {output_file}...")
    filtered_df.to_excel(output_file, index=False)
    print("Done.")

if __name__ == "__main__":
    extract_school_data()
