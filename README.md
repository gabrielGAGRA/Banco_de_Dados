# USPerdidos - Plataforma de Achados e Perdidos da POLI-USP

Plataforma de gerenciamento de itens achados e perdidos da Universidade de São Paulo (USPerdidos). Este repositório contém a infraestrutura do banco de dados (PostgreSQL via Docker), a interface de acesso à nuvem (Google Cloud Storage) e os scripts de população inicial.

---

## Arquitetura do Projeto

O projeto está dividido nas seguintes camadas físicas e lógicas:

- **Banco de Dados Local (`docker-compose.yml`)**: Instância isolada do PostgreSQL rodando na porta local `5432`.
- **Armazenamento em Nuvem (GCP)**: Bucket no Google Cloud Storage para hospedagem das fotos dos itens.
- **Camada de Infra (`src/`)**: Códigos em Python responsáveis por integrar e conectar o servidor de Front-end (Streamlit) com a infraestrutura (Banco + Nuvem) em uma operação atômica.

### Estrutura de Pastas

```text
 Banco_de_Dados/
 ┣  db/                       <-- Scripts de SQL e Massa Inicial
 ┃ ┣  init_db/
 ┃ ┃ ┗  schema.sql            (DDL de Criação)
 ┃ ┗  seed_db.py              (Gera Carga Fake de Teste)
 ┣  docs/                     <-- Documentações
 ┣  src/                      <-- Core da Aplicação
 ┃ ┗  infra_manager.py        (API de GCS + PostgreSQL)
 ┣  tests/                    <-- Validação e Testes
 ┃ ┗  test_infra.py           (Inicializa DDL e testa as conexões)
 ┣  .streamlit/
 ┃ ┗  secrets.toml            (Credenciais - Ignorado no Git)
 ┣  docker-compose.yml        (Definição do Container do BD)
 ┗  requirements.txt          (Dependências Python)
```

---

##  Como Iniciar o Projeto 

**1. Instale as Dependências Python:**
Certifique-se de estar usando um ambiente virtual e execute:
```bash
pip install -r requirements.txt
```

**2. Configure as Credenciais:**
O projeto necessita do arquivo `.streamlit/secrets.toml` na raiz com as chaves corretas do PostgreSQL local e da Service Account do Google Cloud.

**3. Suba o Banco de Dados (Docker):**
Com o Docker Desktop aberto, na raiz do projeto, rode:
```bash
docker-compose up -d
```

**4. Crie as Tabelas e Popule os Dados:**
O banco levanta vazio. Execute os scripts sequencialmente para montar e popular o banco:
```bash
python tests/test_infra.py   # Cria o DDL físico (Tabelas)
python db/seed_db.py         # Insere dezenas de itens/avisos fakes para teste
```

---