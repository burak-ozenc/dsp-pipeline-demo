import os


class Config:
    CONNECTION_STRING = os.getenv('CONNECTION_STRING')

config = Config()