import psycopg2
from faker import Faker
import random
from datetime import date, timedelta

# Inicializa o gerador de dados falsos 
fake = Faker('pt_BR')

# Dados fixos exigidos pelo projeto
UNIDADES = [
    ("Secretaria do PSI", "Prédio da Engenharia Elétrica, 1º Andar", "psi@usp.br"),
    ("Secretaria do PCS", "Prédio da Engenharia Elétrica, Térreo", "pcs@usp.br"),
    ("CEE", "Prédio da Engenharia Elétrica, Vivência", "cee@usp.br"),
    ("Portaria da Entrada", "Entrada principal do prédio da Elétrica", "portaria.eletrica@usp.br"),
    ("Labs Digitais", "Prédio da Elétrica, Bloco C", "labs@usp.br"),
    ("Sala ao lado de Circuitos", "Prédio da Elétrica, Bloco A", "circuitos@usp.br")
]

CATEGORIAS = [
    ("Eletrônicos", 90), # 90 dias de prazo
    ("Documentos", 180),
    ("Vestuário", 30),
    ("Estojos", 30),
    ("Garrafas", 15)
]

CORES = ['PRETO', 'BRANCO', 'AZUL', 'VERMELHO', 'OUTROS']
STATUS = ['Pendente', 'Devolvido', 'Descartado']

def get_connection():
    # Ajuste os parâmetros se o seu docker-compose usar senhas diferentes
    return psycopg2.connect(
        host="127.0.0.1", port=5433, database="usp_found", user="admin", password="poli_usp"
    )

def seed_database():
    conn = get_connection()
    cur = conn.cursor()

    try:
        print("Iniciando a inserção da Massa de Dados...")

        # 1. Popular UNIDADES
        cur.executemany("""
            INSERT INTO UNIDADE (nome_unidade, localizacao_detalhada, contato_responsavel) 
            VALUES (%s, %s, %s)
        """, UNIDADES)
        
        # 2. Popular CATEGORIAS
        cur.executemany("""
            INSERT INTO CATEGORIA (nome_categoria, prazo_descarte) 
            VALUES (%s, %s)
        """, CATEGORIAS)

        # Buscando os IDs gerados para usar nas chaves estrangeiras
        cur.execute("SELECT id_unidade FROM UNIDADE")
        ids_unidades = [row[0] for row in cur.fetchall()]
        
        cur.execute("SELECT id_categoria FROM CATEGORIA")
        ids_categorias = [row[0] for row in cur.fetchall()]

        # 3. Popular ITEM (Inventário da Secretaria) - Mínimo de 15 registros
        itens_data = []
        for _ in range(15):
            status_item = random.choice(STATUS)
            # Se for devolvido, tem NUSP de retirada, senão é NULL
            nusp_retirada = fake.random_int(min=10000000, max=99999999) if status_item == 'Devolvido' else None
            
            itens_data.append((
                random.choice(ids_unidades),
                random.choice(ids_categorias),
                fake.sentence(nb_words=6), # Descrição interna
                random.choice(CORES),
                fake.company(), # Simula uma marca
                f"https://storage.googleapis.com/usp-found-storage/mock_item_{fake.uuid4()}.jpg",
                fake.date_between(start_date='-30d', end_date='today'),
                status_item,
                nusp_retirada
            ))

        cur.executemany("""
            INSERT INTO ITEM (id_unidade, id_categoria, descricao, cor_principal, marca_modelo, gcs_url_foto, data_achado, status, NUSP_retirada)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, itens_data)

        # 4. Popular AVISO_PERDIDO (Módulo do Aluno) - Mínimo de 15 registros
        avisos_data = []
        for _ in range(15):
            # 30% de chance de NÃO ter unidade oficial vinculada (testando cardinalidade 0..1:N)
            tem_unidade = random.random() > 0.3
            id_unidade = random.choice(ids_unidades) if tem_unidade else None
            local_opcional = fake.street_name() if not tem_unidade else None

            avisos_data.append((
                random.choice(ids_categorias),
                id_unidade,
                local_opcional,
                fake.date_between(start_date='-30d', end_date='today'),
                f"https://storage.googleapis.com/usp-found-storage/mock_aluno_{fake.uuid4()}.jpg",
                fake.paragraph(nb_sentences=2), # O que o aluno diz que perdeu
                fake.name(),
                fake.random_int(min=10000000, max=99999999)
            ))

        cur.executemany("""
            INSERT INTO AVISO_PERDIDO (id_categoria, id_unidade, local_perda_opcional, data_achado, gcs_url_foto, descricao_aluno, nome_usuario, NUSP_usuario)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, avisos_data)

        # CASO DE TESTE: O "Match Perfeito" (Para a Consulta 1)
        # Vamos inserir um item na secretaria e um aluno procurando exatamente a mesma coisa no mesmo lugar.
        id_unidade_match = ids_unidades[0]
        id_categoria_match = ids_categorias[0]
        
        cur.execute("""
            INSERT INTO ITEM (id_unidade, id_categoria, descricao, cor_principal, marca_modelo, gcs_url_foto, status)
            VALUES (%s, %s, 'Estojo preto com 3 canetas bic', 'PRETO', 'Faber-Castell', 'https://storage.../estojo.jpg', 'Pendente')
        """, (id_unidade_match, id_categoria_match))

        cur.execute("""
            INSERT INTO AVISO_PERDIDO (id_categoria, id_unidade, descricao_aluno, nome_usuario, NUSP_usuario)
            VALUES (%s, %s, 'Perdi meu estojo preto com minhas canetas bic', 'Aluno Teste', 12345678)
        """, (id_categoria_match, id_unidade_match))

        # Commit final
        conn.commit()
        print("✅ Massa de dados gerada com sucesso! Testes prontos.")

    except Exception as e:
        print(f"❌ Erro ao popular o banco: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    seed_database()