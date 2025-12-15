import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import sys

class NutritionalAnalyzer:
    def __init__(self):
        self.df_oms_boys = None
        self.df_oms_girls = None
        self.df_ninos = None
        self.z_labels = {
            "SD3neg": "Desnutrición severa (-3 SD)",
            "SD2neg": "Desnutrición moderada (-2 SD)",
            "SD0": "Peso normal (0 SD)",
            "SD2": "Sobrepeso (+2 SD)",
            "SD3": "Obesidad (+3 SD)"
        }
        
        # Get the directory where the script is located
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load WHO files automatically
        self._load_who_files()

    def _load_excel_safe(self, filepath):
        """Helper to load Excel file even if it is open by another process."""
        import shutil
        import tempfile
        
        try:
            # Create a temporary file
            fd, temp_path = tempfile.mkstemp(suffix='.xlsx')
            os.close(fd)
            # Copy the original file to the temp path
            shutil.copy2(filepath, temp_path)
            # Read from the temp file
            df = pd.read_excel(temp_path)
            # Clean up
            os.remove(temp_path)
            return df, None
        except Exception as e:
            # Try reading directly if copy fails (fallback)
            try:
                return pd.read_excel(filepath), None
            except Exception as e2:
                return None, str(e)

    def _load_who_files(self):
        """Load WHO reference files for boys and girls."""
        boys_file = os.path.join(self.script_dir, "..", "data", "references", "bmi-boys-z-who-2007-exp.xlsx")
        girls_file = os.path.join(self.script_dir, "..", "data", "references", "bmi-girls-z-who-2007-exp.xlsx")
        
        try:
            self.df_oms_boys, error = self._load_excel_safe(boys_file)
            if error:
                raise Exception(f"Error al cargar archivo de niños: {error}")
            
            self.df_oms_girls, error = self._load_excel_safe(girls_file)
            if error:
                raise Exception(f"Error al cargar archivo de niñas: {error}")
            
            return True, "Archivos OMS cargados exitosamente."
        except Exception as e:
            return False, f"Error al cargar archivos OMS: {e}"

    def load_children_data(self, filepath):
        try:
            if filepath.endswith('.csv'):
                # Try to detect delimiter automatically
                try:
                    # First, try reading with tab separator (common in exports)
                    self.df_ninos = pd.read_csv(filepath, sep='\t')
                except:
                    # If that fails, try with comma separator
                    self.df_ninos = pd.read_csv(filepath)
            else:
                self.df_ninos, error = self._load_excel_safe(filepath)
                if error:
                    return False, f"Error al leer archivo Menores: {error}"
            
            # Check for required columns
            required_cols = ['NOMBRE_ALU', 'MESES', 'IMC']
            missing = [col for col in required_cols if col not in self.df_ninos.columns]
            if missing:
                return False, f"Faltan columnas en archivo Menores: {missing}"
            
            # Check if GÉNERO column exists
            if 'GÉNERO' not in self.df_ninos.columns:
                return False, "La columna 'GÉNERO' es requerida (MASCULINO o FEMENINO)"
            
            return True, f"Archivo Menores cargado exitosamente ({len(self.df_ninos)} registros)."
        except Exception as e:
            return False, f"Error al leer archivo Menores: {e}"

    def generate_report(self, output_filename="reporte_nutricional.pdf", progress_callback=None):
        if self.df_oms_boys is None or self.df_oms_girls is None or self.df_ninos is None:
            return False, "Datos no cargados completamente."

        try:
            with PdfPages(output_filename) as pdf:
                total = len(self.df_ninos)
                for index, menor in self.df_ninos.iterrows():
                    if progress_callback:
                        progress_callback(index + 1, total)
                    
                    # Select the appropriate WHO data based on gender
                    genero = str(menor.get('GÉNERO', '')).strip().upper()
                    # Accept both M/F and MASCULINO/FEMENINO
                    if genero in ['M', 'MASCULINO']:
                        df_oms = self.df_oms_boys
                    elif genero in ['F', 'FEMENINO']:
                        df_oms = self.df_oms_girls
                    else:
                        # Skip this record if gender is invalid
                        continue
                    
                    plt.figure(figsize=(11, 8.5))
                    plt.suptitle(
                        "SERVICIOS DE SALUD DE DURANGO\nDIRECCIÓN DE SALUD PÚBLICA\nEvaluación Nutricional Escolares",
                        fontsize=14, fontweight='bold', y=0.97
                    )

                    # Plot WHO curves
                    for z_col, label in self.z_labels.items():
                        if z_col in df_oms.columns:
                            plt.plot(df_oms['Month'], df_oms[z_col], linestyle='--', color='gray', zorder=1, linewidth=0.8)
                            
                            # Label placement
                            label_x_pos = df_oms['Month'].iloc[int(len(df_oms['Month']) * 0.85)]
                            label_y_val = df_oms.loc[df_oms['Month'] == label_x_pos, z_col].values
                            if len(label_y_val) > 0:
                                plt.text(label_x_pos + 2, label_y_val[0], label, fontsize=8, ha='left', va='center', color='dimgray')

                    # Plot Child data
                    plt.scatter(menor["MESES"], menor["IMC"], color='red', zorder=5, s=60, label="IMC del Menor")
                    plt.legend(loc='upper left', fontsize=9, frameon=True, facecolor='white', framealpha=0.7)

                    # Build concatenated info
                    grado = str(menor.get('GRADO', '')).strip()
                    grupo = str(menor.get('GRUPO', '')).strip()
                    cct = str(menor.get('CCT', '')).strip()
                    zona_ef = str(menor.get('ZONA_EF', '')).strip()
                    nombre_prof = str(menor.get('NOMBRE_PROF', '')).strip()
                    escuela = str(menor.get('ESCUELA', '')).strip()
                    
                    # Create concatenated info line
                    extra_info = f"{grado}° {grupo} | CCT: {cct} | Zona EF: {zona_ef} | Prof: {nombre_prof}"
                    if escuela:
                        extra_info = f"{escuela} | " + extra_info
                    
                    # Info text with name and basic data
                    info_menor = f"Nombre: {menor['NOMBRE_ALU']}   |   Edad: {menor['MESES']} meses   |   IMC: {menor['IMC']:.2f} Kg/m²"
                    plt.figtext(0.5, 0.04, info_menor, fontsize=10, ha="center", fontweight="normal",
                                bbox=dict(boxstyle="round,pad=0.3", fc="lightgray", ec="black", lw=0.5, alpha=0.5))
                    
                    # Additional info line below
                    plt.figtext(0.5, 0.01, extra_info, fontsize=8, ha="center", fontweight="normal", style='italic',
                                bbox=dict(boxstyle="round,pad=0.25", fc="lightyellow", ec="gray", lw=0.5, alpha=0.6))

                    # Axes setup
                    plt.xlabel("Edad (meses)", fontsize=10)
                    plt.ylabel("IMC (Kg/m²)", fontsize=10)
                    plt.grid(True, linestyle=':', alpha=0.6, linewidth=0.5)
                    
                    min_val_oms = df_oms[[col for col in self.z_labels.keys() if col in df_oms.columns]].min().min()
                    max_val_oms = df_oms[[col for col in self.z_labels.keys() if col in df_oms.columns]].max().max()
                    
                    plt.xlim(df_oms['Month'].min(), df_oms['Month'].max())
                    plt.ylim(max(10, min_val_oms - 2), min(38, max_val_oms + 2))
                    plt.tick_params(axis='both', which='major', labelsize=9)
                    
                    pdf.savefig(bbox_inches='tight')
                    plt.close()

            return True, f"Reporte generado: {output_filename}"
        except Exception as e:
            return False, f"Error generando PDF: {e}"

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Reportes Nutricionales - Batch")
        self.root.geometry("700x550")
        
        self.analyzer = NutritionalAnalyzer()
        self.selected_files = []

        self.create_widgets()

    def create_widgets(self):
        # Header
        tk.Label(self.root, text="Generador de Reportes de IMC (Lotes)", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Info label
        info_text = "Archivos OMS cargados. Seleccione archivos o carpetas para procesar."
        tk.Label(self.root, text=info_text, font=("Arial", 10), fg="green").pack(pady=5)

        # File Selection Frame
        frame_files = tk.Frame(self.root)
        frame_files.pack(pady=10, padx=20, fill="x")

        # Buttons
        tk.Button(frame_files, text="Seleccionar Archivos", command=self.select_files, font=("Arial", 10), width=20).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(frame_files, text="Seleccionar Carpeta", command=self.select_folder, font=("Arial", 10), width=20).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(frame_files, text="Limpiar Lista", command=self.clear_list, font=("Arial", 10), width=15).grid(row=0, column=2, padx=5, pady=5)

        # Listbox for files
        tk.Label(self.root, text="Archivos a procesar:", anchor="w").pack(padx=20, fill="x")
        self.listbox_files = tk.Listbox(self.root, height=8, selectmode=tk.EXTENDED)
        self.listbox_files.pack(padx=20, pady=5, fill="x")
        
        # Scrollbar for listbox
        scrollbar = tk.Scrollbar(self.listbox_files)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox_files.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox_files.yview)

        # Generate Button
        self.btn_generate = tk.Button(self.root, text="Generar Reportes PDF", command=self.process_batch, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), state="disabled")
        self.btn_generate.pack(pady=15)

        # Log Area
        tk.Label(self.root, text="Registro de Actividad:").pack(anchor="w", padx=20)
        self.log_area = scrolledtext.ScrolledText(self.root, height=10, state="disabled")
        self.log_area.pack(padx=20, pady=5, fill="both", expand=True)

    def log(self, message):
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")

    def select_files(self):
        filenames = filedialog.askopenfilenames(filetypes=[("Excel/CSV files", "*.xlsx *.xls *.csv")])
        if filenames:
            for f in filenames:
                if f not in self.selected_files:
                    self.selected_files.append(f)
                    self.listbox_files.insert(tk.END, os.path.basename(f))
            self.update_button_state()

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            count = 0
            for root_dir, dirs, files in os.walk(folder):
                for file in files:
                    if file.endswith(('.xlsx', '.xls', '.csv')) and not file.startswith('~$'):
                        full_path = os.path.join(root_dir, file)
                        if full_path not in self.selected_files:
                            self.selected_files.append(full_path)
                            self.listbox_files.insert(tk.END, os.path.basename(full_path))
                            count += 1
            self.log(f"Se agregaron {count} archivos de la carpeta.")
            self.update_button_state()

    def clear_list(self):
        self.selected_files = []
        self.listbox_files.delete(0, tk.END)
        self.update_button_state()

    def update_button_state(self):
        if self.selected_files:
            self.btn_generate.config(state="normal")
        else:
            self.btn_generate.config(state="disabled")

    def process_batch(self):
        self.btn_generate.config(state="disabled")
        self.log("--- Iniciando procesamiento por lotes ---")
        self.root.update()
        
        success_count = 0
        error_count = 0
        
        for i, filepath in enumerate(self.selected_files):
            filename = os.path.basename(filepath)
            self.log(f"[{i+1}/{len(self.selected_files)}] Procesando: {filename}")
            self.root.update()
            
            # Load data
            success, msg = self.analyzer.load_children_data(filepath)
            if not success:
                self.log(f"  Error cargando: {msg}")
                error_count += 1
                continue
                
            # Generate report
            # Output name: same as input but with .pdf extension, in the same folder
            base_name = os.path.splitext(filepath)[0]
            output_pdf = f"{base_name}_reporte.pdf"
            
            success, msg = self.analyzer.generate_report(output_pdf)
            if success:
                self.log(f"  OK: Reporte generado.")
                success_count += 1
            else:
                self.log(f"  Error generando PDF: {msg}")
                error_count += 1
            
            self.root.update()

        self.log(f"--- Finalizado: {success_count} éxitos, {error_count} errores ---")
        messagebox.showinfo("Proceso Completado", f"Se procesaron {len(self.selected_files)} archivos.\nÉxitos: {success_count}\nErrores: {error_count}")
        self.btn_generate.config(state="normal")

if __name__ == "__main__":
    # If arguments are passed (for headless testing), run without GUI
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Running in test mode...")
        analyzer = NutritionalAnalyzer()
        success, msg = analyzer.load_who_data("dummy_who.xlsx")
        print(msg)
        if not success: sys.exit(1)
        
        success, msg = analyzer.load_children_data("dummy_children.csv")
        print(msg)
        if not success: sys.exit(1)
        
        success, msg = analyzer.generate_report("test_report.pdf")
        print(msg)
        if not success: sys.exit(1)
        print("Test completed successfully.")
    else:
        root = tk.Tk()
        app = AppGUI(root)
        root.mainloop()
