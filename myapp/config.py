import os
from dotenv import load_dotenv
from datetime import timedelta


load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '6ce880509867e095b667acbf863b5a987a647c196ed246a7'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///don.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CLOUDINARY_URL = os.getenv('CLOUDINARY_URL')


    # JWT configurations
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'fb7735a66fa196e5ed0eb045e3f00f12e6722f88b1793840fb273c4b37dc1d5a') 
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers', 'cookies']  
    JWT_COOKIE_SECURE = True 
    JWT_COOKIE_CSRF_PROTECT = True 