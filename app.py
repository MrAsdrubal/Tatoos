from flask import Flask
import os
# Importar los paquetes
from controladores.AuthController import AuthController
from controladores.PrevisualizadorController import PrevisualizadorController
from modelo.UsersModel import UsersModel
from flask import Flask, send_from_directory, render_template

# Crear la aplicación principal
app = Flask(__name__)
app.secret_key = 'clave_secreta_para_sesiones'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Inicializar clases
users_model = UsersModel('users.json')
auth_controller = AuthController(users_model)
previsualizador_controller = PrevisualizadorController(app.config['UPLOAD_FOLDER'])

# Configuración de la carpeta estática para CSS
STATIC_FOLDER = 'static'
os.makedirs(STATIC_FOLDER, exist_ok=True)

# Rutas
app.add_url_rule('/', 'home', auth_controller.home)
app.add_url_rule('/login', 'login', auth_controller.login, methods=['GET', 'POST'])
app.add_url_rule('/register', 'register', auth_controller.register, methods=['GET', 'POST'])
app.add_url_rule('/logout', 'logout', auth_controller.logout)
app.add_url_rule('/previsualizador', 'previsualizador', previsualizador_controller.previsualizador, methods=['GET', 'POST'])
app.add_url_rule('/uploads/<filename>', 'uploaded_file', previsualizador_controller.uploaded_file)
app.add_url_rule('/previsualizar_tatuaje', 'previsualizar_tatuaje', previsualizador_controller.previsualizar_tatuaje, methods=['POST'])
app.add_url_rule('/preparar_tatuaje', 'preparar_tatuaje', previsualizador_controller.preparar_tatuaje, methods=['POST'])
app.add_url_rule('/refrescar_tatuaje', 'refrescar_tatuaje', previsualizador_controller.refrescar_tatuaje, methods=['GET', 'POST'])

# Ruta para servir archivos de la carpeta 'uploads'
@app.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory('uploads', filename)

@app.route('/')
def index():
    return render_template('previsualizador.html')

if __name__ == '__main__':
    app.run(debug=True)
