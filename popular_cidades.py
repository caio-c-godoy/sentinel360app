from app import app
from models import db, Estado, Municipio

# Lista com todas as cidades do Brasil (UF -> lista de cidades)
# Exemplo resumido para SP e RJ – posso te mandar o completo depois (5000+ cidades)
cidades_por_estado = {
    'SP': ['São Paulo', 'Campinas', 'Santos', 'São Bernardo do Campo', 'Ribeirão Preto'],
    'RJ': ['Rio de Janeiro', 'Niterói', 'Petrópolis', 'Volta Redonda', 'Campos dos Goytacazes'],
    'MG': ['Belo Horizonte', 'Uberlândia', 'Contagem', 'Juiz de Fora', 'Betim'],
    'BA': ['Salvador', 'Feira de Santana', 'Vitória da Conquista', 'Camaçari'],
    'RS': ['Porto Alegre', 'Caxias do Sul', 'Pelotas', 'Santa Maria'],
    # Adicionaremos todas depois se quiser, ou importar de CSV
}

with app.app_context():
    total = 0
    for sigla, cidades in cidades_por_estado.items():
        estado = Estado.query.filter_by(sigla=sigla).first()
        if not estado:
            print(f"Estado com sigla {sigla} não encontrado.")
            continue
        for nome_cidade in cidades:
            municipio = Municipio(nome=nome_cidade, estado_id=estado.id)
            db.session.add(municipio)
            total += 1

    db.session.commit()
    print(f"✅ Inseridas {total} cidades com sucesso.")
