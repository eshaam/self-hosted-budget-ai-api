from .config import settings


def load_keys(file_path):
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


def verify_api_key(api_key: str):
    valid_keys = load_keys(settings.API_KEYS_FILE)
    return api_key in valid_keys


def is_whitelisted(ip: str):
    if settings.DEV_MODE and ip in ["127.0.0.1", "::1"]:
        return True

    whitelist = load_keys(settings.WHITELIST_FILE)
    return ip in whitelist
