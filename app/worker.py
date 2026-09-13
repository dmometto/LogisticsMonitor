import time
import os
from app.processor import LogisticsProcessor
from app.configs import settings

def start_worker():
    engine = LogisticsProcessor()
    print("Monitor de Logística iniciado...")
    
    while True:
        try:
            files = os.listdir(settings.INPUT_PATH)
            for file in files:
                if file.endswith(".csv"):
                    full_path = os.path.join(settings.INPUT_PATH, file)
                    success = engine.process_shipments(full_path)
                    if success:
                        os.rename(full_path, full_path.replace("input", "processed"))
            
            time.sleep(10)
        except Exception as e:
            print(f"Erro no loop do worker: {e}")
            time.sleep(30)