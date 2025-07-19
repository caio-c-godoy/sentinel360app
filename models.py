from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from flask import current_app


db = SQLAlchemy()

# ────────────────────────────────────────────────────────────
#  EMPRESA  (única definição)
# ────────────────────────────────────────────────────────────
class Empresa(db.Model):
    __tablename__ = "empresas"

    id      = db.Column(db.Integer, primary_key=True)
    nome    = db.Column(db.String(120), unique=True, nullable=False)

    # dados administrativos
    cnpj    = db.Column(db.String(20))
    endereco = db.Column(db.String(200))
    telefone = db.Column(db.String(20))
    contato  = db.Column(db.String(100))
    email    = db.Column(db.String(120))

    # localização
    cidade   = db.Column(db.String(80))
    estado   = db.Column(db.String(2))
    cep      = db.Column(db.String(10))

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # parceiros N:N
    parceiros = db.relationship(
        "Parceiro",
        secondary="parceiros_empresas",
        back_populates="empresas",
    )

    def __repr__(self):
        return f"<Empresa {self.nome}>"


# ────────────────────────────────────────────────────────────
#  TABELA DE ASSOCIAÇÃO Parceiro x Empresa (N:N)
# ────────────────────────────────────────────────────────────
parceiros_empresas = db.Table(
    "parceiros_empresas",
    db.Column("parceiro_id", db.Integer, db.ForeignKey("parceiros.id")),
    db.Column("empresa_id",  db.Integer, db.ForeignKey("empresas.id")),
)


# ────────────────────────────────────────────────────────────
#  PARCEIRO
# ────────────────────────────────────────────────────────────
class Parceiro(db.Model):
    __tablename__ = "parceiros"

    id       = db.Column(db.Integer, primary_key=True)
    nome     = db.Column(db.String(120), nullable=False, unique=True)
    telefone = db.Column(db.String(40))
    cidade   = db.Column(db.String(80))
    uf       = db.Column(db.String(2))
    cpf      = db.Column(db.String(14))
    pix      = db.Column(db.String(100))
    cep      = db.Column(db.String(80))
    rua      = db.Column(db.String(120))
    numero   = db.Column(db.String(14))
    complemento = db.Column(db.String(40))
    bairro   = db.Column(db.String(120))

    empresas = db.relationship(
        "Empresa",
        secondary=parceiros_empresas,
        back_populates="parceiros",
    )

    def __repr__(self):
        return f"<Parceiro {self.nome}>"


# ────────────────────────────────────────────────────────────
#  TIPOS
# ────────────────────────────────────────────────────────────
class TipoSonda(db.Model):
    __tablename__ = "tipos_sonda"

    id        = db.Column(db.Integer, primary_key=True)
    nome      = db.Column(db.String(100), unique=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TipoSonda {self.nome}>"


class TipoDevice(db.Model):
    __tablename__ = "tipos_device"

    id        = db.Column(db.Integer, primary_key=True)
    nome      = db.Column(db.String(100), unique=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TipoDevice {self.nome}>"


# ────────────────────────────────────────────────────────────
#  SENSOR
# ────────────────────────────────────────────────────────────
class Sensor(db.Model):
    __tablename__ = "sensors"

    id   = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

    codigo        = db.Column(db.String(100), unique=True, nullable=False)
    codigo_sonda  = db.Column(db.String(100))

    empresa       = db.Column(db.String(100))  # mantém como texto curto
    tipo_device   = db.Column(db.Integer, db.ForeignKey("tipos_device.id"))
    tipo_sonda    = db.Column(db.Integer, db.ForeignKey("tipos_sonda.id"))

    status        = db.Column(db.String(50))
    localizacao   = db.Column(db.String(100))
    estoque_minimo = db.Column(db.Integer)
    criado_em     = db.Column(db.DateTime, default=datetime.utcnow)

    certificado_path = db.Column(db.String(200))
    responsavel_tec  = db.Column(db.String(100))
    contato          = db.Column(db.String(100))

    data_calibracao    = db.Column(db.Date)
    proxima_calibracao = db.Column(db.Date)

    nomenclatura       = db.Column(db.String(100))
    local_calibracao   = db.Column(db.String(100))
    empresa_calibracao = db.Column(db.String(100))

    # relacionamento para obter nome do tipo de device
    tipo_device_rel = db.relationship("TipoDevice")

    def __repr__(self):
        return f"<Sensor {self.nome}>"


# ────────────────────────────────────────────────────────────
#  MODELOS ADICIONAIS (se estiverem em uso)
# ────────────────────────────────────────────────────────────
class Product(db.Model):
    __tablename__ = "products"

    product_id    = db.Column(db.String(200), primary_key=True)
    date_created  = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Product {self.product_id}>"


class Location(db.Model):
    __tablename__ = "locations"

    location_id   = db.Column(db.String(200), primary_key=True)
    date_created  = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Location {self.location_id}>"
# ─── IBGE ─────────────────────────────────────────────────────────────
class Estado(db.Model):
    __tablename__ = "estados"

    id     = db.Column(db.Integer, primary_key=True)       # id IBGE
    sigla  = db.Column(db.String(2),  unique=True, nullable=False)
    nome   = db.Column(db.String(80), nullable=False)

    # 1 → N   (um estado → muitas cidades)
    municipios = db.relationship(
        "Municipio",
        back_populates="estado",
        order_by="Municipio.nome",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Estado {self.sigla}>"


class Municipio(db.Model):
    __tablename__ = "municipios"

    id        = db.Column(db.Integer, primary_key=True)    # id IBGE
    nome      = db.Column(db.String(120), nullable=False)
    estado_id = db.Column(db.Integer, db.ForeignKey("estados.id"))

    estado    = db.relationship("Estado", back_populates="municipios")

    def __repr__(self):
        return f"<Municipio {self.nome}/{self.estado.sigla}>"

#----------------Configuracao Usuarios------

class User(db.Model, UserMixin):  # <- HERDA DE UserMixin
    __tablename__ = "usuarios"
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    
    reset_token = db.Column(db.String(100), nullable=True)
    
    permissoes = db.Column(db.JSON, nullable=True)
    
    can_view = db.Column(db.Boolean, default=False)
    can_create = db.Column(db.Boolean, default=False)
    can_edit = db.Column(db.Boolean, default=False)
    can_delete = db.Column(db.Boolean, default=False)
    can_export = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    trocar_senha = db.Column(db.Boolean, default=False)

    def set_password(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_password(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f"<User {self.email}>"

    def get_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expires_sec)
            user_id = data['user_id']
        except Exception:
            return None
        return User.query.get(user_id)


