from dataclasses import dataclass
from secret import API_TOKEN

@dataclass
class AppConfig:
    api_token: str

def load():
    return AppConfig(api_token=API_TOKEN)


