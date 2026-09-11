from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Evento(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(120),
        nullable=False
    )

    data = db.Column(
        db.Date,
        nullable=False
    )

    cidade = db.Column(
        db.String(100),
        nullable=False
    )

    estado = db.Column(
        db.String(2),
        nullable=False
    )

    imagem = db.Column(
        db.String(255),
        nullable=True
    )

    link_ingresso = db.Column(
        db.String(500),
        nullable=True
    )

    descricao = db.Column(
        db.Text,
        nullable=True
    )

    publicado = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )


class Admin(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    usuario = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    senha_hash = db.Column(
        db.String(255),
        nullable=False
    )