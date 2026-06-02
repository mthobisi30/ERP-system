"""PDF generation for invoices and quotes (reportlab, pure-Python)."""
from io import BytesIO

from flask import current_app
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle)

from config.database import db
from app.models.customer import Customer
from app.models.accounting import Invoice, InvoiceItem
from app.models.sales import Quotation, QuotationItem

PRIMARY = colors.HexColor('#ea580c')
GREY = colors.HexColor('#6b7280')


def _money(symbol, amount):
    return f"{symbol} {float(amount or 0):,.2f}"


def _customer_name(customer_id):
    if not customer_id:
        return '—'
    c = db.session.get(Customer, customer_id)
    if not c:
        return '—'
    return c.company_name or c.contact_person or c.email or '—'


def _render(title, number, meta_rows, line_rows, totals):
    """Build a document PDF and return raw bytes."""
    cfg = current_app.config
    symbol = totals.get('symbol', cfg.get('CURRENCY_SYMBOL', 'R'))
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=18 * mm, bottomMargin=18 * mm,
                            leftMargin=18 * mm, rightMargin=18 * mm, title=f"{title} {number}")
    styles = getSampleStyleSheet()
    h_company = ParagraphStyle('company', parent=styles['Title'], textColor=PRIMARY, fontSize=20, spaceAfter=2)
    small = ParagraphStyle('small', parent=styles['Normal'], textColor=GREY, fontSize=9, leading=12)
    right = ParagraphStyle('right', parent=styles['Normal'], alignment=2, fontSize=9, leading=13)
    label = ParagraphStyle('label', parent=styles['Normal'], textColor=GREY, fontSize=8)
    elements = []

    # Header: company (left) + document title/number (right)
    company_block = [Paragraph(cfg.get('COMPANY_NAME', 'Company'), h_company)]
    company_lines = [cfg.get('COMPANY_EMAIL', ''), cfg.get('COMPANY_WEBSITE', '')]
    if cfg.get('VAT_REGISTRATION_NUMBER'):
        company_lines.append(f"VAT No: {cfg.get('VAT_REGISTRATION_NUMBER')}")
    company_block.append(Paragraph('<br/>'.join(x for x in company_lines if x), small))

    meta_html = '<br/>'.join(f"<b>{k}:</b> {v}" for k, v in meta_rows)
    doc_block = [Paragraph(f"<b>{title.upper()}</b>", ParagraphStyle('t', parent=right, fontSize=16, textColor=PRIMARY)),
                 Paragraph(f"#{number}", right), Spacer(1, 4), Paragraph(meta_html, right)]

    header = Table([[company_block, doc_block]], colWidths=[100 * mm, 70 * mm])
    header.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements += [header, Spacer(1, 14)]

    # Bill-to
    elements += [Paragraph('BILL TO', label),
                 Paragraph(totals.get('bill_to', '—'), styles['Normal']), Spacer(1, 14)]

    # Line items table
    data = [['Description', 'Qty', 'Unit Price', 'Amount']]
    for desc, qty, price, line in line_rows:
        data.append([Paragraph(str(desc or '—'), small),
                     f"{float(qty or 0):g}", _money(symbol, price), _money(symbol, line)])
    table = Table(data, colWidths=[95 * mm, 18 * mm, 30 * mm, 31 * mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ('LINEBELOW', (0, 0), (-1, -1), 0.4, colors.HexColor('#e5e7eb')),
        ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements += [table, Spacer(1, 10)]

    # Totals (right-aligned)
    tot = [['Subtotal', _money(symbol, totals['subtotal'])],
           [f"VAT ({totals.get('vat_rate', 0):g}%)", _money(symbol, totals['vat_amount'])],
           ['Total', _money(symbol, totals['total'])]]
    tt = Table(tot, colWidths=[40 * mm, 34 * mm], hAlign='RIGHT')
    tt.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10), ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEABOVE', (0, -1), (-1, -1), 0.6, colors.HexColor('#111827')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, -1), (-1, -1), PRIMARY),
        ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements += [tt]

    if totals.get('notes'):
        elements += [Spacer(1, 16), Paragraph('Notes', label), Paragraph(totals['notes'], small)]

    doc.build(elements)
    return buf.getvalue()


def invoice_pdf(invoice_id):
    inv = db.session.get(Invoice, invoice_id)
    if inv is None:
        return None, None
    items = InvoiceItem.query.filter_by(invoice_id=inv.id).all()
    line_rows = [(it.description, it.quantity, it.unit_price, it.line_total) for it in items]
    meta = [('Date', inv.invoice_date.isoformat() if inv.invoice_date else '—'),
            ('Due', inv.due_date.isoformat() if inv.due_date else '—'),
            ('Status', (inv.status or '').title())]
    pdf = _render('Invoice', inv.invoice_number, meta, line_rows, {
        'bill_to': _customer_name(inv.customer_id),
        'subtotal': inv.subtotal, 'vat_rate': float(inv.vat_rate or 0),
        'vat_amount': inv.vat_amount, 'total': inv.total_amount, 'notes': inv.notes,
    })
    return pdf, inv.invoice_number


def quote_pdf(quote_id):
    q = db.session.get(Quotation, quote_id)
    if q is None:
        return None, None
    items = QuotationItem.query.filter_by(quotation_id=q.id).all()
    line_rows = [(it.description, it.quantity, it.unit_price, it.line_total) for it in items]
    meta = [('Date', q.quote_date.isoformat() if q.quote_date else '—'),
            ('Valid until', q.valid_until.isoformat() if q.valid_until else '—'),
            ('Status', (q.status or '').title())]
    pdf = _render('Quote', q.quote_number, meta, line_rows, {
        'bill_to': _customer_name(q.customer_id),
        'subtotal': q.subtotal, 'vat_rate': float(q.vat_rate or 0),
        'vat_amount': q.tax_amount, 'total': q.total_amount, 'notes': q.notes,
    })
    return pdf, q.quote_number
