from pydantic import BaseModel, Field
from os import environ
import toml
from pathlib import Path
_settings: "Settings | None" = None
def load_settings() -> "Settings":
    global _settings
    if _settings is None:
        _settings = Settings.new()
    return _settings

class DatabaseSettings(BaseModel):
    """数据库配置"""

    url: str = Field(
        default="postgresql+async://user:password@localhost/smarthydra", description="数据库连接URL"
    )
    pool_size: int = Field(default=20, description="连接池大小")
    max_overflow: int = Field(default=30, description="最大溢出连接数")
    pool_recycle: int = Field(default=3600, description="连接回收时间（秒）")
    echo: bool = Field(default=False, description="是否打印SQL语句")


class SecuritySettings(BaseModel):
    """安全配置"""

    secret_key: str = Field(default="your-secret-key-here", description="JWT密钥")
    algorithm: str = Field(default="HS256", description="JWT算法")
    access_token_expire_minutes: int = Field(default=30, description="访问令牌过期时间（分钟）")


class LoggingSettings(BaseModel):
    """日志配置"""

    level: str = Field(default="INFO", description="日志级别")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="日志格式"
    )


class Settings(BaseModel):
    """应用配置"""

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    config_file: str = Field(default="config.toml", description="配置文件路径")

    @property
    def database_url(self) -> str:
        """获取数据库URL"""
        return self.database.url

    @property
    def secret_key(self) -> str:
        """获取密钥"""
        return self.security.secret_key

    @property
    def algorithm(self) -> str:
        """获取算法"""
        return self.security.algorithm

    @property
    def access_token_expire_minutes(self) -> int:
        """获取访问令牌过期时间"""
        return self.security.access_token_expire_minutes

    @property
    def logging_level(self) -> str:
        """获取日志级别"""
        return self.logging.level

    @staticmethod
    def new() -> "Settings":
        """创建配置实例"""
        db_url = environ.get("DATABASE_URL")
        db_pool_size = environ.get("DB_POOL_SIZE")
        db_max_overflow = environ.get("DB_MAX_OVERFLOW")
        db_pool_recycle = environ.get("DB_POOL_RECYCLE")
        db_echo = environ.get("DB_ECHO")

        secret_key = environ.get("SECRET_KEY")
        jwt_algorithm = environ.get("JWT_ALGORITHM")
        token_expire = environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")

        log_level = environ.get("LOG_LEVEL")

        database_config = {}
        if db_url is not None:
            database_config["url"] = db_url
        if db_pool_size is not None:
            database_config["pool_size"] = int(db_pool_size)
        if db_max_overflow is not None:
            database_config["max_overflow"] = int(db_max_overflow)
        if db_pool_recycle is not None:
            database_config["pool_recycle"] = int(db_pool_recycle)
        if db_echo is not None:
            database_config["echo"] = db_echo.lower() == "true"

        security_config = {}
        if secret_key is not None:
            security_config["secret_key"] = secret_key
        if jwt_algorithm is not None:
            security_config["algorithm"] = jwt_algorithm
        if token_expire is not None:
            security_config["access_token_expire_minutes"] = int(token_expire)

        logging_config = {}
        if log_level is not None:
            logging_config["level"] = log_level

        config_path = environ.get("CONFIG_PATH", None)
        default_config = Path("config.toml") if config_path is None else Path(config_path)

        if default_config.exists():
            file_config = toml.load(default_config)
            if "database" not in file_config:
                file_config["database"] = {}
            if "security" not in file_config:
                file_config["security"] = {}
            if "logging" not in file_config:
                file_config["logging"] = {}

            for key, value in database_config.items():
                file_config["database"][key] = value

            for key, value in security_config.items():
                file_config["security"][key] = value

            for key, value in logging_config.items():
                file_config["logging"][key] = value

            return Settings(**file_config)
        else:
            return Settings(
                database=DatabaseSettings(**database_config),
                security=SecuritySettings(**security_config),
                logging=LoggingSettings(**logging_config),
                config_file=environ.get("CONFIG_FILE", "config.toml"),
            )
