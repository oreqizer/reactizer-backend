import os

DEBUG = os.environ.get('DEBUG') or True
SECRET_KEY = os.environ.get('SECRET_KEY') or 'potato'

# DB stuff
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgres://oreqizer@localhost/reactizer'
SQLALCHEMY_ECHO = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

# JWT sutff
JWT_ISS = os.environ.get('JWT_ISS') or 'reactizer'
