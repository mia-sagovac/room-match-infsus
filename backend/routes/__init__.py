"""Blueprintovi grupirani po use-caseovima i šifrarnicima."""
from .auth import bp as auth_bp
from .profil import bp as profil_bp
from .upitnik import bp as upitnik_bp
from .match import bp as match_bp
from .razgovor import bp as razgovor_bp
from .oglas import bp as oglas_bp
from .pitanje import bp as pitanje_bp                  # DZ2: šifrarnik
from .upitnik_admin import bp as upitnik_admin_bp      # DZ2: master-detail

ALL_BLUEPRINTS = [
    auth_bp, profil_bp, upitnik_bp, match_bp, razgovor_bp, oglas_bp,
    pitanje_bp, upitnik_admin_bp,
]
