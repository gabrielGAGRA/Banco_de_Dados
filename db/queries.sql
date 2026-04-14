-- ==============================================================================
-- Consultas Estratégicas - USPerdidos
-- ==============================================================================

SELECT
 ap.nome_usuario,
 ap.NUSP_usuario,
 c.nome_categoria,
 u.nome_unidade,
 ap.descricao_aluno AS descricao_perdido,
 i.descricao AS descricao_achado,
 i.data_achado
FROM
 AVISO_PERDIDO ap
INNER JOIN
 ITEM i ON ap.id_categoria = i.id_categoria AND ap.id_unidade = i.id_unidade
INNER JOIN
 CATEGORIA c ON ap.id_categoria = c.id_categoria
INNER JOIN
 UNIDADE u ON ap.id_unidade = u.id_unidade
WHERE
 i.status = 'Pendente'
ORDER BY
 i.data_achado DESC;

SELECT
 u.nome_unidade,
 i.status,
 COUNT(i.id_item) AS total_itens
FROM
 UNIDADE u
LEFT JOIN
 ITEM i ON u.id_unidade = i.id_unidade
GROUP BY
 u.nome_unidade,
 i.status
ORDER BY
 u.nome_unidade,
 i.status;

SELECT
 i.id_item,
 c.nome_categoria,
 i.descricao,
 i.cor_principal,
 i.marca_modelo,
 u.nome_unidade,
 i.data_achado
FROM
 ITEM i
INNER JOIN
 CATEGORIA c ON i.id_categoria = c.id_categoria
INNER JOIN
 UNIDADE u ON i.id_unidade = u.id_unidade
WHERE
 i.gcs_url IS NOT NULL 
ORDER BY
 c.nome_categoria,
 i.data_achado DESC;

SELECT
 i.id_item,
 c.nome_categoria,
 i.descricao,
 i.NUSP_retirada,
 u.nome_unidade AS local_retirada,
 i.data_achado
FROM
 ITEM i
INNER JOIN
 CATEGORIA c ON i.id_categoria = c.id_categoria
INNER JOIN
 UNIDADE u ON i.id_unidade = u.id_unidade
WHERE
 i.NUSP_retirada IS NOT NULL
 OR i.status = 'Devolvido'
ORDER BY
 i.data_achado ASC;

SELECT
 c.nome_categoria,
 COUNT(i.id_item) AS quantidade_achada
FROM
 CATEGORIA c
LEFT JOIN
 ITEM i ON c.id_categoria = i.id_categoria
GROUP BY
 c.nome_categoria
ORDER BY
 quantidade_achada DESC;