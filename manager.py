import streamlit as st
import psycopg2
from google.cloud import storage
from google.oauth2 import service_account


class USPFoundInfra:
    def __init__(self):
        # Conexão DB com Singleton para performance [cite: 257]
        self.db_conn = self._get_db_connection()
        # Cliente GCS
        self.gcs_client = self._get_gcs_client()
        self.bucket = self.gcs_client.bucket("seu-bucket-name")

    @st.cache_resource
    def _get_db_connection(_self):
        return psycopg2.connect(**st.secrets["postgres"])

    @st.cache_resource
    def _get_gcs_client(_self):
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        return storage.Client(credentials=creds)

    def save_item(self, metadata, image_file):
        """
        Função mestre para a Secretaria[cite: 22, 296]:
        1. Sobe imagem pro GCS
        2. Salva metadados e link no Postgres
        """
        # Lógica de upload e insert aqui...
        pass
