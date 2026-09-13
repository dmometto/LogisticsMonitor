import pandas as pd
import os
from datetime import datetime, timedelta

def generate_test_data():
    """Gera um CSV de logística na pasta data/input"""
    data = {
        'order_id': ['LOG100', 'LOG200', 'LOG300'],
        'carrier': ['Loggi', 'Correios', 'FedEx'],
        'departure_date': [datetime.now() - timedelta(days=3)] * 3,
        'estimated_at': [datetime.now() - timedelta(days=1)] * 3,
        'delivered_at': [datetime.now()] * 3 # Aqui todos estarão atrasados (SLA breached)
    }
    
    df = pd.DataFrame(data)
    os.makedirs('data/input', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    filename = f"data/input/manifest_{datetime.now().strftime('%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    print(f"Arquivo de teste gerado: {filename}")

if __name__ == "__main__":
    generate_test_data()