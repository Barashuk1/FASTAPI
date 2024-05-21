from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Settings class defining configuration options for the application.

    Attributes:
    - POSTGRES_DB (str): The name of the PostgreSQL database.
    - POSTGRES_USER (str): The username for accessing the PostgreSQL database.
    - POSTGRES_PASSWORD (str): The password for accessing the PostgreSQL database.
    - POSTGRES_PORT (int): The port number for the PostgreSQL database.
    - sqlalchemy_database_url (str): The URL for connecting to the PostgreSQL database.
    - secret_key (str): The secret key used for cryptographic operations.
    - algorithm (str): The algorithm used for cryptographic operations.
    - mail_username (str): The username for accessing the mail server.
    - mail_password (str): The password for accessing the mail server.
    - mail_from (str): The email address from which emails are sent.
    - mail_port (int): The port number for the mail server.
    - mail_server (str): The address of the mail server.
    - redis_host (str): The hostname of the Redis server.
    - redis_port (int): The port number for the Redis server.
    - cloudinary_name (str): The name of the Cloudinary account.
    - cloudinary_api_key (str): The API key for accessing the Cloudinary API.
    - cloudinary_api_secret (str): The API secret for accessing the Cloudinary API.

    Configuration:
    - env_file (str): The path to the environment file containing configuration variables (default: ".env").
    - env_file_encoding (str): The encoding of the environment file (default: "utf-8").
    """
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int
    sqlalchemy_database_url: str
    secret_key: str
    algorithm: str
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    redis_host: str
    redis_port: int
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    class ConfigDict:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
