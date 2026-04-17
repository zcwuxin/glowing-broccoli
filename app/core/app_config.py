import os
from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    # --- 基础应用配置 ---
    APP_ENV: str = "production"  # 环境：development, production
    DEBUG: bool = False   #开启调试模式
    SECRET_KEY: str = "change_me_in_production"

    # --- 数据库配置 ---
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "mydb"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    # --- 数据库连接 URL (自动拼接) ---
    @property
    def DATABASE_URL(self):
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}" \
               f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # --- 配置类 ---
    model_config = SettingsConfigDict(
        # __file__ 是当前文件路径，获取项目根目录路径下.env文件
        env_file=os.path.join(__file__, "..", "..", "..", ".env"),
        env_file_encoding='utf-8',
        # 是否区分大小写
        case_sensitive=True,
        # 允许额外的字段（如果 .env 里有没定义的变量，不会报错）
        extra='ignore',
    )

# 实例化配置对象
settings = Settings()