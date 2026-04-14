import streamlit as st
import psycopg2
from google.cloud import storage
import uuid


class USPerdidosManager:
    def __init__(self):
        # Configuração do PostgreSQL
        self.conn = self._init_connection()
        # Configuração do Google Cloud Storage
        self.storage_client = storage.Client.from_service_account_json("sua-chave.json")
        self.bucket = self.storage_client.bucket("usperdidos")

    @st.cache_resource
    def _init_connection(_self):
        return psycopg2.connect(
            host=st.secrets["postgres"]["host"],
            port=st.secrets["postgres"]["port"],
            database=st.secrets["postgres"]["database"],
            user=st.secrets["postgres"]["user"],
            password=st.secrets["postgres"]["password"],
        )

    def upload_image_to_gcs(self, file, folder="itens"):
        """Sobe a imagem e retorna o caminho único"""
        filename = f"{folder}/{uuid.uuid4()}_{file.name}"
        blob = self.bucket.blob(filename)
        blob.upload_from_file(file)
        return filename

    def register_item(self, data):
        """Método que o Fernando (Secretaria) vai chamar"""
        query = """
            INSERT INTO ITEM (id_unidade, id_categoria, descricao, gcs_url_foto)
            VALUES (%s, %s, %s, %s)
        """
        with self.conn.cursor() as cur:
            cur.execute(query, data)
            self.conn.commit()
