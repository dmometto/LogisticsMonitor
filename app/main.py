from fastapi import FastAPI
import threading
from app.database import DatabaseManager
from app.worker import start_worker

app = FastAPI(title="Logistics Operations API")
db = DatabaseManager() # Instância global do banco

@app.get("/")
async def root():
    return {"message": "Sistema de Monitoramento de Operações Online"}

@app.get("/metrics/sla")
async def get_sla_metrics():
    """
    Rota que apenas chama o método de métricas do banco. [cite: 3]
    Requisito: Método Assíncrono.
    """
    try:
        data = db.get_sla_metrics()
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.on_event("startup")
async def startup_event():
    thread = threading.Thread(target=start_worker, daemon=True)
    thread.start()