"""
reportes/reporte_pdf.py — Genera un reporte PDF completo con ReportLab.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from io import BytesIO


BRAND       = colors.HexColor('#0d6efd')
BRAND_DARK  = colors.HexColor('#084298')
DANGER      = colors.HexColor('#dc3545')
SUCCESS     = colors.HexColor('#198754')
WARNING     = colors.HexColor('#ffc107')
LIGHT_GREY  = colors.HexColor('#f8f9fa')
DARK        = colors.HexColor('#212529')
WHITE       = colors.white


def _styles():
    base = getSampleStyleSheet()
    return {
        'title': ParagraphStyle(
            'ReportTitle', fontSize=22, textColor=WHITE,
            alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=4
        ),
        'subtitle': ParagraphStyle(
            'SubTitle', fontSize=10, textColor=colors.HexColor('#adb5bd'),
            alignment=TA_CENTER, fontName='Helvetica', spaceAfter=2
        ),
        'section': ParagraphStyle(
            'Section', fontSize=13, textColor=BRAND_DARK,
            fontName='Helvetica-Bold', spaceBefore=14, spaceAfter=6
        ),
        'normal': ParagraphStyle(
            'NormalText', fontSize=9, textColor=DARK,
            fontName='Helvetica', leading=14
        ),
        'footer': ParagraphStyle(
            'Footer', fontSize=8, textColor=colors.grey,
            alignment=TA_CENTER, fontName='Helvetica'
        ),
    }


def _header(styles, fecha_str):
    """Bloque de encabezado con fondo degradado simulado."""
    header_data = [[
        Paragraph('<b>🛒 SmartShop</b>', styles['title']),
    ]]
    header_table = Table(header_data, colWidths=[17 * cm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, -1), BRAND_DARK),
        ('ROWPADDING',   (0, 0), (-1, -1), 14),
        ('ROUNDEDCORNERS', [8]),
    ]))

    subtitle = Paragraph(
        f'Reporte de Inventario — Generado el {fecha_str}',
        styles['subtitle']
    )
    return [header_table, Spacer(1, 0.3 * cm), subtitle, Spacer(1, 0.5 * cm)]


def _kpi_row(total_prods, total_units, valor_total):
    data = [[
        _kpi_cell('Productos', str(total_prods), BRAND),
        _kpi_cell('Unidades en stock', str(total_units), SUCCESS),
        _kpi_cell('Valor total', f'${valor_total:,.2f}', WARNING),
    ]]
    t = Table(data, colWidths=[5.5 * cm, 5.5 * cm, 5.5 * cm])
    t.setStyle(TableStyle([
        ('ALIGN',       (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING',(0, 0), (-1, -1), 6),
    ]))
    return t


def _kpi_cell(label, value, color):
    inner = [
        [Paragraph(f'<font size=18 color="{color.hexval()}"><b>{value}</b></font>',
                   ParagraphStyle('kv', alignment=TA_CENTER))],
        [Paragraph(f'<font size=8 color="#6c757d">{label}</font>',
                   ParagraphStyle('kl', alignment=TA_CENTER))],
    ]
    t = Table(inner, colWidths=[5 * cm])
    t.setStyle(TableStyle([
        ('BOX',         (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('BACKGROUND',  (0, 0), (-1, -1), LIGHT_GREY),
        ('ROWPADDING',  (0, 0), (-1, -1), 8),
        ('ROUNDEDCORNERS', [6]),
    ]))
    return t


def _productos_table(productos):
    headers = ['#', 'Nombre', 'Cantidad', 'Precio', 'Subtotal']
    rows = [headers]
    total_valor = 0.0
    for p in productos:
        subtotal = float(p.get('cantidad', 0)) * float(p.get('precio', 0))
        total_valor += subtotal
        rows.append([
            str(p.get('id', '')),
            str(p.get('nombre', '')),
            str(p.get('cantidad', 0)),
            f"${float(p.get('precio', 0)):.2f}",
            f"${subtotal:.2f}",
        ])
    # Total row
    rows.append(['', '', '', 'TOTAL', f"${total_valor:,.2f}"])

    col_widths = [1.2 * cm, 7 * cm, 2.5 * cm, 3 * cm, 3.3 * cm]
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    n = len(rows)
    t.setStyle(TableStyle([
        # Header
        ('BACKGROUND',    (0, 0), (-1, 0), BRAND),
        ('TEXTCOLOR',     (0, 0), (-1, 0), WHITE),
        ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, 0), 9),
        ('ALIGN',         (0, 0), (-1, 0), 'CENTER'),
        # Data rows
        ('FONTSIZE',      (0, 1), (-1, -1), 8.5),
        ('ROWBACKGROUNDS',(0, 1), (-1, -2), [WHITE, LIGHT_GREY]),
        ('ALIGN',         (2, 1), (-1, -1), 'CENTER'),
        # Total row
        ('BACKGROUND',    (0, -1), (-1, -1), BRAND_DARK),
        ('TEXTCOLOR',     (0, -1), (-1, -1), WHITE),
        ('FONTNAME',      (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN',         (3, -1), (-1, -1), 'RIGHT'),
        # Grid
        ('GRID',          (0, 0), (-1, -2), 0.4, colors.HexColor('#dee2e6')),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    return t


def _usuarios_table(usuarios):
    if not usuarios:
        return Paragraph('<i>No hay usuarios registrados.</i>',
                         ParagraphStyle('u', fontSize=9, textColor=colors.grey))
    headers = ['#', 'Nombre', 'Email', 'Creado']
    rows = [headers]
    for u in usuarios:
        rows.append([
            str(u.get('id_usuario', '')),
            str(u.get('nombre', '')),
            str(u.get('mail', '')),
            str(u.get('creado_en', ''))[:10],
        ])
    col_widths = [1.2 * cm, 5 * cm, 6.5 * cm, 4.3 * cm]
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0), colors.HexColor('#6c757d')),
        ('TEXTCOLOR',     (0, 0), (-1, 0), WHITE),
        ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, -1), 8.5),
        ('ROWBACKGROUNDS',(0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
        ('GRID',          (0, 0), (-1, -1), 0.4, colors.HexColor('#dee2e6')),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    return t


def _facturas_table(facturas):
    if not facturas:
        return Paragraph('<i>No hay facturas registradas.</i>',
                         ParagraphStyle('f', fontSize=9, textColor=colors.grey))
    headers = ['#', 'Cliente', 'Total', 'Estado', 'Fecha']
    rows = [headers]
    for f in facturas:
        rows.append([
            str(f.get('id_factura', '')),
            str(f.get('nombre_cliente', '')),
            f"${float(f.get('total', 0)):.2f}",
            str(f.get('estado', '')),
            str(f.get('creado_en', ''))[:10],
        ])
    col_widths = [1.2 * cm, 5.5 * cm, 3 * cm, 3.5 * cm, 3.8 * cm]
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0), DANGER),
        ('TEXTCOLOR',     (0, 0), (-1, 0), WHITE),
        ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, -1), 8.5),
        ('ROWBACKGROUNDS',(0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
        ('GRID',          (0, 0), (-1, -1), 0.4, colors.HexColor('#dee2e6')),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    return t


def generar_reporte_completo(productos, clientes=None, facturas=None) -> bytes:
    """
    Genera el PDF completo y retorna los bytes.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=2 * cm,
    )

    styles   = _styles()
    fecha_str = datetime.now().strftime('%d/%m/%Y %H:%M')
    story    = []

    # ── Encabezado ──────────────────────────────────────────────────────────
    story += _header(styles, fecha_str)

    # ── KPIs ────────────────────────────────────────────────────────────────
    total_prods  = len(productos)
    total_units  = sum(int(p.get('cantidad', 0)) for p in productos)
    valor_total  = sum(float(p.get('cantidad', 0)) * float(p.get('precio', 0)) for p in productos)

    story.append(_kpi_row(total_prods, total_units, valor_total))
    story.append(Spacer(1, 0.6 * cm))
    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#dee2e6')))

    # ── Tabla de productos ───────────────────────────────────────────────────
    story.append(Paragraph('📦 Inventario de Productos (MySQL)', styles['section']))
    if productos:
        story.append(_productos_table(productos))
    else:
        story.append(Paragraph('<i>No hay productos registrados.</i>',
                                styles['normal']))

    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#dee2e6')))

    # ── Tabla de usuarios ────────────────────────────────────────────────────
    story.append(Paragraph('👥 Usuarios Registrados', styles['section']))
    story.append(_usuarios_table(clientes or []))

    if facturas:
        story.append(Spacer(1, 0.5 * cm))
        story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#dee2e6')))
        story.append(Paragraph('🧾 Facturas', styles['section']))
        story.append(_facturas_table(facturas))

    # ── Footer ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#dee2e6')))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        f'SmartShop © 2026 — Flask + POO + SQLite + SQLAlchemy + MySQL | '
        f'Generado: {fecha_str}',
        styles['footer']
    ))

    doc.build(story)
    return buffer.getvalue()
