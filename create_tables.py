from app import db, app
from models import Sensor, Empresa, TipoSonda, TipoDevice, Product, Location

with app.app_context():
    db.drop_all()     # Remove tudo se já existir (opcional)
    db.create_all()   # Cria as tabelas
    print("Tabelas criadas com sucesso!")
