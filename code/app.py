import json
from flask import Flask, request, jsonify, render_template, abort
import google.generativeai as genai
import os


# Definir la ruta donde se guardarán los archivos cargados
if os.environ.get('DOCKER', '') == "yes":
    UPLOAD_FOLDER = '/usr/src/app/subidas'
else:
    UPLOAD_FOLDER = 'subidas'

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

API_KEY = 'AIzaSyAoytfeTKTKdP4jnOikfUHJeLY_VFpFtb8'

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(model_name='gemini-pro')


def generar_resumen(titulo, descripcion, comentarios):
    preprompt = """
    Contestame siempre en español
    Contestame siempre con un tono formal.
    Siempre que te pregunten por tu nombre responde Business Central Asistente.
    Contestame en pasado. por ejemplo, en vez de He revisado, decir Se ha revisado.
    Intenta omitir nombres propios y referencias a personas.
    Trata de no incluir información personal.
    Trata de no incluir fechas, solo mencionar el problema y la solucion o soluciones realizadas por el tecnico.
    No incluir ninguna frase negativa, como Queda pendiente hablar con David para determinar si el error se debió a un fallo del programa o a una configuración incorrecta.
    hay que tratar de enfocar el problema, que sea culpa del cliente, pero sin culparle directamente, para que el servicio o reparación sea más efectiva y se pueda cobrar.
    """
    prompt = f"{titulo}. {descripcion}. {comentarios}"

    completion = model.generate_content(
        preprompt + prompt,
        generation_config={
            'temperature': 0,
            'max_output_tokens': 8000
        }
    )
    return completion.text


@app.route("/")
def home():
    return render_template('index.html')


@app.route('/resumir', methods=['POST'])
def resumir():
    titulo = request.form['titulo']
    descripcion = request.form['descripcion']
    comentarios = request.form['comentarios']

    try:
        resumen = generar_resumen(titulo, descripcion, comentarios)
        return render_template('resumen.html', resumen=resumen)
    except Exception as e:
        error_message = f"Error al generar el resumen: {str(e)}"
        return render_template('error.html', error_message=error_message)


@app.route('/enviar_datos_bc', methods=['POST'])
def enviar_datos_bc():
    # Comprobar si la petición tiene los datos en formato JSON
    if not request.is_json:
        return jsonify({'error': 'No JSON object in the request.'}), 400

    # Leer los datos del JSON
    datos = request.get_json()
    print(datos)

    # Corregir los nombres de las características
    # for dic in datos:
    #     if 'Precio (â‚¬)' in dic:
    #         dic['Precio (€)'] = dic.pop('Precio (â‚¬)')
    #     if 'Superficie (mÂ²)' in dic:
    #         dic['Superficie (m²)'] = dic.pop('Superficie (mÂ²)')

    # Validar los datos (aquí podrías agregar más validaciones)
    if not isinstance(datos, list):
        print({'error': 'Los datos deben ser una lista.'})
        return jsonify({'error': 'Los datos deben ser una lista.'}), 400

    # # Convertir los datos a DataFrame
    # X = pd.DataFrame(datos)
    # X[num_cols] = estandarizador.transform(X[num_cols])
    # print(X.to_string(index=False))

    # REalizar el resumen
    try:
        resumen = generar_resumen(
            datos[0]['Titulo'], datos[0]['Descripcion'], datos[0]['Comentarios'])
        return jsonify({'resumen': resumen})
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)  # Ejecutar la aplicación
