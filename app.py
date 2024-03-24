import os
from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

app = Flask(__name__)

# Importando as configurações do arquivo config.py
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
mail = Mail(app)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name =db.Column(db.String(80))
    last_name =db.Column(db.String(80))
    email =db.Column(db.String(80))
    resume_filename = db.Column(db.String(255))  # Nome do arquivo do currículo
    resume_path = db.Column(db.String(255))  # Caminho do arquivo do currículo


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        resume_filename = None  # Inicializando resume_filename
        resume_path = None  # Inicializando resume_path
        # Upload do arquivo
        if 'resume' in request.files:
            resume = request.files['resume']
            if resume.filename != '' and resume.filename.endswith('.pdf'):
                resume_filename = resume.filename
                resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_filename)
                resume.save(resume_path)
            else:
                return "Por favor, add um arquivo PDF."

        # Criar instância do objeto Form apenas se o upload do arquivo PDF for bem-sucedido
        form = Form(first_name=first_name, last_name=last_name, email=email,
                    resume_filename=resume_filename, resume_path=resume_path)
        db.session.add(form)
        db.session.commit()

        message_body = f"Hey {first_name}! " \
                       f"We just got your resume, keep it going on."

        message = Message(subject="New resume added",
                          sender=app.config["MAIL_USERNAME"],
                          recipients=[email],
                          body=message_body)
        mail.send(message)

        flash(f"{first_name}, your resume was submitted successfully!", "success")

    return render_template("index.html")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True, port=5001)
