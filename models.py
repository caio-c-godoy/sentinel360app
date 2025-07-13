from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Sensor(db.Model):
    __tablename__ = 'sensors'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(100), unique=True, nullable=False)
    empresa = db.Column(db.String(100))
    tipo = db.Column(db.Integer, db.ForeignKey('tipos_device.id'))
    tipo_sonda = db.Column(db.Integer, db.ForeignKey('tipos_sonda.id'))
    status = db.Column(db.String(50))         # Ex: Em estoque, Em uso, Danificado
    localizacao = db.Column(db.String(100))   # Ex: Cliente, Estoque, Em manutenção
    estoque_minimo = db.Column(db.Integer)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    certificado_path = db.Column(db.String(200))  # caminho do arquivo PDF
    responsavel_tec = db.Column(db.String(100))
    contato = db.Column(db.String(100))
    data_calibracao = db.Column(db.Date)
    proxima_calibracao = db.Column(db.Date)
    nomenclatura = db.Column(db.String(100))
    local_calibracao = db.Column(db.String(100))
    empresa_calibracao = db.Column(db.String(100))


    def __repr__(self):
        return f'<Sensor {self.nome}>'

class Empresa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cnpj = db.Column(db.String(20), nullable=True)
    endereco = db.Column(db.String(200), nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    contato = db.Column(db.String(100))
    email = db.Column(db.String(120), nullable=True)
    cidade = db.Column(db.String(50), nullable=True)
    estado = db.Column(db.String(2), nullable=True)
    cep = db.Column(db.String(10), nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Empresa {self.nome}>'

class TipoSonda(db.Model):
    __tablename__ = 'tipos_sonda'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<TipoSonda {self.nome}>'

class TipoDevice(db.Model):
    __tablename__ = 'tipos_device'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<TipoDevice {self.nome}>'

class Product(db.Model):
    __tablename__ = 'products'

    product_id = db.Column(db.String(200), primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.product_id}>'

class Location(db.Model):
    __tablename__ = 'locations'

    location_id = db.Column(db.String(200), primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Location {self.location_id}>'
