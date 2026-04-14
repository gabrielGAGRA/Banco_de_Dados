import sys
import os
import io

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.infra_manager import USPerdidosInfra

def test_real_upload():
    print("Iniciando upload com imagem real...")
    
    # 1. Instancia a infraestrutura que engloba o banco e o GCS
    infra = USPerdidosInfra()
    
    # 2. Caminho absoluto da imagem fornecida
    image_path = "/home/davidaguina/Workspace/Banco_de_Dados/db/assets/images/WhatsApp Image 2026-04-14 at 12.47.55.jpeg"
    
    # Lendo o arquivo como uma Simulação (Mock) do formato que o Streamlit usaria (BytesIO)
    class MockUploadedFile(io.BytesIO):
        def __init__(self, content, name, type):
            super().__init__(content)
            self.name = name
            self.type = type

    if not os.path.exists(image_path):
        print(f"❌ Imagem não encontrada no caminho absoluto: {image_path}")
        return

    with open(image_path, "rb") as f:
        image_content = f.read()
        
    dummy_file = MockUploadedFile(
        image_content, 
        "mochila_preta.jpeg", 
        "image/jpeg"
    )

    # 3. Mapeamento Inteligente: Identificando os dados pela foto
    with infra.get_db_connection() as conn:
        with conn.cursor() as cur:
            # Buscar ID da unidade "Escola Politécnica" com base no bilhete
            cur.execute("SELECT id_unidade FROM UNIDADE WHERE nome_unidade LIKE '%Poli%';")
            row_un = cur.fetchone()
            id_un = row_un[0] if row_un else 1 # Fallback 
            
            # Buscar ID da categoria (Estojos ou Vestuário)
            cur.execute("SELECT id_categoria FROM CATEGORIA WHERE nome_categoria = 'Vestuário';")
            row_cat = cur.fetchone()
            id_cat = row_cat[0] if row_cat else 1

    # Dicionário do Backend sendo populado com base na sua foto!
    item_data = {
        "unidade": id_un,
        "categoria": id_cat,
        "desc": "Mochila ou bolsa transversal preta encontrada na Sala 1024 (Poli). Bilhete atrelado com a data 06-02/26.",
        "cor_principal": "PRETO",
        "marca_modelo": "EKE" # Detalhe na logo do zíper da bolsa
    }

    print(f"Dados mapeados -> Cor: {item_data['cor_principal']} | Marca: {item_data['marca_modelo']}")
    print("Enviando para GCS e PostgreSQL...")
    
    try:
        # A mágica acontecendo
        url = infra.upload_and_save(item_data, dummy_file)
        print(f"✅ SUCESSO! Item e foto inseridos simultaneamente.")
        print(f"🔗 Link final hospedado: {url}")
    except Exception as e:
        print(f"❌ Erro durante o upload/inserção: {e}")

if __name__ == "__main__":
    test_real_upload()
