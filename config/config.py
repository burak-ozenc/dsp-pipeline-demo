import os
from dotenv import load_dotenv, dotenv_values
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / ".env")

class Config:
    @property
    def CONNECTION_STRING(self):
        return os.getenv('CONNECTION_STRING')

    @property
    def DATA_ROOT_PATH(self):
        return os.getenv('DATA_ROOT_PATH')

config = Config()