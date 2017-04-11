import os ,configparser

conf=configparser.ConfigParser()

conf.read("config.ini")



class Config:
    SECRET_KEY=conf.get('global','SECRET_KEY')
    FLASKY_ADMIN=conf.get('admin','FLASKY_ADMIN')
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI=conf.get('database','DEV_DATABASE_URL')
    HEAD_PORTRAIT=conf.get('img','HEAD_PORTRAIT')


class TestingConfig(Config):
    Testing=True
    SQLALCHEMY_DATABASE_URI = conf.get('database', 'TEST_DATABASE_URL')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = conf.get('database', 'DATABASE_URL')



config={
    'development':DevelopmentConfig,
    'testing':TestingConfig,
    'production':ProductionConfig,
    'default':DevelopmentConfig
}

