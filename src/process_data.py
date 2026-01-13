import pandas as pd
import os
import re
import shutil
import tempfile
import argparse
import sys

def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '_', str(name)).strip()

def filter_data(input_path, output_path):
    print(f"--- Filtering Data ---")
    print(f"Reading: {input_path}")
    
    try:
        df = pd.read_excel(input_path, sheet_name='Hoja1')
        
        if 'PERCENTILES' in df.columns:
            df['PERCENTILES'] = pd.to_numeric(df['PERCENTILES'], errors='coerce')
            
            filtered_df = df[(df['PERCENTILES'] < 15) | (df['PERCENTILES'] > 85.1)]
            
            print(f"Original records: {len(df)}")
            print(f"Filtered records: {len(filtered_df)}")
            
            filtered_df.to_excel(output_path, index=False)
            print(f"Saved filtered data to: {output_path}")
            return filtered_df
        else:
            print("Error: Column 'PERCENTILES' not found.")
            return None
    except Exception as e:
        print(f"Error filtering data: {e}")
        return None

def split_data(input_df, base_output_dir):
    print(f"\n--- Splitting Data ---")
    
    if input_df is None or input_df.empty:
        print("No data to split.")
        return

    required_cols = ['ZONA_EF', 'ESCUELA']
    for col in required_cols:
        if col not in input_df.columns:
            print(f"Error: Column '{col}' missing for splitting logic.")
            return

    grouped = input_df.groupby(['ZONA_EF', 'ESCUELA'])
    print(f"Found {len(grouped)} Zone/School combinations.")
    
    count = 0
    for (zona, escuela), group in grouped:
        zona_safe = sanitize_filename(zona)
        escuela_safe = sanitize_filename(escuela)
        
        output_dir = os.path.join(base_output_dir, f"ZONA_{zona_safe}", escuela_safe)
        os.makedirs(output_dir, exist_ok=True)
        
        output_filename = os.path.join(output_dir, f"{escuela_safe}.xlsx")
        
        group.to_excel(output_filename, index=False)
        count += 1
        
    print(f"Generated {count} school files in {base_output_dir}")

def main():
    parser = argparse.ArgumentParser(description="Process Nutritional Data (Filter & Split)")
    parser.add_argument('--input', default="../data/raw/IMC FEDERAL.xlsx", help="Input Excel file path")
    parser.add_argument('--output-dir', default="../data/processed", help="Output directory for processed files")
    
    args = parser.parse_args()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    if not os.path.isabs(args.input):
        alt_input = os.path.join(script_dir, args.input)
        if not os.path.exists(args.input) and os.path.exists(alt_input):
            args.input = alt_input

    if not os.path.exists(args.input):
        print(f"Error: Input file not found at {args.input}")
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)
    filtered_file_path = os.path.join(args.output_dir, "IMC_FILTERED.xlsx")
    filtered_csv_path = os.path.join(args.output_dir, "IMC_FILTERED.csv")
    
    filtered_df = filter_data(args.input, filtered_file_path)
    
    if filtered_df is not None:
        print(f"Saving filtered data to CSV: {filtered_csv_path}")
        filtered_df.to_csv(filtered_csv_path, index=False, encoding='utf-8-sig')
    
    if filtered_df is not None:
        split_data(filtered_df, os.path.join(args.output_dir, "Desagregado"))

if __name__ == "__main__":
    main()
