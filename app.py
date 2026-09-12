import os
import uuid

from datetime import date

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash

from models import db, Evento, Admin


app = Flask(__name__)


# =========================================================
# CONFIGURAÇÕES
# =========================================================

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "chave-temporaria-apenas-desenvolvimento"
)


database_url = os.environ.get(
    "DATABASE_URL",
    "sqlite:///showbusiness.db"
)

if database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://",
        "postgresql://",
        1
    )

app.config["SQLALCHEMY_DATABASE_URI"] = database_url

app.config[
    "SQLALCHEMY_TRACK_MODIFICATIONS"
] = False


app.config["UPLOAD_FOLDER"] = os.path.join(
    app.root_path,
    "static",
    "uploads"
)


app.config["MAX_CONTENT_LENGTH"] = (
    5 * 1024 * 1024
)


db.init_app(app)


os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True
)


# =========================================================
# UPLOAD
# =========================================================

EXTENSOES_PERMITIDAS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


def arquivo_permitido(nome_arquivo):

    return (
        "." in nome_arquivo
        and nome_arquivo
        .rsplit(".", 1)[1]
        .lower()
        in EXTENSOES_PERMITIDAS
    )


def salvar_imagem(imagem):

    nome_original = secure_filename(
        imagem.filename
    )

    extensao = (
        nome_original
        .rsplit(".", 1)[1]
        .lower()
    )

    nome_seguro = (
        f"{uuid.uuid4().hex}.{extensao}"
    )

    caminho = os.path.join(
        app.config["UPLOAD_FOLDER"],
        nome_seguro
    )

    imagem.save(caminho)

    return nome_seguro


def excluir_imagem(nome_imagem):

    if not nome_imagem:
        return

    caminho = os.path.join(
        app.config["UPLOAD_FOLDER"],
        nome_imagem
    )

    if os.path.exists(caminho):

        os.remove(caminho)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    proximos_eventos = (
        Evento.query
        .filter(
            Evento.publicado.is_(True),
            Evento.data >= date.today()
        )
        .order_by(
            Evento.data.asc()
        )
        .limit(3)
        .all()
    )

    return render_template(
        "index.html",
        eventos=proximos_eventos
    )


# =========================================================
# EVENTOS PÚBLICOS
# =========================================================

@app.route("/eventos")
def eventos():

    lista_eventos = (
        Evento.query
        .filter(
            Evento.publicado.is_(True),
            Evento.data >= date.today()
        )
        .order_by(
            Evento.data.asc()
        )
        .all()
    )


    cidades_resultado = (
        db.session
        .query(Evento.cidade)
        .filter(
            Evento.publicado.is_(True),
            Evento.data >= date.today()
        )
        .distinct()
        .order_by(
            Evento.cidade.asc()
        )
        .all()
    )


    cidades = [
        cidade[0]
        for cidade in cidades_resultado
    ]


    return render_template(
        "eventos.html",
        eventos=lista_eventos,
        cidades=cidades
    )


# =========================================================
# SOBRE
# =========================================================

@app.route("/sobre")
def sobre():

    return render_template(
        "sobre.html"
    )


# =========================================================
# LOGIN ADMIN
# =========================================================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if session.get("admin_logado"):

        return redirect(
            url_for("admin_dashboard")
        )


    if request.method == "POST":

        usuario = (
            request.form
            .get("usuario", "")
            .strip()
        )

        senha = request.form.get(
            "senha",
            ""
        )


        admin = Admin.query.filter_by(
            usuario=usuario
        ).first()


        if (
            admin
            and check_password_hash(
                admin.senha_hash,
                senha
            )
        ):

            session.clear()

            session["admin_logado"] = True

            session["admin_id"] = admin.id


            flash(
                "Login realizado com sucesso.",
                "sucesso"
            )


            return redirect(
                url_for(
                    "admin_dashboard"
                )
            )


        flash(
            "Usuário ou senha incorretos.",
            "erro"
        )


    return render_template(
        "admin/login.html"
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/admin")
def admin_dashboard():

    if not session.get(
        "admin_logado"
    ):

        return redirect(
            url_for("admin_login")
        )


    eventos = (
        Evento.query
        .order_by(
            Evento.data.asc()
        )
        .all()
    )


    total_eventos = Evento.query.count()


    publicados = (
        Evento.query
        .filter_by(
            publicado=True
        )
        .count()
    )


    ocultos = (
        Evento.query
        .filter_by(
            publicado=False
        )
        .count()
    )


    return render_template(
        "admin/dashboard.html",
        eventos=eventos,
        total_eventos=total_eventos,
        publicados=publicados,
        ocultos=ocultos
    )


# =========================================================
# NOVO EVENTO
# =========================================================

@app.route(
    "/admin/eventos/novo",
    methods=["GET", "POST"]
)
def admin_novo_evento():

    if not session.get(
        "admin_logado"
    ):

        return redirect(
            url_for("admin_login")
        )


    if request.method == "POST":

        nome = request.form.get(
            "nome",
            ""
        ).strip()

        data_evento = request.form.get(
            "data"
        )

        cidade = request.form.get(
            "cidade",
            ""
        ).strip()

        estado = (
            request.form
            .get("estado", "")
            .strip()
            .upper()
        )

        link_ingresso = (
            request.form
            .get("link_ingresso", "")
            .strip()
        )

        descricao = (
            request.form
            .get("descricao", "")
            .strip()
        )

        publicado = (
            request.form.get(
                "publicado"
            )
            == "on"
        )


        imagem = request.files.get(
            "imagem"
        )


        if not nome:

            flash(
                "Informe o nome do evento.",
                "erro"
            )

            return redirect(
                url_for(
                    "admin_novo_evento"
                )
            )


        if not data_evento:

            flash(
                "Informe a data do evento.",
                "erro"
            )

            return redirect(
                url_for(
                    "admin_novo_evento"
                )
            )


        if len(estado) != 2:

            flash(
                "Informe a sigla do estado.",
                "erro"
            )

            return redirect(
                url_for(
                    "admin_novo_evento"
                )
            )


        if (
            not imagem
            or imagem.filename == ""
        ):

            flash(
                "Selecione uma imagem.",
                "erro"
            )

            return redirect(
                url_for(
                    "admin_novo_evento"
                )
            )


        if not arquivo_permitido(
            imagem.filename
        ):

            flash(
                "Formato de imagem inválido.",
                "erro"
            )

            return redirect(
                url_for(
                    "admin_novo_evento"
                )
            )


        nome_imagem = salvar_imagem(
            imagem
        )


        novo_evento = Evento(

            nome=nome,

            data=date.fromisoformat(
                data_evento
            ),

            cidade=cidade,

            estado=estado,

            imagem=nome_imagem,

            link_ingresso=link_ingresso,

            descricao=descricao,

            publicado=publicado
        )


        db.session.add(
            novo_evento
        )

        db.session.commit()


        flash(
            "Evento criado com sucesso.",
            "sucesso"
        )


        return redirect(
            url_for(
                "admin_dashboard"
            )
        )


    return render_template(
        "admin/novo_evento.html"
    )


# =========================================================
# EDITAR EVENTO
# =========================================================

@app.route(
    "/admin/eventos/editar/<int:id>",
    methods=["GET", "POST"]
)
def admin_editar_evento(id):

    if not session.get(
        "admin_logado"
    ):

        return redirect(
            url_for("admin_login")
        )


    evento = Evento.query.get_or_404(
        id
    )


    if request.method == "POST":

        evento.nome = (
            request.form
            .get("nome", "")
            .strip()
        )


        evento.data = date.fromisoformat(
            request.form.get("data")
        )


        evento.cidade = (
            request.form
            .get("cidade", "")
            .strip()
        )


        evento.estado = (
            request.form
            .get("estado", "")
            .strip()
            .upper()
        )


        evento.link_ingresso = (
            request.form
            .get("link_ingresso", "")
            .strip()
        )


        evento.descricao = (
            request.form
            .get("descricao", "")
            .strip()
        )


        evento.publicado = (
            request.form.get(
                "publicado"
            )
            == "on"
        )


        imagem = request.files.get(
            "imagem"
        )


        if (
            imagem
            and imagem.filename != ""
        ):

            if not arquivo_permitido(
                imagem.filename
            ):

                flash(
                    "Formato de imagem inválido.",
                    "erro"
                )

                return redirect(
                    url_for(
                        "admin_editar_evento",
                        id=evento.id
                    )
                )


            imagem_antiga = evento.imagem


            novo_nome = salvar_imagem(
                imagem
            )


            evento.imagem = novo_nome


            excluir_imagem(
                imagem_antiga
            )


        db.session.commit()


        flash(
            "Evento atualizado com sucesso.",
            "sucesso"
        )


        return redirect(
            url_for(
                "admin_dashboard"
            )
        )


    return render_template(
        "admin/editar_evento.html",
        evento=evento
    )


# =========================================================
# EXCLUIR EVENTO
# =========================================================

@app.route(
    "/admin/eventos/excluir/<int:id>",
    methods=["POST"]
)
def admin_excluir_evento(id):

    if not session.get(
        "admin_logado"
    ):

        return redirect(
            url_for("admin_login")
        )


    evento = Evento.query.get_or_404(
        id
    )


    imagem = evento.imagem


    db.session.delete(
        evento
    )

    db.session.commit()


    excluir_imagem(
        imagem
    )


    flash(
        "Evento excluído com sucesso.",
        "sucesso"
    )


    return redirect(
        url_for(
            "admin_dashboard"
        )
    )


# =========================================================
# PUBLICAR / OCULTAR
# =========================================================

@app.route(
    "/admin/eventos/status/<int:id>",
    methods=["POST"]
)
def admin_alterar_status(id):

    if not session.get(
        "admin_logado"
    ):

        return redirect(
            url_for("admin_login")
        )


    evento = Evento.query.get_or_404(
        id
    )


    evento.publicado = (
        not evento.publicado
    )


    db.session.commit()


    if evento.publicado:

        flash(
            "Evento publicado.",
            "sucesso"
        )

    else:

        flash(
            "Evento ocultado.",
            "sucesso"
        )


    return redirect(
        url_for(
            "admin_dashboard"
        )
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/admin/logout")
def admin_logout():

    session.clear()


    flash(
        "Você saiu do painel.",
        "sucesso"
    )


    return redirect(
        url_for(
            "admin_login"
        )
    )


# =========================================================
# BANCO
# =========================================================

with app.app_context():

    db.create_all()


# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )