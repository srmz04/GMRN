
import os
import sys

# Ensure src is in the path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__)))

from nutritional_app import NutritionalAnalyzer

def generate_report():
    input_file = os.path.abspath('data/processed/NUEVO_IDEAL/AMADO_NERVO.xlsx')
    output_file = os.path.abspath('data/processed/NUEVO_IDEAL/AMADO_NERVO_reporte.pdf')
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return

    print(f"Initializing Analyzer...")
    analyzer = NutritionalAnalyzer()
    
    print(f"Loading data from {input_file}...")
    success, msg = analyzer.load_children_data(input_file)
    
    if not success:
        print(f"Failed to load data: {msg}")
        return

    print(f"Generating report to {output_file}...")
    # Use multiprocessing for speed, though for one school it might not be strictly necessary, 
    # but good to test the feature.
    success, msg = analyzer.generate_report(output_file, use_multiprocessing=True)
    
    if success:
        print(f"Report generated successfully: {msg}")
    else:
        print(f"Failed to generate report: {msg}")

if __name__ == "__main__":
    generate_report()
