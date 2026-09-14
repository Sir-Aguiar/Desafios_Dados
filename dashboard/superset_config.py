import os

# Segredo de sessão
SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "desafio_dados_fic_dev_secret_key_2026_super_safe")

# Habilitar acesso público e iframe embutido
AUTH_ROLE_PUBLIC = "Admin"
PUBLIC_ROLE_LIKE_GAMMA = True

# Feature Flags
FEATURE_FLAGS = {
    "EMBEDDED_SUPERSET": True,
    "DASHBOARD_NATIVE_FILTERS": True,
}

# Desativar restrições de CSP/Talisman para permitir iframe
TALISMAN_ENABLED = False
HTTP_HEADERS = {}

# Habilitar CORS
ENABLE_CORS = True
CORS_OPTIONS = {
    "supports_credentials": True,
    "allow_headers": ["*"],
    "resources": ["*"],
    "origins": ["*"]
}

# Configuração de cookies para permitir iframe
SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = False
