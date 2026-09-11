from datetime import date

from app import app
from models import db, Evento


with app.app_context():

    evento = Evento(
        nome="Henry Freitas",
        data=date(2026, 9, 17),
        cidade="Uruará",
        estado="PA",
        imagem="Henry-Freitas.jpeg",
        link_ingresso="https://exemplo.com",
        descricao="Show de Henry Freitas em Uruará.",
        publicado=True
    )

    db.session.add(evento)

    db.session.commit()

    print("Evento cadastrado com sucesso!")