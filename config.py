import os


class Config:
    CONNECTION_STRING = os.getenv('CONNECTION_STRING')
    DATA_ROOT_PATH = os.getenv('DATA_ROOT_PATH')

config = Config()