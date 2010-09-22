## -*- coding: utf-8 -*-

from pytis.lib.app_globals import Globals
from pytis.model.invoice import Invoice, InvoiceCorrect

from sqlalchemy.orm import eagerload
from pylons import request, response, session, tmpl_context as c
from decimal import Decimal

import StringIO
import xlwt

'''
Klasa odpowiedzialna za wydruk dokumentów
'''
class Printer(object):   
    def sell_registry(self):
        date_from = request.params.get('from')
        date_to = request.params.get('to')
                
        buffer = StringIO.StringIO()               

        columns = ['Numer', 
                   'NIP', 
                   'Kontrahent', 
                   'Data wyst.', 
                   'Data sprzed.', 
                   'Razem brutto', 
                   'Netto bez ZW, BO, np.', 
                   'Razem VAT',
                   'Stawka 22% netto',
                   'Stawka 22% VAT',
                   'NPO']
        invoices = Invoice.query.options(eagerload('elements')).filter(Invoice.issueDate.between(date_from , date_to)).order_by(Invoice.series_number).all()
        corrects = InvoiceCorrect.query.options(eagerload('positions')).filter(InvoiceCorrect.correct_date.between(date_from, date_to)).order_by(InvoiceCorrect.series_number).all()

        wb = xlwt.Workbook()
        ws = wb.add_sheet('Rejestr')        
        
        font0 = xlwt.Font()
        font0.name = 'Times New Roman'
        font0.colour_index = 0
        font0.bold = True
        
        font1 = xlwt.Font()
        font1.name = 'Times New Roman'
        font1.colour_index = 0
        font1.bold = False 
        
        style0 = xlwt.XFStyle()
        style0.font = font0
        
        style1 = xlwt.XFStyle()        
        style1.font = font1        
        
        for i, column in enumerate(columns):
            ws.write(0, i, column, style0)
        
        for i, invoice in enumerate(invoices):
            ws.write(i + 1, 0, invoice.number, style1)
            ws.write(i + 1, 1, invoice.company.nip, style1)
            ws.write(i + 1, 2, invoice.company.name, style1)
            ws.write(i + 1, 3, str(invoice.issueDate), style1)
            ws.write(i + 1, 4, str(invoice.sellDate), style1)
                                  
            # Kontrahent 22%
            if invoice.tax.name != 'NPO':
                ws.write(i + 1, 5, invoice.brutto_value, style1)
                ws.write(i + 1, 6, invoice.netto_value, style1)
                ws.write(i + 1, 7, invoice.tax_value, style1)
                ws.write(i + 1, 8, invoice.netto_value, style1)
                ws.write(i + 1, 9, invoice.tax_value, style1)
                ws.write(i + 1, 10, '-', style1)
            else:
                ws.write(i + 1, 5, invoice.netto_value * Decimal(repr(invoice.currencyValue or 1)), style1)
                ws.write(i + 1, 6, invoice.netto_value * Decimal(repr(invoice.currencyValue or 1)), style1)
                ws.write(i + 1, 7, 0, style1)
                ws.write(i + 1, 8, '-', style1)
                ws.write(i + 1, 9, '-', style1)
                ws.write(i + 1, 10, invoice.netto_value * Decimal(repr(invoice.currencyValue or 1)), style1)          
                
        rows_count = len(ws.rows)

        for i, invoice in enumerate(corrects):
            ws.write(i + rows_count, 0, invoice.number, style1)
            ws.write(i + rows_count, 1, invoice.company.nip, style1)
            ws.write(i + rows_count, 2, invoice.company.name, style1)
            ws.write(i + rows_count, 3, str(invoice.correct_date), style1)
            ws.write(i + rows_count, 4, str(invoice.sell_date), style1)
                                  
            # Kontrahent 22%
            if invoice.positions[0].tax.name != 'NPO':
                ws.write(i + rows_count, 5, invoice.diff_brutto_value, style1)
                ws.write(i + rows_count, 6, invoice.diff_netto_value, style1)
                ws.write(i + rows_count, 7, invoice.diff_tax_value, style1)
                ws.write(i + rows_count, 8, invoice.diff_netto_value, style1)
                ws.write(i + rows_count, 9, invoice.diff_tax_value, style1)
                ws.write(i + rows_count, 10, '-', style1)
            else:
                ws.write(i + rows_count, 5, invoice.diff_netto_value * (invoice.currency_value or 1), style1)
                ws.write(i + rows_count, 6, invoice.diff_netto_value * (invoice.currency_value or 1), style1)
                ws.write(i + rows_count, 7, 0, style1)
                ws.write(i + rows_count, 8, '-', style1)
                ws.write(i + rows_count, 9, '-', style1)
                ws.write(i + rows_count, 10, invoice.diff_netto_value * (invoice.currency_value or 1), style1)        
                
        wb.save(buffer)
        return buffer