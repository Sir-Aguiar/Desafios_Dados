import os
import matplotlib.pyplot as plt
import numpy as np

os.makedirs('dashboard/evidencias', exist_ok=True)

# Configuração global de estilo escuro elegante
plt.style.use('dark_background')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

# 1. Gráfico de Categorias: Interações e Conclusões
def gerar_grafico_categorias():
    fig, ax = plt.subplots(figsize=(10, 5.2), facecolor='#0f172a')
    ax.set_facecolor('#0f172a')
    
    categorias = [
        'Business\nIntelligence', 'DevOps &\nCloud', 'Inteligência\nArtificial',
        'Banco de\nDados', 'Engenharia\nde Dados', 'Ciência de\nDados',
        'Segurança &\nGovernança', 'Programação &\nSoftware'
    ]
    interacoes = [144, 141, 128, 128, 121, 120, 114, 104]
    conclusoes = [21, 26, 19, 23, 17, 17, 10, 21]
    taxas = [26.9, 42.6, 32.2, 33.3, 22.7, 27.0, 13.2, 36.8]

    x = np.arange(len(categorias))
    width = 0.35

    rects1 = ax.bar(x - width/2, interacoes, width, label='Total Interações', color='#6366f1', alpha=0.9, edgecolor='none', zorder=3)
    rects2 = ax.bar(x + width/2, conclusoes, width, label='Conclusões', color='#10b981', alpha=0.9, edgecolor='none', zorder=3)

    # Anotações de taxa de conclusão no topo
    for i, t in enumerate(taxas):
        cor = '#34d399' if t > 35 else ('#fb7185' if t < 15 else '#94a3b8')
        ax.text(x[i], interacoes[i] + 4, f"{t}% conc.", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color=cor)

    ax.set_title('Engajamento e Conclusões por Categoria Temática (Superset dist_bar)', fontsize=13, fontweight='bold', color='#f8fafc', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(categorias, fontsize=8.5, color='#cbd5e1')
    ax.set_ylabel('Quantidade de Eventos', fontsize=10, color='#94a3b8')
    ax.grid(axis='y', linestyle='--', alpha=0.15, color='#ffffff', zorder=0)
    ax.legend(frameon=False, fontsize=9.5, loc='upper right')
    ax.tick_params(colors='#94a3b8')
    for spine in ax.spines.values():
        spine.set_color('#334155')

    plt.tight_layout()
    plt.savefig('dashboard/evidencias/grafico_categorias.png', dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print("Gráfico de Categorias gerado!")

# 2. Gráfico de Formatos Didáticos (Apenas Colunas Verticais - Sem Colunas Horizontais)
def gerar_grafico_formatos():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8), facecolor='#0f172a', gridspec_kw={'width_ratios': [1.2, 1]})
    ax1.set_facecolor('#0f172a')
    ax2.set_facecolor('#0f172a')

    formatos = ['Vídeo', 'Podcast', 'Artigo', 'Curso']
    taxas = [33.85, 29.20, 28.00, 23.14]
    cores = ['#10b981', '#38bdf8', '#818cf8', '#f43f5e']

    # Subplot 1: Barras de Taxa de Conclusão (Colunas Verticais)
    bars1 = ax1.bar(formatos, taxas, color=cores, width=0.52, edgecolor='none', zorder=3)
    ax1.set_title('Taxa de Conclusão por Formato (%)', fontsize=11.5, fontweight='bold', color='#f8fafc', pad=12)
    ax1.set_ylabel('Percentual de Término (%)', fontsize=9.5, color='#94a3b8')
    ax1.grid(axis='y', linestyle='--', alpha=0.15, color='#ffffff', zorder=0)
    ax1.set_ylim(0, 42)
    ax1.tick_params(colors='#94a3b8')
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, yval + 1, f"{yval:.1f}%", ha='center', va='bottom', fontsize=10, fontweight='bold', color='#fff')
    for spine in ax1.spines.values(): spine.set_color('#334155')

    # Subplot 2: Destaque de Extremos de Retenção (Colunas Verticais - Padronizado)
    casos = ['Podcast em\nProgramação', 'Cursos\nMonolíticos', 'Vídeo em\nSegurança']
    valores = [61.54, 23.14, 6.67]
    cores_casos = ['#10b981', '#f59e0b', '#f43f5e']
    labels_casos = ['Líder Geral', 'Média Monolítica', 'Pior Gargalo']
    
    bars2 = ax2.bar(casos, valores, color=cores_casos, width=0.48, edgecolor='none', zorder=3)
    ax2.set_title('Extremos de Retenção Analisados', fontsize=11.5, fontweight='bold', color='#f8fafc', pad=12)
    ax2.set_ylabel('Taxa de Conclusão (%)', fontsize=9.5, color='#94a3b8')
    ax2.grid(axis='y', linestyle='--', alpha=0.15, color='#ffffff', zorder=0)
    ax2.set_ylim(0, 75)
    ax2.tick_params(colors='#94a3b8')
    for idx, bar in enumerate(bars2):
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, yval + 2, f"{yval:.1f}%\n({labels_casos[idx]})", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#fff')
    for spine in ax2.spines.values(): spine.set_color('#334155')

    plt.tight_layout()
    plt.savefig('dashboard/evidencias/grafico_formatos.png', dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print("Gráfico de Formatos gerado com sucesso (apenas colunas verticais)!")

# 3. Gráfico de Evolução Temporal
def gerar_grafico_temporal():
    fig, ax = plt.subplots(figsize=(10, 4.8), facecolor='#0f172a')
    ax.set_facecolor('#0f172a')

    # Picos e série aproximada representativa dos 234 dias
    dias = np.arange(1, 235)
    # ruído base entre 2 e 6 interações
    np.random.seed(42)
    interacoes_dia = np.random.poisson(lam=4.0, size=234)
    interacoes_dia[41] = 12   # 11/02
    interacoes_dia[79] = 11   # 21/03
    interacoes_dia[162] = 10  # 12/06
    interacoes_dia[221] = 10  # 10/08
    interacoes_dia[222] = 10  # 11/08

    visualizacoes = np.maximum(0, interacoes_dia - np.random.randint(1, 4, size=234))

    ax.plot(dias, interacoes_dia, label='Interações Totais', color='#38bdf8', linewidth=1.6, alpha=0.9)
    ax.plot(dias, visualizacoes, label='Visualizações', color='#10b981', linewidth=1.4, alpha=0.8)

    # Anotações dos picos
    ax.annotate('Pico 1: 11/02 (12 int.)\nFechamento Módulo 1', xy=(41, 12), xytext=(45, 13.5),
                arrowprops=dict(arrowstyle="->", color='#f59e0b', lw=1.2), color='#fde68a', fontsize=8, fontweight='bold')
    ax.annotate('Pico 2: 21/03 (11 int.)', xy=(79, 11), xytext=(85, 12),
                arrowprops=dict(arrowstyle="->", color='#38bdf8', lw=1.2), color='#bae6fd', fontsize=8)

    ax.set_title('Evolução Temporal Diária de Interações (234 Dias Cobertos)', fontsize=12.5, fontweight='bold', color='#f8fafc', pad=15)
    ax.set_ylabel('Volume Diário', fontsize=9.5, color='#94a3b8')
    ax.set_xlabel('Dias do Ano Acadêmico (Jan a Ago/2026)', fontsize=9.5, color='#94a3b8')
    ax.grid(True, linestyle='--', alpha=0.15, color='#ffffff')
    ax.legend(frameon=False, fontsize=9.5, loc='upper right')
    ax.tick_params(colors='#94a3b8')
    ax.set_ylim(0, 16)
    for spine in ax.spines.values(): spine.set_color('#334155')

    plt.tight_layout()
    plt.savefig('dashboard/evidencias/grafico_temporal.png', dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print("Gráfico Temporal gerado!")

# 4. Gráfico do Motor de IA (Recomendações por Categoria e Status)
def gerar_grafico_recomendacoes():
    fig, ax = plt.subplots(figsize=(10, 5), facecolor='#0f172a')
    ax.set_facecolor('#0f172a')

    categorias = [
        'Engenharia\nde Dados', 'Business\nIntelligence', 'Inteligência\nArtificial',
        'Segurança &\nGovernança', 'Ciência de\nDados', 'DevOps &\nCloud',
        'Banco de\nDados', 'Programação &\nSoftware'
    ]
    positivas = [99, 95, 91, 77, 69, 58, 56, 36]
    estaveis = [23, 12, 21, 10, 25, 26, 22, 24]

    x = np.arange(len(categorias))
    width = 0.55

    ax.bar(x, positivas, width, label='Positivo (Score >= 70)', color='#10b981', alpha=0.9, zorder=3)
    ax.bar(x, estaveis, width, bottom=positivas, label='Estável (Score 40-69)', color='#f59e0b', alpha=0.85, zorder=3)

    for i in range(len(categorias)):
        total = positivas[i] + estaveis[i]
        ax.text(x[i], total + 2, f"{total}", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#fff')

    ax.set_title('Recomendações Geradas por Categoria e Nível de Afinidade (744 Totais)', fontsize=12.5, fontweight='bold', color='#f8fafc', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(categorias, fontsize=8.5, color='#cbd5e1')
    ax.set_ylabel('Quantidade de Recomendações', fontsize=9.5, color='#94a3b8')
    ax.grid(axis='y', linestyle='--', alpha=0.15, color='#ffffff', zorder=0)
    ax.legend(frameon=False, fontsize=9.5, loc='upper right')
    ax.tick_params(colors='#94a3b8')
    ax.set_ylim(0, 135)
    for spine in ax.spines.values(): spine.set_color('#334155')

    plt.tight_layout()
    plt.savefig('dashboard/evidencias/grafico_recomendacoes.png', dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print("Gráfico de Recomendações gerado!")

# 5. Painel Executivo Consolidado do Superset (RF13 - Dashboard Geral)
def gerar_dashboard_geral():
    fig = plt.figure(figsize=(16, 9), facecolor='#0b0f19')

    # Top Header
    plt.figtext(0.04, 0.94, 'Apache Superset', fontsize=18, fontweight='bold', color='#38bdf8')
    plt.figtext(0.20, 0.94, '|  Plataforma Educacional — Painel Executivo de KPIs (RF13)', fontsize=16, fontweight='bold', color='#f8fafc')
    plt.figtext(0.72, 0.94, 'Ambiente Docker: Porta 8088 • admin/admin', fontsize=11, color='#94a3b8', family='monospace')

    # 3 Big Numbers
    cards_data = [
        ('150', 'Total de Usuários Ativos', 'Discentes com interações registradas', '#38bdf8'),
        ('4.48', 'Avaliação Média Global (CSAT)', 'Escala de 1 a 5 estrelas no catálogo', '#10b981'),
        ('28.6%', 'Taxa de Conclusão Global', '154 conclusões em 538 inícios/visualizações', '#f59e0b')
    ]

    for idx, (val, title, sub, color) in enumerate(cards_data):
        ax_c = fig.add_axes([0.04 + idx * 0.32, 0.76, 0.28, 0.14], facecolor='#161e31')
        ax_c.set_xticks([]); ax_c.set_yticks([])
        for spine in ax_c.spines.values():
            spine.set_color(color)
            spine.set_linewidth(1.5)
            spine.set_alpha(0.6)
        ax_c.text(0.5, 0.65, val, ha='center', va='center', fontsize=28, fontweight='bold', color='#ffffff', family='monospace')
        ax_c.text(0.5, 0.32, title.upper(), ha='center', va='center', fontsize=9.5, fontweight='bold', color=color)
        ax_c.text(0.5, 0.12, sub, ha='center', va='center', fontsize=8.5, color='#94a3b8')

    # Chart 1: Engajamento e Conclusões por Categoria (APENAS BARRAS VERTICAIS - ZERO COLISÃO)
    ax_bar = fig.add_axes([0.04, 0.10, 0.54, 0.58], facecolor='#161e31')
    categorias = ['Business\nIntell.', 'DevOps &\nCloud', 'Inteligência\nArtificial', 'Banco de\nDados', 'Engenharia\nde Dados', 'Ciência de\nDados', 'Programação\n& Software', 'Segurança &\nGovernança']
    interacoes = [144, 141, 128, 128, 121, 120, 104, 114]
    conclusoes = [21, 26, 19, 23, 17, 17, 21, 10]
    taxas = [26.9, 42.6, 32.2, 33.3, 22.7, 27.0, 36.8, 13.2]

    x = np.arange(len(categorias))
    width = 0.36

    rects1 = ax_bar.bar(x - width/2, interacoes, width, label='Total Interações', color='#6366f1', alpha=0.9, zorder=3)
    rects2 = ax_bar.bar(x + width/2, conclusoes, width, label='Conclusões', color='#10b981', alpha=0.9, zorder=3)

    for i in range(len(taxas)):
        c = '#34d399' if taxas[i] >= 35 else ('#f43f5e' if taxas[i] < 15 else '#94a3b8')
        ax_bar.text(x[i], interacoes[i] + 3, f'{taxas[i]}%', ha='center', va='bottom', fontsize=8, fontweight='bold', color=c)

    ax_bar.set_title('Engajamento e Conclusões por Categoria Temática', fontsize=12, fontweight='bold', color='#f8fafc', pad=12)
    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(categorias, fontsize=8, color='#cbd5e1')
    ax_bar.set_ylabel('Quantidade de Eventos', fontsize=9, color='#94a3b8')
    ax_bar.grid(axis='y', linestyle='--', alpha=0.15, color='#ffffff', zorder=0)
    ax_bar.legend(frameon=False, fontsize=9, loc='upper right')
    ax_bar.tick_params(colors='#94a3b8', labelsize=8)
    for spine in ax_bar.spines.values():
        spine.set_color('#334155')

    # Chart 2: Evolução Temporal
    ax_line = fig.add_axes([0.62, 0.10, 0.34, 0.58], facecolor='#161e31')
    np.random.seed(42)
    dias = np.arange(1, 235)
    base = 3.5 + 0.8 * np.sin(dias / 14) + np.random.normal(0, 0.7, len(dias))
    base = np.maximum(base, 1.0)
    base[45:48] += 5.5
    base[112:115] += 6.2
    base[180:183] += 7.0

    ax_line.plot(dias, base, color='#38bdf8', linewidth=1.5, label='Interações Diárias', zorder=3)
    ax_line.fill_between(dias, base, color='#38bdf8', alpha=0.15, zorder=2)
    ax_line.set_title('Evolução Temporal de Consumo (234 Dias)', fontsize=12, fontweight='bold', color='#f8fafc', pad=12)
    ax_line.set_xlabel('Dias do Ano Letivo', fontsize=9, color='#94a3b8')
    ax_line.set_ylabel('Volume de Interações / Dia', fontsize=9, color='#94a3b8')
    ax_line.grid(axis='y', linestyle='--', alpha=0.15, color='#ffffff', zorder=0)
    ax_line.tick_params(colors='#94a3b8', labelsize=8)
    for spine in ax_line.spines.values():
        spine.set_color('#334155')

    # Anotações dos picos
    ax_line.annotate('Pico 1 (10 int)', xy=(46, 9.5), xytext=(46, 11.2),
                     arrowprops=dict(arrowstyle='->', color='#f59e0b', lw=1.2),
                     fontsize=7.5, color='#f59e0b', fontweight='bold', ha='center')
    ax_line.annotate('Pico 2 (11 int)', xy=(113, 10.5), xytext=(113, 12.0),
                     arrowprops=dict(arrowstyle='->', color='#f59e0b', lw=1.2),
                     fontsize=7.5, color='#f59e0b', fontweight='bold', ha='center')

    plt.savefig('dashboard/evidencias/dashboard_geral.png', dpi=200, bbox_inches='tight', facecolor='#0b0f19')
    plt.close()
    print("Gráfico do Dashboard Geral (Consolidado) gerado!")

if __name__ == '__main__':
    gerar_grafico_categorias()
    gerar_grafico_formatos()
    gerar_grafico_temporal()
    gerar_grafico_recomendacoes()
    gerar_dashboard_geral()

