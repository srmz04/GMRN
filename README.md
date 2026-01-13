# GMRN: Generador Masivo de Reportes Nutricionales

## 📋 Contexto del Proyecto
Iniciativa tecnológica conjunta para la **Secretaría de Salud (SSD)** y la **Secretaría de Educación (SEED)** del Estado de Durango.
Este sistema fue diseñado para procesar, analizar y clasificar masivamente los datos de somatometría de aproximadamente **63,000 menores** (de 6 a 12 años) del subsistema federal, recolectados por profesores de educación física durante 2 años consecutivos.

## 🚀 Evolución y Justificación Técnica
Este repositorio consolida la evolución de herramientas desarrolladas y probadas en campo ("in-house") antes de su versionado centralizado.

*   **Origen ("Fase Artesanal"):** El proyecto inició como una serie de scripts locales (Python/Colab) ejecutados manualmente para validar la metodología de cálculo de Z-Scores de la OMS en muestras piloto.
*   **Consolidación:** Tras validar la utilidad clínica y logística, el código fue refactorizado en un motor de procesamiento por lotes (*batch processing*) robusto, capaz de manejar la carga estatal completa.
*   **Estado Actual (v1.0):** El código fuente importado representa una versión estable, optimizada para multiprocesamiento y lista para producción.

## ⚙️ Funcionalidad Principal
El sistema transforma datos crudos (Excel/CSV de zonas escolares) en expedientes clínicos individuales estandarizados.

### Componentes del Reporte (3 Páginas por Menor)
1.  **Gráfica de Crecimiento OMS:** Visualización precisa del IMC vs. Edad sobre las curvas de referencia de la OMS (2007). Identifica visualmente Desnutrición, Sobrepeso u Obesidad.
2.  **Cartilla de Salud Escolar:** Formato institucional con datos demográficos y tabla de control de citas médicas.
3.  **Hoja de Referencia:** Documento oficial pre-llenado para facilitar la canalización del menor a su Centro de Salud correspondiente.

## 🛠️ Stack Tecnológico
*   **Core:** Python 3.8+
*   **Análisis de Datos:** Pandas (Vectorización de cálculos de edad y percentiles).
*   **Visualización:** Matplotlib (Backend 'Agg' para generación masiva no interactiva).
*   **Performance:** Multiprocessing (Paralelización a nivel de CPU).

## 📊 Métricas de Rendimiento
*   **Velocidad:** ~1.05 segundos por reporte completo (3 páginas).
*   **Escalabilidad:** Probado con lotes de miles de registros sin fugas de memoria.
*   **Trazabilidad:** Logs en formato JSONL para auditoría de procesos.

---
**Desarrollado para:** Servicios de Salud de Durango & Secretaría de Educación del Estado de Durango.
