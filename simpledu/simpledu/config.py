class BaseConfig(object):
    ''' 配置基类 '''
    SECRET_KEY = 'makesure to set a very secret key'
    INDEX_PER_PAGE = 9

class DevelopmentConfig(BaseConfig):
    ''' 开发 '''
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root@localhost:3306/simpledu?charset=utf8' # +mysqldb 强制底层使用mysqlclient连接数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = False # 防止 flask run 时出现警告

class ProductionConfig(BaseConfig):
    ''' 生产 '''
    pass

class TestingConfig(BaseConfig):
    ''' 测试 '''
    pass

configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
        }
