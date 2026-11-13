from pathlib import Path
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth

def gerar_pdf(df_compras, caminho_saida="data/processed/relatorio_compras.pdf"):
    colunas_obrigatorias = {
        "produto",
        "qtd_atual",
        "caixas_a_comprar",
        "custo_reposicao",
        "fornecedor",
    }
    faltantes = sorted(colunas_obrigatorias - set(df_compras.columns))
    if not df_compras.empty and faltantes:
        raise ValueError(
            f"Colunas necessárias para gerar o PDF ausentes: {', '.join(faltantes)}"
        )

    destino = Path(caminho_saida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(destino), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    titulo_estilo = ParagraphStyle(
        'TituloRelatorio',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1A202C'),
        spaceAfter=6
    )
    
    subtitulo_estilo = ParagraphStyle(
        'SubtituloRelatorio',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#4A5568'),
        spaceAfter=15
    )
    
    # Cabeçalho do Relatório
    story.append(Paragraph("<b>Relatório de Necessidade de Compras - Estoque Cinema</b>", titulo_estilo))
    story.append(Paragraph(f"Data de Emissão: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", subtitulo_estilo))
    story.append(Spacer(1, 10))
    
    if df_compras.empty:
        story.append(Paragraph("Nenhum item abaixo do estoque mínimo no momento. Estoque regularizado!", styles['Normal']))
    else:
        # Montar os dados da tabela
        # Cabeçalho da tabela
        dados_tabela = [["Produto", "Qtd Atual", "Caixas Necessárias", "Custo Total", "Fornecedor"]]
        
        # Adicionar as linhas dos produtos críticos
        for _, row in df_compras.iterrows():
            dados_tabela.append([
                str(row['produto']),
                str(row['qtd_atual']),
                str(row['caixas_a_comprar']),
                f"R$ {row['custo_reposicao']:.2f}",
                str(row['fornecedor'])
            ])
            
        # Linha de Custo Total Geral
        custo_total_geral = df_compras['custo_reposicao'].sum()
        dados_tabela.append(["", "", "Custo Total:", f"R$ {custo_total_geral:.2f}", ""])
        
        estilo_celula = ParagraphStyle(
            'CelulaTabela',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=11
        )
        estilo_cabecalho = ParagraphStyle(
            'CabecalhoTabela',
            parent=estilo_celula,
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=12,
            textColor=colors.white
        )
        estilo_total = ParagraphStyle(
            'TotalTabela',
            parent=estilo_celula,
            fontName='Helvetica-Bold'
        )

        # Dimensiona as colunas pelo conteúdo e limita a tabela à largura útil da página.
        larguras_naturais = []
        for coluna in zip(*dados_tabela):
            medidas = []
            for linha_idx, valor in enumerate(coluna):
                fonte = 'Helvetica-Bold' if linha_idx in (0, len(dados_tabela) - 1) else 'Helvetica'
                tamanho = 10 if linha_idx == 0 else 9
                medidas.extend(
                    stringWidth(linha, fonte, tamanho)
                    for linha in str(valor).splitlines() or ['']
                )
            maior_largura = max(medidas)
            larguras_naturais.append(maior_largura + 12)

        largura_minima = min(42, doc.width / len(larguras_naturais))
        pesos = [max(largura - largura_minima, 1) for largura in larguras_naturais]
        espaco_restante = doc.width - largura_minima * len(pesos)
        larguras_colunas = [
            largura_minima + espaco_restante * peso / sum(pesos)
            for peso in pesos
        ]

        dados_formatados = []
        for linha_idx, linha in enumerate(dados_tabela):
            estilo = estilo_cabecalho if linha_idx == 0 else (
                estilo_total if linha_idx == len(dados_tabela) - 1 else estilo_celula
            )
            dados_formatados.append([
                Paragraph(escape(str(valor)).replace('\n', '<br/>'), estilo)
                for valor in linha
            ])

        tabela = Table(dados_formatados, colWidths=larguras_colunas)
        
        # Estilização visual da tabela
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B6CB0')), # Azul corporativo no cabeçalho
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-2), colors.HexColor('#F7FAFC')), # Linhas alternadas claras
            ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor('#CBD5E0')),
            ('FONTNAME', (0,1), (-1,-2), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 9),
            # Linha final de Total destaque
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#EDF2F7')),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
            ('LINEABOVE', (0,-1), (-1,-1), 1.5, colors.HexColor('#2B6CB0')),
        ]))
        
        story.append(tabela)
        
    # Construir o PDF
    doc.build(story)
    print(f"[SUCESSO] PDF gerado com sucesso em: {destino}")

if __name__ == "__main__":
    # Teste rápido do gerador simulando dados
    print("Módulo generator.py carregado com sucesso.")