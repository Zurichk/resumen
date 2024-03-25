from flask import Flask, render_template, request
import google.generativeai as genai

app = Flask(__name__)

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


@app.route('/')
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


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)  # Ejecutar la aplicación
