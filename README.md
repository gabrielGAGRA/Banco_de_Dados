# USPerdidos - Plataforma de Achados e Perdidos 

A plataforma de gerenciamento de itens achados e perdidos da Universidade de São Paulo (USPerdidos). Este repositório foca na infraestrutura de Dados e Engenharia de Software, englobando a camada de persistência (PostgreSQL via Docker), infraestrutura de nuvem para objetos estáticos (Google Cloud Storage) e gerenciadores de API (Data Access Layer) para a interface front-end (Streamlit).

---

## 🏗️ Arquitetura do Projeto

Desenvolvido sob o paradigma de arquitetura em camadas e utilizando boas práticas de Cloud e Data Engineering, o projeto divide-se em:

- **Banco de Dados Relacional**: Instância local do PostgreSQL provisionada via docker-compose.yml, atuando como Single Source of Truth para metadados, controle de transações e regras de negócio.
- **Armazenamento de Objetos (GCP)**: Bucket no Google Cloud Storage (GCS) configurado com *Uniform bucket-level access* para hospedagem e distribuição em larga escala das imagens associadas aos itens.
- **Data Access Layer (src/)**: Gerenciador Python central (infra_manager.py) aplicando os padrões **Singleton** e **Connection Pooling**, responsável pela orquestração de transações atômicas distribuídas entre banco relacional e Cloud.

### 🗂️ Estrutura Físico-Lógica

`	ext
Banco_de_Dados/
├── db/                       # Artefatos do Banco de Dados
│   ├── init_db/
│   │   └── schema.sql        # DDL (Definição de Tipos, Tabelas, Constraints e Índices)
│   └── queries.sql           # DML (Views e consultas estratégicas/analíticas)
├── src/                      # Regras de Integração e Infraestrutura
│   └── infra_manager.py      # DAL (Gerenciador de Conexões e GCS Uploads)
├── tests/                    # Validações, Seed de Banco e Idempotência
│   ├── seed_db.py            # Geração massiva de dados falsos (Faker) para homologação
│   └── test_infra.py         # Valida DDL, conexão de rede e testes unitários de banco
├── ARCHITECTURE.md           # Decisões de Arquitetura e Engenharia (Novo)
├── docker-compose.yml        # Provisionamento Local (Container do BD PostgreSQL)
└── requirements.txt          # Gerenciamento de dependências (Python)
`

---

## 🚀 Como Iniciar o Projeto (Setup de Ambiente)

**1. Instale as Dependências Python:**
Sempre atue isolado em um ambiente virtual (.venv).
`ash
python -m venv .venv
source .venv/Scripts/activate  # No macOS/Linux use .venv/bin/activate
pip install -r requirements.txt
`

**2. Configure Credenciais Injetadas (Secrets):**
Para obedecer às práticas de segurança e evitar chave no repositório (*hardcoded secrets*), configure o .streamlit/secrets.toml com os pares chave-valor para conexão com o Postgres (host, port, db, user, pass) e as configurações da Service Account do GCP.

**3. Provisione a Infraestrutura em Container:**
Instancie o serviço via Docker para garantir que o ambiente seja replicável.
`ash
docker-compose up -d
`

**4. DDL e Geração de Massa (Seed Idempotente):**
Execute os scripts analíticos e de carga na raiz:
`ash
python tests/test_infra.py   # Valida a conexão DDL/GCS e cria a estrutura física
python tests/seed_db.py      # Aplica a idempotência e gera massa falsa (Fake Data)
`

> **Atenção:** Os dados inseridos pelo seed_db.py realizam TRUNCATE CASCADE automaticamente para que o setup seja 100% idempotente (perfeito para CI/CD).
