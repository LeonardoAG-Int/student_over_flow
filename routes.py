from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from models import User, Question, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

class RegistrationForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    email = StringField('Correo', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrarse')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('El usuario ya existe.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('El correo ya está registrado.')

class LoginForm(FlaskForm):
    email = StringField('Correo', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar sesión')

class QuestionForm(FlaskForm):
    title = StringField('Título de tu pregunta', validators=[DataRequired()])
    body = TextAreaField('Detalles de tu pregunta', validators=[DataRequired()])
    submit = SubmitField('Publicar pregunta')

def configure_routes(app):
    @app.route('/')
    def home():
        questions = Question.query.all()
        return render_template('home.html', questions=questions)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = generate_password_hash(form.password.data)
            user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                flash('Inicio de sesión exitoso.', 'success')
                return redirect(url_for('home'))
            else:
                flash('Correo o contraseña incorrectos.', 'danger')
        return render_template('login.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Has cerrado sesión.', 'info')
        return redirect(url_for('home'))

    @app.route('/ask', methods=['GET', 'POST'])
    @login_required
    def ask():
        form = QuestionForm()
        if form.validate_on_submit():
            question = Question(
                title=form.title.data,
                body=form.body.data,
                author=current_user
            )
            db.session.add(question)
            db.session.commit()
            flash('¡Tu pregunta ha sido publicada!', 'success')
            return redirect(url_for('home'))
        return render_template('ask.html', form=form)
