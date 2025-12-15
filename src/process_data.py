import pandas as pd
import os
import re
import shutil
import tempfile
import argparse
import sys

def sanitize_filename(name):
    """Clean filename to be valid."""
    return re.sub(r'[<>:"/\\|?*]', '_', str(name)).strip()

def filter_data(input_path, output_path):
    """
    Filters data: Keep only records with PERCENTILES < 15 or > 85.1
    """
    print(f"--- Filtering Data ---")
    print(f"Reading: {input_path}")
    
    try:
        # Read specifically Hoja1 where raw data resides
        df = pd.read_excel(input_path, sheet_name='Hoja1')
        
        # Ensure PERCENTILES is numeric
        if 'PERCENTILES' in df.columns:
            df['PERCENTILES'] = pd.to_numeric(df['PERCENTILES'], errors='coerce')
            
            # Filter: Below 15 OR Above 85.1
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
    """
    Splits the dataframe by ZONA_EF and ESCUELA.
    """
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
        # Clean names
        zona_safe = sanitize_filename(zona)
        escuela_safe = sanitize_filename(escuela)
        
        # Create structure: base_dir / ZONA / ESCUELA
        output_dir = os.path.join(base_output_dir, f"ZONA_{zona_safe}", escuela_safe)
        os.makedirs(output_dir, exist_ok=True)
        
        # File name
        output_filename = os.path.join(output_dir, f"{escuela_safe}.xlsx")
        
        # Save
        group.to_excel(output_filename, index=False)
        count += 1
        
    print(f"Generated {count} school files in {base_output_dir}")

def main():
    parser = argparse.ArgumentParser(description="Process Nutritional Data (Filter & Split)")
    parser.add_argument('--input', default="../data/raw/IMC FEDERAL.xlsx", help="Input Excel file path")
    parser.add_argument('--output-dir', default="../data/processed", help="Output directory for processed files")
    
    args = parser.parse_args()
    
    # Absolutize paths relative to this script if they are relative
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Handle default paths being relative to where script is run, generally we want relative to script_dir if hardcoded defaults
    # But since we run from root usually, let's just ensure we find the file.
    if not os.path.isabs(args.input):
        # Try finding it relative to script directory if not found in cwd
        alt_input = os.path.join(script_dir, args.input)
        if not os.path.exists(args.input) and os.path.exists(alt_input):
            args.input = alt_input

    if not os.path.exists(args.input):
        print(f"Error: Input file not found at {args.input}")
        sys.exit(1)

    # Output for intermediate filtered file
    os.makedirs(args.output_dir, exist_ok=True)
    filtered_file_path = os.path.join(args.output_dir, "IMC_FILTERED.xlsx")
    filtered_csv_path = os.path.join(args.output_dir, "IMC_FILTERED.csv")
    
    # 1. Filter
    filtered_df = filter_data(args.input, filtered_file_path)
    
    if filtered_df is not None:
        print(f"Saving filtered data to CSV: {filtered_csv_path}")
        filtered_df.to_csv(filtered_csv_path, index=False, encoding='utf-8-sig') # utf-8-sig for Excel compatibility
    
    # 2. Split (using the dataframe in memory)
    if filtered_df is not None:
        split_data(filtered_df, os.path.join(args.output_dir, "Desagregado"))

if __name__ == "__main__":
    main()
