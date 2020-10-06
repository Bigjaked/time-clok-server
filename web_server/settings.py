from pydantic import BaseSettings as Base


class BaseSettings(Base):
    # copy and past the output from openssl rand -base64 128
    # don't save the value to version control
    # it should look like the text below
    SECRET_KEY: str = (
        "fTv+Q8jZmms7qSFjHWbgnmJujCmIix0iMuioaX6jM7ls8FJar0tI2Sg/jD0Fo"
        "bkkj0zirFrINiRirptx7hgq3gD3GKKHA1CXHlTrZdTTpoYBd5HCt2KndX+FaI"
        "TUqYMAMVhLE24G+jPOYRU21IkdRjS8sHhJhPkuhVy56yvEOj4="
    )
    TOKEN_SALT_LENGTH: int = 32
    TOKEN_TIMEOUT: int = 60 * 60 * 24  # 24 hours
    PASSWORD_HASH_MODE: str = "pbkdf2:sha256:50000"
    PASSWORD_SALT_LENGTH: int = 16

    DATABASE_USERNAME: str = ""
    DATABASE_PASSWORD: str = ""
    DATABASE_NAME: str = "clok_db"
    DATABASE_HOST: str = "127.0.0.1"
    DATABASE_PORT: int = 3306
    DATABASE_CONNECTOR: str = ""
    DATABASE_POOL_SIZE: int = ""
    # set this to True to enable sqlite database
    USE_SQLITE_DATABASE: bool = False
    # if **USE_SQLITE_DATABASE** is set to true, then this can be used
    # to declare a file_path to store an sqlite database
    # leave blank for an in memory database
    SQLITE_DATABASE_NAME: str = ""
    # Declare this variable to override the database connection pool class
    # DATABASE_POOL_TYPE: object = QueuePool
    DATABASE_ECHO: bool = False
