from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_SERVER: str = "localhost" 
    DB_DATABASE: str = "LogisticsDB"
    
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    
    DB_DRIVER: str = "ODBC Driver 17 for SQL Server"
    
    INPUT_PATH: str = "data/input"
    PROCESSED_PATH: str = "data/processed"
    
    @property
    def connection_string(self):
        if self.DB_USER and self.DB_PASSWORD:
            auth_part = f"UID={self.DB_USER};PWD={self.DB_PASSWORD}"
        else:
            auth_part = "Trusted_Connection=yes"
            
        return (
            f"DRIVER={{{self.DB_DRIVER}}};"
            f"SERVER={self.DB_SERVER};"
            f"DATABASE={self.DB_DATABASE};"
            f"{auth_part}"
        )

settings = Settings()