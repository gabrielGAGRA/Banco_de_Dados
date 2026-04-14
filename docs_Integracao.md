## Manual para o Frontend (Fernando)

Você vai utilizar o módulo `USPerdidosInfra` que atua como Singleton (performance) para simplificar a vida no Streamlit. 

Sempre importe-o no início do seu código apontando para a pasta `src`:

```python
import streamlit as st
from src.infra_manager import USPerdidosInfra

# 1. Instancie o motor de Infra
infra = USPerdidosInfra()

# 2. Tela da Secretaria (Exemplo)
uploaded_file = st.file_uploader("Foto do Item", type=["jpg", "png", "jpeg"])
if st.button("Registrar Item Achado"):
    item_data = {
        'unidade': 1, # ID extraído do Selectbox
        'categoria': 2, # ID extraído do Selectbox
        'desc': "Descrição do que foi achado na recepção"
    }
    
    # MAGIC FUNCTION: Já sobe para o GCP Cloud e Grava no Postgres
    url_publica = infra.upload_and_save(item_data, uploaded_file)
    st.success(f"Registrado com sucesso! Link seguro: {url_publica}")

# 3. Busca Cega (Painel do Aluno)
# Esse método já está blindado e RETIRA o URL das fotos para não vazar informações
itens_blindados = infra.list_items_for_students()
st.dataframe(itens_blindados)

# 4. Painel Detalhado (Painel Secretaria)
# Usa esse método passando o ID para obter todas a informações (Incluindo FOTO) do item
dados_da_secretaria = infra.get_item_detail_for_admin(id_do_item)
```