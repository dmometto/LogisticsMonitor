# LogisticsMonitor

Sistema inteligente de monitoramento de SLAs de logística para acompanhar entregas atrasadas a partir de manifestos de transporte enviados em CSV, normalizar os dados e disponibilizar métricas via API.

## Visão geral

O projeto foi pensado para apoiar operações logísticas, permitindo:

- Ler manifestos de transporte em arquivos CSV
- Normalizar campos de data e identificar entregas com quebra de SLA
- Persistir os dados em um banco SQL Server
- Expor métricas por transportadora através de uma API
- Processar arquivos automaticamente em um worker em background

## Funcionalidades

- Leitura de manifestos de diferentes transportadoras
- Geração de dados de teste para simular o fluxo
- Cálculo automático de SLA com base em `estimated_at` e `delivered_at`
- Armazenamento em tabela SQL Server
- Consulta de métricas por transportadora na rota `/metrics/sla`
- Suporte a processamento contínuo da pasta `data/input`

## Arquitetura

O sistema é composto por:

- `app/main.py`: inicializa a API FastAPI
- `app/processor.py`: processa os arquivos CSV e calcula o indicador de SLA
- `app/database.py`: gerencia conexão e consultas no SQL Server
- `app/configs.py`: configurações da aplicação
- `app/worker.py`: worker que monitora a pasta de entrada
- `gerar_input.py`: gera arquivos CSV de exemplo para testes

## Fluxo de processamento

1. O usuário coloca um arquivo CSV em `data/input`
2. O worker detecta o arquivo e o processa
3. O sistema converte as datas para datetime
4. A lógica calcula `sla_breached = delivered_at > estimated_at`
5. Os dados relevantes são salvos no SQL Server
6. Em seguida, o arquivo é movido para `data/processed`
7. A API retorna métricas consolidadas por transportadora

## Estrutura do projeto

```text
LogisticsMonitor/
├── app/
│   ├── configs.py
│   ├── database.py
│   ├── main.py
│   ├── processor.py
│   └── worker.py
├── data/
│   ├── input/
│   └── processed/
├── gerar_input.py
├── README.md
└── .gitignore
```

## Requisitos

- Python 3.10+
- SQL Server
- ODBC Driver 17 para SQL Server
- Dependências Python listadas abaixo

## Dependências

```bash
pip install fastapi uvicorn pandas pyodbc pydantic-settings
```

## Configuração do SQL Server

A aplicação usa a classe `Settings` em `app/configs.py` para montar a string de conexão do SQL Server.

Você pode configurar os valores abaixo:

- `DB_SERVER`
- `DB_DATABASE`
- `DB_USER`
- `DB_PASSWORD`
- `DB_DRIVER`

Exemplo de configuração:

```python
DB_SERVER = "localhost"
DB_DATABASE = "LogisticsDB"
DB_USER = "sa"
DB_PASSWORD = "SuaSenha123"
DB_DRIVER = "ODBC Driver 17 for SQL Server"
```

Se você estiver usando autenticação do Windows, pode deixar `DB_USER` e `DB_PASSWORD` vazios para usar `Trusted_Connection=yes`.

## Como executar

### 1. Preparar o ambiente

Crie um ambiente virtual e instale as dependências:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install fastapi uvicorn pandas pyodbc pydantic-settings
```

### 2. Configurar o SQL Server

Certifique-se de que o banco e a instância do SQL Server estejam acessíveis.

### 3. Iniciar a API

```bash
uvicorn app.main:app --reload
```

A API ficará disponível em:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/metrics/sla`

### 4. Gerar dados de teste

Para simular manifestos de transporte e popular a pasta de entrada:

```bash
python gerar_input.py
```

Isso cria um CSV em `data/input` com dados de exemplo.

## Estrutura do CSV de entrada

O sistema espera um arquivo CSV com colunas como:

```csv
order_id,carrier,departure_date,estimated_at,delivered_at
LOG100,Loggi,2026-09-01 10:00:00,2026-09-02 10:00:00,2026-09-03 10:00:00
```

- `order_id`: identificador da entrega
- `carrier`: transportadora
- `estimated_at`: data estimada de entrega
- `delivered_at`: data real da entrega

## API

### Endpoint raiz

```http
GET /
```

Retorna uma mensagem de boas-vindas do sistema.

### Endpoint de métricas de SLA

```http
GET /metrics/sla
```

Retorna um conjunto de registros com:

- `carrier`
- `total_deliveries`
- `total_delayed`
- `delay_rate`

Exemplo de retorno:

```json
[
  {
    "carrier": "Loggi",
    "total_deliveries": 10,
    "total_delayed": 3,
    "delay_rate": 30.0
  }
]
```