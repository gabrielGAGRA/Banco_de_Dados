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