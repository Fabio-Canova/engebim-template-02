import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from pythreejs import *
import matplotlib.pyplot as plt
import plotly.express as px

import trimesh
import base64
import os
import tempfile


########################################################
##########TITULOS#######################################
########################################################
# Define o layout da página para 'wide'
st.set_page_config(layout="wide")

# Adiciona widgets na barra lateral
st.sidebar.title("Filtros")

st.title("ENGEBIM - Modelo de apresetação")
st.write(
    "Quantitativo e Detalhamento"
)

########################################################
##########TELA PARA BUSCAR OS ARQUIVOS##################
########################################################
st.subheader("Carregar Arquivos")


# Seção expansível
with st.expander("Carregar Arquivos", expanded=False):
    # Upload do arquivo
    uploaded_file1 = st.file_uploader("Faça o upload do arquivo .glb", type=["glb"])

    if uploaded_file1:
        # Ler o conteúdo do arquivo
        modelo_bytes = uploaded_file1.read()

        # Salvar localmente (opcional)
        with open("modelo.glb", "wb") as f:
            f.write(modelo_bytes)
        
        st.success("Arquivo carregado com sucesso!")

    # Upload do arquivo
    uploaded_file2 = st.file_uploader("Faça o upload do arquivo .txt", type=["txt"])

    if uploaded_file2:
        # Ler o conteúdo do arquivo
        modelo_bytes = uploaded_file2.read()

        # Salvar localmente (opcional)
        with open("modelo.txt", "wb") as f:
            f.write(modelo_bytes)
        
        st.success("Arquivo carregado com sucesso!")





###################################################
##########BUSCA OS ARQUIVOS########################
###################################################

# Função para remover ou substituir caracteres indesejados
def importar_CSV(caminho_arquivo):

    df = pd.read_csv(caminho_arquivo,
                                sep=";",  # Delimitador usado no CSV
                                header = 0,
                                encoding="utf-8",  # Define a codificação do arquivo
                                na_values=["<Nenhum>","NaN","N/A", "", "NULL"],  # Considera "NaN", valores vazios e "NULL" como NaN
                                encoding_errors='replace',
                                on_bad_lines="skip",
                                keep_default_na=False,  # Ignora os valores padrão do Pandas para NaN
                                na_filter=True,  # Mantém a detecção de NaN ativada
                                skip_blank_lines=False,  # Mantém as linhas em branco
                                low_memory=False,  # Habilita leitura em pedaços menores para economizar memória
                                memory_map=True  # Usa mapeamento de memória para leitura mais rápida
    ) #Elementos
    df.fillna("")

    # Retorna o DataFrame com os dados limpos
    return df

# Carregar os CSVs como DataFrames
@st.cache_data
def load_table_1():
    # Carrega a primeira tabela
    arquivo_elmentos="data/elementos.csv"
    return importar_CSV(arquivo_elmentos)

@st.cache_data
def load_table_2():
    # Carrega a segunda tabela
    arquivo_elmentos_unique="data/elementos_unique.csv"
    return importar_CSV(arquivo_elmentos_unique)

@st.cache_data
def load_table_3():
    # Carrega a terceira tabela
    arquivo_elmentos_xyz="data/elementos_xyz.csv"
    return importar_CSV(arquivo_elmentos_xyz)

@st.cache_data
def load_table_4():
    # Carrega a quarta tabela
    arquivo_elmentos_unique_transp="data/elementos_unique_transp.csv"
    return importar_CSV(arquivo_elmentos_unique_transp)

# Carrega as tabelas
df_elementos = load_table_1()
df_elementos_unique = load_table_2()
df_elementos_xyz = load_table_3()
df_elementos_unique_transp = load_table_4()


#Remove registros desnecessarios
def filter_dataframe(df: pd.DataFrame, filters: dict, exclude: dict = None):
    """Filtra um DataFrame para conter apenas as linhas onde as colunas especificadas têm determinados valores,
    e exclui linhas onde as colunas especificadas têm determinados valores."""
    for column, value in filters.items():
        df = df[df[column] == value]
    if exclude:
        for column, value in exclude.items():
            df = df[df[column] != value]
    return df

filters = {"tagnum": "OK"}
exclude = {"Parametro_group": "OUTROS"}
df_elementos_filter = filter_dataframe(df_elementos, filters, exclude)
df_elementos_unique_filter = filter_dataframe(df_elementos_unique, filters, exclude)

#Converte para numerico
df_elementos['Valuenum'] = pd.to_numeric(df_elementos['Valuenum'], errors='coerce')
df_elementos_unique['Valuenum'] = pd.to_numeric(df_elementos_unique['Valuenum'], errors='coerce')
df_elementos_xyz['X'] = pd.to_numeric(df_elementos_xyz['X'], errors='coerce')
df_elementos_xyz['Y'] = pd.to_numeric(df_elementos_xyz['Y'], errors='coerce')
df_elementos_xyz['Z'] = pd.to_numeric(df_elementos_xyz['Z'], errors='coerce')
df_elementos_unique_transp['Altura'] = pd.to_numeric(df_elementos_unique_transp['Altura'], errors='coerce')
df_elementos_unique_transp['Comprimento'] = pd.to_numeric(df_elementos_unique_transp['Comprimento'], errors='coerce')
df_elementos_unique_transp['Contador'] = pd.to_numeric(df_elementos_unique_transp['Contador'], errors='coerce')
df_elementos_unique_transp['rea'] = pd.to_numeric(df_elementos_unique_transp['rea'], errors='coerce')
df_elementos_unique_transp['rea Calculada'] = pd.to_numeric(df_elementos_unique_transp['rea Calculada'], errors='coerce')
 
# Unindo as tabelas para criar um banco de dados único
df_completo = df_elementos_unique_transp.merge(df_elementos_xyz, on="Element ID", how="left")
#df_completo = df_elementos_unique_transp


###################################################
######## FILROS ###################################
# Usando groupby para agrupar por 'Categoria' e somar os valores de 'Valor' e 'Quantidade'
grupo = df_elementos_unique_transp.groupby(['Category', 'Family', 'Level', 'Type', ]).agg({
    'Comprimento': 'sum',          # Soma dos valores na coluna 'Valor'
    'rea': 'sum',          # Soma dos valores na coluna 'Valor'
    'Contador': 'sum'      # Soma dos valores na coluna 'Quantidade'
}).reset_index()

grupo_elementos_unique = df_elementos_unique.groupby(['Category', 'Family', 'Level', 'Type','Parametro' ]).agg({
    'Valuenum': 'sum'      # Soma dos valores na coluna 'Quantidade'
}).reset_index()

grupo_elementos = df_elementos.groupby(['Category', 'Family', 'Level', 'Type','Parametro','File Name' ]).agg({
    'Valuenum': 'sum'      # Soma dos valores na coluna 'Quantidade'
}).reset_index()


# Criando os filtros
categoria1_options = grupo['Category'].unique()  # Obtém as categorias únicas da coluna Categoria1
categoria2_options = grupo['Level'].unique()  # Obtém as categorias únicas da coluna Categoria2
categoria3_options = grupo['Family'].unique()  # Obtém as categorias únicas da coluna Categoria2
categoria4_options = grupo['Type'].unique()  # Obtém as categorias únicas da coluna Categoria2
categoria5_options = grupo_elementos_unique['Parametro'].unique()  # Obtém as categorias únicas da coluna Categoria2
categoria6_options = grupo_elementos['File Name'].unique()  # Obtém as categorias únicas da coluna Categoria2

#categoria1_filter = st.selectbox('Selecione Category:', categoria1_options)
#categoria2_filter = st.selectbox('Selecione Level:', categoria2_options)
#categoria1_filter = st.selectbox('Selecione a Categoria 1:', ['Todas'] + list(categoria1_options))
#categoria2_filter = st.selectbox('Selecione a Categoria 2:', ['Todas'] + list(categoria2_options))
categoria1_filter = st.sidebar.multiselect('Selecione Category:', options=list(categoria1_options), default=None)
categoria2_filter = st.sidebar.multiselect('Selecione Level:', options=list(categoria2_options), default=None)
categoria3_filter = st.sidebar.multiselect('Selecione Family:', options=list(categoria3_options), default=None)
categoria4_filter = st.sidebar.multiselect('Selecione Type:', options=list(categoria4_options), default=None)
categoria5_filter = st.sidebar.multiselect('Selecione Parametro:', options=list(categoria5_options), default=None)
categoria6_filter = st.sidebar.multiselect('Selecione File Name:', options=list(categoria6_options), default=None)


# Adicionando 'Todas' apenas quando nenhuma opção for selecionada
if not categoria1_filter:
    categoria1_filter = ['Todas']
if not categoria2_filter:
    categoria2_filter = ['Todas']
if not categoria3_filter:
    categoria3_filter = ['Todas']
if not categoria4_filter:
    categoria4_filter = ['Todas']
if not categoria5_filter:
    categoria5_filter = ['Todas']
if not categoria6_filter:
    categoria6_filter = ['Todas']


# Exibindo o filtro selecionado
#st.write("Categoria selecionado:", categoria1_filter)
#st.write("Level selecionado:", categoria2_filter)


###################################################
######## CRIA TABELA COMUM#########################
# Exibindo a tabela com Streamlit
st.subheader("Tabela de Dados:")

# Aplicando os filtros aos dados
#grupo_filtered = grupo[(grupo['Category'] == categoria1_filter) & (grupo['Level'] == categoria2_filter)]
#grupo_filtered = grupo[grupo['Category'].isin(categoria1_filter) & grupo['Level'].isin(categoria2_filter)]
if 'Todas' not in categoria1_filter and 'Todas' not in categoria2_filter:
    grupo_filtered = grupo[(grupo['Category'].isin(categoria1_filter)) & (grupo['Level'].isin(categoria2_filter))]
elif 'Todas' not in categoria1_filter:
    grupo_filtered = grupo[grupo['Category'].isin(categoria1_filter)]
elif 'Todas' not in categoria2_filter:
    grupo_filtered = grupo[grupo['Level'].isin(categoria2_filter)]
else:
    grupo_filtered = grupo  # Se "Todas" foi selecionado em ambos os filtros, retorna o DataFrame original

st.dataframe(grupo_filtered)  # Exibe a tabela com interação, você pode filtrar e ordenar


###################################################
######## CRIA TABELA DINAMICA######################
# Criando um DataFrame
df = df_completo

# Configurando o AgGrid
builder = GridOptionsBuilder.from_dataframe(df_elementos_unique_transp)
#builder.configure_pagination(enabled=True)
builder.configure_side_bar()
#builder.configure_default_column(groupable=True, value=True, enableRowGroup=True, pivotable=True)
# Habilitando o modo de Pivot
builder.configure_column("Category", rowGroup=True)  # Definindo como "Row"
builder.configure_column("Family", rowGroup=True)  # Segunda coluna como Row
builder.configure_column("Level", pivot=True)  # Definindo como "Column"
builder.configure_column("rea", header_name="Total Area", aggFunc="sum", type=["numericColumn"], valueFormatter='x.toFixed(2)')  # Definindo como "Value" e formatando para 2 casas decimais)  # Definindo como "Value"

# Configurando o modo de Pivot como padrão
gridOptions = builder.build()
gridOptions['pivotMode'] = True  # Habilita o modo pivot por padrão

# Criando a grade interativa
st.write("### Pivot Table Interativa")
AgGrid(df, gridOptions=gridOptions, enable_enterprise_modules=True)





###################################################
######## CRIA GRAFICO##############################
# Verifique os dados (opcional)

st.subheader("Grafico:")
# Usando groupby para agrupar por 'Categoria' e somar os valores de 'Valor' e 'Quantidade'
grafico01 = df_elementos_unique_transp.groupby('Category').agg({
    'rea': 'sum',
    'Contador': 'sum'      # Soma dos valores na coluna 'Quantidade'
}).reset_index()


# Crie o gráfico de barras
plt.figure(figsize=(10,6))
plt.bar(grafico01['Category'], grafico01['Contador'])
plt.xticks(rotation=90) 
plt.xlabel('Contador')
plt.ylabel('Category')
plt.title('Gráfico de Barras')

# Exiba o gráfico no Streamlit
st.pyplot(plt)


###################################################
######## CRIA GRAFICO2#############################
# Verifique os dados (opcional)
# Limpeza dos dados
grafico01['Category'] = grafico01['Category'].str.strip()  # Remove espaços extras
grafico01['Category'] = grafico01['Category'].str.replace(',', '.', regex=True)  # Substitui vírgulas por pontos


# Criando o gráfico de barras interativo
fig1 = px.bar(
    grafico01,
    x='Contador',  # Ajuste conforme necessário
    y='Category',  # Ajuste conforme necessário
    text='Category',  # Mostra os valores nas barras
    title="Gráfico Interativo1",
    labels={'day': 'Category', 'total_bill': 'Contador'},  # Legendas
    color='Contador',  # Aplica um degradê de cores
    color_continuous_scale='viridis'  # Escolhe uma paleta de cores
)

# Melhorando layout
fig1.update_layout(
    xaxis_tickangle=-45,  # Inclina os rótulos do eixo X
    plot_bgcolor='white',  # Fundo branco
    title_font_size=18  # Tamanho do título
)

# Criando o gráfico de barras interativo
fig2 = px.bar(
    grafico01,
    x='rea',  # Ajuste conforme necessário
    y='Category',  # Ajuste conforme necessário
    text='Category',  # Mostra os valores nas barras
    title="Gráfico Interativo2",
    labels={'day': 'Category', 'total_bill': 'Category'},  # Legendas
    color='rea',  # Aplica um degradê de cores
    color_continuous_scale='plasma'  # Escolhe uma paleta de cores
)

# Melhorando layout
fig2.update_layout(
    xaxis_tickangle=-45,  # Inclina os rótulos do eixo X
    plot_bgcolor='black',  # Fundo branco
    title_font_size=18  # Tamanho do título
)

# Criando colunas para exibir os gráficos lado a lado
col1, col2 = st.columns(2)

# Exibindo os gráficos em colunas separadas
with col1:
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.plotly_chart(fig2, use_container_width=True)



###################################################
######## CRIA BOX COM FORMATAÇÃO CONDICIONAL#######

st.subheader("Grafico:")
# Usando groupby para agrupar por 'Categoria' e somar os valores de 'Valor' e 'Quantidade'
grupo_filtered_box1 = grupo_filtered["Contador"].sum()
grupo_filtered_box2 = grupo_filtered["rea"].sum()

# Função para determinar as cores com base no valor
def get_colors(valor):
    if valor > 0:
        cor_fundo = "#d4edda"  # Verde claro
        cor_borda = "#155724"  # Verde escuro
        cor_texto = "#155724"  # Verde escuro
    else:
        cor_fundo = "#f8d7da"  # Vermelho claro
        cor_borda = "#721c24"  # Vermelho escuro
        cor_texto = "#721c24"  # Vermelho escuro
    return cor_fundo, cor_borda, cor_texto

# Layout com três colunas
col1, col2= st.columns(2)

# Exibir título e valor dentro de um box estilizado
# Exibir boxes nas colunas
for i, (col, valor) in enumerate(zip([col1, col2], [grupo_filtered_box1, grupo_filtered_box2])):
    cor_fundo, cor_borda, cor_texto = get_colors(valor)
    
    # Formatação do valor com duas casas decimais e separador de milhar
    valor_formatado = "{:,.2f}".format(valor)
    
    with col:
        st.markdown(
            f"""
            <div style="
                background-color: {cor_fundo};
                border-left: 5px solid {cor_borda};
                padding: 15px;
                border-radius: 5px;
                text-align: center;
                color: {cor_texto};
                font-size: 24px;
                font-weight: bold;">
                <p>Resultado {i+1}</p>
                <p>{valor_formatado}</p>
            </div>
            """,
            unsafe_allow_html=True
        )


###################################################
######## CRIA 3D###################################

##################################################
# Seleciona o ID

categoria_ID = df_elementos_unique['Element ID'].unique()  # Obtém as categorias únicas da coluna Categoria1
ID_filter = st.selectbox('Selecione o ID:', categoria_ID)
#ID_selected = ID_filter["Element ID"]


###########################################
########## CARREGA OS DADOS VIA open3D#####
import open3d as o3d
import open3d.core as o3c

def load_fbx_ids(file_path):
    try:
        mesh = o3d.io.read_triangle_mesh(file_path)
        element_ids = list(range(len(mesh.vertices)))
        
        # Criando colunas adicionais caso existam atributos
        names = [f"Elemento_{i}" for i in element_ids]  # Nome fictício caso não haja nome
        types = ["Mesh" for _ in element_ids]  # Assumindo que todos são meshes
        categories = ["Geometria" for _ in element_ids]  # Categoria padrão
        
        df = pd.DataFrame({
            "Element ID": element_ids,
            "Name": names,
            "Tipo": types,
            "Categoria": categories
        })
        return df
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo FBX: {e}")
        return None

st.title("Visualizador de IDs de Elementos do Arquivo FBX")
file_path = "modelo/3DsimplificadoMetade.fbx"
data = load_fbx_ids(file_path)
if data is not None:
    st.dataframe(data)
else:
    st.write("Não foi possível carregar os IDs dos elementos do arquivo FBX.")


###########################################
########## CARREGA OS DADOS VIA pyassimp#####
import pyassimp

def load_fbx_attributes(file_path):
    try:
        # Carrega a cena FBX
        scene = pyassimp.load(file_path)
        
        # Verifica se a cena foi carregada corretamente
        if scene is None:
            raise Exception("Não foi possível carregar a cena do arquivo FBX.")
        
        elements = []
        
        # Itera sobre os nós e meshes da cena
        for node in scene.rootnode.children:
            for mesh in node.meshes:
                element = {
                    "Element ID": id(mesh),
                    "Nome": node.name if node.name else "Desconhecido",
                    "Tipo": "Mesh",
                    "Categoria": "Geometria",
                    "Número de Vértices": len(mesh.vertices),
                    "Número de Triângulos": len(mesh.faces),
                    "Possui Normais": mesh.normals is not None,
                    "Possui Cores": mesh.colors is not None,
                    "Possui UVs": mesh.texcoords is not None
                }
                elements.append(element)
        
        pyassimp.release(scene)  # Libera recursos do Assimp
        return pd.DataFrame(elements)
    
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo FBX: {e}")
        return None

st.title("Visualizador de Atributos do Arquivo FBX")
file_path = "modelo/3DsimplificadoMetade.fbx"
data = load_fbx_attributes(file_path)

if data is not None:
    st.dataframe(data)
else:
    st.write("Não foi possível carregar os atributos do arquivo FBX.")















import fbx
import os

def open_fbx(file_path):
    # Verifica se o caminho para o arquivo FBX existe
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"O arquivo {file_path} não foi encontrado.")
    
    # Inicializa o manager do FBX
    manager = fbx.FbxManager.Create()
    
    # Cria o IOSettings para o FBX
    ios = fbx.FbxIOSettings.Create(manager, fbx.FbxIOSettings.IOSROOT)
    manager.SetIOSettings(ios)

    # Cria o cenário FBX
    scene = fbx.FbxScene.Create(manager, "scene")

    # Carrega o arquivo FBX
    importer = fbx.FbxImporter.Create(manager, "")
    if not importer.Initialize(file_path, -1, manager.GetIOSettings()):
        print("Erro ao importar o arquivo FBX:", importer.GetStatus().GetErrorString())
        return None

    # Importa o conteúdo do arquivo para o cenário
    importer.Import(scene)
    importer.Destroy()
    
    return scene

def get_element_info(scene):
    elements_info = []

    # Itera por todos os nós da cena e busca as informações
    def recursive_node_check(node):
        # Obtém o ID do elemento, categoria, família e tipo de família
        element_data = {
            "Element ID": node.GetUniqueID(),
            "Category": node.GetName(),
            "Family": "N/A",  # Isso depende da estrutura do FBX
            "Family Type": "N/A"  # Isso depende da estrutura do FBX
        }
        
        elements_info.append(element_data)

        # Verifica os filhos do nó
        for i in range(node.GetChildCount()):
            recursive_node_check(node.GetChild(i))
    
    # Começa a busca no nó raiz
    root_node = scene.GetRootNode()
    recursive_node_check(root_node)

    return elements_info

def main():
    # Caminho para o arquivo FBX
    file_path = "modelo/3DsimplificadoMetade.FBX"
    
    # Abre o arquivo FBX
    scene = open_fbx(file_path)
    
    if scene:
        # Busca as informações de elementos no arquivo FBX
        elements_info = get_element_info(scene)
        
        # Exibe as informações encontradas
        for element in elements_info:
            print(f"Element ID: {element['Element ID']}")
            print(f"Category: {element['Category']}")
            print(f"Family: {element['Family']}")
            print(f"Family Type: {element['Family Type']}")
            print("-" * 50)

if __name__ == "__main__":
    main()


# Carregar a página
url = "https://glb.ee/6wb9dedd"

# zoom no objeto
# Procuramos o ID completo do modelo que termina com os 8 caracteres selecionados
##matching_element = next((e for e in model_elements if e["ID_Modelo"].endswith(selected_id)), None)

# Se encontramos um match, geramos a URL correta
##if matching_element:
##    full_id = matching_element["ID_Modelo"]
##    iframe_url = f"{url}?highlight={full_id}"
##else:
##    iframe_url = url  # Caso não encontre, mantém a URL padrão

##################################
## Comprimi glb https://optimizeglb.com/dashboard
#opção via https://glb.ee/upload
#url = "https://glb.ee/6wb9dedd"  # Substitua pelo link do seu modelo


st.markdown(f'<iframe src="{url}" width="100%" height="500"></iframe>', unsafe_allow_html=True)









