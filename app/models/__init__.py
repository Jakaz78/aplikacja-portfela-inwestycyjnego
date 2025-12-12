# app/models/__init__.py

# Importujemy obiekt db, żeby był dostępny
from .. import db


# Funkcja importująca modele (używana w create_app)
def import_models():
    from . import user
    from . import portfolio
    from . import bond_definition
    from . import holding
    from . import transaction

    # --- NOWE MODELE ---
    from . import user_settings
    from . import portfolio_history
    # -------------------