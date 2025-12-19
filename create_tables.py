from apps.core.database import Base, engine
from apps.fazendas import models_sqla

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Tables created.")

# Load seed data
try:
    from load_seeds import load_seeds

    load_seeds()
except Exception as e:
    print(f"Warning: Could not load seed data: {e}")
