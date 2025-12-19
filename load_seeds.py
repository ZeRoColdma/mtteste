import json
import os

from geoalchemy2 import WKTElement

from apps.core.database import SessionLocal
from apps.fazendas.models_sqla import AreaImovel


def load_seeds():
    print("Loading seed data...")

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    seeds_file = os.path.join(script_dir, "seeds.json")

    # Read seeds from JSON file
    with open(seeds_file, "r", encoding="utf-8") as f:
        seeds = json.load(f)

    db = SessionLocal()
    try:
        # Check if data already exists
        existing_count = db.query(AreaImovel).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} records. Skipping seed data.")
            return

        # Insert seed data
        for seed in seeds:
            # Convert hex geometry to WKT format
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
                geom=geom_hex,  # PostGIS can handle hex-encoded geometry directly
            )
            db.add(fazenda)

        db.commit()
        print(f"Successfully loaded {len(seeds)} seed records.")
    except Exception as e:
        db.rollback()
        print(f"Error loading seeds: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    load_seeds()
