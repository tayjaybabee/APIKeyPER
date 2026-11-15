import re


def normalize_env_prefix(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").upper()


def is_env_name(value: str) -> bool:
    return re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value) is not None


def key_env_name(prefix: str, key_name: str | None = None) -> str:
    parts = [normalize_env_prefix(prefix)]
    if key_name is not None:
        parts.append(normalize_env_prefix(key_name))
    if not all(parts):
        raise ValueError("Cannot derive an environment variable name. Set a valid prefix or --name.")
    name = "_".join([*parts, "API_KEY"])
    if not is_env_name(name):
        raise ValueError("Invalid environment variable name. Set a valid prefix or --name.")
    return name
