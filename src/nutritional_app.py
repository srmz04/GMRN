import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import sys
import multiprocessing as mp
from functools import partial
from typing import Optional, Tuple, List, Dict, Any
import tempfile
import shutil

from logger import get_logger

plt.ioff()


class OMSCache:
    def __init__(self, df_boys: pd.DataFrame, df_girls: pd.DataFrame, z_labels: dict):
        self.df_boys = df_boys
        self.df_girls = df_girls
        self.z_labels = z_labels
        
        self.z_cols_boys = [col for col in z_labels.keys() if col in df_boys.columns]
        self.z_cols_girls = [col for col in z_labels.keys() if col in df_girls.columns]
        
        self.min_val_boys = df_boys[self.z_cols_boys].min().min()
        self.max_val_boys = df_boys[self.z_cols_boys].max().max()
        self.min_val_girls = df_girls[self.z_cols_girls].min().min()
        self.max_val_girls = df_girls[self.z_cols_girls].max().max()
        
        self.month_min = df_boys['Month'].min()
        self.month_max = df_boys['Month'].max()
        
        self.label_x_pos = df_boys['Month'].iloc[int(len(df_boys['Month']) * 0.85)]
    
    def get_for_gender(self, genero: str):
        genero = str(genero).strip().upper()
        if genero in ['M', 'MASCULINO']:
            return self.df_boys, self.z_cols_boys, self.min_val_boys, self.max_val_boys
        elif genero in ['F', 'FEMENINO']:
            return self.df_girls, self.z_cols_girls, self.min_val_girls, self.max_val_girls
        else:
            return None, [], 0, 0





def gen_referencia_page(menor_data: dict, logo_data=None):
    import io
    from datetime import datetime
    
    fig = plt.figure(figsize=(8.27, 11.69))
    
    if logo_data is not None:
        logo_ax = fig.add_axes([0, 0.88, 1, 0.12])
        logo_ax.imshow(logo_data, aspect='equal')
        logo_ax.axis('off')
        
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    nombre = str(menor_data.get('NOMBRE_ALU', '')).strip()
    escuela = str(menor_data.get('ESCUELA', '')).strip()
    cct = str(menor_data.get('CCT', '')).strip()
    zona_ef = str(menor_data.get('ZONA_EF', '')).strip()
    grado = str(menor_data.get('GRADO', '')).strip()
    grupo = str(menor_data.get('GRUPO', '')).strip()
    
    fecha_nac = menor_data.get('FECHA_NAC', '')
    if isinstance(fecha_nac, datetime):
        fecha_nac_str = fecha_nac.strftime('%d/%m/%Y')
    else:
        fecha_nac_str = str(fecha_nac).split(' ')[0] if fecha_nac else ''
    
    meses = menor_data.get('MESES', 0)
    try:
        meses_int = int(meses)
        años = meses_int // 12
        meses_resto = meses_int % 12
    except:
        años = 0
        meses_resto = meses
        
    fecha_tam = menor_data.get('FECHA_TAM', '')
    if isinstance(fecha_tam, datetime):
        fecha_tam_str = fecha_tam.strftime('%d/%m/%Y')
    else:
        fecha_tam_str = str(fecha_tam).split(' ')[0] if fecha_tam else ''
    
    peso = menor_data.get('PESO_Kg', '')
    talla = menor_data.get('TALLA_Mts', '')
    imc = menor_data.get('IMC', 0)
    diagnostico = str(menor_data.get('INTERPRETACIÓN', menor_data.get('INTERPRETACION', ''))).strip()
    
    def draw_field(label, value, x, y, x_value, line_end=50):
        ax.text(x, y, f"- {label}:", fontsize=11, ha='left', va='center')
        ax.text(x_value, y, str(value), fontsize=11, ha='left', va='center', fontweight='bold')
        ax.axhline(y=y-1, xmin=x_value/100, xmax=line_end/100, color='gray', linewidth=0.3)
    
    y_pos = 84
    ax.text(3, y_pos, "Informacion del Paciente", fontsize=14, fontweight='bold', ha='left', va='center')
    y_pos -= 4
    
    draw_field("Nombre completo del menor", nombre[:40], 3, y_pos, 35, 90)
    y_pos -= 3
    
    ax.text(3, y_pos, "- Fecha de nacimiento:", fontsize=11, ha='left', va='center')
    ax.text(28, y_pos, fecha_nac_str, fontsize=11, ha='left', va='center', fontweight='bold')
    ax.text(45, y_pos, "Edad:", fontsize=11, ha='left', va='center')
    ax.text(52, y_pos, f"{años}", fontsize=11, ha='left', va='center', fontweight='bold')
    ax.text(56, y_pos, "años", fontsize=11, ha='left', va='center')
    ax.text(64, y_pos, f"{meses_resto}", fontsize=11, ha='left', va='center', fontweight='bold')
    ax.text(68, y_pos, "meses", fontsize=11, ha='left', va='center')
    y_pos -= 3
    
    sexo = str(menor_data.get('GÉNERO', menor_data.get('SEXO', ''))).strip()
    curp = str(menor_data.get('CURP', '')).strip()
    
    ax.text(3, y_pos, "- Sexo:", fontsize=11, ha='left', va='center')
    ax.text(12, y_pos, sexo, fontsize=11, ha='left', va='center', fontweight='bold')
    
    ax.text(35, y_pos, "- CURP:", fontsize=11, ha='left', va='center')
    ax.text(45, y_pos, curp, fontsize=11, ha='left', va='center', fontweight='bold')
    y_pos -= 6
    
    ax.text(3, y_pos, "Informacion de la Escuela", fontsize=14, fontweight='bold', ha='left', va='center')
    y_pos -= 4
    
    draw_field("Nombre de la escuela", escuela[:35], 3, y_pos, 30, 90)
    y_pos -= 3
    draw_field("Clave escolar", cct, 3, y_pos, 20, 45)
    y_pos -= 3
    draw_field("Zona escolar", zona_ef, 3, y_pos, 18, 40)
    y_pos -= 3
    draw_field("Grado y grupo", f"{grado} {grupo}", 3, y_pos, 20, 40)
    y_pos -= 6
    
    ax.text(3, y_pos, "Somatometria", fontsize=14, fontweight='bold', ha='left', va='center')
    y_pos -= 4
    
    draw_field("Fecha del tamizaje", fecha_tam_str, 3, y_pos, 22, 45)
    ax.text(45, y_pos, "- Peso:", fontsize=11, ha='left', va='center')
    ax.text(55, y_pos, f"{peso}", fontsize=11, ha='left', va='center', fontweight='bold')
    ax.text(63, y_pos, "kg", fontsize=11, ha='left', va='center')
    ax.text(70, y_pos, "- Talla:", fontsize=11, ha='left', va='center')
    try:
        talla_cm = float(talla) * 100 if float(talla) < 3 else float(talla)
        ax.text(80, y_pos, f"{talla_cm:.0f}", fontsize=11, ha='left', va='center', fontweight='bold')
    except:
        ax.text(80, y_pos, f"{talla}", fontsize=11, ha='left', va='center', fontweight='bold')
    ax.text(86, y_pos, "cm", fontsize=11, ha='left', va='center')
    y_pos -= 3
    
    try:
        imc_formatted = f"{float(imc):.2f}"
    except:
        imc_formatted = str(imc)
    draw_field("Indice de Masa Corporal (IMC)", imc_formatted, 3, y_pos, 35, 55)
    y_pos -= 6
    
    y_pos -= 6
    
    ax.text(3, y_pos, "Recomendaciones y Seguimiento", fontsize=14, fontweight='bold', ha='left', va='center')
    y_pos -= 4
    
    import textwrap
    mensaje_recomendacion = (
        "Se sugiere acudir a una valoracion clinica en su Unidad de Salud. "
        "Con base en los datos recabados, es valioso realizar este seguimiento preventivo "
        "para asegurar que el desarrollo de su hijo(a) sea el optimo y descartar situaciones "
        "que pudieran afectar su salud a largo plazo."
    )
    
    lines = textwrap.wrap(mensaje_recomendacion, width=95)
    for line in lines:
        ax.text(3, y_pos, line, fontsize=11, ha='left', va='center')
        y_pos -= 2.5
        
    y_pos -= 3
    
    recomendaciones = [
        "Acudir a la Unidad de Salud antes del: _______________________________",
        "Llevar Cartilla Nacional de Salud",
        "Llevar el carnet de seguimiento del menor",
        "Informar a la escuela sobre la asistencia y seguimiento recibido",
        "Cualquier duda o comentario, comunicarse al 618 137 7190 (ext. 77305)"
    ]
    
    for rec in recomendaciones:
        ax.text(5, y_pos, f"- {rec}", fontsize=11, ha='left', va='center')
        y_pos -= 3
    
    buf = io.BytesIO()
    fig.savefig(buf, format='pdf', dpi=150)
    plt.close(fig)
    buf.seek(0)
    
    return buf.getvalue()


def gen_cartilla_page(menor_data: dict, logo_data=None):
    import io
    from datetime import datetime
    
    fig = plt.figure(figsize=(11.69, 8.27))
    
    if logo_data is not None:
        logo_ax = fig.add_axes([0, 0.85, 1, 0.12])
        logo_ax.imshow(logo_data, aspect='equal') 
        logo_ax.axis('off')

    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    ax.text(50, 82, "CARTILLA DE SALUD ESCOLAR COMPLEMENTARIA",
            fontsize=16, fontweight='bold', ha='center', va='top',
            color='#8B0000')
    
    ax.axhline(y=78, xmin=0.03, xmax=0.97, color='gray', linewidth=0.5)
    
    ax.axvline(x=50, ymin=0.05, ymax=0.78, color='gray', linewidth=0.8)
    
    nombre = str(menor_data.get('NOMBRE_ALU', '')).strip()
    derechohabiencia = str(menor_data.get('DERECHOHABIENCIA', 'NO TIENE')).strip()
    escuela = str(menor_data.get('ESCUELA', '')).strip()
    cct = str(menor_data.get('CCT', '')).strip()
    grado = str(menor_data.get('GRADO', '')).strip()
    grupo = str(menor_data.get('GRUPO', '')).strip()
    
    fecha_nac = menor_data.get('FECHA_NAC', '')
    if isinstance(fecha_nac, datetime):
        fecha_nac_str = fecha_nac.strftime('%d/%m/%Y')
    else:
        fecha_nac_str = str(fecha_nac).split(' ')[0] if fecha_nac else ''
    
    meses = menor_data.get('MESES', 0)
    try:
        meses = int(meses)
        años = meses // 12
        meses_resto = meses % 12
        edad_str = f"{años} años, {meses_resto} meses"
    except:
        edad_str = f"{meses} meses"
    
    fecha_tam = menor_data.get('FECHA_TAM', '')
    if isinstance(fecha_tam, datetime):
        fecha_tam_str = fecha_tam.strftime('%d/%m/%Y')
    else:
        fecha_tam_str = str(fecha_tam).split(' ')[0] if fecha_tam else ''
    
    peso = menor_data.get('PESO_Kg', '')
    talla = menor_data.get('TALLA_Mts', '')
    imc = menor_data.get('IMC', 0)
    diagnostico = str(menor_data.get('INTERPRETACIÓN', menor_data.get('INTERPRETACION', ''))).strip()
    
    y_pos = 72
    line_height = 7
    x_label = 3
    x_value = 22
    
    def draw_field_left(label, value, y, max_chars=30):
        ax.text(x_label, y, f"{label}:", fontsize=9, ha='left', va='center')
        display_value = str(value)[:max_chars] if len(str(value)) > max_chars else str(value)
        ax.text(x_value, y, display_value, fontsize=9, ha='left', va='center', fontweight='bold')
        ax.axhline(y=y-1.5, xmin=x_value/100, xmax=0.45, color='gray', linewidth=0.3)
    
    draw_field_left("Nombre y apellidos", nombre, y_pos, 25)
    y_pos -= line_height
    
    draw_field_left("Derechohabiencia", derechohabiencia, y_pos)
    y_pos -= line_height
    
    escuela_display = f"{escuela[:18]}..." if len(escuela) > 18 else escuela
    draw_field_left("Nombre escuela y clave", f"{escuela_display} ({cct})", y_pos, 28)
    y_pos -= line_height
    
    draw_field_left("Grado escolar", f"{grado} {grupo}", y_pos)
    y_pos -= line_height
    
    draw_field_left("Fecha de Nacimiento", fecha_nac_str, y_pos)
    y_pos -= line_height
    
    draw_field_left("Edad", edad_str, y_pos)
    y_pos -= line_height
    
    ax.text(x_label, y_pos, "Fecha Tam:", fontsize=9, ha='left', va='center')
    ax.text(12, y_pos, fecha_tam_str, fontsize=8, ha='left', va='center', fontweight='bold')
    
    ax.text(22, y_pos, "Peso:", fontsize=9, ha='left', va='center')
    ax.text(29, y_pos, f"{peso}", fontsize=9, ha='left', va='center', fontweight='bold')
    
    ax.text(36, y_pos, "Talla:", fontsize=9, ha='left', va='center')
    ax.text(43, y_pos, f"{talla}", fontsize=9, ha='left', va='center', fontweight='bold')
    y_pos -= line_height
    
    try:
        imc_formatted = f"{float(imc):.2f}"
    except:
        imc_formatted = str(imc)
    draw_field_left("IMC", imc_formatted, y_pos)
    y_pos -= line_height
    
    draw_field_left("Diagnostico", diagnostico, y_pos)
    y_pos -= line_height
    
    ax.text(x_label, y_pos, "Cuenta con Cartilla Nacional de Salud?", fontsize=8, ha='left', va='center')
    ax.add_patch(plt.Rectangle((36, y_pos-1.5), 4, 3.5, fill=False, edgecolor='black', linewidth=0.5))
    ax.text(38, y_pos, "SI", fontsize=8, ha='center', va='center')
    ax.add_patch(plt.Rectangle((42, y_pos-1.5), 4, 3.5, fill=False, edgecolor='black', linewidth=0.5))
    ax.text(44, y_pos, "NO", fontsize=8, ha='center', va='center')
    y_pos -= line_height
    
    ax.text(x_label, y_pos, "Referido a:", fontsize=9, ha='left', va='center')
    ax.axhline(y=y_pos-1.5, xmin=0.12, xmax=0.45, color='gray', linewidth=0.3)
    
    ax.text(75, 75, "CONSULTAS", fontsize=12, fontweight='bold', ha='center', va='center')
    
    table_x = 53
    table_y = 70
    
    col_headers = ["SERVICIO\n(Medicina,\nNutricion,\nPsicologia)", "FECHA", "HORA", "NOMBRE DE\nQUIEN ATENDIO"]
    col_widths = [12, 9, 7, 16]
    col_x = [table_x]
    for w in col_widths[:-1]:
        col_x.append(col_x[-1] + w)
    
    header_height = 10
    row_height = 7
    
    for header, x, w in zip(col_headers, col_x, col_widths):
        ax.add_patch(plt.Rectangle((x, table_y - header_height), w, header_height, 
                                    fill=True, facecolor='#e0e0e0', edgecolor='black', linewidth=0.5))
        ax.text(x + w/2, table_y - header_height/2, header, fontsize=6, 
                ha='center', va='center', linespacing=0.85)
    
    for row in range(8):
        row_y = table_y - header_height - (row + 1) * row_height
        for x, w in zip(col_x, col_widths):
            ax.add_patch(plt.Rectangle((x, row_y), w, row_height, 
                                        fill=False, edgecolor='black', linewidth=0.3))
    
    buf = io.BytesIO()
    fig.savefig(buf, format='pdf', dpi=150)
    plt.close(fig)
    buf.seek(0)
    
    return buf.getvalue()


def gen_single_page(menor_data: dict, oms_cache_data: dict, z_labels: dict, logo_data=None):
    import io
    
    genero = str(menor_data.get('GÉNERO', '')).strip().upper()
    
    if genero in ['M', 'MASCULINO']:
        df_oms = pd.DataFrame(oms_cache_data['boys'])
        z_cols = oms_cache_data['z_cols_boys']
        min_val = oms_cache_data['min_val_boys']
        max_val = oms_cache_data['max_val_boys']
    elif genero in ['F', 'FEMENINO']:
        df_oms = pd.DataFrame(oms_cache_data['girls'])
        z_cols = oms_cache_data['z_cols_girls']
        min_val = oms_cache_data['min_val_girls']
        max_val = oms_cache_data['max_val_girls']
    else:
        return None
    
    fig = plt.figure(figsize=(11.69, 8.27))
    
    plt.subplots_adjust(top=0.82)
    
    ax = fig.add_subplot(111)
    
    if logo_data is not None:
        logo_ax = fig.add_axes([0, 0.85, 1, 0.15])
        logo_ax.imshow(logo_data, aspect='equal') 
        logo_ax.axis('off')
        
    plt.sca(ax)
    
    label_x_pos = oms_cache_data['label_x_pos']
    for z_col in z_cols:
        if z_col in df_oms.columns:
            plt.plot(df_oms['Month'], df_oms[z_col], linestyle='--', color='gray', zorder=1, linewidth=0.8)
            
            label_y_val = df_oms.loc[df_oms['Month'] == label_x_pos, z_col].values
            if len(label_y_val) > 0:
                plt.text(label_x_pos + 2, label_y_val[0], z_labels[z_col], 
                        fontsize=8, ha='left', va='center', color='dimgray')
    
    plt.scatter(menor_data["MESES"], menor_data["IMC"], color='red', zorder=5, s=60, label="IMC del Menor")
    plt.legend(loc='upper left', fontsize=9, frameon=True, facecolor='white', framealpha=0.7)
    
    grado = str(menor_data.get('GRADO', '')).strip()
    grupo = str(menor_data.get('GRUPO', '')).strip()
    cct = str(menor_data.get('CCT', '')).strip()
    zona_ef = str(menor_data.get('ZONA_EF', '')).strip()
    nombre_prof = str(menor_data.get('NOMBRE_PROF', '')).strip()
    escuela = str(menor_data.get('ESCUELA', '')).strip()
    
    extra_info = f"{grado} {grupo} | CCT: {cct} | Zona EF: {zona_ef} | Prof: {nombre_prof}"
    if escuela:
        extra_info = f"{escuela} | " + extra_info
    
    imc_value = menor_data['IMC']
    meses_total = menor_data['MESES']
    try:
        meses_int = int(meses_total)
        años = meses_int // 12
        meses_resto = meses_int % 12
        edad_display = f"{años} años, {meses_resto} meses"
    except:
        edad_display = f"{meses_total} meses"

    fecha_tam = menor_data.get('FECHA_TAM', '')
    if hasattr(fecha_tam, 'strftime'):
        fecha_tam_str = fecha_tam.strftime('%d/%m/%Y')
    else:
        fecha_tam_str = str(fecha_tam).split(' ')[0] if fecha_tam else ''

    info_menor = f"Nombre: {menor_data['NOMBRE_ALU']}   |   Edad: {edad_display}   |   IMC: {imc_value:.2f} Kg/m2   |   Fecha: {fecha_tam_str}"
    plt.figtext(0.5, 0.04, info_menor, fontsize=10, ha="center", fontweight="normal",
                bbox=dict(boxstyle="round,pad=0.3", fc="lightgray", ec="black", lw=0.5, alpha=0.5))
    
    plt.figtext(0.5, 0.01, extra_info, fontsize=8, ha="center", fontweight="normal", style='italic',
                bbox=dict(boxstyle="round,pad=0.25", fc="lightyellow", ec="gray", lw=0.5, alpha=0.6))
    
    oms_ref_text = "Estandares de crecimiento OMS (2007). Predichos: https://www.who.int/tools/growth-reference-data-for-5to19-years"
    plt.figtext(0.5, 0.075, oms_ref_text, fontsize=7, ha='center', style='italic', color='dimgray')
    
    plt.xlabel("Edad (meses)", fontsize=10)
    plt.ylabel("IMC (Kg/m2)", fontsize=10)
    plt.grid(True, linestyle=':', alpha=0.6, linewidth=0.5)
    
    plt.xlim(oms_cache_data['month_min'], oms_cache_data['month_max'])
    plt.ylim(max(10, min_val - 2), min(38, max_val + 2))
    plt.tick_params(axis='both', which='major', labelsize=9)
    
    buf = io.BytesIO()
    fig.savefig(buf, format='pdf')
    plt.close(fig)
    buf.seek(0)
    grafica_bytes = buf.getvalue()
    
    cartilla_bytes = gen_cartilla_page(menor_data, logo_data)
    
    referencia_bytes = gen_referencia_page(menor_data, logo_data)
    
    pages = [grafica_bytes]
    if cartilla_bytes:
        pages.append(cartilla_bytes)
    if referencia_bytes:
        pages.append(referencia_bytes)
    return pages


class NutritionalAnalyzer:
    def __init__(self):
        self.log = get_logger("nutritional_analyzer")
        self.df_oms_boys = None
        self.df_oms_girls = None
        self.df_ninos = None
        self.oms_cache = None
        
        self.z_labels = {
            "SD3neg": "Desnutricion severa (-3 SD)",
            "SD2neg": "Desnutricion moderada (-2 SD)",
            "SD0": "Peso normal (0 SD)",
            "SD2": "Sobrepeso (+2 SD)",
            "SD3": "Obesidad (+3 SD)"
        }
        
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        self._load_who_files()
    
    def _load_excel_safe(self, filepath: str):
        try:
            fd, temp_path = tempfile.mkstemp(suffix='.xlsx')
            os.close(fd)
            shutil.copy2(filepath, temp_path)
            df = pd.read_excel(temp_path)
            os.remove(temp_path)
            return df, None
        except Exception as e:
            try:
                return pd.read_excel(filepath), None
            except Exception as e2:
                return None, str(e)
    
    def _load_who_files(self):
        start = self.log.operation_start("cargar_archivos_oms")
        
        boys_file = os.path.join(self.script_dir, "..", "data", "references", "bmi-boys-z-who-2007-exp.xlsx")
        girls_file = os.path.join(self.script_dir, "..", "data", "references", "bmi-girls-z-who-2007-exp.xlsx")
        
        try:
            self.df_oms_boys, error = self._load_excel_safe(boys_file)
            if error:
                raise Exception(f"Error archivo ninos: {error}")
            
            self.df_oms_girls, error = self._load_excel_safe(girls_file)
            if error:
                raise Exception(f"Error archivo ninas: {error}")
            
            self.oms_cache = OMSCache(self.df_oms_boys, self.df_oms_girls, self.z_labels)
            
            self.log.operation_end("cargar_archivos_oms", start, success=True)
            return True, "Archivos OMS cargados exitosamente."
        except Exception as e:
            self.log.operation_end("cargar_archivos_oms", start, success=False, error=str(e))
            return False, f"Error al cargar archivos OMS: {e}"
    
    def load_children_data(self, filepath: str):
        start = self.log.operation_start("cargar_datos_menores", archivo=filepath)
        
        try:
            if filepath.endswith('.csv'):
                self.df_ninos = pd.read_csv(filepath)
            else:
                self.df_ninos, error = self._load_excel_safe(filepath)
                if error:
                    self.log.operation_end("cargar_datos_menores", start, success=False, error=error)
                    return False, f"Error al leer archivo Menores: {error}"
            
            required_cols = ['NOMBRE_ALU', 'MESES', 'IMC']
            missing = [col for col in required_cols if col not in self.df_ninos.columns]
            if missing:
                error_msg = f"Faltan columnas: {missing}"
                self.log.operation_end("cargar_datos_menores", start, success=False, error=error_msg)
                return False, error_msg
            
            if 'GÉNERO' not in self.df_ninos.columns:
                error_msg = "Columna 'GENERO' requerida"
                self.log.operation_end("cargar_datos_menores", start, success=False, error=error_msg)
                return False, error_msg
            
            records = len(self.df_ninos)
            self.log.operation_end("cargar_datos_menores", start, success=True, records=records)
            return True, f"Archivo cargado exitosamente ({records} registros)."
        
        except Exception as e:
            self.log.operation_end("cargar_datos_menores", start, success=False, error=str(e))
            return False, f"Error al leer archivo: {e}"
    
    def _prep_cache(self):
        return {
            'boys': self.df_oms_boys.to_dict('list'),
            'girls': self.df_oms_girls.to_dict('list'),
            'z_cols_boys': self.oms_cache.z_cols_boys,
            'z_cols_girls': self.oms_cache.z_cols_girls,
            'min_val_boys': self.oms_cache.min_val_boys,
            'max_val_boys': self.oms_cache.max_val_boys,
            'min_val_girls': self.oms_cache.min_val_girls,
            'max_val_girls': self.oms_cache.max_val_girls,
            'month_min': self.oms_cache.month_min,
            'month_max': self.oms_cache.month_max,
            'label_x_pos': self.oms_cache.label_x_pos,
        }
    
    def generate_report(self, output_filename: str = "reporte_nutricional.pdf", progress_callback=None, use_multiprocessing: bool = True, num_workers: int = None):
        if self.df_oms_boys is None or self.df_oms_girls is None or self.df_ninos is None:
            return False, "Datos no cargados completamente."
        
        total = len(self.df_ninos)
        start = self.log.operation_start("generar_reporte", 
                                          output=output_filename, 
                                          records=total,
                                          multiprocessing=use_multiprocessing)
        
        try:
            menores_data = self.df_ninos.to_dict('records')
            oms_cache_data = self._prep_cache()
            
            if use_multiprocessing and total > 10:
                if num_workers is None:
                    num_workers = max(1, mp.cpu_count() - 1)
                
                self.log.info(f"Usando {num_workers} workers para {total} registros")
                
                logo_path = "data/raw/ssd-seed.png"
                logo_data = None
                if os.path.exists(logo_path):
                    try:
                        logo_data = mpimg.imread(logo_path)
                        self.log.info(f"Logo cargado desde {logo_path}")
                    except Exception as e:
                        self.log.error(f"Error cargando logo: {e}")

                generate_func = partial(gen_single_page, oms_cache_data=oms_cache_data, z_labels=self.z_labels, logo_data=logo_data)
                
                with mp.Pool(num_workers) as pool:
                    pages = []
                    for i, result in enumerate(pool.imap(generate_func, menores_data)):
                        if result is not None:
                            pages.append(result)
                        if progress_callback:
                            progress_callback(i + 1, total)
                
                self._merge_pdfs(pages, output_filename)
                
            else:
                logo_path = "data/raw/ssd-seed.png"
                logo_data = None
                if os.path.exists(logo_path):
                    try:
                        logo_data = mpimg.imread(logo_path)
                    except:
                        pass

                pages = []
                for i, menor_data in enumerate(menores_data):
                    page_bytes = gen_single_page(menor_data, oms_cache_data, self.z_labels, logo_data)
                    if page_bytes:
                        pages.append(page_bytes)
                    
                    if progress_callback:
                        progress_callback(i + 1, total)
                
                self._merge_pdfs(pages, output_filename)
            
            self.log.operation_end("generar_reporte", start, success=True, pages=total)
            return True, f"Reporte generado: {output_filename}"
        
        except Exception as e:
            self.log.operation_end("generar_reporte", start, success=False, error=str(e))
            return False, f"Error generando PDF: {e}"


    
    def _merge_pdfs(self, page_bytes_list, output_filename: str):
        from pypdf import PdfWriter, PdfReader
        import io
        
        writer = PdfWriter()
        
        for item in page_bytes_list:
            if isinstance(item, list):
                pages_bytes = item
            else:
                pages_bytes = [item]
            
            for page_bytes in pages_bytes:
                if page_bytes:
                    reader = PdfReader(io.BytesIO(page_bytes))
                    for page in reader.pages:
                        writer.add_page(page)
        
        with open(output_filename, 'wb') as f:
            writer.write(f)


class AppGUI:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Reportes Nutricionales")
        self.root.geometry("750x600")
        
        self.analyzer = NutritionalAnalyzer()
        self.selected_files = []
        self.log_instance = get_logger("gui")
        
        self.create_widgets()
    
    def create_widgets(self):
        tk.Label(self.root, text="Generador de Reportes IMC", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        tk.Label(self.root, text="Procesamiento por lotes", font=("Arial", 10), fg="green").pack(pady=5)
        
        frame_files = tk.Frame(self.root)
        frame_files.pack(pady=10, padx=20, fill="x")
        
        tk.Button(frame_files, text="Seleccionar Archivos", command=self.select_files,
                 font=("Arial", 10), width=20).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(frame_files, text="Seleccionar Carpeta", command=self.select_folder,
                 font=("Arial", 10), width=20).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(frame_files, text="Limpiar Lista", command=self.clear_list,
                 font=("Arial", 10), width=15).grid(row=0, column=2, padx=5, pady=5)
        
        tk.Label(self.root, text="Archivos a procesar:", anchor="w").pack(padx=20, fill="x")
        self.listbox_files = tk.Listbox(self.root, height=8, selectmode=tk.EXTENDED)
        self.listbox_files.pack(padx=20, pady=5, fill="x")
        
        scrollbar = tk.Scrollbar(self.listbox_files)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox_files.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox_files.yview)
        
        frame_options = tk.Frame(self.root)
        frame_options.pack(pady=5, padx=20, fill="x")
        
        self.use_mp_var = tk.BooleanVar(value=True)
        tk.Checkbutton(frame_options, text="Usar multiprocesamiento", 
                      variable=self.use_mp_var).pack(side=tk.LEFT)
        
        self.btn_generate = tk.Button(self.root, text="Generar Reportes PDF", 
                                      command=self.process_batch, bg="#4CAF50", fg="white",
                                      font=("Arial", 12, "bold"), state="disabled")
        self.btn_generate.pack(pady=15)
        
        tk.Label(self.root, text="Registro de Actividad:").pack(anchor="w", padx=20)
        self.log_area = scrolledtext.ScrolledText(self.root, height=10, state="disabled")
        self.log_area.pack(padx=20, pady=5, fill="both", expand=True)
    
    def log(self, message):
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")
    
    def select_files(self):
        filenames = filedialog.askopenfilenames(
            filetypes=[("CSV/Excel", "*.csv *.xlsx *.xls")]
        )
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
                    if file.endswith(('.csv', '.xlsx', '.xls')) and not file.startswith('~$'):
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
        self.log("--- Iniciando procesamiento ---")
        self.log(f"Multiprocesamiento: {'SI' if self.use_mp_var.get() else 'NO'}")
        self.root.update()
        
        import time
        batch_start = time.time()
        
        success_count = 0
        error_count = 0
        
        for i, filepath in enumerate(self.selected_files):
            filename = os.path.basename(filepath)
            self.log(f"[{i+1}/{len(self.selected_files)}] Procesando: {filename}")
            self.root.update()
            
            file_start = time.time()
            
            success, msg = self.analyzer.load_children_data(filepath)
            if not success:
                self.log(f"  Error cargando: {msg}")
                error_count += 1
                continue
            
            base_name = os.path.splitext(filepath)[0]
            output_pdf = f"{base_name}_reporte.pdf"
            
            success, msg = self.analyzer.generate_report(output_pdf, use_multiprocessing=self.use_mp_var.get())
            
            file_duration = time.time() - file_start
            
            if success:
                self.log(f"  OK: Reporte generado ({file_duration:.1f}s)")
                success_count += 1
            else:
                self.log(f"  Error generando PDF: {msg}")
                error_count += 1
            
            self.root.update()
        
        batch_duration = time.time() - batch_start
        self.log(f"--- Finalizado en {batch_duration:.1f}s: {success_count} exitos, {error_count} errores ---")
        
        messagebox.showinfo(
            "Proceso Completado", 
            f"Se procesaron {len(self.selected_files)} archivos.\n"
            f"Exitos: {success_count}\n"
            f"Errores: {error_count}\n"
            f"Tiempo total: {batch_duration:.1f}s"
        )
        self.btn_generate.config(state="normal")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--benchmark":
        import time
        
        if len(sys.argv) < 3:
            print("Uso: python nutritional_app.py --benchmark <archivo.csv>")
            sys.exit(1)
        
        input_file = sys.argv[2]
        print(f"Benchmark: {input_file}")
        
        analyzer = NutritionalAnalyzer()
        
        start = time.time()
        success, msg = analyzer.load_children_data(input_file)
        load_time = time.time() - start
        print(f"Carga: {load_time:.2f}s - {msg}")
        
        if not success:
            sys.exit(1)
        
        output = input_file.replace('.csv', '_benchmark.pdf').replace('.xlsx', '_benchmark.pdf')
        
        start = time.time()
        success, msg = analyzer.generate_report(output, use_multiprocessing=True)
        gen_time = time.time() - start
        print(f"Generacion: {gen_time:.2f}s - {msg}")
        
        print(f"TOTAL: {load_time + gen_time:.2f}s")
        
    else:
        root = tk.Tk()
        app = AppGUI(root)
        root.mainloop()
