# Milésima adptação e correção do codigo para criar uma plataforma de visualização automatizada de dados
# Cristiane 2025-06-08

# Testada em 2025-06-08
import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Configuração da página
st.set_page_config(page_title="Datux: Facilitando a visualização de dados", layout="wide")

# Menu lateral
st.sidebar.title("⚙️ Mais")
menu_opcao = st.sidebar.radio("Navegação", ["Visualização", "Sobre / Ajuda"])

# Campo para relatar problema no menu lateral (envia email via mailto)
st.sidebar.markdown("---")
st.sidebar.markdown("### 🐞 Relatar problema")
feedback = st.sidebar.text_area("Descreva aqui o problema ou sugestão:")
if st.sidebar.button("Enviar feedback"):
    if feedback.strip():
        mailto_link = f"mailto:seu_email@exemplo.com?subject=Feedback%20Datux&body={feedback.replace(' ', '%20')}"
        st.sidebar.markdown(f"[Clique aqui para enviar seu feedback por e-mail]({mailto_link})")
    else:
        st.sidebar.warning("Por favor, escreva algo antes de enviar.")

if menu_opcao == "Sobre / Ajuda":
    st.sidebar.markdown("""
        ### Sobre esta Plataforma
        - Usuário carrega seu CSV ou XLSX, escolhe as colunas.
        - Sugestão do melhor gráfico para as colunas selecionadas.
        - Pode testar outros gráficos.
        - Pode baixar o gráfico gerado em PNG.
        - Pode copiar o código para incorporar o gráfico.
        
        **Desenvolvido por Cristiane Antunes Rodrigues - 2025**
    """)
    st.stop()

################################################################################################################

# CSS personalizado
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: Verdana, sans-serif;
        }
        .titulo {
            font-size: 30px;
            font-weight: bold;
            color: #2c3e50;
            text-align: center;
        }
        .descricao {
            font-size: 16px;
            color: #34495e;
            margin-bottom: 10px;
            text-align: center;
        }
        .assinatura {
            font-size: 13px;
            color: #7f8c8d;
            margin-top: 30px;
            text-align: center;
        }
        .bloco {
            background-color: #f7f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .stButton > button {
            background-color: #2980b9;
            color: white;
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 16px;
            font-weight: bold;
            margin-top: 10px;
            margin-right: 10px;
        }
        .botoes-linha {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 10px;
        }
        .aviso-erro {
            color: #c0392b;
            font-weight: bold;
            margin-bottom: 10px;
        }
        textarea {
            width: 100%;
            height: 80px;
            font-family: monospace;
            font-size: 14px;
            padding: 8px;
            border-radius: 6px;
            border: 1px solid #ddd;
            resize: vertical;
        }
    </style>
""", unsafe_allow_html=True)

################################################################################################################

# Título e descrição
st.markdown('<div class="titulo">Plataforma de Visualização automatizada de Dados</div>', unsafe_allow_html=True)
st.markdown('<div class="descricao">Ferramenta interativa para visualização de dados, a partir de uma base em formato CSV ou XLSX, com suporte de IA para sugerir a melhor representação das colunas escolhidas e analisar o gráfico.</div>', unsafe_allow_html=True)

# Upload do arquivo CSV ou XLSX
upload_col1, upload_col2, upload_col3 = st.columns([1, 2, 1])
with upload_col2:
    arquivo = st.file_uploader("📁 Envie seu arquivo CSV ou XLSX", type=["csv", "xlsx"], label_visibility="visible")

if arquivo:
    # Lê CSV ou XLSX conforme extensão
    if arquivo.name.endswith(".csv"):
        df = pd.read_csv(arquivo)
    else:
        df = pd.read_excel(arquivo)

    st.success("✅ Seu arquivo foi carregado com sucesso!")

    st.markdown("#### 👀 Pré-visualização dos dados")
    st.dataframe(df.head(), use_container_width=True)

    colunas_numericas = df.select_dtypes(include='number').columns.tolist()
    colunas_categoricas = df.select_dtypes(include='object').columns.tolist()

    st.markdown('<hr>', unsafe_allow_html=True)

    # Enunciado simples
    st.markdown("Escolha as colunas para visualizar no gráfico:")

    seletores = st.columns(2)
    col_x = seletores[0].selectbox("📌 Eixo X (horizontal)", df.columns)
    col_y = seletores[1].selectbox("📌 Eixo Y (vertical)", df.columns)

    # Sugestão da IA
    prompt = f"""Qual o melhor tipo de gráfico para visualizar a relação entre as colunas '{col_x}' e '{col_y}'?
    Responda apenas com: coluna, barra, linha, dispersão, pizza, rosca, histograma ou outro."""

    try:
        resposta = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt, "stream": False},
            timeout=20
        )
        sugestao = resposta.json()["response"].strip().lower()
    except:
        sugestao = "coluna"

    def verifica_incompatibilidade(tipo, x_col, y_col):
        x_num = x_col in colunas_numericas
        x_cat = x_col in colunas_categoricas
        y_num = y_col in colunas_numericas
        y_cat = y_col in colunas_categoricas

        if tipo in ["pizza", "rosca"]:
            if not (x_cat and y_num):
                return True, "Para gráficos de Pizza/Rosca, o eixo X deve ser categórico e o eixo Y numérico."
        elif tipo == "histograma":
            if not x_num:
                return True, "Para histograma, o eixo X deve ser numérico."
        elif tipo in ["linha", "dispersão"]:
            if not (x_num and y_num):
                return True, "Para gráficos de Linha/Dispersão, ambos eixos devem ser numéricos."
        elif tipo == "coluna":
            if not ((x_cat and y_num) or (x_num and y_num)):
                return True, "Para gráfico de Coluna, eixo Y deve ser numérico; eixo X pode ser categórico ou numérico."
        elif tipo == "barra":
            if not ((y_cat and x_num) or (y_num and x_num)):
                return True, "Para gráfico de Barra, eixo X deve ser numérico; eixo Y pode ser categórico ou numérico."
        return False, ""

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<div class="bloco">', unsafe_allow_html=True)
        st.subheader("📈 Representação Gráfica")
        st.markdown(f"Sugestão da IA: **{sugestao.capitalize()}**")

        tipo_grafico = st.radio("🧩 Escolha o tipo de gráfico:", options=[
            "coluna", "barra", "linha", "dispersão", "pizza", "rosca", "histograma"
        ], index=0 if sugestao not in ["coluna", "barra", "linha", "dispersão", "pizza", "rosca", "histograma"]
           else ["coluna", "barra", "linha", "dispersão", "pizza", "rosca", "histograma"].index(sugestao),
           horizontal=True)

        incompativel, mensagem_erro = verifica_incompatibilidade(tipo_grafico, col_x, col_y)
        if incompativel:
            st.markdown(f'<div class="aviso-erro">⚠️ Incompatibilidade: {mensagem_erro}</div>', unsafe_allow_html=True)
        else:
            if tipo_grafico == "coluna":
                fig = px.bar(df, x=col_x, y=col_y, color=col_x)
            elif tipo_grafico == "barra":
                fig = px.bar(df, x=col_y, y=col_x, orientation='h', color=col_x)
            elif tipo_grafico == "linha":
                fig = px.line(df, x=col_x, y=col_y)
            elif tipo_grafico == "dispersão":
                fig = px.scatter(df, x=col_x, y=col_y, color=col_x)
            elif tipo_grafico == "pizza":
                fig = px.pie(df, names=col_x, values=col_y)
            elif tipo_grafico == "rosca":
                fig = px.pie(df, names=col_x, values=col_y, hole=0.4)
            elif tipo_grafico == "histograma":
                fig = px.histogram(df, x=col_x, y=col_y, color=col_x)
            else:
                fig = px.bar(df, x=col_x, y=col_y, color=col_x)

            st.plotly_chart(fig, use_container_width=True)

            # Botões lado a lado: baixar PNG + incorporar
            col_btn1, col_btn2 = st.columns([1,1])
            with col_btn1:
                st.download_button(
                    label="🔽 Baixar gráfico como PNG",
                    data=fig.to_image(format="png"),
                    file_name="grafico.png",
                    mime="image/png"
                )
            with col_btn2:
                if st.button("🧩 Incorporar"):
                    iframe_html = f"""<iframe srcdoc='{fig.to_html(full_html=False)}' width="600" height="400" frameborder="0"></iframe>"""
                    st.code(iframe_html, language="html")

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="bloco">', unsafe_allow_html=True)
        st.subheader("🤖 Análise da IA")

        if st.button("💡 Gerar análise"):
            with st.spinner("Gerando análise..."):
                pergunta = f"O que este gráfico representa sobre a relação entre {col_x} e {col_y}?"
                try:
                    resposta = requests.post(
                        "http://localhost:11434/api/generate",
                        json={"model": "mistral", "prompt": pergunta, "stream": False},
                        timeout=30
                    )
                    texto = resposta.json()["response"]
                    st.write(texto)
                except Exception as e:
                    st.warning(f"⚠️ Erro na comunicação com IA: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="assinatura">📌 Desenvolvido por Cristiane Antunes Rodrigues – 2025</div>', unsafe_allow_html=True)

