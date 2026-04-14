import streamlit as st
import psycopg2
from faker import Faker
import random

fake = Faker("pt_BR")

UNIDADES = [
    ("Secretaria do PSI", "Prédio da Engenharia Elétrica, 1º Andar", "psi@usp.br"),
    ("Secretaria do PCS", "Prédio da Engenharia Elétrica, Térreo", "pcs@usp.br"),
    ("CEE", "Prédio da Engenharia Elétrica, Vivência", "cee@usp.br"),
    ("Portaria da Entrada", "Entrada principal do prédio da Elétrica", "portaria.eletrica@usp.br"),
    ("Labs Digitais", "Prédio da Elétrica, Bloco C", "labs@usp.br"),
    ("Sala ao lado de Circuitos", "Prédio da Elétrica, Bloco A", "circuitos@usp.br"),
    ("Escola Politécnica", "Engenharia (Prédios: Civil, Elétrica, Mecânica, Biênio, etc.)", "poli@usp.br"),
    ("Faculdade de Filosofia, Letras e Ciências Humanas", "História, Letras, Geografia, Sociais, Filosofia", "fflch@usp.br"),
    ("Faculdade de Economia, Administração e Contabilidade", "Administração, Economia e Contabilidade", "fea@usp.br"),
    ("Instituto de Matemática e Estatística", "Matemática, Computação e Estatística", "ime@usp.br"),
    ("Instituto de Física", "Física", "if@usp.br"),
    ("Instituto de Química", "Química", "iq@usp.br"),
    ("Faculdade de Arquitetura e Urbanismo", "Arquitetura e Design", "fau@usp.br"),
    ("Escola de Comunicações e Artes", "Artes, Jornalismo, Editoração", "eca@usp.br"),
    ("Faculdade de Educação", "Pedagogia e Licenciaturas", "fe@usp.br"),
    ("Instituto de Biociências", "Biologia", "ib@usp.br"),
    ("Instituto de Psicologia", "Psicologia", "ip@usp.br"),
    ("Instituto de Ciências Biomédicas", "Prédios I, II, III e IV", "icb@usp.br"),
    ("Faculdade de Odontologia", "Odontologia", "fo@usp.br"),
    ("Fac. de Medicina Veterinária e Zootecnia", "Veterinária", "fmvz@usp.br"),
    ("Escola de Educação Física e Esporte", "Esportes", "eefe@usp.br"),
    ("Outros Institutos", "Astronomia, Geociências, Oceanografia, Relações Internacionais, Energia", "outros@usp.br"),
    ("Faculdade de Direito", "Largo São Francisco, Direito", "fd@usp.br"),
    ("Faculdade de Saúde Pública", "Saúde Pública e Nutrição", "fsp@usp.br"),
    ("Escola de Enfermagem", "Enfermagem e Cuidados de Saúde", "ee@usp.br"),
    ("Instituto de Medicina Tropical de São Paulo", "Doenças Tropicais e Infecciosas", "imt@usp.br"),
    ("Instituto de Estudos Brasileiros", "Cultura e História do Brasil", "ieb@usp.br"),
]

CATEGORIAS = [
    ("Eletrônicos",),
    ("Documentos",),
    ("Vestuário",),
    ("Estojos",),
    ("Garrafas",),
    ("Mochilas e Bolsas",),
    ("Chaves e Chaveiros",),
    ("Livros e Cadernos",),
    ("Óculos",),
    ("Guarda-chuvas",),
    ("Cartões (USP, Bancário, Bilhete)",),
]

CORES = ["PRETO", "BRANCO", "AZUL", "VERMELHO", "VERDE", "AMARELO", "CINZA", "MARROM", "ROSA", "ROXO", "LARANJA", "OUTROS"]
STATUS = ["Pendente", "Devolvido", "Descartado"]


def get_connection():
    return psycopg2.connect(
        host=st.secrets["postgres"]["host"],
        port=st.secrets["postgres"]["port"],
        database=st.secrets["postgres"]["database"],
        user=st.secrets["postgres"]["user"],
        password=st.secrets["postgres"]["password"],
    )


def seed_database():
    conn = get_connection()
    cur = conn.cursor()

    try:
        print("Iniciando a inserção da Massa de Dados...")

        # NOTE: Cascading truncation is required here to ensure idempotency.
        # Without it, test runs would accumulate duplicate inventory entries and fail foreign key constraints.
        cur.execute(
            "TRUNCATE TABLE AVISO_PERDIDO, ITEM, CATEGORIA, UNIDADE RESTART IDENTITY CASCADE;"
        )

        cur.executemany(
            """
            INSERT INTO UNIDADE (nome_unidade, localizacao_detalhada, contato_responsavel) 
            VALUES (%s, %s, %s)
        """,
            UNIDADES,
        )

        cur.executemany(
            """
            INSERT INTO CATEGORIA (nome_categoria) 
            VALUES (%s)
        """,
            CATEGORIAS,
        )

        cur.execute("SELECT id_unidade FROM UNIDADE")
        ids_unidades = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT id_categoria FROM CATEGORIA")
        ids_categorias = [row[0] for row in cur.fetchall()]

        # TODO(database): Update the schema to support partial matching of items (Issue #140). Currently generating 15 items exactly as the legacy spec requires.
        itens_data = []
        for _ in range(15):
            status_item = random.choice(STATUS)

            nusp_retirada = (
                fake.random_int(min=10000000, max=99999999)
                if status_item == "Devolvido"
                else None
            )

            itens_data.append(
                (
                    random.choice(ids_unidades),
                    random.choice(ids_categorias),
                    fake.sentence(nb_words=6),
                    random.choice(CORES),
                    fake.company(),
                    f"https://storage.googleapis.com/usperdidos/mock_item_{fake.uuid4()}.jpg",
                    fake.date_between(start_date="-30d", end_date="today"),
                    status_item,
                    nusp_retirada,
                )
            )

        cur.executemany(
            """
            INSERT INTO ITEM (id_unidade, id_categoria, descricao, cor_principal, marca_modelo, gcs_url, data_achado, status, NUSP_retirada)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
            itens_data,
        )

        # 4. Popular AVISO_PERDIDO (Módulo do Aluno) - Mínimo de 15 registros
        avisos_data = []
        for _ in range(15):
            # 30% de chance de NÃO ter unidade oficial vinculada (testando cardinalidade 0..1:N)
            tem_unidade = random.random() > 0.3
            id_unidade = random.choice(ids_unidades) if tem_unidade else None
            local_opcional = fake.street_name() if not tem_unidade else None

            descricoes_possiveis = [
                "Perdi durante a aula, acho que ficou na carteira.",
                "Deixei no bandejão na hora do almoço.",
                "Esqueci na sala de estudos da biblioteca.",
                "Caiu do meu bolso no corredor principal do prédio.",
                "Acho que deixei no banheiro do térreo.",
                "Perdi a caminho do ponto do circular.",
                "Esqueci na mesa da lanchonete da vivência.",
                "Ficou na tomada do saguão e quando voltei não estava.",
                "Deixei na praça enquanto conversava com meus amigos.",
                "Deve ter caído da minha mochila perto da portaria.",
                "Tinha deixado em cima da mesa e quando voltei alguém tinha levado.",
                "Perdi no laboratório de informática, estava no fundo da sala."
            ]

            avisos_data.append(
                (
                    random.choice(ids_categorias),
                    id_unidade,
                    local_opcional,
                    fake.date_between(start_date="-30d", end_date="today"),
                    f"https://storage.googleapis.com/usperdidos/mock_aluno_{fake.uuid4()}.jpg",
                    random.choice(descricoes_possiveis),  # O que o aluno diz que perdeu
                    fake.name(),
                    fake.random_int(min=10000000, max=99999999),
                )
            )

        cur.executemany(
            """
            INSERT INTO AVISO_PERDIDO (id_categoria, id_unidade, local_perda_opcional, data_achado, gcs_url, descricao_aluno, nome_usuario, NUSP_usuario)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
            avisos_data,
        )

        # CASO DE TESTE: O "Match Perfeito" (Para a Consulta 1)
        # Vamos inserir um item na secretaria e um aluno procurando exatamente a mesma coisa no mesmo lugar.
        id_unidade_match = ids_unidades[0]
        id_categoria_match = ids_categorias[0]

        cur.execute(
            """
            INSERT INTO ITEM (id_unidade, id_categoria, descricao, cor_principal, marca_modelo, gcs_url, status)
            VALUES (%s, %s, 'Estojo preto com 3 canetas bic', 'PRETO', 'Faber-Castell', 'https://storage.../estojo.jpg', 'Pendente')
        """,
            (id_unidade_match, id_categoria_match),
        )

        cur.execute(
            """
            INSERT INTO AVISO_PERDIDO (id_categoria, id_unidade, descricao_aluno, nome_usuario, NUSP_usuario)
            VALUES (%s, %s, 'Perdi meu estojo preto com minhas canetas bic', 'Aluno Teste', 12345678)
        """,
            (id_categoria_match, id_unidade_match),
        )

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
