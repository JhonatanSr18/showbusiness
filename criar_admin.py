from app import app
from models import db, Admin
from werkzeug.security import generate_password_hash


with app.app_context():

    usuario = "jhonatansr990@gmail.com"
    senha = "1234"

    admin_existente = Admin.query.filter_by(
        usuario=usuario
    ).first()

    if admin_existente:
        print("Esse usuário já existe.")

    else:
        novo_admin = Admin(
            usuario=usuario,
            senha_hash=generate_password_hash(senha)
        )

        db.session.add(novo_admin)
        db.session.commit()

        print("Admin criado com sucesso!")