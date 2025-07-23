from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import db, TipoDevice, TipoSonda, Empresa, Sensor
import os

# Caminho do banco SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
sqlite_url = f"sqlite:///{os.path.join(basedir, 'inventory.db')}"

# Conexão com PostgreSQL no Azure (corrigida)
postgres_url = "postgresql+psycopg2://adminsentinel360%40sentinel360server:%40Sen360banco123@sentinel360server.postgres.database.azure.com:5432/inventory_db"

# Criar engines
engine_sqlite = create_engine(sqlite_url)
SessionSQLite = sessionmaker(bind=engine_sqlite)
session_sqlite = SessionSQLite()

engine_postgres = create_engine(postgres_url)
SessionPostgres = sessionmaker(bind=engine_postgres)
session_postgres = SessionPostgres()

def migrar_modelos(Model):
    dados = session_sqlite.query(Model).all()
    for item in dados:
        novo = Model(**{col.name: getattr(item, col.name) for col in Model.__table__.columns})
        session_postgres.add(novo)
    session_postgres.commit()
    print(f"{Model.__tablename__}: {len(dados)} registros migrados.")

def main():
    print("🚀 Iniciando migração dos dados...")

    migrar_modelos(TipoDevice)
    migrar_modelos(TipoSonda)
    migrar_modelos(Empresa)
    migrar_modelos(Sensor)

    print("✅ Migração concluída.")

if __name__ == "__main__":
    main()
