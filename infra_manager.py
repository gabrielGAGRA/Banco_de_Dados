import streamlit as st
import psycopg2
from google.cloud import storage
from google.oauth2 import service_account
import uuid  # Importante para nomes únicos


class USPFoundInfra:
    @st.cache_resource  # Garante que a conexão seja única (Singleton)
    def _get_connection(_self):
        return psycopg2.connect(
            host=st.secrets["postgres"]["host"],
            database=st.secrets["postgres"]["database"],
            user=st.secrets["postgres"]["user"],
            password=st.secrets["postgres"]["password"],
        )

    def __init__(self):
        self.conn = self._get_connection()
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        self.storage_client = storage.Client(credentials=creds)
        # O nome do seu bucket agora é puxado direto do secrets.toml em [gcp][bucket_name]
        self.bucket = self.storage_client.bucket(st.secrets["gcp"]["bucket_name"])

    def upload_and_save(self, item_data, image_file):
        # Gerar nome único para evitar colisões no bucket
        ext = image_file.name.split(".")[-1]
        unique_name = f"itens/{uuid.uuid4()}.{ext}"

        blob = self.bucket.blob(unique_name)
        blob.upload_from_string(image_file.getvalue(), content_type=image_file.type)

        # Como o GCP está com "Uniform bucket-level access" ativado,
        # a permissão de público deve ser dada na aba "Permissões" do Bucket no GCP
        # e não por arquivo (removido blob.make_public()).
        gcs_url = blob.public_url

        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO ITEM (id_unidade, id_categoria, descricao, gcs_url, status) 
                VALUES (%s, %s, %s, %s, 'Pendente')
                """,
                (
                    item_data["unidade"],
                    item_data["categoria"],
                    item_data["desc"],
                    gcs_url,
                ),
            )
            self.conn.commit()
        return gcs_url

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
        with self.conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

    def get_item_detail_for_admin(self, item_id):
        """
        Retorna todos os dados, INCLUINDO a URL da foto.
        Acesso restrito apenas ao Módulo Secretaria.
        """
        query = "SELECT *, gcs_url FROM ITEM WHERE id_item = %s"
        with self.conn.cursor() as cur:
            cur.execute(query, (item_id,))
            return cur.fetchone()
