import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os

# Configuração visual
st.set_page_config(page_title="Fábrica da Ste", page_icon="🖍️", layout="centered")

# Garante que a pasta de fontes exista no computador
pasta_fontes = "fontes"
os.makedirs(pasta_fontes, exist_ok=True)

st.title("🖍️ Fábrica de Lembrancinhas da Ste")
st.markdown("Chega de escrever nomes à mão! Suba a arte, cole os nomes e baixe tudo prontinho para a impressora.")

# dados base
st.divider()
st.subheader("1️⃣ A Arte e os Alunos")
col_base1, col_base2 = st.columns(2)

with col_base1:
    uploaded_file = st.file_uploader("Suba a arte em branco (PNG ou JPG):", type=["png", "jpg", "jpeg"])

with col_base2:
    nomes_input = st.text_area("Cole a lista de alunos (um nome por linha):", "Joãozinho\nMariazinha\nPedrinho\nAna\nCarlos\nBeatriz")
    nomes = [n.strip() for n in nomes_input.split('\n') if n.strip()]

if uploaded_file and nomes:
    imagem_base = Image.open(uploaded_file)
    largura, altura = imagem_base.size

    # fontes
    st.divider()
    st.subheader(" 2️⃣ Escolha a Letra")
    
    fontes_disponiveis = [f for f in os.listdir(pasta_fontes) if f.endswith(('.ttf', '.otf'))]
    opcoes_fontes = ["Padrão do Sistema"] + fontes_disponiveis
    
    col_fonte1, col_fonte2 = st.columns(2)
    with col_fonte1:
        fonte_selecionada = st.selectbox("Escolha uma fonte da biblioteca:", opcoes_fontes)
    with col_fonte2:
        fonte_upload = st.file_uploader("Ou suba um arquivo de fonte na hora (.ttf / .otf)", type=["ttf", "otf"])

    # ajustes visuais
    st.divider()
    st.subheader(" 3️⃣ Ajuste a Posição")
    st.markdown("Use os controles abaixo para posicionar o nome no espaço em branco da arte.")
    
    col_ajuste1, col_ajuste2 = st.columns(2)
    with col_ajuste1:
        pos_x = st.slider("⬅️ Horizontal ➡️", 0, largura, largura // 3)
        pos_y = st.slider("⬆️ Vertical ⬇️", 0, altura, altura // 2)
    with col_ajuste2:
        tamanho_fonte = st.slider("Tamanho da Letra", 10, 300, 60)
        cor = st.color_picker("Cor da Letra", "#000000")

    try:
        if fonte_upload is not None:
            fonte = ImageFont.truetype(fonte_upload, tamanho_fonte)
        elif fonte_selecionada != "Padrão do Sistema":
            caminho_fonte = os.path.join(pasta_fontes, fonte_selecionada)
            fonte = ImageFont.truetype(caminho_fonte, tamanho_fonte)
        else:
            fonte = ImageFont.truetype("arial.ttf", tamanho_fonte)
    except Exception:
        st.warning("⚠️ Usando a fonte fixa do sistema (o tamanho não vai mudar). Escolha uma fonte na lista!")
        fonte = ImageFont.load_default()

    # preview da arte com o primeiro nome
    st.divider()
    preview = imagem_base.copy()
    draw = ImageDraw.Draw(preview)
    draw.text((pos_x, pos_y), nomes[0], font=fonte, fill=cor)
    
    st.markdown("### 👀 Espiadinha na Arte")
    st.image(preview, caption=f"É assim que vai ficar (mostrando: {nomes[0]})", use_container_width=True)

    # finalização e download
    st.divider()
    st.subheader("🖨️ 4️⃣ Finalizar e Baixar")
    
    formato_download = st.radio(
        "Como deseja organizar o PDF?",
        ["📄 1 por folha (Para Certificados e Lembranças Grandes)", 
         "🗂️ Várias por folha A4 (Para Tags e Lembrancinhas Pequenas)"]
    )

    if "Várias" in formato_download:
        col_grid1, col_grid2 = st.columns(2)
        with col_grid1:
            cols_por_pagina = st.number_input("Quantas colunas?", min_value=1, max_value=6, value=2)
        with col_grid2:
            linhas_por_pagina = st.number_input("Quantas linhas?", min_value=1, max_value=10, value=3)

        # NOVA SEÇÃO: Preview da folha A4 inteira com Borda
        if st.button("👀 Ver rascunho da folha A4"):
            with st.spinner("Montando o rascunho da folha..."):
                A4_W, A4_H = 2480, 3508
                margem = 50 
                
                espaco_w = (A4_W - (margem * (cols_por_pagina + 1))) // cols_por_pagina
                espaco_h = (A4_H - (margem * (linhas_por_pagina + 1))) // linhas_por_pagina
                
                def redimensionar_prev(img, max_w, max_h):
                    proporcao = min(max_w / img.width, max_h / img.height)
                    novo_w = int(img.width * proporcao)
                    novo_h = int(img.height * proporcao)
                    return img.resize((novo_w, novo_h), Image.Resampling.LANCZOS)
                
                itens_por_pagina = cols_por_pagina * linhas_por_pagina
                nomes_preview = nomes[:itens_por_pagina]
                
                folha_preview = Image.new('RGB', (A4_W, A4_H), (255, 255, 255))
                
                for idx, nome_prev in enumerate(nomes_preview):
                    img_temp = imagem_base.copy()
                    draw = ImageDraw.Draw(img_temp)
                    draw.text((pos_x, pos_y), nome_prev, font=fonte, fill=cor)
                    
                    tag_ajustada = redimensionar_prev(img_temp.convert('RGB'), espaco_w, espaco_h)
                    
                    linha_atual = idx // cols_por_pagina
                    coluna_atual = idx % cols_por_pagina
                    
                    x = margem + (coluna_atual * (espaco_w + margem))
                    y = margem + (linha_atual * (espaco_h + margem))
                    
                    folha_preview.paste(tag_ajustada, (x, y))
                
                # ADICIONA UMA BORDA CINZA DE 5 PIXELS NA IMAGEM DE PREVIEW PARA DESTACAR DO FUNDO
                folha_preview_com_borda = ImageOps.expand(folha_preview, border=5, fill='gray')
                    
                st.markdown("#### 📄 Rascunho de Impressão:")
                st.image(folha_preview_com_borda, caption="Esta é uma simulação de como a primeira página sairá na impressora.")

    st.markdown("---")

    if st.button("Gerar PDF Completo"):
        with st.spinner("Desenhando e organizando tudo... 🖍️"):
            
            imagens_geradas = []
            for nome in nomes:
                img_temp = imagem_base.copy()
                draw = ImageDraw.Draw(img_temp)
                draw.text((pos_x, pos_y), nome, font=fonte, fill=cor)
                imagens_geradas.append(img_temp.convert('RGB'))

            pdf_bytes = io.BytesIO()

            if "1 por folha" in formato_download:
                imagens_geradas[0].save(
                    pdf_bytes, format="PDF", resolution=100.0, save_all=True, append_images=imagens_geradas[1:]
                )
            else:
                A4_W, A4_H = 2480, 3508
                margem = 50 
                
                espaco_w = (A4_W - (margem * (cols_por_pagina + 1))) // cols_por_pagina
                espaco_h = (A4_H - (margem * (linhas_por_pagina + 1))) // linhas_por_pagina
                
                def redimensionar(img, max_w, max_h):
                    proporcao = min(max_w / img.width, max_h / img.height)
                    novo_w = int(img.width * proporcao)
                    novo_h = int(img.height * proporcao)
                    return img.resize((novo_w, novo_h), Image.Resampling.LANCZOS)
                
                tags_ajustadas = [redimensionar(img, espaco_w, espaco_h) for img in imagens_geradas]
                
                itens_por_pagina = cols_por_pagina * linhas_por_pagina
                paginas_a4 = []
                
                for i in range(0, len(tags_ajustadas), itens_por_pagina):
                    lote = tags_ajustadas[i:i + itens_por_pagina]
                    folha = Image.new('RGB', (A4_W, A4_H), (255, 255, 255))
                    
                    for idx, tag in enumerate(lote):
                        linha_atual = idx // cols_por_pagina
                        coluna_atual = idx % cols_por_pagina
                        
                        x = margem + (coluna_atual * (espaco_w + margem))
                        y = margem + (linha_atual * (espaco_h + margem))
                        
                        folha.paste(tag, (x, y))
                        
                    paginas_a4.append(folha)

                paginas_a4[0].save(
                    pdf_bytes, format="PDF", resolution=300.0, save_all=True, append_images=paginas_a4[1:]
                )

            pdf_bytes.seek(0)
            
            st.success("Tudo pronto! 🥳 O PDF já está montado e pronto para a impressora.")
            st.download_button(
                label="⬇️ Baixar PDF Completo", 
                data=pdf_bytes, 
                file_name="material_turma.pdf", 
                mime="application/pdf"
            )