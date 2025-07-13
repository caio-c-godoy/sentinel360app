from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Sensor(db.Model):
    __tablename__ = 'sensors'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(100), unique=True, nullable=False)
    empresa = db.Column(db.String(100))
    tipo = db.Column(db.String(50))
    status = db.Column(db.String(50))
    localizacao = db.Column(db.String(100))
    estoque_minimo = db.Column(db.Integer)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Sensor {self.nome}>'

class Empresa(db.Model):
    __tablename__ = 'empresas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
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

class ProductMovement(db.Model):
    __tablename__ = 'productmovements'

    movement_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(200), db.ForeignKey('products.product_id'))
    qty = db.Column(db.Integer)
    from_location = db.Column(db.String(200), db.ForeignKey('locations.location_id'))
    to_location = db.Column(db.String(200), db.ForeignKey('locations.location_id'))
    movement_time = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', foreign_keys=[product_id])
    fromLoc = db.relationship('Location', foreign_keys=[from_location])
    toLoc = db.relationship('Location', foreign_keys=[to_location])

    def __repr__(self):
        return f'<ProductMovement {self.movement_id}>'
