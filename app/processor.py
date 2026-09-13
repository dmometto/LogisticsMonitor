import pandas as pd
import time
import os
import asyncio
from app.database import DatabaseManager
from app.configs import settings

class LogisticsProcessor:
    def __init__(self):
        self.db = DatabaseManager()
        self.input_dir = settings.INPUT_PATH

    async def save_to_db_async(self, df):
        try:
            # Selecionando apenas o necessário para o banco
            summary = df[['order_id', 'carrier', 'sla_breached']]
            
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    for _, row in summary.iterrows():
                        cursor.execute(
                            f"INSERT INTO {self.db.table_name} (order_id, carrier, sla_breached) VALUES (?, ?, ?)",
                            row.order_id, row.carrier, int(row.sla_breached)
                        )
                    conn.commit()
            print(">>> Banco de dados alimentado com sucesso!")
            return True
        except Exception as e:
            print(f"Erro ao salvar no banco: {e}")
            return False

    def process_shipments(self, file_path: str):
        print("--- Monitor de Operações Iniciado ---")
        self.db.create_table()
        
        while True:
            try:
                if not os.path.exists(self.input_dir):
                    os.makedirs(self.input_dir, exist_ok=True)
                
                files = [f for f in os.listdir(self.input_dir) if f.endswith('.csv')]
                
                for file in files:
                    path = os.path.join(self.input_dir, file)
                    print(f"Processando: {file}")
                    
                    df = pd.read_csv(path)
                    
                    df['delivered_at'] = pd.to_datetime(df['delivered_at'])
                    df['estimated_at'] = pd.to_datetime(df['estimated_at'])
                    
                    # Lógica de SLA: Se entregou depois do estimado, quebrou o SLA
                    df['sla_breached'] = df['delivered_at'] > df['estimated_at']
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    success = loop.run_until_complete(self.save_to_db_async(df))
                    
                    if success:
                        # Move para processados apenas se deu certo no banco
                        dest_path = os.path.join(settings.PROCESSED_PATH, file)
                        os.makedirs(settings.PROCESSED_PATH, exist_ok=True)
                        os.rename(path, dest_path)
                        print(f"Arquivo {file} finalizado.")
                
                time.sleep(5)
            except Exception as e:
                print(f"Erro crítico no loop: {e}")
                time.sleep(10)