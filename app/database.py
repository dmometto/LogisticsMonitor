import pyodbc
from app.configs import settings
import pandas as pd

class DatabaseManager:
    def __init__(self):
        self.conn_str = settings.connection_string
        self.table_name = "Logistics_Deliveries"

    def get_connection(self):
        try:
            return pyodbc.connect(self.conn_str)
        except Exception as e:
            print(f"Erro ao conectar ao SQL Server: {e}")
            raise

    def create_table(self):
        """Cria a tabela inicial se não existir"""
        query = f"""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = '{self.table_name}')
        CREATE TABLE {self.table_name} (
            id INT IDENTITY(1,1) PRIMARY KEY,
            order_id VARCHAR(50),
            carrier VARCHAR(100),
            sla_breached BIT,
            processed_at DATETIME DEFAULT GETDATE()
        )
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    conn.commit()
        except Exception as e:
            print(f"Erro ao criar tabela: {e}")

    def get_sla_metrics(self):
        """
        Busca os dados reais do SQL Server e processa indicadores com Pandas.
        """
        try:
            query = f"""
                SELECT 
                    carrier, 
                    COUNT(*) as total_deliveries, 
                    SUM(CAST(sla_breached AS INT)) as total_delayed 
                FROM {self.table_name} 
                GROUP BY carrier
            """
            
            with self.get_connection() as conn:
                df = pd.read_sql(query, conn)
            
            if not df.empty:
                # Cálculo de indicador de performance via Pandas
                df['delay_rate'] = (df['total_delayed'] / df['total_deliveries'] * 100).round(2)
                return df.to_dict(orient='records')
            
            return []
            
        except Exception as e:
            print(f"Erro na consulta de métricas: {e}")
            raise