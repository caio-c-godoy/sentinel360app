from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import func
from datetime import datetime
from werkzeug.utils import secure_filename
from models import TipoDevice, TipoSonda, Empresa


import os

from models import db, Empresa, TipoSonda, TipoDevice, Sensor

app = Flask(__name__)
app.secret_key = '1q2w3e!Q@W#E'

# Caminho absoluto para o arquivo SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'inventory.db')}"

# Debug config
app.config['DEBUG'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True

db.init_app(app)
migrate = Migrate(app, db)


@app.route('/')
def index():
    sensores_por_device = db.session.query(TipoDevice.nome, func.count(Sensor.id))\
        .select_from(Sensor)\
        .join(TipoDevice, Sensor.tipo == TipoDevice.id)\
        .group_by(TipoDevice.nome).all()

    total_sensores = sum([count for _, count in sensores_por_device]) or 1
    sensores_por_device_pct = [(nome, round(count / total_sensores * 100, 2), count) for nome, count in sensores_por_device]

    sensores_por_tipo_sonda = db.session.query(TipoSonda.nome, func.count(Sensor.id))\
        .select_from(Sensor)\
        .join(TipoSonda, Sensor.tipo_sonda == TipoSonda.id)\
        .group_by(TipoSonda.nome).all()

    sensores_por_status_query = db.session.query(Sensor.status, func.count(Sensor.id))\
        .group_by(Sensor.status).all()

    sensores_por_status = [
        {"status": status, "count": count} for status, count in sensores_por_status_query
    ]

    return render_template(
        "index.html",
        sensores_por_device=sensores_por_device_pct,
        sensores_por_tipo_sonda=sensores_por_tipo_sonda,
        sensores_por_status=sensores_por_status
    )


UPLOAD_FOLDER = 'static/certificados'  # pasta onde salvará os arquivos
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/form-upload-certificado/<int:id>', methods=['GET'])
def upload_certificado_form(id):
    sensor = Sensor.query.get_or_404(id)
    return render_template('upload_certificado.html', sensor=sensor)


@app.route('/upload-certificado/<int:id>', methods=['POST'])
def upload_certificado(id):
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

    return redirect(url_for('sensors'))  # redireciona para a listagem


@app.route('/sensors', methods=["GET", "POST"])
def sensors():
    if request.method == 'POST':
        nome = request.form['nome']
        codigo = request.form['codigo']
        tipo = request.form['tipo']
        status = request.form['status']
        localizacao = request.form['localizacao']
        empresa = request.form['empresa']
        responsavel_tec = request.form.get('responsavel_tec')
        contato = request.form.get('contato')
        data_calibracao = request.form.get('data_calibracao')
        proxima_calibracao = request.form.get('proxima_calibracao')
        nomenclatura = request.form.get('nomenclatura')
        local_calibracao = request.form.get('local_calibracao')
        empresa_calibracao = request.form.get('empresa_calibracao')

        novo_sensor = Sensor(
            nome=nome,
            codigo=codigo,
            tipo=tipo,
            status=status,
            localizacao=localizacao,
            empresa=empresa,
            responsavel_tec=responsavel_tec,
            contato=contato,
            data_calibracao=data_calibracao,
            proxima_calibracao=proxima_calibracao,
            nomenclatura=nomenclatura,
            local_calibracao=local_calibracao,
            empresa_calibracao=empresa_calibracao
        )

        try:
            db.session.add(novo_sensor)
            db.session.commit()
            flash('Sensor cadastrado com sucesso!', 'success')
            return redirect('/sensors')
        except Exception as e:
            db.session.rollback()
            if 'UNIQUE constraint failed: sensors.codigo' in str(e):
                flash('Erro: já existe um sensor com esse código.', 'danger')
            else:
                flash('Erro ao cadastrar o sensor.', 'danger')

    # FILTROS
    filtro_nome = request.args.get('filtro_nome')
    filtro_tipo = request.args.get('filtro_tipo')
    filtro_status = request.args.get('filtro_status')
    filtro_empresa = request.args.get('filtro_empresa')
    filtro_localizacao = request.args.get('filtro_localizacao')

    query = Sensor.query

    if filtro_nome:
        query = query.filter(Sensor.nome.ilike(f'%{filtro_nome}%'))
    if filtro_tipo:
        query = query.filter(Sensor.tipo.ilike(f'%{filtro_tipo}%'))
    if filtro_status:
        query = query.filter(Sensor.status.ilike(f'%{filtro_status}%'))
    if filtro_empresa:
        query = query.filter(Sensor.empresa.ilike(f'%{filtro_empresa}%'))
    if filtro_localizacao:
        query = query.filter(Sensor.localizacao.ilike(f'%{filtro_localizacao}%'))

    sensores = query.order_by(Sensor.criado_em.desc()).all()

    devices = TipoDevice.query.order_by(TipoDevice.nome).all()
    sondas = TipoSonda.query.order_by(TipoSonda.nome).all()
    empresas = Empresa.query.order_by(Empresa.nome).all()

    return render_template(
        'sensors.html',
        sensores=sensores,
        devices=devices,
        sondas=sondas,
        empresas=empresas
    )


@app.route('/delete_sensor/<int:id>', methods=['POST'])
def delete_sensor(id):
    sensor = Sensor.query.get_or_404(id)
    try:
        db.session.delete(sensor)
        db.session.commit()
        flash('Sensor excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir o sensor.', 'danger')
    return redirect('/sensors')


@app.route('/sensors/<int:id>/edit', methods=['GET', 'POST'])
def edit_sensor(id):
    sensor = Sensor.query.get_or_404(id)
    devices = TipoDevice.query.all()
    sondas = TipoSonda.query.all()
    empresas = Empresa.query.all()

    if request.method == 'POST':
        sensor.tipo_device = request.form.get('tipo_device')
        sensor.codigo = request.form.get('codigo')
        sensor.tipo_sonda = request.form.get('tipo_sonda')
        sensor.status = request.form.get('status')
        sensor.localizacao = request.form.get('localizacao')
        sensor.empresa = request.form.get('empresa')
        sensor.responsavel_tec = request.form.get('responsavel_tec')
        sensor.contato = request.form.get('contato')
        sensor.nomenclatura = request.form.get('nomenclatura')
        sensor.local_calibracao = request.form.get('local_calibracao')
        sensor.empresa_calibracao = request.form.get('empresa_calibracao')
        
        # Datas com conversão segura
        try:
            sensor.data_calibracao = datetime.strptime(request.form.get('data_calibracao'), '%Y-%m-%d') if request.form.get('data_calibracao') else None
        except:
            sensor.data_calibracao = None

        try:
            sensor.proxima_calibracao = datetime.strptime(request.form.get('proxima_calibracao'), '%Y-%m-%d') if request.form.get('proxima_calibracao') else None
        except:
            sensor.proxima_calibracao = None

        db.session.commit()
        flash('Sensor atualizado com sucesso!', 'success')
        return redirect(url_for('list_sensors'))

    return render_template('edit_sensor.html', sensor=sensor, devices=devices, sondas=sondas, empresas=empresas)



# CADASTRO DE EMPRESA
@app.route('/cadastro/empresa', methods=['GET', 'POST'])
def cadastro_empresa():
    if request.method == 'POST':
        nome = request.form.get('nome')
        cnpj = request.form.get('cnpj')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        contato=request.form['contato']
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

    empresas = Empresa.query.order_by(Empresa.nome).all()
    return render_template('empresa.html', empresas=empresas)


# EDITAR CADASTRO DE EMPRESA
@app.route('/edit/empresa/<int:id>', methods=['POST'])
def edit_empresa(id):
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
def delete_empresa(id):
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
def cadastro_tipo_sonda():
    if request.method == 'POST':
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
def edit_tipo_sonda(id):
    sonda = TipoSonda.query.get_or_404(id)
    novo_nome = request.form.get('nome')
    if novo_nome:
        try:
            sonda.nome = novo_nome
            db.session.commit()
            flash('Tipo de Sonda atualizado com sucesso!', 'success')
        except:
            db.session.rollback()
            flash('Erro ao atualizar tipo de sonda.', 'danger')
    return redirect('/cadastro/tipo-sonda')

#DELETAR CADASTRO DE TIPO DE SONDA

@app.route('/cadastro/tipo-sonda/<int:id>/excluir', methods=['POST'])
def delete_tipo_sonda(id):
    sonda = TipoSonda.query.get_or_404(id)
    try:
        db.session.delete(sonda)
        db.session.commit()
        flash('Tipo de Sonda excluído com sucesso!', 'success')
    except:
        db.session.rollback()
        flash('Erro ao excluir tipo de sonda.', 'danger')
    return redirect('/cadastro/tipo-sonda')


@app.route('/cadastro/tipo-device', methods=['GET', 'POST'])
def cadastro_tipo_device():
    if request.method == 'POST':
        nome = request.form.get('nome')
        if nome:
            novo_device = TipoDevice(nome=nome)
            try:
                db.session.add(novo_device)
                db.session.commit()
                flash('Tipo de Device cadastrado com sucesso!', 'success')
            except:
                db.session.rollback()
                flash('Erro ao cadastrar tipo de device.', 'danger')
        return redirect('/cadastro/tipo-device')

    devices = TipoDevice.query.order_by(TipoDevice.nome).all()
    return render_template('tipo_device.html', devices=devices)


@app.route('/edit/tipo-device/<int:id>', methods=['POST'])
def edit_tipo_device(id):
    nome = request.form.get('nome')
    device = TipoDevice.query.get_or_404(id)
    if nome:
        device.nome = nome
        try:
            db.session.commit()
            flash('Tipo de Device editado com sucesso!', 'success')
        except:
            db.session.rollback()
            flash('Erro ao editar tipo de device.', 'danger')
    return redirect('/cadastro/tipo-device')


@app.route('/delete/tipo-device/<int:id>', methods=['POST'])
def delete_tipo_device(id):
    device = TipoDevice.query.get_or_404(id)
    try:
        db.session.delete(device)
        db.session.commit()
        flash('Tipo de Device excluído com sucesso!', 'success')
    except:
        db.session.rollback()
        flash('Erro ao excluir tipo de device.', 'danger')
    return redirect('/cadastro/tipo-device')


if (__name__ == "__main__"):
    with app.app_context():
        db.create_all()
    app.run(debug=True)

app.config['DEBUG'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True

import csv
from flask import Response

@app.route('/exportar_empresas')
def exportar_empresas():
    empresas = Empresa.query.all()

    def gerar_csv():
        data = []
        header = ['Nome', 'CNPJ', 'Telefone', 'Email', 'Contato', 'Endereço', 'Cidade', 'Estado', 'CEP']
        data.append(header)
        for e in empresas:
            data.append([
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
        # Gera o conteúdo do CSV
        si = csv.StringIO()
        writer = csv.writer(si)
        writer.writerows(data)
        return si.getvalue()

    return Response(
        gerar_csv(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=empresas.csv'}
    )