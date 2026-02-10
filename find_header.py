
import pandas as pd

def find_header():
    file_path = 'data/raw/IMC FEDERAL.xlsx'
    xls = pd.ExcelFile(file_path)
    
    for sheet_name in xls.sheet_names:
        print(f"--- Checking Sheet: {sheet_name} ---")
        try:
            # Read first 20 rows
            df = pd.read_excel(xls, sheet_name=sheet_name, header=None, nrows=20)
            print("First 5 rows:")
            print(df.head(5))
            
            # Search for 'NOMBRE' or 'ESCUELA'
            for idx, row in df.iterrows():
                row_str = row.astype(str).str.upper().tolist()
                if any('NOMBRE' in s for s in row_str) or any('ESCUELA' in s for s in row_str):
                    print(f"Possible header found at row {idx}:")
                    print(row.tolist())
                    return sheet_name, idx
        except Exception as e:
            print(f"Error reading {sheet_name}: {e}")

    return None, None

if __name__ == "__main__":
    sheet, row = find_header()
    if sheet:
        print(f"Loading data from '{sheet}' starting at row {row}...")
        df = pd.read_excel('data/raw/IMC FEDERAL.xlsx', sheet_name=sheet, header=row)
        print("Columns found:", df.columns.tolist())
        
        # Check for Nuevo Ideal
        print("Searching for 'Nuevo Ideal'...")
        # Check in string columns
        found = False
        for col in df.select_dtypes(include=['object']).columns:
             if df[col].astype(str).str.contains('Nuevo Ideal', case=False, na=False).any():
                print(f"Found 'Nuevo Ideal' in column '{col}'")
                print(df[df[col].astype(str).str.contains('Nuevo Ideal', case=False, na=False)][col].unique())
                found = True
        
        if not found:
            print("'Nuevo Ideal' not found in any column. checking unique values in 'ZONA_EF' and 'ESCUELA' if they exist")
            if 'ZONA_EF' in df.columns:
                 print("Unique ZONA_EF:", df['ZONA_EF'].unique()[:10])
            if 'ESCUELA' in df.columns:
                 print("Unique ESCUELA sample:", df['ESCUELA'].unique()[:10])

    else:
        print("Could not find a valid header row.")
