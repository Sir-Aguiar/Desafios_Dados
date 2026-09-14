import os
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def criar_apresentacao_powerpoint():
    prs = Presentation()
    # Slide 16:9 Widescreen (13.33 x 7.5 polegadas)
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Cores corporativas modernas
    C_BG = RGBColor(15, 23, 42)       # #0f172a escuro profundo
    C_CARD = RGBColor(26, 32, 53)     # #1a2035
    C_WHITE = RGBColor(248, 250, 252) # #f8fafc
    C_MUTED = RGBColor(148, 163, 184) # #94a3b8
    C_BLUE = RGBColor(56, 189, 248)   # #38bdf8
    C_INDIGO = RGBColor(99, 102, 241) # #6366f1
    C_GREEN = RGBColor(16, 185, 129)  # #10b981
    C_RED = RGBColor(244, 63, 94)     # #f43f5e
    C_AMBER = RGBColor(245, 158, 11)  # #f59e0b

    def add_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_BG
        bg.line.fill.background()
        return bg

    def add_header(slide, tag, title):
        # Tag
        tb_tag = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(11.7), Inches(0.35))
        p_tag = tb_tag.text_frame.paragraphs[0]
        p_tag.text = tag.upper()
        p_tag.font.name = 'Arial'
        p_tag.font.size = Pt(10)
        p_tag.font.bold = True
        p_tag.font.color.rgb = C_BLUE

        # Title
        tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(11.7), Inches(0.7))
        p_title = tb_title.text_frame.paragraphs[0]
        p_title.text = title
        p_title.font.name = 'Arial'
        p_title.font.size = Pt(21)
        p_title.font.bold = True
        p_title.font.color.rgb = C_WHITE

    def add_card(slide, left, top, width, height, val, lbl, sub="", color=C_BLUE, val_size=Pt(22)):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = C_CARD
        card.line.color.rgb = color
        card.line.width = Pt(1.5)

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.18)
        tf.margin_right = Inches(0.18)
        tf.margin_top = Inches(0.12)
        tf.margin_bottom = Inches(0.12)

        p0 = tf.paragraphs[0]
        p0.text = str(val)
        p0.font.name = 'Arial'
        p0.font.size = val_size
        p0.font.bold = True
        p0.font.color.rgb = C_WHITE

        p1 = tf.add_paragraph()
        p1.text = lbl
        p1.font.name = 'Arial'
        p1.font.size = Pt(10.5)
        p1.font.bold = True
        p1.font.color.rgb = color

        if sub:
            p2 = tf.add_paragraph()
            p2.text = sub
            p2.font.name = 'Arial'
            p2.font.size = Pt(8.5)
            p2.font.color.rgb = C_MUTED

    def add_fitted_picture(slide, img_path, left, top, max_width, max_height):
        """
        Insere imagem com proporção exata respeitando estritamente max_width e max_height.
        Garante que a imagem NUNCA extrapole o slide e fique perfeitamente centralizada.
        """
        if not os.path.exists(img_path):
            return None
        
        with Image.open(img_path) as im:
            img_w, img_h = im.size
        
        img_aspect = img_w / img_h
        box_aspect = max_width / max_height

        if img_aspect > box_aspect:
            # Imagem proporcionalmente mais larga que o container: fixa largura
            target_w = max_width
            target_h = max_width / img_aspect
        else:
            # Imagem proporcionalmente mais alta que o container: fixa altura
            target_h = max_height
            target_w = max_height * img_aspect

        # Centraliza horizontalmente e verticalmente no box reservado
        actual_left = left + (max_width - target_w) / 2
        actual_top = top + (max_height - target_h) / 2

        # Moldura estética sutil atrás da imagem
        border_box = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            actual_left - Inches(0.03),
            actual_top - Inches(0.03),
            target_w + Inches(0.06),
            target_h + Inches(0.06)
        )
        border_box.fill.solid()
        border_box.fill.fore_color.rgb = RGBColor(15, 23, 42)
        border_box.line.color.rgb = RGBColor(56, 189, 248)
        border_box.line.width = Pt(1.2)

        pic = slide.shapes.add_picture(img_path, actual_left, actual_top, width=target_w, height=target_h)
        return pic

    # =========================================================================
    # SLIDE 1: Abertura e Arquitetura
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    add_background(s1)
    add_header(s1, "Slide 1 de 9 • Visão Geral (~35s)", "Pipeline de Recomendação e Dashboard Educacional")
    
    add_card(s1, Inches(0.8), Inches(1.6), Inches(3.6), Inches(2.1), "Evasão Discente", "Problema Central de Negócio", "Plataforma multiformato com alto volume de dados, mas baixa visibilidade de conclusão.", C_AMBER, Pt(22))
    add_card(s1, Inches(4.8), Inches(1.6), Inches(3.6), Inches(2.1), "Híbrida & Vetorial", "Arquitetura Ponta a Ponta", "PostgreSQL + pgvector (384d) e MongoDB (NoSQL) orquestrados em Docker.", C_INDIGO, Pt(22))
    add_card(s1, Inches(8.8), Inches(1.6), Inches(3.6), Inches(2.1), "Apache Superset", "Entrega Visual Executiva", "10 visões analíticas em tempo real transformando 3.000 registros em planos de ação.", C_GREEN, Pt(22))

    tb1 = s1.shapes.add_textbox(Inches(0.8), Inches(4.1), Inches(11.6), Inches(2.4))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "• Desafio Estratégico: Alunos avaliam o catálogo com notas de excelência, mas abandonam trilhas teóricas no meio do caminho."
    p.font.size = Pt(14)
    p.font.color.rgb = C_WHITE
    p2 = tf1.add_paragraph()
    p2.text = "• Solução Integrada: Da ingestão com 100% de integridade ao motor preditivo vetorial e painel interativo no Superset."
    p2.font.size = Pt(14)
    p2.font.color.rgb = C_WHITE
    
    s1.notes_slide.notes_text_frame.text = (
        "Bom dia a todos os membros da banca. Hoje apresentamos a solução da nossa equipe para a plataforma de conteúdos educacionais. "
        "Nosso desafio principal não foi apenas construir um pipeline que funcionasse tecnicamente, mas responder a uma dor crítica de qualquer edtech: "
        "como transformar dados brutos de navegação em decisões pedagógicas concretas para combater a evasão de alunos. "
        "Nossa arquitetura conecta fontes multimodais em CSV e JSON, passa por um armazenamento híbrido no PostgreSQL e MongoDB, "
        "utiliza representações vetoriais com pgvector para inteligência semântica e entrega os resultados mastigados em um dashboard analítico no Apache Superset. "
        "Vamos ver como esses dados se comportaram na prática."
    )

    # =========================================================================
    # SLIDE 2: Qualidade e Ingestão
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_background(s2)
    add_header(s2, "Slide 2 de 9 • Governança de Dados (~55s)", "Qualidade e Confiabilidade na Ingestão (RF12 / KPI 3)")

    add_card(s2, Inches(0.8), Inches(1.6), Inches(3.6), Inches(1.8), "0,0%", "Catálogo de Conteúdos", "1.000 lidos • 0 correções (100% íntegro na origem)", C_BLUE, Pt(24))
    add_card(s2, Inches(4.8), Inches(1.6), Inches(3.6), Inches(1.8), "35,6%", "Interações dos Alunos", "1.000 lidos • 356 corrigidos (nulos e percentuais)", C_GREEN, Pt(24))
    add_card(s2, Inches(8.8), Inches(1.6), Inches(3.6), Inches(1.8), "83,7%", "Comentários (MongoDB)", "1.000 lidos • 837 sanitizados (strings e notas)", C_INDIGO, Pt(24))

    add_card(s2, Inches(0.8), Inches(3.8), Inches(11.6), Inches(2.6), "100% de Conformidade Operacional Final", "Zero Descarte de Registros", 
             "Nenhum dado do estudante foi eliminado. O pipeline aplicou regras de validação defensiva em camadas:\n"
             "• Catálogo: Normalização semântica de categorias e padronização de carga horária.\n"
             "• Interações: Imputação determinística de percentuais de conclusão faltantes baseados no tipo de evento.\n"
             "• Comentários: Limpeza de espaços em branco, formatação de tags opcionais e conversão estrita de escalas 1-5 no MongoDB.", C_GREEN, Pt(20))

    s2.notes_slide.notes_text_frame.text = (
        "Começando pela base de tudo: a confiabilidade da ingestão. Processamos três mil registros no total, mil de cada fonte, "
        "e aplicamos regras rigorosas de saneamento antes de qualquer gravação. O catálogo de conteúdos chegou perfeito: mil itens lidos, zero correções necessárias. "
        "Já nas interações dos estudantes, 35,6% dos registros precisaram de tratamento de valores nulos e normalização de percentuais. "
        "Nos comentários em MongoDB, 83,7% passaram por higienização de strings e validação de notas. "
        "O grande diferencial de engenharia da nossa equipe foi garantir 100% de conformidade operacional final com zero descarte de linhas. "
        "Nenhum dado foi varrido para debaixo do tapete: tudo foi validado, corrigido e integrado com rastreabilidade."
    )

    # =========================================================================
    # SLIDE 3: IA Vetorial e Recomendação
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_background(s3)
    add_header(s3, "Slide 3 de 9 • IA Vetorial (~60s)", "Inteligência Semântica e Motor de Recomendação")

    add_card(s3, Inches(0.8), Inches(1.50), Inches(2.7), Inches(1.35), "0,84", "Busca Específica", "'Python avançado com POO' (pgvector)", C_BLUE, Pt(20))
    add_card(s3, Inches(3.7), Inches(1.50), Inches(2.7), Inches(1.35), "0,66", "Busca Ampla", "'Fundamentos de banco para IA'", C_BLUE, Pt(20))
    add_card(s3, Inches(6.6), Inches(1.50), Inches(2.7), Inches(1.35), "78,09%", "Alta Afinidade", "581 recomendações (score >= 70)", C_GREEN, Pt(20))
    add_card(s3, Inches(9.5), Inches(1.50), Inches(2.9), Inches(1.35), "1,96%", "Seletividade", "744 selecionadas de 38.007 pares", C_INDIGO, Pt(20))

    # Imagem perfeitamente enquadrada sem extrapolar
    add_fitted_picture(s3, 'dashboard/evidencias/grafico_recomendacoes.png', Inches(0.8), Inches(3.05), Inches(11.7), Inches(3.95))

    s3.notes_slide.notes_text_frame.text = (
        "Para a busca e recomendação, geramos vetores de 384 dimensões utilizando o modelo MiniLM-L6-v2 integrado nativamente ao PostgreSQL via extensão pgvector. "
        "Validamos que a busca semântica responde com altíssima precisão quando a intenção do aluno é clara: para uma consulta como 'Python avançado com POO', "
        "atingimos similaridade de 0,84 no topo do ranking. Para termos mais amplos, como 'Fundamentos de banco para IA', a similaridade fica em torno de 0,66, "
        "refletindo com precisão a dispersão do tema. Nosso motor de recomendação combina histórico de visualização e curtida com uma trava obrigatória: "
        "conteúdos já concluídos têm pontuação zerada automaticamente. Avaliamos mais de 38 mil pares possíveis de usuário e conteúdo, e o motor foi cirúrgico: "
        "persistiu apenas 744 recomendações — uma taxa de seletividade de 1,96% —, sendo que mais de 78% dessas sugestões são de altíssima afinidade, com pontuação superior a 70 pontos."
    )

    # =========================================================================
    # SLIDE 4: Dashboard - Diagnóstico Global
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_background(s4)
    add_header(s4, "Slide 4 de 9 • Dashboard: Diagnóstico (~60s)", "Painel Executivo Superset: O Paradoxo do Negócio")

    add_card(s4, Inches(0.8), Inches(1.45), Inches(2.15), Inches(1.20), "150", "Usuários Ativos", "Discentes com interações", C_BLUE, Pt(19))
    add_card(s4, Inches(3.15), Inches(1.45), Inches(2.15), Inches(1.20), "4,48", "Satisfação CSAT", "Escala de 1 a 5 estrelas", C_GREEN, Pt(19))
    add_card(s4, Inches(5.50), Inches(1.45), Inches(2.15), Inches(1.20), "28,6%", "Taxa Conclusão", "154 de 538 inícios/views", C_AMBER, Pt(19))
    add_card(s4, Inches(7.85), Inches(1.45), Inches(2.15), Inches(1.20), "144,9 m", "Tempo Médio", "Média por conteúdo", C_INDIGO, Pt(19))
    add_card(s4, Inches(10.20), Inches(1.45), Inches(2.25), Inches(1.20), "78,1%", "Afinidade IA", "Score >= 70 no lote", C_GREEN, Pt(19))

    # Botão de Acesso Direto ao Superset (compacto e elegante)
    btn_box = s4.shapes.add_textbox(Inches(0.8), Inches(2.72), Inches(11.7), Inches(0.35))
    tf_btn = btn_box.text_frame
    tf_btn.margin_top = 0
    tf_btn.margin_bottom = 0
    p_btn = tf_btn.paragraphs[0]
    run_btn = p_btn.add_run()
    run_btn.text = "🚀 Acessar Apache Superset ao Vivo: http://localhost:8088/superset/dashboard/1/ (Login: admin / admin)"
    run_btn.font.name = 'Arial'
    run_btn.font.size = Pt(10.5)
    run_btn.font.bold = True
    run_btn.font.color.rgb = C_BLUE
    run_btn.hyperlink.address = "http://localhost:8088/superset/dashboard/1/"

    # Imagem geral do Superset - Enquadrada rigorosamente no espaço restante (altura máxima 4.15 polegadas)
    add_fitted_picture(s4, 'dashboard/evidencias/dashboard_geral.png', Inches(0.8), Inches(3.10), Inches(11.7), Inches(3.95))

    s4.notes_slide.notes_text_frame.text = (
        "Entrando agora no coração do nosso projeto: o que esses números realmente nos dizem sobre o negócio no nosso Dashboard do Superset? "
        "Temos uma base ativa de 150 alunos interagindo com mil conteúdos. À primeira vista, o cenário parece dos sonhos: a avaliação média global é de 4,48 estrelas em 5. "
        "Os estudantes que avaliam o catálogo atribuem notas de excelência. Porém, ao cruzar esse dado com a conclusão, encontramos o grande paradoxo da plataforma: "
        "a taxa de conclusão global é de apenas 28,62%. Foram 154 conclusões para mais de 530 materiais iniciados ou visualizados, com um tempo médio de consumo de cerca de 145 minutos. "
        "A pergunta que fizemos aos dados foi: se o conteúdo é tão bem avaliado, por que menos de um terço dos alunos chega até o fim? Fomos investigar onde está esse atrito."
    )

    # =========================================================================
    # SLIDE 5: Descoberta 1 - Categorias
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_background(s5)
    add_header(s5, "Slide 5 de 9 • Descoberta 1 (~90s)", "Desempenho por Categorias: A Ilusão da Evasão Temática")

    add_card(s5, Inches(0.8), Inches(1.48), Inches(5.6), Inches(1.22), "42,6% Conclusão", "Líder em Engajamento: DevOps & Cloud", "141 interações • 26 conclusões • Alunos concluem pela aplicação prática imediata.", C_GREEN, Pt(20))
    add_card(s5, Inches(6.8), Inches(1.48), Inches(5.6), Inches(1.22), "13,2% Conclusão", "Ponto Crítico: Segurança & Governança", "195 min médios gastos • Menor término, mas nota altíssima de 4,68 estrelas.", C_RED, Pt(20))

    # Imagem enquadrada perfeitamente
    add_fitted_picture(s5, 'dashboard/evidencias/grafico_categorias.png', Inches(0.8), Inches(2.90), Inches(11.7), Inches(4.15))

    s5.notes_slide.notes_text_frame.text = (
        "Nossa primeira hipótese foi: será que algumas áreas do conhecimento são rejeitadas pelos alunos? Olhamos para o gráfico de barras por categoria. "
        "Vejam o contraste: DevOps & Cloud é o nosso campeão de engajamento prático, atingindo 42,6% de taxa de conclusão com 141 interações. "
        "Logo ao lado, Business Intelligence lidera o volume bruto com 144 interações. Por outro lado, encontramos um abismo em Segurança & Governança: "
        "a taxa de término cai para alarmantes 13,16%, mesmo sendo a categoria com maior tempo médio gasto por aluno — quase 195 minutos. "
        "E aqui está a chave: em Segurança, a nota média é altíssima: 4,68 estrelas! E Engenharia de Dados lidera a satisfação com 4,75. "
        "Isso prova tecnicamente que o aluno não abandona por falta de interesse no tema. O problema é a forma como o conteúdo está empacotado."
    )

    # =========================================================================
    # SLIDE 6: Descoberta 2 - Formato Didático
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_background(s6)
    add_header(s6, "Slide 6 de 9 • O Maior Insight (~90s)", "O Formato Didático Define a Retenção do Aluno")

    add_card(s6, Inches(0.8), Inches(1.48), Inches(5.6), Inches(1.22), "61,54%", "Campeão do Acervo: Podcast em Programação", "Maior taxa de conclusão absoluta de todo o dataset (28,8 min • CSAT 4,27)", C_GREEN, Pt(20))
    add_card(s6, Inches(6.8), Inches(1.48), Inches(5.6), Inches(1.22), "6,67%", "Pior Gargalo: Vídeo em Segurança", "Apenas 1 conclusão para 15 inícios/views (Fadiga audiovisual extrema)", C_RED, Pt(20))

    # Imagem enquadrada perfeitamente
    add_fitted_picture(s6, 'dashboard/evidencias/grafico_formatos.png', Inches(0.8), Inches(2.90), Inches(11.7), Inches(4.15))

    s6.notes_slide.notes_text_frame.text = (
        "Quando cruzamos Categoria com Formato Didático, encontramos a resposta definitiva — este é o insight mais forte de todo o projeto. "
        "O conteúdo com maior taxa de término absoluto de todo o dataset é Podcast em Programação & Software, com 61,54% de conclusão. "
        "Os alunos escutam os 28 minutos médios de áudio e concluem o aprendizado com nota 4,27. "
        "No extremo oposto, o pior gargalo de toda a plataforma é Vídeo em Segurança & Governança, onde a conclusão despenca para meros 6,67%. "
        "Olhando a visão geral de formatos, o padrão é irrefutável: Vídeos e Podcasts sustentam taxas médias de 29% a 34% de conclusão, "
        "porque exigem cerca de 30 minutos de atenção. Já os Cursos Longos tradicionais têm a pior retenção média da plataforma, com apenas 23,1%, "
        "exigindo mais de 560 minutos. A recomendação executiva para a diretoria pedagógica é clara: não criem cursos monolíticos de 10 horas. "
        "Quebrem esses temas em trilhas de microlearning com vídeos curtos e podcasts temáticos."
    )

    # =========================================================================
    # SLIDE 7: Descoberta 3 - Temporalidade
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_background(s7)
    add_header(s7, "Slide 7 de 9 • Sazonalidade (~60s)", "Evolução Temporal e Comportamento de Consumo")

    add_card(s7, Inches(0.8), Inches(1.48), Inches(3.6), Inches(1.22), "234 Dias", "Cobertura Cronológica", "Atividade contínua mapeada no ano letivo", C_BLUE, Pt(20))
    add_card(s7, Inches(4.8), Inches(1.48), Inches(3.6), Inches(1.22), "4,3 int./dia", "Ritmo Médio Estável", "Regularidade basal de estudo na plataforma", C_INDIGO, Pt(20))
    add_card(s7, Inches(8.8), Inches(1.48), Inches(3.6), Inches(1.22), "Até 12 int.", "Picos de Engajamento", "Concentração em entregas e novos módulos", C_AMBER, Pt(20))

    # Imagem enquadrada perfeitamente
    add_fitted_picture(s7, 'dashboard/evidencias/grafico_temporal.png', Inches(0.8), Inches(2.90), Inches(11.7), Inches(4.15))

    s7.notes_slide.notes_text_frame.text = (
        "No gráfico temporal de linhas do Superset, mapeamos 234 dias de consumo contínuo durante o ano letivo. "
        "Identificamos uma média saudável de 4,3 interações diárias. No entanto, o aprendizado não acontece em fluxo estritamente uniforme: "
        "temos picos expressivos que chegam a 7, 10 e até 12 interações em um único dia. "
        "Ao correlacionar esses picos com o calendário, percebemos que eles coincidem exatamente com semanas de encerramento de ciclos e lançamentos de materiais novos. "
        "O aluno reage fortemente a estímulos de novidade e prazos bem definidos, o que valida o uso de campanhas periódicas de reengajamento."
    )

    # =========================================================================
    # SLIDE 8: Desafios Técnicos e Rigor de Engenharia
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_background(s8)
    add_header(s8, "Slide 8 de 9 • Rigor Técnico (~60s)", "Desafios Técnicos Superados e Engenharia com IA")

    add_card(s8, Inches(0.8), Inches(1.6), Inches(5.6), Inches(2.3), "Erro de Coluna Temporal", "Desafio no Apache Superset", 
             "Ao configurar os gráficos de barras no Superset, o componente timeseries exigia campo de data obrigatório.\n"
             "• Diagnóstico: Views agregadas de categorias não possuem séries cronológicas.\n"
             "• Solução de Engenharia: Migração para o componente 'dist_bar' com reestruturação do payload JSON.", C_AMBER, Pt(20))

    add_card(s8, Inches(6.8), Inches(1.6), Inches(5.6), Inches(2.3), "Auditoria 100% Humana", "Uso Responsável da IA (Seção 10)", 
             "Utilizamos o modelo Gemini como parceiro de pair programming para acelerar queries e orquestração Docker.\n"
             "• Toda lógica SQL foi recalculada e validada manualmente pela equipe contra o PostgreSQL.\n"
             "• Fórmulas de taxa de conclusão protegidas contra divisão por zero via NULLIF.", C_GREEN, Pt(20))

    s8.notes_slide.notes_text_frame.text = (
        "Como em qualquer projeto de engenharia de dados em produção, enfrentamos desafios técnicos reais que nos exigiram senso crítico. "
        "No Superset, por exemplo, ao tentar plotar os gráficos de barras por categoria, a ferramenta exigia uma coluna temporal obrigatória porque estava configurada como série temporal. "
        "Diagnosticamos que o componente adequado para dados categóricos sem data é o dist_bar, reestruturando o payload e restabelecendo o painel com sucesso. "
        "Em relação ao uso de Inteligência Artificial, utilizamos o modelo Gemini como parceiro de pair programming para acelerar a escrita das visões SQL e scripts de automação. "
        "Mas como rege a boa prática de engenharia, 100% dos cálculos, agrupamentos com NULLIF e métricas foram auditados e recalculados pela equipe contra o PostgreSQL, "
        "garantindo total integridade das fórmulas."
    )

    # =========================================================================
    # SLIDE 9: Conclusão
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_background(s9)
    add_header(s9, "Slide 9 de 9 • Fechamento (~60s)", "Recomendações Estratégicas para a Instituição")

    add_card(s9, Inches(0.8), Inches(1.6), Inches(3.6), Inches(2.4), "Priorizar Formatos Ágeis", "Ação 1: Produção Didática", 
             "Expandir acervo de Vídeos práticos e Podcasts em DevOps e Programação, que provaram atingir até 61,5% de conclusão.", C_GREEN, Pt(20))
    
    add_card(s9, Inches(4.8), Inches(1.6), Inches(3.6), Inches(2.4), "Reformular Segurança", "Ação 2: Intervenção Urgente", 
             "Quebrar os cursos densos e vídeos longos de Segurança & Governança em microlearning de 15 minutos e estudos de caso.", C_AMBER, Pt(20))

    add_card(s9, Inches(8.8), Inches(1.6), Inches(3.6), Inches(2.4), "Retenção Preditiva", "Ação 3: Ativação da IA", 
             "Acionar o motor de recomendação vetorial (78% de alta afinidade) para sugerir novos passos antes que o aluno evada.", C_BLUE, Pt(20))

    add_card(s9, Inches(0.8), Inches(4.3), Inches(11.6), Inches(1.7), "Pipeline 100% Validado de Ponta a Ponta", "Prontos para a Arguição da Banca", 
             "PostgreSQL + pgvector • MongoDB • Apache Superset operando com dados reais e 10 visões analíticas interativas.", C_INDIGO, Pt(18))

    # Links diretos
    links_box = s9.shapes.add_textbox(Inches(0.8), Inches(6.25), Inches(11.6), Inches(0.45))
    tf_links = links_box.text_frame
    p_l1 = tf_links.paragraphs[0]
    run_l1 = p_l1.add_run()
    run_l1.text = "📊 Superset: http://localhost:8088/superset/dashboard/1/    |    📑 Apresentação Web: http://localhost:8085/"
    run_l1.font.name = 'Arial'
    run_l1.font.size = Pt(11)
    run_l1.font.bold = True
    run_l1.font.color.rgb = C_BLUE
    run_l1.hyperlink.address = "http://localhost:8088/superset/dashboard/1/"

    s9.notes_slide.notes_text_frame.text = (
        "Para concluir, entregamos três ações estratégicas imediatas para a liderança da instituição: "
        "Primeira: Priorizar a produção de vídeos práticos e podcasts nas áreas de maior tração, como DevOps e Programação, que já provaram reter mais de 60% dos estudantes. "
        "Segunda: Intervir urgentemente nos materiais de Segurança & Governança, substituindo vídeos longos e monótonos por estudos de caso fragmentados. "
        "E terceira: Ativar em produção o motor de recomendação vetorial, que com seus 78% de precisão positiva consegue sugerir o próximo passo ideal antes que o aluno evada. "
        "A plataforma está 100% conteinerizada, documentada e com o dashboard operando em tempo real. Estamos prontos para as perguntas da banca. Muito obrigado."
    )

    output_path = 'apresentacao_plataforma_educacional.pptx'
    prs.save(output_path)
    print(f"Apresentação PowerPoint gerada com sucesso e sem extrapolação em: {output_path}")

if __name__ == '__main__':
    criar_apresentacao_powerpoint()
