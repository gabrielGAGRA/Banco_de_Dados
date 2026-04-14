import streamlit as st
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from google.cloud import storage
from google.oauth2 import service_account
import uuid


class USPerdidosInfra:
    @st.cache_resource
    def _get_connection_pool(_self):
        return pool.SimpleConnectionPool(
            1,
            20,
            host=st.secrets["postgres"]["host"],
            database=st.secrets["postgres"]["database"],
            user=st.secrets["postgres"]["user"],
            password=st.secrets["postgres"]["password"],
            port=st.secrets["postgres"].get("port", 5432),
        )

    def __init__(self):
        self.pool = self._get_connection_pool()
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        self.storage_client = storage.Client(credentials=creds)
        self.bucket = self.storage_client.bucket(st.secrets["gcp"]["bucket_name"])

    @contextmanager
    def get_db_connection(self):
        """Gerenciador de contexto para obter e devolver conexões ao pool de maneira segura."""
        conn = self.pool.getconn()
        try:
            yield conn
        finally:
            self.pool.putconn(conn)

    def upload_and_save(self, item_data, image_file):
        ext = image_file.name.split(".")[-1]
        unique_name = f"itens/{uuid.uuid4()}.{ext}"

        blob = self.bucket.blob(unique_name)
        blob.upload_from_string(image_file.getvalue(), content_type=image_file.type)

        # NOTE: GCP bucket has "Uniform bucket-level access" enabled.
        # Object ACLs like make_public() are restricted.
        # Public permission is granted in the GCP Console Bucket Permissions instead.
        gcs_url = blob.public_url

        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO ITEM (
                            id_unidade, id_categoria, descricao, 
                            cor_principal, marca_modelo, gcs_url, status
                        ) 
                        VALUES (%s, %s, %s, %s, %s, %s, 'Pendente')
                        """,
                        (
                            item_data.get("unidade"),
                            item_data.get("categoria"),
                            item_data.get("desc"),
                            item_data.get("cor_principal"),
                            item_data.get("marca_modelo"),
                            gcs_url,
                        ),
                    )
                    conn.commit()
            return gcs_url
        except Exception as e:
            # NOTE: Simulate distributed transaction rollback. Clean up orphaned GCS object if DB insertion fails.
            blob.delete()
            raise e

    def list_items_for_students(self):
        """
        Retorna itens para a 'Busca Cega' dos alunos.
        A regra de segurança diz que o link da foto (gcs_url) é ocultado.
        """
        query = """
            SELECT id_item, id_unidade, id_categoria, descricao, data_achado 
            FROM ITEM 
            WHERE status = 'Pendente'
        """
        with self.get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchall()

    def get_item_detail_for_admin(self, item_id):
        """
        Retorna todos os dados, INCLUINDO a URL da foto.
        Acesso restrito apenas ao Módulo Secretaria.
        """
        query = "SELECT *, gcs_url FROM ITEM WHERE id_item = %s"
        with self.get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (item_id,))
                return cur.fetchone()
