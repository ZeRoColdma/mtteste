import os
import sys

# Adiciona diretório pai ao path para permitir imports de app/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, engine
from app.fazendas import models_sqla

print("Criando tabelas do banco de dados...")
Base.metadata.create_all(bind=engine)
print("Tabelas criadas.")

# Carrega dados de seed
try:
    from scripts.load_seeds import load_seeds

    load_seeds()
except Exception as e:
    print(f"Aviso: Não foi possível carregar dados de seed: {e}")
