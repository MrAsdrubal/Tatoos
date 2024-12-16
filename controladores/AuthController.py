from flask import render_template, redirect, url_for, session, request

class AuthController:
    def __init__(self, users_model):
        self.users_model = users_model

    def home(self):
        if 'username' in session:
            return redirect(url_for('previsualizador'))
        return redirect(url_for('login'))

    def login(self):
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            if self.users_model.validate_user(username, password):
                session['username'] = username
                return redirect(url_for('previsualizador'))
            else:
                return render_template('login.html', error='Credenciales inválidas')
        return render_template('login.html')

    def register(self):
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            if self.users_model.register_user(username, password):
                return redirect(url_for('login'))
            else:
                return render_template('register.html', error='El usuario ya existe')
        return render_template('register.html')

    def logout(self):
        session.pop('username', None)
        return redirect(url_for('login'))