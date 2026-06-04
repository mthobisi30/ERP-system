"""PDF generation for the Rephina document pack (reportlab, pure-Python).

Generators:
  invoice_pdf(invoice_id)        -> (bytes, ref)
  quote_pdf(quote_id)            -> (bytes, ref)
  milestone_report_pdf(phase_id) -> (bytes, ref)
  endorsement_pdf(doc_id)        -> (bytes, ref)     # ProjectDocument (END)
  pmn_pdf(doc_id)                -> (bytes, ref)      # ProjectDocument (PMN)
  brd_pdf(project_id)            -> (bytes, ref)

Design: a clean letterhead (logo + contact strip), a restrained palette (navy +
grey, green used only as a thin accent), "Page X of Y" numbering, and paragraphs
kept whole — a paragraph that does not fit starts on the next page rather than
splitting. All issuer/letterhead + banking come from CompanySettings (falling back
to config), the client from Customer, and contract/schedule data from the project.
"""
import os
from io import BytesIO

from flask import current_app
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as _canvas
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, KeepTogether)

from config.database import db
from app.models.settings import CompanySettings
from app.models.customer import Customer
from app.models.project import Project, ProjectPhase, PhaseDeliverable, Milestone
from app.models.accounting import Invoice, InvoiceItem
from app.models.sales import Quotation, QuotationItem
from app.models.projectdoc import ProjectDocument

# Restrained palette — navy is the brand colour, grey for support, green a rare accent.
NAVY = colors.HexColor('#14223f')
GREEN = colors.HexColor('#4e7d32')
GREY = colors.HexColor('#6b7280')
DARK = colors.HexColor('#1f2937')
LIGHT = colors.HexColor('#f4f6f9')   # subtle zebra / panel fill
LINE = colors.HexColor('#dfe3e8')    # hairlines

# Page geometry (A4). Content sits between the letterhead and the footer.
_MARGIN = 18 * mm
_TOP = 35 * mm       # leaves room for the letterhead drawn on every page
_BOTTOM = 22 * mm    # leaves room for the footer
CONTENT_W = A4[0] - 2 * _MARGIN   # 174 mm

# Bundled letterhead logo. Prefer the print-sized asset (static/img) over the
# full-resolution source so generated PDFs stay small. Loaded once; degrades
# gracefully if absent.
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_LOGO = None
for _cand in (os.path.join(_ROOT, 'static', 'img', 'rephina-logo.png'),
              os.path.join(_ROOT, 'rephina-logo.png')):
    if os.path.exists(_cand):
        try:
            _LOGO = ImageReader(_cand)
            break
        except Exception:
            _LOGO = None


# ---------------------------------------------------------------- issuer / data

def _issuer():
    cfg = current_app.config
    s = CompanySettings.query.first()
    sym = cfg.get('CURRENCY_SYMBOL', 'R')
    base = {
        'legal_name': cfg.get('COMPANY_NAME', 'Company'),
        'name': cfg.get('COMPANY_NAME', 'Company'),
        'reg': '', 'tax_number': '', 'signatory': '', 'address': '',
        'email': cfg.get('COMPANY_EMAIL', ''), 'phone': '',
        'website': cfg.get('COMPANY_WEBSITE', ''),
        'vat_registered': cfg.get('VAT_ENABLED', True), 'vat_number': cfg.get('VAT_REGISTRATION_NUMBER', ''),
        'prefix': 'RSS', 'symbol': sym,
        'bank_name': '', 'bank_account_name': '', 'bank_account_number': '',
        'bank_branch_code': '', 'bank_account_type': '',
    }
    if s:
        base.update({
            'legal_name': s.legal_name or s.company_name or base['legal_name'],
            'name': s.company_name or base['name'],
            'reg': s.registration_number or '', 'tax_number': s.tax_number or '',
            'signatory': s.signatory_name or '',
            'address': s.address or '', 'email': s.email or base['email'],
            'phone': s.phone or '', 'website': s.website or base['website'],
            'vat_registered': s.vat_registered, 'vat_number': s.vat_number or '',
            'prefix': s.doc_ref_prefix or 'RSS',
            'bank_name': s.bank_name or '', 'bank_account_name': s.bank_account_name or '',
            'bank_account_number': s.bank_account_number or '', 'bank_branch_code': s.bank_branch_code or '',
            'bank_account_type': s.bank_account_type or '',
        })
    return base


def _money(sym, v):
    return f"{sym} {float(v or 0):,.2f}"


def _site(url):
    """Display form of a website URL — no scheme, no trailing slash."""
    return (url or '').replace('https://', '').replace('http://', '').rstrip('/')


def _styles():
    s = getSampleStyleSheet()

    def mk(name, **kw):
        return ParagraphStyle(name, parent=s['Normal'], **kw)

    return {
        'doctitle': ParagraphStyle('doctitle', parent=s['Title'], fontSize=21, leading=24,
                                   textColor=NAVY, alignment=0, spaceBefore=0, spaceAfter=0),
        'subtitle': mk('subtitle', fontSize=12.5, leading=16, textColor=NAVY, fontName='Helvetica-Bold'),
        'section': ParagraphStyle('section', parent=s['Heading4'], fontSize=10.5, leading=13,
                                  textColor=NAVY, fontName='Helvetica-Bold', spaceBefore=12, spaceAfter=2),
        'body': mk('body', fontSize=9.5, leading=14, textColor=DARK, spaceAfter=4,
                   allowWidows=0, allowOrphans=0),
        'small': mk('small', fontSize=8, leading=11, textColor=GREY),
        'cell': mk('cell', fontSize=8.5, leading=12, textColor=DARK),
        'cellb': mk('cellb', fontSize=9, leading=12, fontName='Helvetica-Bold', textColor=NAVY),
        'kvhead': mk('kvhead', fontSize=7.5, leading=10, fontName='Helvetica-Bold', textColor=NAVY),
        'whiteb': mk('whiteb', fontSize=8.5, leading=11, fontName='Helvetica-Bold', textColor=colors.white),
    }


# ---------------------------------------------------------------- letterhead / furniture

def _draw_header(c, iss):
    """Letterhead drawn at the top of every page: logo + contact strip + accent rule."""
    pw, ph = A4
    x0, x1 = _MARGIN, pw - _MARGIN
    if _LOGO:
        sz = 19 * mm
        c.drawImage(_LOGO, x0, ph - 10.5 * mm - sz, width=sz, height=sz,
                    preserveAspectRatio=True, mask='auto')
    else:
        c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 15)
        c.drawString(x0, ph - 18 * mm, iss['legal_name'])

    # Contact details, right-aligned.
    c.setFont('Helvetica', 8); c.setFillColor(GREY)
    rlines = [v for v in [_site(iss['website']), iss['email'], iss['phone'],
                          (iss['address'] or '').replace('\n', ', ')] if v]
    y = ph - 12.5 * mm
    for ln in rlines[:4]:
        c.drawRightString(x1, y, ln); y -= 4.2 * mm

    # Divider: full navy hairline with a short green accent on the left.
    ry = ph - 32 * mm
    c.setStrokeColor(LINE); c.setLineWidth(0.8); c.line(x0, ry, x1, ry)
    c.setStrokeColor(GREEN); c.setLineWidth(2.2); c.line(x0, ry, x0 + 26 * mm, ry)


def _draw_footer(c, iss, ref, page, total):
    pw, ph = A4
    x0, x1 = _MARGIN, pw - _MARGIN
    c.setStrokeColor(LINE); c.setLineWidth(0.6); c.line(x0, 16 * mm, x1, 16 * mm)

    c.setFont('Helvetica', 7.5); c.setFillColor(GREY)
    ident = '  ·  '.join(b for b in [iss['legal_name'], (f"Reg {iss['reg']}" if iss['reg'] else ''),
                                     (f"Tax {iss['tax_number']}" if iss['tax_number'] else '')] if b)
    c.drawCentredString(pw / 2, 11.6 * mm, ident)
    contact = '  ·  '.join(b for b in [(iss['address'] or '').replace('\n', ', '),
                                       _site(iss['website']), iss['email'], iss['phone']] if b)
    c.drawCentredString(pw / 2, 8.0 * mm, contact)

    if ref:
        c.drawString(x0, 11.6 * mm, ref)
    c.setFont('Helvetica-Bold', 7.5); c.setFillColor(NAVY)
    c.drawRightString(x1, 11.6 * mm, f"Page {page} of {total}")


class _DocCanvas(_canvas.Canvas):
    """Two-pass canvas so the footer can print 'Page X of Y' with the real total,
    and the letterhead/footer render identically on every page."""

    def __init__(self, *args, issuer=None, ref='', **kwargs):
        super().__init__(*args, **kwargs)
        self._issuer = issuer or {}
        self._ref = ref
        self._pages = []

    def showPage(self):
        self._pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._pages)
        for i, state in enumerate(self._pages, 1):
            self.__dict__.update(state)
            self.saveState()
            _draw_header(self, self._issuer)
            _draw_footer(self, self._issuer, self._ref, i, total)
            self.restoreState()
            super().showPage()
        super().save()


def _doc(ref, title):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=_TOP, bottomMargin=_BOTTOM,
                            leftMargin=_MARGIN, rightMargin=_MARGIN, title=f"{title} {ref}")
    return buf, doc


def _build(doc, buf, el, iss, ref):
    doc.build(el, canvasmaker=lambda *a, **k: _DocCanvas(*a, issuer=iss, ref=ref, **k))
    return buf.getvalue()


# ---------------------------------------------------------------- content helpers

def _banner(el, st, title, accent=NAVY):
    """Clean document title: large navy heading with a navy rule + short accent tick."""
    el += [Paragraph(title.upper(), st['doctitle']),
           HRFlowable(width='100%', thickness=1.1, color=NAVY, spaceBefore=3, spaceAfter=0),
           HRFlowable(width='24%', thickness=2.4, color=(accent or GREEN), spaceBefore=0,
                      spaceAfter=9, hAlign='LEFT')]


def _p(el, text, style):
    """Append a narrative paragraph that is kept whole (never split across a page)."""
    el.append(KeepTogether([Paragraph(text, style)]))


def _kv_block(st, heading, lines, accent=NAVY):
    """A boxed info panel: light heading band (navy text) over stacked lines."""
    head = Table([[Paragraph(heading, st['kvhead'])]], colWidths=[None])
    head.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), LIGHT),
                              ('LINEBELOW', (0, 0), (-1, -1), 0.6, LINE),
                              ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                              ('LEFTPADDING', (0, 0), (-1, -1), 8)]))
    body_rows = [[l if hasattr(l, 'wrap') else Paragraph(str(l), st['cell'])] for l in lines]
    body = Table(body_rows, colWidths=[None])
    body.setStyle(TableStyle([('TOPPADDING', (0, 0), (-1, -1), 1.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
                             ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8)]))
    wrap = Table([[head], [body]], colWidths=[None])
    wrap.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.6, LINE), ('TOPPADDING', (0, 1), (-1, 1), 5),
                             ('BOTTOMPADDING', (0, 1), (-1, 1), 6)]))
    return wrap


def _section(elements, st, title):
    elements += [Spacer(1, 6), Paragraph(title, st['section']),
                 HRFlowable(width='100%', thickness=0.6, color=LINE, spaceAfter=4)]


def _signatures(elements, st, client_name, issuer):
    elements += [Spacer(1, 14)]
    cl = [Paragraph(f"<b>CLIENT — {client_name}</b>", st['cell']), Spacer(1, 22),
          Paragraph("Authorised Signatory: ______________________", st['cell']), Spacer(1, 8),
          Paragraph("Name &amp; Title: ______________________", st['cell']), Spacer(1, 8),
          Paragraph("Date: ______________________", st['cell'])]
    dv = [Paragraph(f"<b>DEVELOPMENT CONSULTANT — {issuer['name']}</b>", st['cell']), Spacer(1, 22),
          Paragraph("Signature: ______________________", st['cell']), Spacer(1, 8),
          Paragraph(f"Name: {issuer['signatory'] or ''}", st['cell']), Spacer(1, 8),
          Paragraph("Date: ______________________", st['cell'])]
    t = Table([[cl, dv]], colWidths=[87 * mm, 87 * mm])
    t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('BOX', (0, 0), (0, 0), 0.6, LINE),
                          ('BOX', (1, 0), (1, 0), 0.6, LINE), ('LEFTPADDING', (0, 0), (-1, -1), 10),
                          ('RIGHTPADDING', (0, 0), (-1, -1), 10), ('TOPPADDING', (0, 0), (-1, -1), 10),
                          ('BOTTOMPADDING', (0, 0), (-1, -1), 10)]))
    elements += [KeepTogether([t])]


def _client_lines(st, customer):
    if not customer:
        return [Paragraph('—', st['cell'])]
    lines = [Paragraph(f"<b>{customer.company_name or customer.contact_person or '—'}</b>", st['cell'])]
    if customer.contact_person:
        lines.append(Paragraph(f"Att: {customer.contact_person}", st['cell']))
    contact = ' · '.join(x for x in [customer.email, customer.phone] if x)
    if contact:
        lines.append(Paragraph(contact, st['cell']))
    return lines


def _issuer_lines(st, iss, compact=False):
    """Issuer identity for an info panel. `compact` (for narrow columns) omits the
    address/email/phone — the letterhead already shows them on every page — which
    also avoids long emails breaking mid-word in tight columns."""
    lines = [Paragraph(f"<b>{iss['legal_name']}</b>", st['cell'])]
    if iss['reg']:
        lines.append(Paragraph(f"Reg. No. {iss['reg']}", st['cell']))
    if iss['tax_number']:
        lines.append(Paragraph(f"Tax No. {iss['tax_number']}", st['cell']))
    if not compact:
        if iss['address']:
            lines.append(Paragraph(iss['address'].replace('\n', ', '), st['cell']))
        contact = ' · '.join(x for x in [iss['email'], iss['phone']] if x)
        if contact:
            lines.append(Paragraph(contact, st['cell']))
    lines.append(Paragraph('VAT Registered: ' + iss['vat_number'] if (iss['vat_registered'] and iss['vat_number'])
                           else ('VAT Registered' if iss['vat_registered'] else 'Not VAT Registered'), st['small']))
    return lines


# ---------------------------------------------------------------- INVOICE

def invoice_pdf(invoice_id):
    inv = db.session.get(Invoice, invoice_id)
    if inv is None:
        return None, None
    iss = _issuer(); sym = iss['symbol']
    st = _styles()
    customer = db.session.get(Customer, inv.customer_id) if inv.customer_id else None
    project = db.session.get(Project, inv.project_id) if inv.project_id else None
    items = InvoiceItem.query.filter_by(invoice_id=inv.id).all()

    buf, doc = _doc(inv.invoice_number, 'Invoice')
    el = []
    _banner(el, st, 'INVOICE', GREEN)

    details = [Paragraph('<b>Invoice No.</b>  ' + inv.invoice_number, st['cell']),
               Paragraph('<b>Date</b>  ' + (inv.invoice_date.isoformat() if inv.invoice_date else '—'), st['cell'])]
    if inv.due_date:
        details.append(Paragraph('<b>Due</b>  ' + inv.due_date.isoformat(), st['cell']))
    top = Table([[_kv_block(st, 'FROM', _issuer_lines(st, iss)), _kv_block(st, 'INVOICE DETAILS', details)]],
                colWidths=[92 * mm, 82 * mm])
    top.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (0, 0), 6)]))
    el += [top, Spacer(1, 8)]

    proj_lines = [Paragraph(f"<b>{(project.system_name or project.name) if project else '—'}</b>", st['cell'])]
    if project and project.contract_ref:
        signed = f" · Signed {project.contract_signed_date.isoformat()}" if project.contract_signed_date else ''
        proj_lines.append(Paragraph(project.contract_ref + signed, st['cell']))
    mid = Table([[_kv_block(st, 'BILLED TO', _client_lines(st, customer)), _kv_block(st, 'PROJECT', proj_lines)]],
                colWidths=[92 * mm, 82 * mm])
    mid.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('RIGHTPADDING', (0, 0), (0, 0), 6)]))
    el += [mid, Spacer(1, 10)]

    rows = [[Paragraph('<b>DESCRIPTION</b>', st['whiteb']), Paragraph('<b>QTY</b>', st['whiteb']),
             Paragraph('<b>UNIT PRICE</b>', st['whiteb']), Paragraph('<b>AMOUNT</b>', st['whiteb'])]]
    for it in items:
        rows.append([Paragraph(it.description or '—', st['cell']), str(it.quantity or 0).rstrip('0').rstrip('.') or '0',
                     _money(sym, it.unit_price), _money(sym, it.line_total)])
    tbl = Table(rows, colWidths=[97 * mm, 15 * mm, 30 * mm, 32 * mm], repeatRows=1)
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY), ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 9), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT]),
        ('LINEBELOW', (0, 0), (-1, -1), 0.4, LINE),
        ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8)]))
    el += [tbl, Spacer(1, 8)]

    vat_label = f"VAT ({float(inv.vat_rate or 0):g}%)" if iss['vat_registered'] else 'VAT (Not Registered)'
    tot = [['Subtotal', _money(sym, inv.subtotal)],
           [vat_label, _money(sym, inv.vat_amount)],
           ['TOTAL DUE', _money(sym, inv.total_amount)]]
    tt = Table(tot, colWidths=[40 * mm, 34 * mm], hAlign='RIGHT')
    tt.setStyle(TableStyle([('FONTSIZE', (0, 0), (-1, -1), 10), ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                           ('LINEABOVE', (0, -1), (-1, -1), 0.8, NAVY), ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                           ('TEXTCOLOR', (0, -1), (-1, -1), GREEN), ('FONTSIZE', (0, -1), (-1, -1), 12),
                           ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4)]))
    el += [tt, Spacer(1, 14)]

    # Banking + payment reference
    bank_lines = []
    for lbl, val in [('Bank', iss['bank_name']), ('Account Name', iss['bank_account_name']),
                     ('Account No.', iss['bank_account_number']), ('Branch Code', iss['bank_branch_code']),
                     ('Account Type', iss['bank_account_type'])]:
        if val:
            bank_lines.append(Paragraph(f"<b>{lbl}</b>  {val}", st['cell']))
    if not bank_lines:
        bank_lines = [Paragraph('Banking details on request.', st['cell'])]
    payref = [Paragraph(f"<b>{inv.invoice_number}</b>", ParagraphStyle('pr', fontSize=12, textColor=GREEN, alignment=1)),
              Spacer(1, 4), Paragraph(f"Amount: {_money(sym, inv.total_amount)}", st['cell'])]
    bank = Table([[_kv_block(st, 'BANKING DETAILS', bank_lines), _kv_block(st, 'PAYMENT REFERENCE', payref)]],
                 colWidths=[92 * mm, 82 * mm])
    bank.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('RIGHTPADDING', (0, 0), (0, 0), 6)]))
    el += [KeepTogether([bank])]

    return _build(doc, buf, el, iss, inv.invoice_number), inv.invoice_number


# ---------------------------------------------------------------- QUOTE

def quote_pdf(quote_id):
    q = db.session.get(Quotation, quote_id)
    if q is None:
        return None, None
    iss = _issuer(); sym = iss['symbol']; st = _styles()
    customer = db.session.get(Customer, q.customer_id) if q.customer_id else None
    items = QuotationItem.query.filter_by(quotation_id=q.id).all()
    buf, doc = _doc(q.quote_number, 'Quotation')
    el = []
    _banner(el, st, 'QUOTATION', NAVY)
    details = [Paragraph('<b>Quote No.</b>  ' + q.quote_number, st['cell']),
               Paragraph('<b>Date</b>  ' + (q.quote_date.isoformat() if q.quote_date else '—'), st['cell'])]
    if q.valid_until:
        details.append(Paragraph('<b>Valid Until</b>  ' + q.valid_until.isoformat(), st['cell']))
    top = Table([[_kv_block(st, 'FROM', _issuer_lines(st, iss)),
                  _kv_block(st, 'QUOTE FOR', _client_lines(st, customer) + details)]], colWidths=[92 * mm, 82 * mm])
    top.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('RIGHTPADDING', (0, 0), (0, 0), 6)]))
    el += [top, Spacer(1, 4)]
    if q.title:
        el += [Spacer(1, 6), Paragraph(f"<b>{q.title}</b>", st['body'])]
    rows = [[Paragraph('<b>DESCRIPTION</b>', st['whiteb']), Paragraph('<b>QTY</b>', st['whiteb']),
             Paragraph('<b>UNIT PRICE</b>', st['whiteb']), Paragraph('<b>AMOUNT</b>', st['whiteb'])]]
    for it in items:
        rows.append([Paragraph(it.description or '—', st['cell']), str(it.quantity or 0).rstrip('0').rstrip('.') or '0',
                     _money(sym, it.unit_price), _money(sym, it.line_total)])
    tbl = Table(rows, colWidths=[97 * mm, 15 * mm, 30 * mm, 32 * mm], repeatRows=1)
    tbl.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), NAVY), ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                            ('FONTSIZE', (0, 0), (-1, -1), 9), ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT]),
                            ('LINEBELOW', (0, 0), (-1, -1), 0.4, LINE), ('TOPPADDING', (0, 0), (-1, -1), 6),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 6), ('LEFTPADDING', (0, 0), (-1, -1), 8),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 8)]))
    vat_label = f"VAT ({float(q.vat_rate or 0):g}%)" if iss['vat_registered'] else 'VAT (Not Registered)'
    tot = [['Subtotal', _money(sym, q.subtotal)], [vat_label, _money(sym, q.tax_amount)],
           ['TOTAL', _money(sym, q.total_amount)]]
    tt = Table(tot, colWidths=[40 * mm, 34 * mm], hAlign='RIGHT')
    tt.setStyle(TableStyle([('FONTSIZE', (0, 0), (-1, -1), 10), ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                           ('LINEABOVE', (0, -1), (-1, -1), 0.8, NAVY), ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                           ('TEXTCOLOR', (0, -1), (-1, -1), GREEN), ('FONTSIZE', (0, -1), (-1, -1), 12)]))
    el += [Spacer(1, 8), tbl, Spacer(1, 8), tt]
    if q.notes:
        _section(el, st, 'NOTES'); _p(el, q.notes, st['body'])
    return _build(doc, buf, el, iss, q.quote_number), q.quote_number


# ---------------------------------------------------------------- MILESTONE REPORT

def milestone_report_pdf(phase_id):
    ph = db.session.get(ProjectPhase, phase_id)
    if ph is None:
        return None, None
    iss = _issuer(); sym = iss['symbol']; st = _styles()
    project = db.session.get(Project, ph.project_id)
    customer = db.session.get(Customer, project.customer_id) if project and project.customer_id else None
    deliverables = PhaseDeliverable.query.filter_by(phase_id=ph.id).order_by(PhaseDeliverable.sequence).all()

    doc_ref, _seq = ProjectDocument.next_ref('MILE', iss['prefix'])
    buf, doc = _doc(doc_ref, 'Milestone Completion Report')
    el = []
    _banner(el, st, 'MILESTONE COMPLETION REPORT', GREEN)
    phase_title = f"Phase {ph.number} of {ph.total_phases} — {ph.title}" if ph.number else ph.title
    el += [Paragraph(f"{phase_title}", st['subtitle']),
           Paragraph(f"{doc_ref}", st['small']), Spacer(1, 6)]

    period = ''
    if ph.period_start or ph.period_end:
        period = f"{ph.period_start.isoformat() if ph.period_start else ''} – {ph.period_end.isoformat() if ph.period_end else ''}"
    contract_lines = [Paragraph(f"<b>{project.contract_ref or project.name}</b>", st['cell'])] if project else [Paragraph('—', st['cell'])]
    if period:
        contract_lines.append(Paragraph(f"Period: {period}", st['cell']))
    if ph.phase_value is not None:
        contract_lines.append(Paragraph(f"Phase value: {_money(sym, ph.phase_value)}", st['cell']))
    trig = [Paragraph(f"<b>{ph.triggers_invoice_ref or '—'}</b>", st['cell'])]
    blocks = Table([[_kv_block(st, 'FROM', _issuer_lines(st, iss, compact=True)), _kv_block(st, 'TO', _client_lines(st, customer)),
                     _kv_block(st, 'CONTRACT', contract_lines), _kv_block(st, 'TRIGGERS INVOICE', trig)]],
                   colWidths=[46 * mm, 44 * mm, 44 * mm, 40 * mm])
    blocks.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 2),
                               ('RIGHTPADDING', (0, 0), (-1, -1), 2)]))
    el += [blocks]

    if ph.gate_criteria or ph.gate_status:
        _section(el, st, 'MILESTONE GATE CRITERIA & STATUS')
        if ph.gate_criteria:
            _p(el, f"<i>{ph.gate_criteria}</i>", st['body'])
        if ph.gate_status:
            _p(el, f"<b>Status:</b> {ph.gate_status}", st['body'])

    _section(el, st, 'DELIVERABLES')
    rows = [[Paragraph('<b>Deliverable</b>', st['whiteb']), Paragraph('<b>Implementation</b>', st['whiteb']),
             Paragraph('<b>Evidence</b>', st['whiteb']), Paragraph('<b>Status</b>', st['whiteb'])]]
    for d in deliverables:
        rows.append([Paragraph(f"<b>{d.name}</b>", st['cell']), Paragraph(d.implementation or '', st['cell']),
                     Paragraph(d.evidence or '', st['cell']), Paragraph(d.status or '', st['cell'])])
    if len(rows) == 1:
        rows.append([Paragraph('—', st['cell']), '', '', ''])
    dt = Table(rows, colWidths=[40 * mm, 76 * mm, 34 * mm, 24 * mm], repeatRows=1)
    dt.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), NAVY), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                           ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT]),
                           ('LINEBELOW', (0, 0), (-1, -1), 0.4, LINE), ('TOPPADDING', (0, 0), (-1, -1), 6),
                           ('BOTTOMPADDING', (0, 0), (-1, -1), 6), ('LEFTPADDING', (0, 0), (-1, -1), 6),
                           ('RIGHTPADDING', (0, 0), (-1, -1), 6)]))
    el += [dt]
    if ph.additional_scope:
        _section(el, st, 'ADDITIONAL SCOPE — DELIVERED AT NO EXTRA COST')
        _p(el, ph.additional_scope, st['body'])

    _section(el, st, 'FORMAL ACCEPTANCE')
    acc = f"By signing below, {customer.company_name if customer else 'the Client'} confirms that this phase has been reviewed and the milestone gate demonstrated."
    if ph.triggers_invoice_ref:
        acc += f" This acceptance triggers invoice {ph.triggers_invoice_ref}."
    _p(el, acc, st['body'])
    _signatures(el, st, customer.company_name if customer else 'Client', iss)

    return _build(doc, buf, el, iss, doc_ref), doc_ref


# ---------------------------------------------------------------- schedule helper

def _schedule_table(st, sym, milestones):
    rows = [[Paragraph('<b>Payment</b>', st['whiteb']), Paragraph('<b>Invoice</b>', st['whiteb']),
             Paragraph('<b>Trigger</b>', st['whiteb']), Paragraph('<b>Amount</b>', st['whiteb']),
             Paragraph('<b>Status</b>', st['whiteb'])]]
    total = 0.0
    for m in milestones:
        total += float(m.amount or 0)
        rows.append([Paragraph(m.name, st['cell']), Paragraph(m.invoice_ref or '', st['cell']),
                     Paragraph(m.trigger or '', st['cell']), _money(sym, m.amount),
                     Paragraph((m.payment_status or '').title(), st['cell'])])
    rows.append([Paragraph('<b>TOTAL</b>', st['cell']), '', '', _money(sym, total), ''])
    t = Table(rows, colWidths=[30 * mm, 38 * mm, 56 * mm, 28 * mm, 22 * mm], repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), NAVY), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                          ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, LIGHT]),
                          ('ALIGN', (3, 0), (3, -1), 'RIGHT'), ('LINEBELOW', (0, 0), (-1, -1), 0.4, LINE),
                          ('LINEABOVE', (0, -1), (-1, -1), 0.8, NAVY), ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                          ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                          ('LEFTPADDING', (0, 0), (-1, -1), 6), ('RIGHTPADDING', (0, 0), (-1, -1), 6)]))
    # Payment schedules are short — keep the whole table (incl. TOTAL) on one page.
    return KeepTogether([t])


# ---------------------------------------------------------------- ENDORSEMENT

def endorsement_pdf(doc_id):
    pd = db.session.get(ProjectDocument, doc_id)
    if pd is None or pd.doc_type != 'END':
        return None, None
    iss = _issuer(); sym = iss['symbol']; st = _styles()
    data = pd.data or {}
    project = db.session.get(Project, pd.project_id) if pd.project_id else None
    customer = db.session.get(Customer, project.customer_id) if project and project.customer_id else None
    milestones = (Milestone.query.filter_by(project_id=pd.project_id).order_by(Milestone.sequence).all()
                  if pd.project_id else [])

    buf, doc = _doc(pd.doc_ref, pd.title or 'Endorsement')
    el = []
    _banner(el, st, (pd.title or 'ENDORSEMENT').upper(), NAVY)
    top = Table([[_kv_block(st, 'FROM', _issuer_lines(st, iss)), _kv_block(st, 'TO', _client_lines(st, customer))]],
                colWidths=[87 * mm, 87 * mm])
    top.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('RIGHTPADDING', (0, 0), (0, 0), 6)]))
    el += [top, Spacer(1, 8)]

    # key strip
    strip = [[Paragraph('<b>Original Value</b><br/>' + _money(sym, data.get('original_value')), st['cell']),
              Paragraph('<b>Adjustment</b><br/>' + _money(sym, data.get('discount')), st['cell']),
              Paragraph('<b>Revised Value</b><br/>' + _money(sym, data.get('revised_value')), st['cell']),
              Paragraph('<b>Period</b><br/>' + (data.get('delay_period') or '—'), st['cell'])]]
    ks = Table(strip, colWidths=[44 * mm, 44 * mm, 44 * mm, 42 * mm])
    ks.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), LIGHT), ('BOX', (0, 0), (-1, -1), 0.6, LINE),
                           ('INNERGRID', (0, 0), (-1, -1), 0.6, colors.white), ('TOPPADDING', (0, 0), (-1, -1), 6),
                           ('BOTTOMPADDING', (0, 0), (-1, -1), 6), ('LEFTPADDING', (0, 0), (-1, -1), 8)]))
    el += [ks]

    _section(el, st, '1. PURPOSE')
    _p(el, data.get('purpose') or '', st['body'])
    if data.get('reason'):
        _section(el, st, '2. TERMS')
        _p(el, '<b>Reason:</b> ' + data.get('reason'), st['body'])
        if data.get('terms'):
            _p(el, data.get('terms'), st['body'])
    if milestones:
        _section(el, st, '3. REVISED PAYMENT SCHEDULE')
        el += [_schedule_table(st, sym, milestones)]
    _section(el, st, 'CLIENT ACKNOWLEDGEMENT')
    _p(el, data.get('acknowledgement') or
       f"By signing below, {customer.company_name if customer else 'the Client'} accepts this endorsement.", st['body'])
    _signatures(el, st, customer.company_name if customer else 'Client', iss)
    return _build(doc, buf, el, iss, pd.doc_ref), pd.doc_ref


# ---------------------------------------------------------------- PROJECT MIGRATION NOTICE

def pmn_pdf(doc_id):
    pd = db.session.get(ProjectDocument, doc_id)
    if pd is None or pd.doc_type != 'PMN':
        return None, None
    iss = _issuer(); sym = iss['symbol']; st = _styles()
    data = pd.data or {}
    project = db.session.get(Project, pd.project_id) if pd.project_id else None
    customer = db.session.get(Customer, project.customer_id) if project and project.customer_id else None
    milestones = (Milestone.query.filter_by(project_id=pd.project_id).order_by(Milestone.sequence).all()
                  if pd.project_id else [])

    buf, doc = _doc(pd.doc_ref, pd.title or 'Project Migration Notice')
    el = []
    _banner(el, st, 'PROJECT MIGRATION NOTICE', NAVY)
    retired = [Paragraph(x, st['cell']) for x in (data.get('retired') or [])] or [Paragraph('—', st['cell'])]
    replacement = [Paragraph(x, st['cell']) for x in (data.get('replacement') or [])] or [Paragraph('—', st['cell'])]
    top = Table([[_kv_block(st, 'FROM', _issuer_lines(st, iss, compact=True)), _kv_block(st, 'TO', _client_lines(st, customer)),
                  _kv_block(st, 'RETIRED', retired), _kv_block(st, 'REPLACEMENT', replacement)]],
                colWidths=[46 * mm, 44 * mm, 42 * mm, 42 * mm])
    top.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 2)]))
    el += [top]

    _section(el, st, '1. NOTICE')
    _p(el, data.get('notice') or '', st['body'])
    reasons = data.get('reasons') or []
    if reasons:
        _section(el, st, '2. REASONS')
        rows = [[Paragraph('<b>#</b>', st['whiteb']), Paragraph('<b>Issue</b>', st['whiteb']), Paragraph('<b>Severity</b>', st['whiteb'])]]
        for i, r in enumerate(reasons, 1):
            rows.append([str(i), Paragraph(r.get('issue', '') if isinstance(r, dict) else str(r), st['cell']),
                         Paragraph(r.get('severity', '') if isinstance(r, dict) else '', st['cell'])])
        rt = Table(rows, colWidths=[10 * mm, 134 * mm, 30 * mm], repeatRows=1)
        rt.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), NAVY), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                               ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT]),
                               ('LINEBELOW', (0, 0), (-1, -1), 0.4, LINE), ('TOPPADDING', (0, 0), (-1, -1), 5),
                               ('BOTTOMPADDING', (0, 0), (-1, -1), 5), ('LEFTPADDING', (0, 0), (-1, -1), 6)]))
        el += [rt]
    if milestones:
        _section(el, st, '3. PAYMENT SCHEDULE — CARRIED FORWARD')
        el += [_schedule_table(st, sym, milestones)]
    _section(el, st, 'CLIENT ACKNOWLEDGEMENT')
    _p(el, data.get('acknowledgement') or
       f"By signing below, {customer.company_name if customer else 'the Client'} confirms the migration and that scope, value and schedule remain binding.", st['body'])
    _signatures(el, st, customer.company_name if customer else 'Client', iss)
    return _build(doc, buf, el, iss, pd.doc_ref), pd.doc_ref


# ---------------------------------------------------------------- BRD / SCOPE

def brd_pdf(project_id):
    project = db.session.get(Project, project_id)
    if project is None:
        return None, None
    iss = _issuer(); sym = iss['symbol']; st = _styles()
    customer = db.session.get(Customer, project.customer_id) if project.customer_id else None
    phases = ProjectPhase.query.filter_by(project_id=project.id).order_by(ProjectPhase.number).all()
    milestones = Milestone.query.filter_by(project_id=project.id).order_by(Milestone.sequence).all()
    ref = project.contract_ref or ((project.project_code + ' BRD') if project.project_code else 'BRD')

    buf, doc = _doc(ref, 'Business Requirements Document')
    el = []
    _banner(el, st, 'BUSINESS REQUIREMENTS DOCUMENT', NAVY)
    el += [Paragraph(f"{project.system_name or project.name}", st['subtitle']),
           Paragraph(ref + (f" · {project.project_type}" if project.project_type else ''), st['small']), Spacer(1, 6)]

    over = [Paragraph(f"<b>{project.system_name or project.name}</b>", st['cell'])]
    if project.project_type:
        over.append(Paragraph(f"Type: {project.project_type}", st['cell']))
    if project.project_code:
        over.append(Paragraph(f"Project code: {project.project_code}", st['cell']))
    top = Table([[_kv_block(st, 'PREPARED BY', _issuer_lines(st, iss, compact=True)),
                  _kv_block(st, 'FOR', _client_lines(st, customer)),
                  _kv_block(st, 'PROJECT', over)]], colWidths=[58 * mm, 58 * mm, 58 * mm])
    top.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 2)]))
    el += [top]

    if project.scope:
        _section(el, st, '1. SCOPE OF WORK')
        for para in str(project.scope).split('\n'):
            if para.strip():
                _p(el, para.strip(), st['body'])

    stack = [t.strip() for t in (project.tech_stack or '').split(',') if t.strip()]
    if stack:
        _section(el, st, '2. TECHNOLOGY STACK')
        _p(el, ' · '.join(stack), st['body'])

    if phases:
        _section(el, st, '3. PHASES & DELIVERABLES')
        for ph in phases:
            ptitle = f"Phase {ph.number} of {ph.total_phases} — {ph.title}" if ph.number else ph.title
            block = [Paragraph(f"<b>{ptitle}</b>" + (f"  ({_money(sym, ph.phase_value)})" if ph.phase_value is not None else ''), st['body'])]
            if ph.gate_criteria:
                block.append(Paragraph(f"<i>Gate: {ph.gate_criteria}</i>", st['small']))
            for d in PhaseDeliverable.query.filter_by(phase_id=ph.id).order_by(PhaseDeliverable.sequence).all():
                block.append(Paragraph(f"• <b>{d.name}</b> — {d.implementation or ''}", st['cell']))
            el.append(KeepTogether([Spacer(1, 4)] + block))

    if milestones:
        _section(el, st, '4. PAYMENT SCHEDULE')
        el += [_schedule_table(st, sym, milestones)]

    _section(el, st, '5. ESTIMATES')
    est = []
    if project.estimated_cost is not None:
        est.append(f"Estimated cost: {_money(sym, project.estimated_cost)}")
    if project.estimated_hours is not None:
        est.append(f"Estimated effort: {float(project.estimated_hours):g} hours")
    if project.contract_value is not None:
        est.append(f"Contract value: {_money(sym, project.contract_value)}")
    _p(el, ' · '.join(est) if est else 'To be determined.', st['body'])

    _section(el, st, 'ACCEPTANCE')
    _p(el, f"By signing below, {customer.company_name if customer else 'the Client'} approves the scope, "
       f"phases and estimates set out in this document.", st['body'])
    _signatures(el, st, customer.company_name if customer else 'Client', iss)

    return _build(doc, buf, el, iss, ref), ref
