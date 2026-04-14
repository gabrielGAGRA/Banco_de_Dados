import streamlit as st
import psycopg2
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.infra_manager import USPerdidosInfra
import io


def run_ddl():
    print("1. Conectando ao Banco de Dados (PostgreSQL via Docker)...")
    try:
        conn = psycopg2.connect(
            host=st.secrets["postgres"]["host"],
            port=st.secrets["postgres"]["port"],
            database=st.secrets["postgres"]["database"],
            user=st.secrets["postgres"]["user"],
            password=st.secrets["postgres"]["password"],
        )
        conn.autocommit = True
        cur = conn.cursor()

        print("2. Lendo e aplicando 'db/init_db/schema.sql' (DDL)...")
        schema_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "db", "init_db", "schema.sql")
        )
        with open(schema_path, "r", encoding="utf-8") as f:
            sql = f.read()
            cur.execute(sql)
        print("✅ DDL aplicado com sucesso! Banco estruturado.")
        conn.close()
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False
    return True


def test_integration():
    print("\n3. Iniciando Teste de Integração (GCS + PostgreSQL)...")
    try:
        infra = USPerdidosInfra()
    except Exception as e:
        print(f"⚠️ Atenção: Falha de autenticação com o Google Cloud (GCS).")
        print(f"Detalhe: {e}")
        print(
            "Isso é normal se a chave no 'secrets.toml' for um teste. Atualize com a chave real para testar o GCS.\n"
        )
        return

    # NOTE: Streamlit's UploadedFile is required by infra_manager.upload_and_save(),
    # so we mock it using BytesIO for testing without the UI.
    class MockUploadedFile(io.BytesIO):
        def __init__(self, content, name, type):
            super().__init__(content)
            self.name = name
            self.type = type

    dummy_file = MockUploadedFile(
        b"foto_fake_em_bytes", "imagem_teste_infra.jpg", "image/jpeg"
    )

    print(
        "4. Inserindo dados base (Unidade e Categoria) para contornar as Foreign Keys..."
    )
    with infra.get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO UNIDADE (nome_unidade, localizacao_detalhada) VALUES ('Prédio da Administração', 'Térreo') RETURNING id_unidade;"
            )
            row_un = cur.fetchone()
            id_un = row_un[0] if row_un else None
            cur.execute(
                "INSERT INTO CATEGORIA (nome_categoria) VALUES ('Eletrônicos Teste') RETURNING id_categoria;"
            )
            row_cat = cur.fetchone()
            id_cat = row_cat[0] if row_cat else None
            conn.commit()

    if id_un is None or id_cat is None:
        print("❌ Erro ao inserir dados base (RETURNING falhou).")
        return

    item_data = {
        "unidade": id_un,
        "categoria": id_cat,
        "desc": "Item inserido automaticamente pelo teste de infraestrutura.",
        "cor_principal": "PRETO",
        "marca_modelo": "InfraCorp Teste",
    }

    print("5. Executando 'upload_and_save' (GCS -> Postgres)...")
    try:
        url = infra.upload_and_save(item_data, dummy_file)
        print(f"✅ SUCESSO ABSOLUTO! Integração concluída.")
        print(f"🔗 Link público gerado (GCS): {url}")
    except Exception as e:
        print(f"❌ Erro no envio simultâneo: {e}")


if __name__ == "__main__":
    print(f"{'#'*50}\nIniciando Script de Teste e Configuração Inicial\n{'#'*50}")
    if run_ddl():
        test_integration()
