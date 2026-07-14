import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os

st.set_page_config(page_title="Fábrica da Ste", page_icon="🖍️", layout="wide")

pasta_fontes = "fontes"
os.makedirs(pasta_fontes, exist_ok=True)

st.title("🖍️ Fábrica de Lembrancinhas da Ste")
st.markdown("Chega de escrever nomes à mão! Deixe o computador trabalhar por você. ")

# Arte e alunos
with st.container(border=True):
    st.subheader("A Arte e os Alunos")
    col_base1, col_base2 = st.columns(2)

    with col_base1:
        uploaded_file = st.file_uploader("Suba a arte em branco (PNG ou JPG):", type=["png", "jpg", "jpeg"])

    with col_base2:
        nomes_input = st.text_area("Cole a lista de alunos (um nome por linha):", "João\nMaria")
        nomes = [n.strip() for n in nomes_input.split('\n') if n.strip()]

# restante do app somente com upload da arte e nomes
if uploaded_file and nomes:
    imagem_base = Image.open(uploaded_file)
    largura, altura = imagem_base.size

    # sidebar
    st.sidebar.title("🎨 Ajustes da Arte")
    st.sidebar.markdown("Mexa aqui para deixar o nome no lugar certinho!")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔤 Escolha a Letra")
    fontes_disponiveis = [f for f in os.listdir(pasta_fontes) if f.endswith(('.ttf', '.otf'))]
    opcoes_fontes = ["Padrão do Sistema"] + fontes_disponiveis
    fonte_selecionada = st.sidebar.selectbox("Fonte da biblioteca:", opcoes_fontes)
    fonte_upload = st.sidebar.file_uploader("Ou suba uma fonte na hora:", type=["ttf", "otf"])

    st.sidebar.markdown("---")
    st.sidebar.subheader("📐 Tamanho e Cor")
    tamanho_fonte = st.sidebar.slider("Tamanho da Letra", 10, 300, 60)
    cor = st.sidebar.color_picker("Cor da Letra", "#000000")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📍 Posição do Texto")
    pos_x = st.sidebar.slider("⬅️ Horizontal ➡️", 0, largura, largura // 3)
    pos_y = st.sidebar.slider("⬆️ Vertical ⬇️", 0, altura, altura // 2)

    # Carrega a fonte
    try:
        if fonte_upload is not None:
            fonte = ImageFont.truetype(fonte_upload, tamanho_fonte)
        elif fonte_selecionada != "Padrão do Sistema":
            caminho_fonte = os.path.join(pasta_fontes, fonte_selecionada)
            fonte = ImageFont.truetype(caminho_fonte, tamanho_fonte)
        else:
            fonte = ImageFont.truetype("arial.ttf", tamanho_fonte)
    except Exception:
        st.sidebar.warning("⚠️ Usando a fonte fixa do sistema.")
        fonte = ImageFont.load_default()

    # preview
    with st.container(border=True):
        st.subheader("👀 Espiadinha na Arte")
        
        preview = imagem_base.copy()
        draw = ImageDraw.Draw(preview)
        draw.text((pos_x, pos_y), nomes[0], font=fonte, fill=cor)
        
        # Cria colunas para a imagem não ficar gigante na tela
        col_esp1, col_esp2, col_esp3 = st.columns([1, 2, 1])
        with col_esp2:
            st.image(preview, caption=f"Mostrando o primeiro aluno da lista: {nomes[0]}", use_container_width=True)

    # finalização e download
    with st.container(border=True):
        st.subheader("🖨️ 3️⃣ Organizar e Baixar")
        
        formato_download = st.radio(
            "Como deseja organizar o PDF?",
            ["📄 1 por folha (Para Certificados e Lembranças Grandes)", 
             "🗂️ Várias por folha A4 (Para Tags e Lembrancinhas Pequenas)"]
        )

        if "Várias" in formato_download:
            # O EXPANDER esconde as configurações avançadas!
            with st.expander("⚙️ Configurações de Grade (Clique para abrir)"):
                col_grid1, col_grid2 = st.columns(2)
                with col_grid1:
                    cols_por_pagina = st.number_input("Quantas colunas?", min_value=1, max_value=6, value=2)
                with col_grid2:
                    linhas_por_pagina = st.number_input("Quantas linhas?", min_value=1, max_value=10, value=3)

                if st.button("👀 Ver rascunho da folha A4"):
                    with st.spinner("Montando o rascunho..."):
                        A4_W, A4_H = 2480, 3508
                        margem = 50 
                        espaco_w = (A4_W - (margem * (cols_por_pagina + 1))) // cols_por_pagina
                        espaco_h = (A4_H - (margem * (linhas_por_pagina + 1))) // linhas_por_pagina
                        
                        def redimensionar_prev(img, max_w, max_h):
                            proporcao = min(max_w / img.width, max_h / img.height)
                            return img.resize((int(img.width * proporcao), int(img.height * proporcao)), Image.Resampling.LANCZOS)
                        
                        itens_por_pagina = cols_por_pagina * linhas_por_pagina
                        nomes_preview = nomes[:itens_por_pagina]
                        folha_preview = Image.new('RGB', (A4_W, A4_H), (255, 255, 255))
                        
                        for idx, nome_prev in enumerate(nomes_preview):
                            img_temp = imagem_base.copy()
                            draw = ImageDraw.Draw(img_temp)
                            draw.text((pos_x, pos_y), nome_prev, font=fonte, fill=cor)
                            tag_ajustada = redimensionar_prev(img_temp.convert('RGB'), espaco_w, espaco_h)
                            linha_atual, coluna_atual = idx // cols_por_pagina, idx % cols_por_pagina
                            x = margem + (coluna_atual * (espaco_w + margem))
                            y = margem + (linha_atual * (espaco_h + margem))
                            folha_preview.paste(tag_ajustada, (x, y))
                        
                        folha_preview_com_borda = ImageOps.expand(folha_preview, border=5, fill='gray')
                        st.image(folha_preview_com_borda, caption="Simulação da folha A4 para a impressora.")

        if st.button("Gerar PDF Completo", type="primary"):
            with st.spinner("Desenhando e organizando tudo... 🖍️"):
                imagens_geradas = []
                for nome in nomes:
                    img_temp = imagem_base.copy()
                    draw = ImageDraw.Draw(img_temp)
                    draw.text((pos_x, pos_y), nome, font=fonte, fill=cor)
                    imagens_geradas.append(img_temp.convert('RGB'))

                pdf_bytes = io.BytesIO()

                if "1 por folha" in formato_download:
                    imagens_geradas[0].save(pdf_bytes, format="PDF", resolution=100.0, save_all=True, append_images=imagens_geradas[1:])
                else:
                    A4_W, A4_H = 2480, 3508
                    margem = 50 
                    espaco_w = (A4_W - (margem * (cols_por_pagina + 1))) // cols_por_pagina
                    espaco_h = (A4_H - (margem * (linhas_por_pagina + 1))) // linhas_por_pagina
                    
                    def redimensionar(img, max_w, max_h):
                        proporcao = min(max_w / img.width, max_h / img.height)
                        return img.resize((int(img.width * proporcao), int(img.height * proporcao)), Image.Resampling.LANCZOS)
                    
                    tags_ajustadas = [redimensionar(img, espaco_w, espaco_h) for img in imagens_geradas]
                    itens_por_pagina = cols_por_pagina * linhas_por_pagina
                    paginas_a4 = []
                    
                    for i in range(0, len(tags_ajustadas), itens_por_pagina):
                        lote = tags_ajustadas[i:i + itens_por_pagina]
                        folha = Image.new('RGB', (A4_W, A4_H), (255, 255, 255))
                        
                        for idx, tag in enumerate(lote):
                            linha_atual, coluna_atual = idx // cols_por_pagina, idx % cols_por_pagina
                            x = margem + (coluna_atual * (espaco_w + margem))
                            y = margem + (linha_atual * (espaco_h + margem))
                            folha.paste(tag, (x, y))
                            
                        paginas_a4.append(folha)

                    paginas_a4[0].save(pdf_bytes, format="PDF", resolution=300.0, save_all=True, append_images=paginas_a4[1:])

                pdf_bytes.seek(0)
                
                # CHUVA DE BALÕES! 🎈
                st.balloons()
                st.success("Tudo pronto! 🥳 O PDF já está montado e pronto para a impressora.")
                st.download_button(
                    label="⬇️ Baixar PDF Completo", 
                    data=pdf_bytes, 
                    file_name="material_turma_organizado.pdf", 
                    mime="application/pdf"
                )
