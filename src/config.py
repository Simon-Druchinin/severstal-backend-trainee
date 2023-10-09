import os
from dotenv import load_dotenv
from dataclasses import dataclass


load_dotenv()
load_dotenv(".env.test")

@dataclass
class DBConfig:
    HOST: str
    PORT: int
    PASSWORD: str
    USER: str
    NAME: str

    def __post_init__(self):
        self.URL: str = f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"

@dataclass
class Config:
    db: DBConfig

config = Config(
    db=DBConfig(
        HOST=os.environ.get("DB_HOST"),
        PORT=os.environ.get("DB_PORT"),
        PASSWORD=os.environ.get("DB_PASS"),
        USER=os.environ.get("DB_USER"),
        NAME=os.environ.get("DB_NAME")
    )
)

test_config = Config(
    db=DBConfig(
        HOST=os.environ.get("DB_HOST_TEST"),
        PORT=os.environ.get("DB_PORT_TEST"),
        PASSWORD=os.environ.get("DB_PASS_TEST"),
        USER=os.environ.get("DB_USER_TEST"),
        NAME=os.environ.get("DB_NAME_TEST")
    )
)
