import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '6ce880509867e095b667acbf863b5a987a647c196ed246a7'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///don.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
