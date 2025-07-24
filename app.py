# Imports padrão
import os
import uuid
import io
import csv
import json
import string
import secrets
import requests
from io import StringIO, TextIOWrapper
from datetime import datetime, timedelta, date
from pathlib import Path

# Carrega variáveis do .env
from dotenv import load_dotenv
load_dotenv()

# Imports do Flask
from flask import (
    Flask, render_template, url_for, request, redirect, flash, jsonify,
    make_response, session, Response, send_file
)
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_mail import Message
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash

# Extensões e banco de dados
from flask_migrate import Migrate
from sqlalchemy import func
from extensions import mail
from models import db, User, Sensor, Empresa
from utils import enviar_email_boas_vindas, enviar_email_recuperacao

# ─────────────── INICIALIZAÇÃO ───────────────
app = Flask(__name__)

# Chave secreta para sessões
app.secret_key = secrets.token_hex(16)

# Configuração do banco (usa DATABASE_URL do .env)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")

# Inicializa extensões
db.init_app(app)
mail.init_app(app)
migrate = Migrate(app, db)

# Login Manager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#-------usuarios-------
@app.route("/usuarios")
@login_required
def usuarios():
    if not current_user.is_admin:
        flash("Você não tem permissão para visualizar usuários.", "danger")
        return redirect(url_for("index"))

    usuarios = User.query.all()
    return render_template("usuarios.html", usuarios=usuarios)

# ROTA: CRIAR NOVO USUÁRIO
@app.route("/criar_usuario", methods=["GET", "POST"])
@login_required
def criar_usuario():
    if not current_user.is_admin:
        flash("Você não tem permissão para criar usuários.", "danger")
        return redirect(url_for("usuarios"))

    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        is_admin = bool(request.form.get("is_admin"))

        if User.query.filter_by(email=email).first():
            flash("E-mail já cadastrado.", "danger")
            return redirect(url_for("criar_usuario"))

        senha_temporaria = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))

        novo_usuario = User(
            nome=nome,
            email=email,
            is_admin=is_admin,
            can_view=True,
            trocar_senha=True
        )
        novo_usuario.set_password(senha_temporaria)

        db.session.add(novo_usuario)
        db.session.commit()

        enviar_email_boas_vindas(novo_usuario, senha_temporaria)

        flash("Usuário criado com sucesso!", "success")
        return redirect(url_for("usuarios"))

    return render_template("criar_usuario.html")



#-----ROTA TROCAR SENHA

@app.route("/trocar_senha", methods=["GET", "POST"])
@login_required
def trocar_senha():
    if request.method == "POST":
        nova_senha = request.form.get("nova_senha")
        current_user.set_password(nova_senha)
        current_user.trocar_senha = False
        db.session.commit()
        flash("Senha alterada com sucesso.", "success")
        return redirect(url_for("index"))
    
    return render_template("trocar_senha.html")


# ROTA: EDITAR USUÁRIO
@app.route("/editar_usuario/<int:user_id>", methods=["GET", "POST"])
@login_required
def editar_usuario(user_id):
    if not current_user.is_admin:
        flash("Você não tem permissão para editar usuários.", "danger")
        return redirect(url_for("usuarios"))

    usuario = User.query.get_or_404(user_id)

    if request.method == "POST":
        usuario.nome = request.form.get("nome")
        usuario.email = request.form.get("email")
        usuario.can_view = bool(request.form.get("can_view"))
        usuario.can_edit = bool(request.form.get("can_edit"))
        usuario.can_delete = bool(request.form.get("can_delete"))
        usuario.can_export = bool(request.form.get("can_export"))
        usuario.is_admin = bool(request.form.get("is_admin"))

        db.session.commit()
        flash("Usuário atualizado com sucesso!", "success")
        return redirect(url_for("usuarios"))

    return render_template("editar_usuario.html", usuario=usuario)


# ROTA: EXCLUIR USUÁRIO
@app.route("/deletar_usuario/<int:user_id>")
@login_required
def deletar_usuario(user_id):
    if not current_user.is_admin:
        flash("Você não tem permissão para excluir usuários.", "danger")
        return redirect(url_for("usuarios"))

    usuario = User.query.get_or_404(user_id)

    if usuario.id == current_user.id:
        flash("Você não pode excluir sua própria conta.", "warning")
        return redirect(url_for("usuarios"))

    db.session.delete(usuario)
    db.session.commit()
    flash("Usuário excluído com sucesso.", "success")
    return redirect(url_for("usuarios"))




from models import Empresa, TipoDevice, TipoSonda, Sensor, Parceiro, Estado, Municipio

# ------Configuracao para envio de e-mail via Office365 (Outlook)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sentinel3601@gmail.com'
app.config['MAIL_PASSWORD'] = 'hbdt lbso cfnn mxaa'  # preferencialmente, use senha de app

mail.init_app(app) # Initialize Mail after app is created and configured


#----------Register---------    
@app.route("/register", methods=["GET", "POST"])
@login_required
def register():
    if not current_user.is_admin:
        flash("Você não tem permissão para cadastrar usuários.", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        can_view = bool(request.form.get("can_view"))
        can_edit = bool(request.form.get("can_edit"))
        can_delete = bool(request.form.get("can_delete"))
        can_export = bool(request.form.get("can_export"))

        if User.query.filter_by(email=email).first():
            flash("Este e-mail já está cadastrado.", "danger")
            return redirect(url_for("register"))

        novo_usuario = User(
            nome=nome,
            email=email,
            can_view=can_view,
            can_edit=can_edit,
            can_delete=can_delete,
            can_export=can_export
        )
        novo_usuario.set_password(senha)

        db.session.add(novo_usuario)
        db.session.commit()
        flash("Usuário cadastrado com sucesso!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


#------- rota esqueci senha---
import secrets
from werkzeug.security import generate_password_hash

@app.route("/esqueci_senha", methods=["GET", "POST"])
def esqueci_senha():
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if user:
            senha_temporaria = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
            user.set_password(senha_temporaria)  # atualiza com a senha temporária
            db.session.commit()
            enviar_email_recuperacao(user, senha_temporaria)  # envia a senha por e-mail
            flash("Instruções enviadas para seu e-mail.", "info")
            return redirect(url_for("login"))
        else:
            flash("E-mail não encontrado.", "danger")
    return render_template("esqueci_senha.html")



#------- rota resetar senha---

@app.route("/resetar_senha/<token>", methods=["GET", "POST"])
def reset_token(token):
    user = User.verify_reset_token(token)
    if not user:
        flash("Token inválido ou expirado.", "warning")
        return redirect(url_for("esqueci_senha"))

    if request.method == "POST":
        senha_temporaria = request.form.get("senha_temporaria")
        nova_senha = request.form.get("senha")
        confirmar_senha = request.form.get("confirmar_senha")

        # 1. Verifica se senha temporária está correta
        if not user.check_password(senha_temporaria):
            flash("Senha temporária incorreta.", "danger")
            return render_template("resetar_senha.html", token=token)

        # 2. Verifica se nova senha foi confirmada corretamente
        if not nova_senha or not confirmar_senha:
            flash("A nova senha e a confirmação são obrigatórias.", "danger")
            return render_template("resetar_senha.html", token=token)

        if nova_senha != confirmar_senha:
            flash("A nova senha e a confirmação não coincidem.", "danger")
            return render_template("resetar_senha.html", token=token)

        # 3. Atualiza a senha
        user.set_password(nova_senha)
        db.session.commit()
        flash("Senha atualizada com sucesso!", "success")
        return redirect(url_for("login"))

    return render_template("resetar_senha.html", token=token)



#---------redefinir senha------
@app.route("/redefinir_senha", methods=["GET", "POST"])
def redefinir_senha():
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if user:
            token = user.get_reset_token()  # usa o método seguro com assinatura
            db.session.commit()

            # Aqui você pode substituir o print por envio real de e-mail
            print(f"[DEBUG] Link de redefinição: http://localhost:5000/resetar_senha/{token}")
            flash("Enviamos um link para redefinir sua senha.", "info")
        else:
            flash("E-mail não encontrado.", "danger")

        return redirect(url_for("login"))

    return render_template("redefinir_senha.html")



#--------Login-------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(senha):
            login_user(user)
            flash("Login realizado com sucesso.", "success")
            return redirect(url_for("index"))  # ou dashboard
        else:
            flash("E-mail ou senha inválidos.", "danger")
    return render_template("login.html")

#---------logout--------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout realizado com sucesso.", "info")
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    if not (current_user.can_view or current_user.is_admin):
        flash("Você não tem permissão para visualizar esta página.", "danger")
        return redirect(url_for("login"))

    # --- Sensores por Device ---
    sensores_por_device = (
        db.session.query(TipoDevice.nome, func.count(Sensor.id))
        .join(TipoDevice, Sensor.tipo_device == TipoDevice.id)
        .group_by(TipoDevice.nome)
        .all()
    )
    total = sum(c for _, c in sensores_por_device) or 1
    sensores_por_device_pct = [
        (nome, round(c / total * 100, 2), c) for nome, c in sensores_por_device
    ]

    # --- Sensores por Tipo de Sonda ---
    sensores_por_tipo_sonda_query = (
        db.session.query(TipoSonda.nome, func.count(Sensor.id))
        .join(TipoSonda, Sensor.tipo_sonda == TipoSonda.id)
        .group_by(TipoSonda.nome)
        .all()
    )
    sensores_por_tipo_sonda = [(nome, count) for nome, count in sensores_por_tipo_sonda_query]

    # --- Sensores por Status ---
    sensores_por_status_query = (
        db.session.query(Sensor.status, func.count(Sensor.id))
        .group_by(Sensor.status)
        .all()
    )
    sensores_por_status = [(status, count) for status, count in sensores_por_status_query]

    # --- Sensores com calibração nos próximos 60 dias ---
    hoje = date.today()
    limite = hoje + timedelta(days=60)

    sensores_a_calibrar = Sensor.query.filter(
        Sensor.proxima_calibracao != None,
        Sensor.proxima_calibracao <= limite
    ).all()

    # --- Sensores por Estado (UF) ---
    sensores_por_estado_query = (
        db.session.query(Empresa.estado, func.count(Sensor.id))
        .join(Empresa, Sensor.empresa == Empresa.nome)
        .group_by(Empresa.estado)
        .all()
    )
    sensores_por_estado = [(estado, count) for estado, count in sensores_por_estado_query]

    # --- Ordem do Dashboard ---
    dashboard_order = json.loads(current_user.dashboard_order or "[]")

    return render_template(
        "index.html",
        sensores_por_device=sensores_por_device_pct,
        sensores_por_tipo_sonda=sensores_por_tipo_sonda,
        sensores_por_status=sensores_por_status,
        sensores_por_estado=sensores_por_estado,
        sensores_a_calibrar=sensores_a_calibrar,
        dashboard_order=dashboard_order
    )


#-----salvar conf dashboard usuario
@app.route('/salvar_ordem_dashboard', methods=['POST'])
@login_required
def salvar_ordem_dashboard():
    data = request.get_json()
    ordem = data.get('ordem')
    if ordem:
        current_user.dashboard_order = json.dumps(ordem)
        db.session.commit()
        return jsonify({'status': 'ok'}), 200
    return jsonify({'error': 'invalid data'}), 400



#-------exportas calibração tela dashboard---------
@app.route('/exportar_calibracao')
@login_required
def exportar_calib_dashboard():
    if not (current_user.can_export or current_user.is_admin):
        flash("Você não tem permissão para exportar dados.", "danger")
        return redirect(url_for("sensors"))

    hoje = date.today()
    limite = hoje + timedelta(days=60)

    sensores = Sensor.query.filter(
        Sensor.proxima_calibracao != None,
        Sensor.proxima_calibracao.between(hoje, limite)
    ).all()

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Nome', 'Código', 'Empresa', 'Próxima Calibração'])

    for s in sensores:
        cw.writerow([
            s.id,
            s.nome,
            s.codigo,
            s.empresa,
            s.proxima_calibracao.strftime('%Y-%m-%d') if s.proxima_calibracao else ''
        ])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=sensores_calibrar.csv"
    output.headers["Content-type"] = "text/csv"
    return output


UPLOAD_FOLDER = 'static/certificados'  # pasta onde salvará os arquivos
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/form-upload-certificado/<int:id>', methods=['GET'])
@login_required
def upload_certificado_form(id):
    if not (current_user.can_edit or current_user.is_admin):
        flash("Você não tem permissão para editar certificados.", "danger")
        return redirect(url_for("sensors"))

    sensor = Sensor.query.get_or_404(id)
    return render_template('upload_certificado.html', sensor=sensor)


@app.route('/upload-certificado/<int:id>', methods=['POST'])
@login_required
def upload_certificado(id):
    if not (current_user.can_edit or current_user.is_admin):
        flash("Você não tem permissão para enviar certificados.", "danger")
        return redirect(url_for("sensors"))

    sensor = Sensor.query.get_or_404(id)
    arquivo = request.files.get('certificado')
    nome_complemento = request.form.get('nome_certificado', '').strip()

    if arquivo and arquivo.filename.endswith('.pdf'):
        # Cria o nome seguro do arquivo
        nome_base = f"Certificado_de_Calibracao_-_Sensor_{nome_complemento}"
        nome_arquivo = secure_filename(nome_base + '.pdf')

        # Caminho completo e relativo
        caminho_absoluto = os.path.join(UPLOAD_FOLDER, nome_arquivo)
        caminho_relativo = os.path.join('certificados', nome_arquivo).replace("\\", "/")

        # Salva o arquivo e atualiza o sensor
        arquivo.save(caminho_absoluto)
        sensor.certificado_path = caminho_relativo
        db.session.commit()

        flash('Certificado enviado com sucesso!', 'success')
    else:
        flash('Por favor, envie um arquivo PDF válido.', 'danger')

    return redirect(url_for('sensors'))



@app.route("/sensors", methods=["GET", "POST"])
@login_required
def sensors():
    if request.method == "POST":
        if not (current_user.can_create or current_user.is_admin):
            flash("Você não tem permissão para cadastrar sensores.", "danger")
            return redirect(url_for("sensors"))
    # ---------- POST = cadastro ----------
    if request.method == "POST":
        # ids dos selects
        tipo_device_id = request.form.get("tipo_device")
        tipo_sonda_id  = request.form.get("tipo_sonda")

        # pega o texto do device para a coluna NOT NULL 'nome'
        device_obj  = TipoDevice.query.get(tipo_device_id)
        nome_sensor = device_obj.nome if device_obj else None

        # demais campos
        codigo        = request.form.get("codigo")
        codigo_sonda  = request.form.get("codigo_sonda")
        status        = request.form.get("status")
        localizacao   = request.form.get("localizacao")
        empresa       = request.form.get("empresa")
        responsavel_tec = request.form.get("responsavel_tec")
        contato       = request.form.get("contato")
        nomenclatura  = request.form.get("nomenclatura")
        local_calib   = request.form.get("local_calibracao")
        empresa_calib = request.form.get("empresa_calibracao")

        data_calib_str = request.form.get("data_calibracao")
        prox_calib_str = request.form.get("proxima_calibracao")
        data_calib = datetime.strptime(data_calib_str, "%Y-%m-%d").date() if data_calib_str else None
        prox_calib = datetime.strptime(prox_calib_str, "%Y-%m-%d").date() if prox_calib_str else None

        novo_sensor = Sensor(
            nome               = nome_sensor,
            codigo             = codigo,
            codigo_sonda       = codigo_sonda,
            tipo_device        = tipo_device_id,
            tipo_sonda         = tipo_sonda_id,
            status             = status,
            localizacao        = localizacao,
            empresa            = empresa,
            responsavel_tec    = responsavel_tec,
            contato            = contato,
            nomenclatura       = nomenclatura,
            local_calibracao   = local_calib,
            empresa_calibracao = empresa_calib,
            data_calibracao    = data_calib,
            proxima_calibracao = prox_calib
        )
        try:
            db.session.add(novo_sensor)
            db.session.commit()
            flash("Sensor cadastrado com sucesso!", "success")
            return redirect(url_for("sensors"))
        except Exception as e:
            db.session.rollback()
            print("ERRO →", e)
            flash("Erro ao cadastrar o sensor.", "danger")

    # ---------- GET = filtros ----------
    f_tipo_device = request.args.get("f_tipo_device")
    f_tipo_sonda  = request.args.get("f_tipo_sonda")
    f_status      = request.args.get("f_status")
    f_empresa     = request.args.get("f_empresa")
    f_cidade      = request.args.get("f_cidade")
    f_uf          = request.args.get("f_uf")

    query = db.session.query(Sensor)

    if f_cidade or f_uf:
        query = query.join(Empresa, Sensor.empresa == Empresa.nome)

    if f_tipo_device:
        query = query.filter(Sensor.tipo_device == f_tipo_device)
    if f_tipo_sonda:
        query = query.filter(Sensor.tipo_sonda == f_tipo_sonda)
    if f_status:
        query = query.filter(Sensor.status == f_status)
    if f_empresa:
        query = query.filter(Sensor.empresa == f_empresa)
    if f_cidade:
        query = query.filter(Empresa.cidade == f_cidade)
    if f_uf:
        query = query.filter(Empresa.estado == f_uf)

    sensores = query.order_by(Sensor.criado_em.desc()).all()

    # Listagem paginada de sensores
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Sensor.id.desc()).paginate(page=page, per_page=10)
    sensores = pagination.items  # lista de sensores visíveis na página

# Alerta de sensores com calibração próxima (com base em TODOS os sensores, não só os paginados
    hoje = datetime.today().date()
    todos_sensores = query.all()
    sensores_calibrar = [
        s for s in todos_sensores
        if s.proxima_calibracao and s.proxima_calibracao <= hoje + timedelta(days=60)
    ]

    # listas para os selects
    devices   = TipoDevice.query.order_by(TipoDevice.nome).all()
    sondas    = TipoSonda.query.order_by(TipoSonda.nome).all()
    empresas  = Empresa.query.order_by(Empresa.nome).all()
    cidades   = [r[0] for r in db.session.query(Empresa.cidade ).distinct().order_by(Empresa.cidade ).all()]
    ufs       = [r[0] for r in db.session.query(Empresa.estado).distinct().order_by(Empresa.estado).all()]

    return render_template(
        "sensors.html",
        sensores=sensores,
        pagination=pagination,
        sensores_calibrar=sensores_calibrar,
        devices=devices,
        sondas=sondas,
        empresas=empresas,
        cidades=cidades,
        ufs=ufs,
        hoje=hoje,
        timedelta=timedelta
    )

@app.route('/delete_sensor/<int:id>', methods=['POST'])
@login_required
def delete_sensor(id):
    if not (current_user.can_delete or current_user.is_admin):
        flash("Você não tem permissão para deletar.", "danger")
        return redirect(url_for("sensors"))

    sensor = Sensor.query.get_or_404(id)
    try:
        db.session.delete(sensor)
        db.session.commit()
        flash('Sensor excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir o sensor.', 'danger')

    return redirect(url_for("sensors"))



@app.route("/sensors/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_sensor(id):
    if not (current_user.can_edit or current_user.is_admin):
        flash("Você não tem permissão para editar.", "danger")
        return redirect(url_for("sensors"))

    sensor   = Sensor.query.get_or_404(id)
    devices  = TipoDevice.query.order_by(TipoDevice.nome).all()
    sondas   = TipoSonda.query.order_by(TipoSonda.nome).all()
    empresas = Empresa.query.order_by(Empresa.nome).all()

    if request.method == "POST":

        # ----------- campos de texto / selects -----------
        sensor.tipo_device        = request.form.get("tipo_device")
        sensor.codigo             = request.form.get("codigo")
        sensor.codigo_sonda       = request.form.get("codigo_sonda")
        sensor.tipo_sonda         = request.form.get("tipo_sonda")
        sensor.status             = request.form.get("status")
        sensor.localizacao        = request.form.get("localizacao")
        sensor.empresa            = request.form.get("empresa")
        sensor.responsavel_tec    = request.form.get("responsavel_tec")
        sensor.contato            = request.form.get("contato")
        sensor.nomenclatura       = request.form.get("nomenclatura")
        sensor.local_calibracao   = request.form.get("local_calibracao")
        sensor.empresa_calibracao = request.form.get("empresa_calibracao")

        # ----------- datas -----------
        def to_date(s):
            try:
                return datetime.strptime(s, "%Y-%m-%d").date() if s else None
            except ValueError:
                return None

        sensor.data_calibracao    = to_date(request.form.get("data_calibracao"))
        sensor.proxima_calibracao = to_date(request.form.get("proxima_calibracao"))

        # ----------- upload / substituição do PDF -----------
        pdf_file = request.files.get("certificado")

        if pdf_file and pdf_file.filename and pdf_file.filename.lower().endswith(".pdf"):

            # remove o certificado antigo (caso exista)
            if sensor.certificado_path:
                antigo = Path(app.static_folder) / sensor.certificado_path
                antigo.unlink(missing_ok=True)

            filename  = secure_filename(pdf_file.filename)
            rel_path  = Path("certificados") / filename          # ex.: certificados/arquivo.pdf
            abs_path  = Path(app.static_folder) / rel_path       # /static/certificados/arquivo.pdf

            abs_path.parent.mkdir(parents=True, exist_ok=True)   # garante a pasta
            pdf_file.save(abs_path)                              # grava o novo PDF

            sensor.certificado_path = str(rel_path)              # salva só o caminho relativo
            sensor.certificado_nome = request.form.get("certificado_nome") or filename

        # ----------- commit -----------
        db.session.commit()
        flash("Sensor atualizado com sucesso!", "success")
        return redirect(url_for("sensors"))

    # GET
    return render_template(
        "edit_sensor.html",
        sensor=sensor,
        devices=devices,
        sondas=sondas,
        empresas=empresas
    )

# REMOVER CERTIFICADO

@app.route('/sensors/<int:id>/remover_certificado', methods=['POST'])
@login_required
def remover_certificado(id):
    if not (current_user.can_edit or current_user.is_admin):
        flash("Você não tem permissão para deletar.", "danger")
        return redirect(url_for("sensors"))

    sensor = Sensor.query.get_or_404(id)

    if sensor.certificado_path:
        caminho = os.path.join(app.root_path, sensor.certificado_path)
        if os.path.exists(caminho):
            os.remove(caminho)
        sensor.certificado_path = None
        db.session.commit()
        flash('Certificado removido com sucesso!', 'success')
    else:
        flash('Nenhum certificado para remover.', 'danger')

    return redirect(url_for('edit_sensor', id=id))

# IMPORTAR EMPRESAS
@app.route('/importar_empresas', methods=['POST'])
@login_required
def importar_empresas():
    if 'arquivo_csv' not in request.files:
        flash('Nenhum arquivo enviado.', 'danger')
        return redirect(url_for('cadastro_empresa'))

    file = request.files['arquivo_csv']

    if file.filename == '':
        flash('Nenhum arquivo selecionado.', 'warning')
        return redirect(url_for('cadastro_empresa'))

    if file and file.filename.endswith('.csv'):
        try:
            stream = io.StringIO(file.stream.read().decode("utf-8"), newline=None)
            csv_input = csv.DictReader(stream, delimiter=";")  # <-- AJUSTE AQUI

            importadas = 0
            ignoradas = 0

            for row in csv_input:
                print(row)  # <-- AJUDA NA DEPURAÇÃO

                nome = row.get('nome', '').strip()
                cnpj = row.get('cnpj', '').strip()

                # Validação mínima
                if not nome or not cnpj:
                    flash('Linha ignorada por dados incompletos.', 'warning')
                    ignoradas += 1
                    continue

                # Verifica se a empresa já existe por CNPJ ou Nome
                empresa_existente = Empresa.query.filter(
                    (Empresa.cnpj == cnpj) | (Empresa.nome == nome)
                ).first()

                if empresa_existente:
                    flash(f"Empresa '{nome}' já cadastrada.", 'warning')
                    ignoradas += 1
                    continue

                # Cria nova empresa
                nova_empresa = Empresa(
                    nome=nome,
                    cnpj=cnpj,
                    telefone=row.get('telefone', '').strip(),
                    endereco=row.get('endereco', '').strip(),
                    cidade=row.get('cidade', '').strip(),
                    estado=row.get('estado', '').strip(),
                    cep=row.get('cep', '').strip(),
                    email=row.get('email', '').strip(),
                    contato=row.get('contato', '').strip()
                )
                db.session.add(nova_empresa)
                importadas += 1

            db.session.commit()
            flash(f'{importadas} empresas importadas com sucesso! {ignoradas} linhas ignoradas.', 'success')

        except Exception as e:
            flash(f'Erro ao importar: {str(e)}', 'danger')

    else:
        flash('Arquivo inválido. Envie um CSV.', 'danger')

    return redirect(url_for('cadastro_empresa'))



# CADASTRO DE EMPRESA
@app.route('/cadastro/empresa', methods=['GET', 'POST'])
@login_required
def cadastro_empresa():
    if not current_user.can_view:
        flash("Você não tem permissão para visualizar esta página.", "danger")
        return redirect(url_for("index"))

    if request.method == 'POST':
        if not (current_user.can_edit or current_user.is_admin):
            flash("Você não tem permissão para cadastrar empresas.", "danger")
            return redirect(url_for("cadastro_empresa"))

        nome = request.form.get('nome')
        cnpj = request.form.get('cnpj')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        contato = request.form['contato']
        endereco = request.form.get('endereco')
        cidade = request.form.get('cidade')
        estado = request.form.get('estado')
        cep = request.form.get('cep')

        if nome:
            nova_empresa = Empresa(
                nome=nome,
                cnpj=cnpj,
                telefone=telefone,
                email=email,
                contato=contato,
                endereco=endereco,
                cidade=cidade,
                estado=estado,
                cep=cep
            )
            try:
                db.session.add(nova_empresa)
                db.session.commit()
                flash('Empresa cadastrada com sucesso!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao cadastrar empresa. {str(e)}', 'danger')

        return redirect('/cadastro/empresa')

# Listagem de empresas com paginação
    page = request.args.get('page', 1, type=int)
    empresas = Empresa.query.order_by(Empresa.nome).paginate(page=page, per_page=10)
    return render_template('empresa.html', empresas=empresas.items, pagination=empresas)

    empresas = Empresa.query.order_by(Empresa.nome).all()
    
    return render_template('empresa.html', empresas=empresas)


# EDITAR CADASTRO DE EMPRESA
@app.route('/edit/empresa/<int:id>', methods=['POST'])
@login_required
def edit_empresa(id):
    if not (current_user.can_edit or current_user.is_admin):
        flash("Você não tem permissão para editar empresas.", "danger")
        return redirect(url_for("cadastro_empresa"))

    empresa = Empresa.query.get_or_404(id)
    nome = request.form.get('nome')
    cnpj = request.form.get('cnpj')
    telefone = request.form.get('telefone')
    email = request.form.get('email')  
    contato = request.form.get('contato')  
    endereco = request.form.get('endereco')
    cidade = request.form.get('cidade')
    estado = request.form.get('estado')
    cep = request.form.get('cep')

    if nome:
        empresa.nome = nome
        empresa.cnpj = cnpj
        empresa.telefone = telefone
        empresa.email = email
        empresa.contato = contato
        empresa.endereco = endereco
        empresa.cidade = cidade
        empresa.estado = estado
        empresa.cep = cep
        try:
            db.session.commit()
            flash('Empresa editada com sucesso!', 'success')
        except:
            db.session.rollback()
            flash('Erro ao editar empresa.', 'danger')
    return redirect('/cadastro/empresa')



# DELETAR CADASTRO DE EMPRESA
@app.route('/delete/empresa/<int:id>', methods=['POST'])
@login_required
def delete_empresa(id):
    if not (current_user.can_delete or current_user.is_admin):
        flash("Você não tem permissão para deletar empresas.", "danger")
        return redirect(url_for("cadastro_empresa"))

    empresa = Empresa.query.get_or_404(id)
    try:
        db.session.delete(empresa)
        db.session.commit()
        flash('Empresa excluída com sucesso!', 'success')
    except:
        db.session.rollback()
        flash('Erro ao excluir empresa.', 'danger')
    return redirect('/cadastro/empresa')



#CADASTRO DE TIPO DE SONDA

@app.route('/cadastro/tipo-sonda', methods=['GET', 'POST'])
@login_required
def cadastro_tipo_sonda():
    if not current_user.can_view:
        flash("Você não tem permissão para visualizar esta página.", "danger")
        return redirect(url_for("index"))

    if request.method == 'POST':
        if not current_user.can_edit:
            flash("Você não tem permissão para cadastrar.", "danger")
            return redirect(url_for("cadastro_tipo_sonda"))

        nome = request.form.get('nome')
        if nome:
            nova_sonda = TipoSonda(nome=nome)
            try:
                db.session.add(nova_sonda)
                db.session.commit()
                flash('Tipo de Sonda cadastrado com sucesso!', 'success')
            except:
                db.session.rollback()
                flash('Erro ao cadastrar tipo de sonda.', 'danger')
        return redirect('/cadastro/tipo-sonda')

    sondas = TipoSonda.query.order_by(TipoSonda.nome).all()
    return render_template('tipo_sonda.html', sondas=sondas)


#EDITAR CADASTRO DE TIPO DE SONDA

@app.route('/cadastro/tipo-sonda/<int:id>/editar', methods=['POST'])
@login_required
def edit_tipo_sonda(id):
    if not current_user.can_edit:
        flash("Você não tem permissão para editar.", "danger")
        return redirect(url_for("cadastro_tipo_sonda"))

    sonda = TipoSonda.query.get_or_404(id)
    novo_nome = request.form.get('nome')
    
    if novo_nome:
        try:
            sonda.nome = novo_nome
            db.session.commit()
            flash('Tipo de Sonda atualizado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar tipo de sonda. {str(e)}', 'danger')
    
    return redirect(url_for('cadastro_tipo_sonda'))

#DELETAR CADASTRO DE TIPO DE SONDA

@app.route('/cadastro/tipo-sonda/<int:id>/excluir', methods=['POST'])
@login_required
def delete_tipo_sonda(id):
    if not current_user.can_delete:
        flash("Você não tem permissão para deletar.", "danger")
        return redirect(url_for("cadastro_tipo_sonda"))

    sonda = TipoSonda.query.get_or_404(id)
    try:
        db.session.delete(sonda)
        db.session.commit()
        flash('Tipo de Sonda excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir tipo de sonda. {str(e)}', 'danger')

    return redirect(url_for('cadastro_tipo_sonda'))

# CADASTRO DE TIPO DE DEVICE


@app.route('/cadastro/tipo-device', methods=['GET', 'POST'])
@login_required
def cadastro_tipo_device():
    if not current_user.can_view:
        flash("Você não tem permissão para visualizar esta página.", "danger")
        return redirect(url_for("index"))

    if request.method == 'POST':
        nome = request.form.get('nome')
        if nome:
            novo_device = TipoDevice(nome=nome)
            try:
                db.session.add(novo_device)
                db.session.commit()
                flash('Tipo de Device cadastrado com sucesso!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao cadastrar tipo de device. {str(e)}', 'danger')

        return redirect(url_for("cadastro_tipo_device"))

    devices = TipoDevice.query.order_by(TipoDevice.nome).all()
    return render_template('tipo_device.html', devices=devices)

# EDIT DE TIPO DE DEVICE

@app.route('/edit/tipo-device/<int:id>', methods=['POST'])
@login_required
def edit_tipo_device(id):
    if not current_user.can_edit:
        flash("Você não tem permissão para editar.", "danger")
        return redirect(url_for("cadastro_tipo_device"))

    nome = request.form.get('nome')
    device = TipoDevice.query.get_or_404(id)

    if nome:
        device.nome = nome
        try:
            db.session.commit()
            flash('Tipo de Device editado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao editar tipo de device. {str(e)}', 'danger')

    return redirect(url_for("cadastro_tipo_device"))

# DELETE DE TIPO DE DEVICE

@app.route('/delete/tipo-device/<int:id>', methods=['POST'])
@login_required
def delete_tipo_device(id):
    if not current_user.can_delete:
        flash("Você não tem permissão para deletar.", "danger")
        return redirect(url_for("cadastro_tipo_device"))

    device = TipoDevice.query.get_or_404(id)

    try:
        db.session.delete(device)
        db.session.commit()
        flash('Tipo de Device excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir tipo de device. {str(e)}', 'danger')

    return redirect(url_for("cadastro_tipo_device"))


# EXPORTAR EMPRESAS

@app.route('/exportar_empresas')
@login_required
def exportar_empresas():
    if not current_user.can_export:
        flash("Você não tem permissão para exportar.", "danger")
        return redirect(url_for("sensors"))

    empresas = Empresa.query.all()

    def gerar_csv():
        output = io.StringIO()
        writer = csv.writer(output)

        # Cabeçalho
        writer.writerow([
            'Nome', 'CNPJ', 'Telefone', 'Email',
            'Contato', 'Endereço', 'Cidade', 'Estado', 'CEP'
        ])

        # Dados
        for e in empresas:
            writer.writerow([
                e.nome or '',
                e.cnpj or '',
                e.telefone or '',
                e.email or '',
                e.contato or '',
                e.endereco or '',
                e.cidade or '',
                e.estado or '',
                e.cep or ''
            ])
        return output.getvalue()

    return Response(
        gerar_csv(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=empresas.csv'}
    )


# --------------   nova rota exportar --------------
@app.route("/exportar_sensores_csv")
@login_required
def exportar_sensores_csv():
    if not current_user.can_export:
        flash("Você não tem permissão para exportar.", "danger")
        return redirect(url_for("index"))

    # ---------- filtros recebidos via query‑string ----------
    f_tipo_device = request.args.get("f_tipo_device")
    f_tipo_sonda  = request.args.get("f_tipo_sonda")
    f_status      = request.args.get("f_status")
    f_empresa     = request.args.get("f_empresa")
    f_cidade      = request.args.get("f_cidade")
    f_uf          = request.args.get("f_uf")

    query = db.session.query(Sensor)
    if f_cidade or f_uf:
        query = query.join(Empresa, Sensor.empresa == Empresa.nome)

    if f_tipo_device:
        query = query.filter(Sensor.tipo_device == f_tipo_device)
    if f_tipo_sonda:
        query = query.filter(Sensor.tipo_sonda == f_tipo_sonda)
    if f_status:
        query = query.filter(Sensor.status == f_status)
    if f_empresa:
        query = query.filter(Sensor.empresa == f_empresa)
    if f_cidade:
        query = query.filter(Empresa.cidade == f_cidade)
    if f_uf:
        query = query.filter(Empresa.estado == f_uf)

    sensores = query.order_by(Sensor.criado_em.desc()).all()

    # ---------- gera CSV ----------
    buf = StringIO()
    w   = csv.writer(buf)
    w.writerow([
        "Empresa","Tipo de Device","Código do Sensor","Tipo de Sonda",
        "Código da Sonda","Responsável Tec","Status","Localização",
        "Nomenclatura","Local Calib.","Empresa Calib.",
        "Data Calib.","Próx. Calib."
    ])
    for s in sensores:
        w.writerow([
            s.empresa,
            s.tipo_device_rel.nome if s.tipo_device_rel else "—",
            s.codigo,
            s.tipo_sonda,
            s.codigo_sonda or "—",
            s.responsavel_tec or "—",
            s.status,
            s.localizacao or "—",
            s.nomenclatura or "—",
            s.local_calibracao or "—",
            s.empresa_calibracao or "—",
            s.data_calibracao or "—",
            s.proxima_calibracao or "—",
        ])

    resp = make_response(buf.getvalue())
    resp.headers["Content-Type"]        = "text/csv; charset=utf-8"
    resp.headers["Content-Disposition"] = "attachment; filename=sensores.csv"
    return resp


#----------------- Exportar Alerta sensor ------------------  
@app.route("/exportar_alerta", methods=["POST"])
@login_required
def exportar_alerta():
    if not current_user.can_export:
        flash("Você não tem permissão para exportar.", "danger")
        return redirect(url_for("index"))

    hoje = datetime.today().date()
    limite = hoje + timedelta(days=60)
    sensores = Sensor.query.filter(Sensor.proxima_calibracao <= limite).all()

    # Criação do CSV
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow([
        "Nome", "Código", "Tipo", "Status", "Empresa", "Localização", "Responsável Técnico", 
        "Contato", "Nomenclatura", "Data Calibração", "Próxima Calibração"
    ])
    for s in sensores:
        cw.writerow([
            s.nome, s.codigo, s.tipo_device, s.status, s.empresa, s.localizacao,
            s.responsavel_tec, s.contato, s.nomenclatura,
            s.data_calibracao, s.proxima_calibra
        ])
    
    output = io.BytesIO()
    output.write(si.getvalue().encode("utf-8"))
    output.seek(0)

    return send_file(output,
                     mimetype="text/csv",
                     download_name="sensores_para_calibrar.csv",
                     as_attachment=True)


# PARCEIROS ----------------------------------------------------------
# from models import db, Empresa, Parceiro, Estado, Municipio # These are already imported at the top


@app.route("/parceiros", methods=["GET", "POST"])
@login_required
def parceiros():
    if not current_user.can_view:
        flash("Você não tem permissão para visualizar esta página.", "danger")
        return redirect(url_for("index"))

    
    # return render_template("sensors.html") # Esta linha parece estar incorreta aqui - commented out as per previous analysis
    if request.method == "POST":
        nome = request.form.get("nome")
        telefone = request.form.get("telefone")
        cidade = request.form.get("cidade")
        uf = request.form.get("uf")
        cpf = request.form.get("cpf")
        pix = request.form.get("pix")
        cep = request.form.get("cep")
        rua = request.form.get("rua")
        numero = request.form.get("numero")
        complemento = request.form.get("complemento")
        bairro = request.form.get("bairro")
        emp_ids = request.form.getlist("empresas")

        novo = Parceiro(
            nome=nome,
            telefone=telefone,
            cidade=cidade,
            uf=uf,
            cpf=cpf,
            pix=pix,
            cep=cep,
            rua=rua,
            numero=numero,
            complemento=complemento,
            bairro=bairro,
        )

        if emp_ids:
            novo.empresas = Empresa.query.filter(Empresa.id.in_(emp_ids)).all()

        db.session.add(novo)
        db.session.commit()
        flash("Parceiro cadastrado com sucesso!", "success")
        return redirect(url_for("parceiros"))

    # -------------------- GET e Filtros ---------------------
    f_nome    = request.args.get("f_nome")
    f_empresa = request.args.get("f_empresa")
    f_uf      = request.args.get("f_uf")
    f_cidade  = request.args.get("f_cidade")


    query = db.session.query(Parceiro)

    if f_nome:
        query = query.filter(Parceiro.nome.ilike(f"%{f_nome}%"))

    if f_empresa:
        query = query.join(Parceiro.empresas).filter(Empresa.nome == f_empresa)

    if f_uf:
        query = query.filter(Parceiro.uf == f_uf)

    if f_cidade:
        query = query.filter(Parceiro.cidade == f_cidade)

    parceiros = query.order_by(Parceiro.nome).all()

    empresas = Empresa.query.order_by(Empresa.nome).all()
    estados  = Estado.query.order_by(Estado.sigla).all()
    cidades  = sorted(set(p.cidade for p in Parceiro.query.with_entities(Parceiro.cidade).distinct() if p.cidade))
    # Removed `nomes` as it was not used and likely a leftover

    return render_template(
        "parceiros.html",
        parceiros=parceiros,
        empresas=empresas,
        estados=estados,
        cidades=cidades # Added cities to context for template if needed
    )


@app.route('/buscar_cep/<cep>')
def buscar_cep(cep):
    try:
        r = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
        data = r.json()
        if "erro" in data:
            return jsonify({"erro": "CEP não encontrado"}), 404
        return jsonify(data)
    except Exception as e:
        return jsonify({"erro": "Erro ao buscar CEP", "detalhes": str(e)}), 500


@app.route("/municipios/<uf>")
def municipios_por_uf(uf):
    estado = Estado.query.filter_by(sigla=uf).first()
    if not estado:
        return jsonify([])
    municipios = [m.nome for m in estado.municipios]
    return jsonify(municipios)

#------EXPORTAR PARCEIROS----------
@app.route("/exportar_parceiros_csv") # Adicionando a rota para esta função
@login_required
def exportar_parceiros_csv():
    if not current_user.can_export:
        flash("Você não tem permissão para exportar.", "danger")
        return redirect(url_for("parceiros"))
    
    f_nome    = request.args.get("f_nome")
    f_empresa = request.args.get("f_empresa")
    f_uf      = request.args.get("f_uf")
    f_cidade  = request.args.get("f_cidade")

    query = db.session.query(Parceiro)

    if f_nome:
        query = query.filter(Parceiro.nome.ilike(f"%{f_nome}%"))

    if f_empresa:
        query = query.join(Parceiro.empresas).filter(Empresa.nome == f_empresa)

    if f_uf:
        query = query.filter(Parceiro.uf == f_uf)

    if f_cidade:
        query = query.filter(Parceiro.cidade == f_cidade)

    parceiros = query.order_by(Parceiro.nome).all()

    # Gera CSV em memória
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Nome", "Telefone", "Cidade", "UF", "CPF", "Pix", "CEP", "Rua", "Número", "Complemento", "Bairro", "Empresas"])

    for p in parceiros:
        empresas = ", ".join([e.nome for e in p.empresas])
        writer.writerow([p.nome, p.telefone, p.cidade, p.uf, p.cpf, p.pix, p.cep, p.rua, p.numero, p.complemento, p.bairro, empresas])

    output.seek(0)
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=parceiros.csv"})

#-------------UF-Cidade-Dinamica------------

@app.route("/get_municipios/<sigla_uf>")
def get_municipios(sigla_uf):
    estado = Estado.query.filter_by(sigla=sigla_uf).first()
    if estado:
        municipios = Municipio.query.filter_by(estado_id=estado.id).order_by(Municipio.nome).all()
        return jsonify([m.nome for m in municipios])
    return jsonify([])


#------------EDITAR PARCEIRO-----------
@app.route("/editar_parceiro/<int:id>", methods=["GET", "POST"])
@login_required
def editar_parceiro(id):
    if not current_user.can_edit:
        flash("Você não tem permissão para editar.", "danger")
        return redirect(url_for("parceiros")) # Corrected redirect target
    parceiro = db.session.get(Parceiro, id)
    empresas = Empresa.query.all()
    estados = Estado.query.order_by(Estado.nome).all()
    estado = Estado.query.filter_by(sigla=parceiro.uf).first()
    municipios = Municipio.query.filter_by(estado_id=estado.id).order_by(Municipio.nome).all() if estado else []

    if request.method == "POST":
        parceiro.nome        = request.form.get("nome")
        parceiro.telefone    = request.form.get("telefone")
        parceiro.cep         = request.form.get("cep")
        parceiro.rua         = request.form.get("rua")
        parceiro.numero      = request.form.get("numero")
        parceiro.complemento = request.form.get("complemento")
        parceiro.bairro      = request.form.get("bairro")
        parceiro.uf          = request.form.get("uf")
        parceiro.cidade      = request.form.get("cidade")
        parceiro.cpf         = request.form.get("cpf")
        parceiro.pix         = request.form.get("pix")

        # empresas
        empresas_ids = request.form.getlist("empresas")
        parceiro.empresas = Empresa.query.filter(Empresa.id.in_(empresas_ids)).all()

        db.session.commit()
        flash("Parceiro atualizado com sucesso!", "success")
        return redirect(url_for("parceiros"))

    return render_template("editar_parceiro.html", parceiro=parceiro, empresas=empresas, estados=estados, municipios=municipios)

#------------DELETAR PARCEIRO-----------

@app.route("/delete_parceiro/<int:id>", methods=["POST"])
@login_required
def delete_parceiro(id):
    if not current_user.can_delete:
        flash("Você não tem permissão para deletar.", "danger")
        return redirect(url_for("parceiros"))

    parceiro = db.session.get(Parceiro, id)
    if parceiro:
        db.session.delete(parceiro)
        db.session.commit()
        flash("Parceiro excluído com sucesso!", "success")
    else:
        flash("Parceiro não encontrado.", "danger")

    return redirect(url_for("parceiros"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
