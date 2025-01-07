import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
import io

def format_brazilian(number):
    return f"{number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def create_pdf(vendedor, data, group_df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=6, bottomMargin=6)
    elements = []

    styles = getSampleStyleSheet()
    header = Paragraph(f"Vendedor: {vendedor} - {data}", styles['Heading2'])
    elements.append(header)

    table_data = [['Sacado', 'Tipo', 'Total', 'Comissao']]
    for index, row in group_df.iterrows():
        table_data.append([
            row['Sacado'], 
            row['Tipo'], 
            format_brazilian(float(row['Total'])), 
            format_brazilian(float(row['Comissao']))
        ])

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

    doc.build(elements)
    
    return buffer

st.title("Gerador de PDF por Vendedor")
uploaded_file = st.file_uploader("Escolha um arquivo Excel", type="xlsx")
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    
    grouped = df.groupby(['Vendedor', 'Data'])
    
    for (vendedor, data), group_df in grouped:
        pdf_buffer = create_pdf(vendedor, data, group_df)
        
        pdf_buffer.seek(0)
        
        st.download_button(
            label=f"Baixar PDF - {vendedor} - {data}",
            data=pdf_buffer.getvalue(),
            file_name=f"{vendedor}_{data}.pdf",
            mime="application/pdf"
        )
