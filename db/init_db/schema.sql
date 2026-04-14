-- Limpando objetos existentes para evitar erros de criação duplicada (Idempotência)
DROP TABLE IF EXISTS AVISO_PERDIDO CASCADE;
DROP TABLE IF EXISTS ITEM CASCADE;
DROP TABLE IF EXISTS CATEGORIA CASCADE;
DROP TABLE IF EXISTS UNIDADE CASCADE;
DROP TYPE IF EXISTS status_item CASCADE;

-- Criando Tipos para integridade (Prática de Engenharia)
CREATE TYPE status_item AS ENUM ('Pendente', 'Devolvido', 'Descartado');

-- Tabela de Unidades (Onde o item está fisicamente)
CREATE TABLE UNIDADE (
    id_unidade SERIAL PRIMARY KEY,
    nome_unidade VARCHAR(100) NOT NULL,
    localizacao_detalhada TEXT,
    contato_responsavel VARCHAR(100)
);

-- Categorias com Regra de Descarte 
CREATE TABLE CATEGORIA (
    id_categoria SERIAL PRIMARY KEY,
    nome_categoria VARCHAR(50) NOT NULL,
    prazo_descarte INTEGER NOT NULL -- dias para o "ciclo de vida" do dado
);

-- Itens Oficiais (Módulo Secretaria)
CREATE TABLE ITEM (
    id_item SERIAL PRIMARY KEY,
    id_unidade INTEGER REFERENCES UNIDADE(id_unidade),
    id_categoria INTEGER REFERENCES CATEGORIA(id_categoria),
    descricao TEXT,
    cor_principal VARCHAR(30),
    marca_modelo VARCHAR(50),
    gcs_url VARCHAR(255),
    data_achado DATE DEFAULT CURRENT_DATE,
    status status_item DEFAULT 'Pendente', 
    NUSP_retirada INTEGER DEFAULT NULL
);

-- Crowdsourcing (Módulo Aluno)
CREATE TABLE AVISO_PERDIDO (
    id_aviso SERIAL PRIMARY KEY,
    id_categoria INTEGER REFERENCES CATEGORIA(id_categoria),
    id_unidade INTEGER REFERENCES UNIDADE(id_unidade), -- Cardinalidade opcional
    local_perda_opcional VARCHAR(100),
    data_achado DATE,
    gcs_url VARCHAR(255),
    descricao_aluno TEXT,
    nome_usuario VARCHAR(100),
    NUSP_usuario INTEGER,
    data_postagem TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================================================
-- VIEWS DE RELATÓRIOS E CONSULTAS
-- ==============================================================================

CREATE OR REPLACE VIEW vw_correspondencia_avisos AS
SELECT
    ap.nome_usuario,
    ap.NUSP_usuario,
    c.nome_categoria,
    u.nome_unidade,
    ap.descricao_aluno AS descricao_perdido,
    i.descricao AS descricao_achado,
    i.data_achado
FROM AVISO_PERDIDO ap
INNER JOIN ITEM i ON ap.id_categoria = i.id_categoria AND ap.id_unidade = i.id_unidade
INNER JOIN CATEGORIA c ON ap.id_categoria = c.id_categoria
INNER JOIN UNIDADE u ON ap.id_unidade = u.id_unidade
WHERE i.status = 'Pendente';

CREATE OR REPLACE VIEW vw_relatorio_itens_unidade AS
SELECT
    u.nome_unidade,
    i.status,
    COUNT(i.id_item) AS total_itens
FROM UNIDADE u
LEFT JOIN ITEM i ON u.id_unidade = i.id_unidade
GROUP BY u.nome_unidade, i.status;

CREATE OR REPLACE VIEW vw_itens_multimidia AS
SELECT
    i.id_item,
    c.nome_categoria,
    i.descricao,
    i.cor_principal,
    i.marca_modelo,
    u.nome_unidade,
    i.data_achado
FROM ITEM i
INNER JOIN CATEGORIA c ON i.id_categoria = c.id_categoria
INNER JOIN UNIDADE u ON i.id_unidade = u.id_unidade
WHERE i.gcs_url IS NOT NULL;

CREATE OR REPLACE VIEW vw_historico_devolucoes AS
SELECT
    i.id_item,
    c.nome_categoria,
    i.descricao,
    i.NUSP_retirada,
    u.nome_unidade AS local_retirada,
    i.data_achado
FROM ITEM i
INNER JOIN CATEGORIA c ON i.id_categoria = c.id_categoria
INNER JOIN UNIDADE u ON i.id_unidade = u.id_unidade
WHERE i.NUSP_retirada IS NOT NULL OR i.status = 'Devolvido';

CREATE OR REPLACE VIEW vw_estatistica_inventario AS
SELECT
    c.nome_categoria,
    COUNT(i.id_item) AS quantidade_achada,
    c.prazo_descarte
FROM CATEGORIA c
LEFT JOIN ITEM i ON c.id_categoria = i.id_categoria
GROUP BY c.nome_categoria, c.prazo_descarte;