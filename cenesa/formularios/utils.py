import os
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject
from django.conf import settings

def copiar_pdf(original_path, nombre_solicitud):
    # Crear la ruta de destino
    destino_carpeta = os.path.join(settings.MEDIA_ROOT, 'pdf/solicitudes')
    if not os.path.exists(destino_carpeta):
        os.makedirs(destino_carpeta)

    nueva_ruta = os.path.join(destino_carpeta, nombre_solicitud + '.pdf')
    
    # Aquí iría la lógica para copiar el archivo PDF
    # Verifica si el archivo original existe antes de copiar
    if not os.path.exists(original_path):
        raise FileNotFoundError(f"El archivo original {original_path} no existe.")
    
    with open(original_path, 'rb') as original_pdf:
        reader = PdfReader(original_pdf)
        writer = PdfWriter()
        
        for page in range(len(reader.pages)):
            writer.add_page(reader.pages[page])
        
        with open(nueva_ruta, 'wb') as new_pdf:
            writer.write(new_pdf)
    
    return nueva_ruta

def rellenar_pdf(pdf_path, datos):
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    # Asumiendo que el PDF tiene campos de formulario
    for page in reader.pages:
        writer.add_page(page)

    # Obtener los campos del formulario en el PDF
    if '/AcroForm' in reader.trailer:
        writer._root_object.update(
            {
                NameObject("/AcroForm"): reader.trailer["/AcroForm"]
            }
        )
        form_fields = writer.get_fields()
        # Actualizar los campos con los datos proporcionados
        for field_name in datos:
            if field_name in form_fields:
                writer.update_page_form_field_values(
                    writer.pages, {field_name: datos[field_name]}
                )

    # Guardar el PDF modificado
    with open(pdf_path, 'wb') as out_pdf:
        writer.write(out_pdf)