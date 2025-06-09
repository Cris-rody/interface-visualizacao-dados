# Milésima adptação e correção do codigo para criar uma plataforma de visualização automatizada de dados
# Cristiane 2025-06-08

# Testada em 2025-06-08
import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Configuração da página
st.set_page_config(page_title="Plataforma de visualização de dados", layout="wide")

# Menu lateral
st.sidebar.title("⚙️ Mais")
menu_opcao = st.sidebar.radio("Navegação", ["Visualização", "Sobre / Ajuda"])
if menu_opcao == "Sobre / Ajuda":
    st.sidebar.markdown("""
        ### Sobre esta Plataforma
        - Usuario carrega seu CSV, escolhe as colunas.
        - Tem uma sugestão do melhor grafico pra representar essas colunas, e tambem pode testar outros graficos
        - E pode baixar o grafico gerado em PNG.

        **Desenvolvido por Cristiane Antunes Rodrigues - 2025**
    """)
    st.stop()

################################################################################################################

# CSS (estilo) personalizado
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
        }
        .stRadio > div {
            display: flex;
            gap: 10px;
        }
    </style>
""", unsafe_allow_html=True)

################################################################################################################

# Título e descrição
st.markdown('<div class="titulo">Plataforma de Visualização automatizada de Dados</div>', unsafe_allow_html=True)
st.markdown('<div class="descricao">Ferramenta interativa para visualização de dados, a partir de uma base em formato CSV, com suporte de IA tanto para sugerir as melhor representação das colunas escolhidas, quanto para analisar o gráfico.</div>', unsafe_allow_html=True)

# Upload do CSV
upload_col1, upload_col2, upload_col3 = st.columns([1, 2, 1])
with upload_col2:
    arquivo = st.file_uploader("📁 Envie seu arquivo CSV", type="csv", label_visibility="visible")

if arquivo:
    df = pd.read_csv(arquivo)
    st.success("✅ Seu CSV foi carregado com sucesso!")

    st.markdown("#### 👀 Pré-visualização dos dados")
    st.dataframe(df.head(), use_container_width=True)

    colunas_numericas = df.select_dtypes(include='number').columns.tolist()
    colunas_categoricas = df.select_dtypes(include='object').columns.tolist()

    st.markdown('<hr>', unsafe_allow_html=True)

    # Seleção de colunas
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

    # Layout com gráfico e análise lado a lado
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown('<div class="bloco">', unsafe_allow_html=True)
        st.subheader("📈 Visualização do Gráfico")
        st.markdown(f"Sugestão da IA: **{sugestao.capitalize()}**")

        tipo_grafico = st.radio("🧩 Escolha o tipo de gráfico:", options=[
            "coluna", "barra", "linha", "dispersão", "pizza", "rosca", "histograma"
        ], index=0 if sugestao not in ["coluna", "barra", "linha", "dispersão", "pizza", "rosca", "histograma"]
           else ["coluna", "barra", "linha", "dispersão", "pizza", "rosca", "histograma"].index(sugestao),
           horizontal=True)

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

        # Botão para salvar em PNG
        st.download_button(
            label="🔽 Baixar gráfico como PNG",
            data=fig.to_image(format="png"),
            file_name="grafico.png",
            mime="image/png"
        )

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

    # Assinatura
    st.markdown('<div class="assinatura">📌 Desenvolvido por Cristiane Antunes Rodrigues – 2025</div>', unsafe_allow_html=True)
