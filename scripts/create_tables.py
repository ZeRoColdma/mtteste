import os
import sys

# Add parent directory to path to allow imports from app/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, engine
from app.fazendas import models_sqla

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Tables created.")

# Load seed data
try:
    from scripts.load_seeds import load_seeds

    load_seeds()
except Exception as e:
    print(f"Warning: Could not load seed data: {e}")
