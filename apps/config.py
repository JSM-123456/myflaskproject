from pathlib import Path

basedir = Path(__file__).parent.parent

class BaseConfig:
    SECRET_KEY="tjdals"
    WTF_CSRF_SECRET_KEY="dlqslek"

class LocalConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:12345678@localhost:3306/pydb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:12345678@localhost:3306/pydb'
    WTF_CSRF_ENABLED = False
    # testing에서 CSRF를 무효로 하기 위해 WTF_CSRF_ENABLED = False 설정한다.

config = {
    "testing" : TestingConfig,
    "local" : LocalConfig
}