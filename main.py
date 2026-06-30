import os
import yaml

from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}


def to_bool(value):
    return str(value).lower() in ("true", "1", "yes", "on")


@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):

    config = DEFAULTS.copy()

    # YAML layer
    with open("config.development.yaml") as f:
        yaml_config = yaml.safe_load(f)

    config.update(yaml_config)

    # .env layer
    env_map = {
        "APP_PORT": "port",
        "APP_DEBUG": "debug",
        "APP_LOG_LEVEL": "log_level",
        "APP_API_KEY": "api_key",
        "NUM_WORKERS": "workers",
    }

    for env_key, cfg_key in env_map.items():
        value = os.getenv(env_key)
        if value is not None:
            config[cfg_key] = value

    # OS environment layer
    for key in ["PORT", "WORKERS", "DEBUG", "LOG_LEVEL", "API_KEY"]:
        value = os.getenv(f"APP_{key}")
        if value is not None:
            config[key.lower()] = value

    # CLI overrides
    for item in set:
        if "=" in item:
            key, value = item.split("=", 1)
            config[key] = value

    # Type coercion
    config["port"] = int(config["port"])
    config["workers"] = int(config["workers"])
    config["debug"] = to_bool(config["debug"])

    config["log_level"] = str(config["log_level"])

    # Secret masking
    config["api_key"] = "****"

    return config