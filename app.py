from flask import Flask, request, render_template, send_from_directory, jsonify
from PIL import Image, ImageDraw, ImageFont
import fitz
import datetime
import io
import os
import base64
import tempfile

app = Flask(__name__)

# Ruta para mostrar el formulario HTML
@app.route('/')
def mostrar_formulario():
    return render_template('formulario.html')

# Ruta para capturar la firma y los datos desde el formulario
@app.route('/captura_firma', methods=['POST'])
def captura_firma():
    try:
        # Captura de datos desde la solicitud POST
        nombre = request.form.get('nombre')
        apellidos = request.form.get('apellidos')
        dni = request.form.get('dni')
        nombre_apellidos = f"{nombre}_{apellidos.replace(' ', '_')}"
        firma_base64 = request.form.get('firma_base64')  # La firma se envía en formato base64 desde el formulario

        # Decodificar la firma base64 a una imagen PIL y guardarla en un archivo temporal
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_firma:
            firma_byte_array = base64.b64decode(firma_base64)
            temp_firma.write(firma_byte_array)
            temp_firma_path = temp_firma.name

        # Abrir el archivo PDF "consentimiento.pdf"
        pdf_file_path = "consentimiento.pdf"
        doc = fitz.open(pdf_file_path)
        page = doc[0]

        # Insertar la imagen de la firma en el borde inferior
        rect = fitz.Rect(page.rect.width - 200, page.rect.height - 100, page.rect.width, page.rect.height)
        page.insert_image(rect, filename=temp_firma_path)

        # Obtener la fecha y hora actual
        fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Agregar nombre, apellidos, DNI y fecha/hora en el lado contrario a la firma
        #rect_texto = fitz.Rect(10, page.rect.height - 140, page.rect.width - 10, page.rect.height - 100)
        rect_texto = fitz.Rect(10, page.rect.height - 80, page.rect.width / 2 - 10, page.rect.height - 40)
        texto_firma = f"Nombre: {nombre} {apellidos}\nDNI: {dni}\nFecha y hora de la firma: {fecha_hora}"
        page.insert_textbox(rect_texto, texto_firma, fontsize=10, align=0)

        # Guardar el PDF con la firma y los datos
        pdf_file_path_output = f"consentimiento_{nombre_apellidos}.pdf"
        doc.save(pdf_file_path_output)
        doc.close()

        # Eliminar el archivo temporal de la firma
        os.remove(temp_firma_path)

        # Devolver el archivo PDF con los datos y la firma
        return send_from_directory('', pdf_file_path_output, as_attachment=True)
    except Exception as e:
        return str(e), 500  # Devuelve un error 500 en caso de problemas

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)