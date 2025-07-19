"""
Baixa a lista oficial de UF / municípios do IBGE
e popula as tabelas Estado e Municipio.
Execute apenas quando precisar atualizar o cadastro.
"""
from pathlib import Path
import requests, sys

# ── coloca a pasta do projeto no PYTHONPATH ──────────────────────────
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import app                 # instancia do Flask (já contém db)
from models import db, Estado, Municipio

UF_URL  = "https://servicodados.ibge.gov.br/api/v1/localidades/estados?orderBy=nome"
MUN_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios?orderBy=nome"


def main() -> None:
    with app.app_context():
        print("⋯ Limpando tabelas Estado/Municipio")
        db.session.query(Municipio).delete()
        db.session.query(Estado).delete()

        print("⋯ Baixando estados do IBGE")
        estados = requests.get(UF_URL, timeout=30).json()

        for est_json in estados:
            est = Estado(
                id=est_json["id"],
                sigla=est_json["sigla"],
                nome=est_json["nome"]
            )
            db.session.add(est)
            print(f"  ▸ {est.sigla}")

            # municípios daquele estado
            munic = requests.get(MUN_URL.format(uf=est.id), timeout=30).json()
            for m in munic:
                db.session.add(
                    Municipio(id=m["id"], nome=m["nome"], estado=est)
                )

        db.session.commit()
        print("✓ Estados e municípios gravados com sucesso!")


if __name__ == "__main__":
    main()
