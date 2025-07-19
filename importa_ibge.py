import requests
from models import db, Estado, Municipio
from app import app

def importar_estados_e_cidades():
    with app.app_context():
        # Remove registros anteriores (opcional)
        db.session.query(Municipio).delete()
        db.session.query(Estado).delete()
        db.session.commit()

        # Buscar todos os estados
        estados_res = requests.get("https://servicodados.ibge.gov.br/api/v1/localidades/estados").json()
        estados_ordenados = sorted(estados_res, key=lambda x: x['sigla'])

        for estado in estados_ordenados:
            novo_estado = Estado(id=estado['id'], sigla=estado['sigla'], nome=estado['nome'])
            db.session.add(novo_estado)
            db.session.flush()  # Garante que o ID esteja disponível

            # Buscar municípios deste estado
            municipios_res = requests.get(f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{estado['id']}/municipios").json()
            for mun in municipios_res:
                novo_mun = Municipio(id=mun['id'], nome=mun['nome'], estado_id=estado['id'])
                db.session.add(novo_mun)

        db.session.commit()
        print("Importação concluída com sucesso.")

if __name__ == "__main__":
    importar_estados_e_cidades()
