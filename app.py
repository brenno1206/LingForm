"""
Módulo Principal da Aplicação.
Controla o Frontend em Streamlit, recebe interações do usuário, 
e gerencia as respostas importadas de `automato.py` e `visualizacao.py`.
"""

import streamlit as st

# Importando nossas classes e funções separadas dos outros arquivos
from automato import Automato
from visualizacao import desenhar_grafo_graphviz

# Configuração primária da página no navegador
st.set_page_config(page_title="Conversor AFND para AFD", layout="wide")

st.title("⚙️ Conversor e Testador de Autômatos")
st.markdown("Alfabeto fixado em `{0, 1}` com movimentos vazios em `h`.")

# Inicializa o 'session_state' para o Streamlit não resetar os dados ao clicar em botões
if 'automato' not in st.session_state:
    st.session_state.automato = None

# ==========================================
# PARTE 1: UPLOAD DO AFND E EXIBIÇÃO
# ==========================================
st.header("1. Carregar Tabela do AFND")
arquivo_afnd = st.file_uploader("Envie o arquivo .txt do AFND", type=['txt'])

if arquivo_afnd:
    linhas = arquivo_afnd.getvalue().decode("utf-8").splitlines()
    try:
        # Se for um arquivo novo ou a sessão estiver vazia, cria a instância
        st.session_state.automato = Automato(linhas)
        auto = st.session_state.automato
        
        # Divide a tela principal em duas metades (Lado a Lado)
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("AFND Original")
            grafo_afnd = desenhar_grafo_graphviz(
                auto.AFND, auto.AFND_estados, auto.estado_inicial, auto.AFND_estados_finais
            )
            # width="stretch" garante que o grafo use todo o quadrado da coluna
            st.graphviz_chart(grafo_afnd, width="stretch")
            
        with col2:
            st.subheader("AFD Equivalente")
            afd_inicial = auto.AFD_estados[0]
            grafo_afd = desenhar_grafo_graphviz(
                auto.AFD_transicoes, auto.AFD_estados, afd_inicial, auto.AFD_estados_finais
            )
            st.graphviz_chart(grafo_afd, width="stretch")
            
        # Botão extra para baixar o arquivo do AFD gerado
        st.download_button(
            label="📥 Baixar Tabela do AFD Equivalente (.txt)",
            data=auto.exportar_AFD_txt(),
            file_name="afd_convertido.txt",
            mime="text/plain"
        )
            
    except Exception as e:
        st.error(f"Erro ao processar o arquivo do autômato: {e}")

st.divider()

# ==========================================
# PARTE 2: LEITURA E TESTE DE PALAVRAS
# ==========================================
st.header("2. Testar Palavras")

# Proteção: não deixa testar palavras sem antes possuir um Autômato em memória
if st.session_state.automato is None:
    st.warning("Carregue o arquivo do AFND primeiro para testar palavras.")
else:
    arquivo_palavras = st.file_uploader("Envie o arquivo .txt com as palavras", type=['txt'])
    
    if arquivo_palavras:
        linhas_palavras = arquivo_palavras.getvalue().decode("utf-8").splitlines()
        palavras = [linha.strip() for linha in linhas_palavras if linha.strip()]
        
        auto = st.session_state.automato
        resultados_txt = []
        resultados_tela = []
        
        # Aplica ambas as lógicas a cada palavra para comparar a integridade
        for palavra in palavras:
            res_afnd = auto.testar_AFND(palavra)
            res_afd = auto.testar_AFD(palavra)
            
            # Formato de exigência acadêmica
            status_afd = "aceito" if res_afd else "não aceito"
            status_afnd = "aceito" if res_afnd else "não aceito"
            
            # String pura a ser gravada no TXT
            resultados_txt.append(f"{palavra} {status_afd}")
            
            # Formatação estilizada para a tabela na tela HTML
            consistencia = "OK" if res_afd == res_afnd else "INCONSISTENTE"
            resultados_tela.append(f"| `{palavra}` | {status_afd} | {status_afnd} | {consistencia} |")

        # Impressão na Tela HTML (Via markdown)
        st.subheader("Resultados da Verificação Dupla")
        st.markdown("| Palavra | Resultado (AFD) | Resultado (AFND) | Integridade |")
        for res in resultados_tela:
            st.markdown(res)
            
        # Gera variável em memória contendo as quebras de linha para o Download
        texto_final = "\n".join(resultados_txt)
        
        st.download_button(
            label="📥 Baixar Arquivo de Teste de Palavras (.txt)",
            data=texto_final,
            file_name="resultados_palavras.txt",
            mime="text/plain"
        )
