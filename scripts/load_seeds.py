import json
import os
import sys

# Adiciona diretório pai ao path para permitir imports de app/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from geoalchemy2 import WKTElement

from app.core.database import SessionLocal
from app.fazendas.models_sqla import AreaImovel


def load_seeds():
    print("Carregando dados de seed...")

    # Obtém o diretório onde este script está localizado
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Sobe um nível para a raiz do projeto para encontrar seeds.json
    project_root = os.path.dirname(script_dir)
    seeds_file = os.path.join(project_root, "seeds.json")

    # Lê seeds do arquivo JSON
    with open(seeds_file, "r", encoding="utf-8") as f:
        seeds = json.load(f)

    db = SessionLocal()
    try:
        # Verifica se os dados já existem
        existing_count = db.query(AreaImovel).count()
        if existing_count > 0:
            print(
                f"Banco de dados já possui {existing_count} registros. Pulando dados de seed."
            )
            return

        # Insere dados de seed
        for seed in seeds:
            # Converte geometria hex para formato WKT
            geom_hex = seed["geom"]

            fazenda = AreaImovel(
                gid=seed["gid"],
                cod_tema=seed.get("cod_tema"),
                nom_tema=seed.get("nom_tema"),
                cod_imovel=seed.get("cod_imovel"),
                mod_fiscal=seed.get("mod_fiscal"),
                num_area=seed.get("num_area"),
                ind_status=seed.get("ind_status"),
                ind_tipo=seed.get("ind_tipo"),
                des_condic=seed.get("des_condic"),
                municipio=seed.get("municipio"),
                cod_estado=seed.get("cod_estado"),
                dat_criaca=seed.get("dat_criaca"),
                dat_atuali=seed.get("dat_atuali"),
                geom=geom_hex,  # PostGIS pode manipular geometria codificada em hex diretamente
            )
            db.add(fazenda)

        db.commit()
        print(f"Carregados com sucesso {len(seeds)} registros de seed.")
    except Exception as e:
        db.rollback()
        print(f"Erro ao carregar seeds: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    load_seeds()
