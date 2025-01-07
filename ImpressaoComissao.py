import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
import io

# Função para formatar números no formato brasileiro
def format_brazilian(number):
    return f"{number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Função para criar um PDF para cada grupo
def create_pdf(vendedor, data, group_df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=6, bottomMargin=6)
    elements = []

    # Adicionar cabeçalho
    styles = getSampleStyleSheet()
    header = Paragraph(f"Vendedor: {vendedor} - {data}", styles['Heading2'])
    elements.append(header)

    # Criar dados da tabela
    table_data = [['Sacado', 'Tipo', 'Total', 'Comissao']]
    for index, row in group_df.iterrows():
        table_data.append([
            row['Sacado'], 
            row['Tipo'], 
            format_brazilian(float(row['Total'])), 
            format_brazilian(float(row['Comissao']))
        ])

    # Criar tabela
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ]))
    elements.append(table)

    # Construir PDF
    doc.build(elements)
    
    return buffer

# Interface do Streamlit
st.title("Gerador de PDF de Carregamento")
uploaded_file = st.file_uploader("Escolha um arquivo Excel", type="xlsx")
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    
    # Agrupar os dados por 'Vendedor' e 'Data'
    grouped = df.groupby(['Vendedor', 'Data'])
    
    # Iterar sobre cada grupo e criar um PDF separado
    for (vendedor, data), group_df in grouped:
        pdf_buffer = create_pdf(vendedor, data, group_df)
        
        # Salvar o PDF final em um buffer
        pdf_buffer.seek(0)
        
        # Botão para download do PDF separado para cada vendedor e data
        st.download_button(
            label=f"Baixar PDF - {vendedor} - {data}",
            data=pdf_buffer.getvalue(),
            file_name=f"{vendedor}_{data}.pdf",
            mime="application/pdf"
        )
