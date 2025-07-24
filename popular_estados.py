from app import app, db
from models import Estado, Municipio
import requests

def popular_estados_municipios():
    url_estados = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
    estados = requests.get(url_estados).json()

    for estado in estados:
        uf = Estado(id=estado["id"], nome=estado["nome"], sigla=estado["sigla"])
        db.session.add(uf)

        url_municipios = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{estado['id']}/municipios"
        municipios = requests.get(url_municipios).json()
        for m in municipios:
            municipio = Municipio(id=m["id"], nome=m["nome"], estado_id=estado["id"])
            db.session.add(municipio)

    db.session.commit()
    print("Estados e municípios populados com sucesso.")

if __name__ == "__main__":
    with app.app_context():
        popular_estados_municipios()
