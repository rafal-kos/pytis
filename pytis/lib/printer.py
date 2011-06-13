## -*- coding: utf-8 -*-

from pytis.lib.app_globals import Globals
from pytis.model.invoice import Invoice, InvoiceCorrect

from sqlalchemy.orm import eagerload
from pylons import request, response, session, tmpl_context as c
from decimal import Decimal

import StringIO
import xlwt
import codecs
from xml.dom.minidom import Document
from pytis.model.company import Company

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

    def _add_element(self, document, key, value, cdata = False):
        element = document.createElement(key)

        if cdata:
            text = document.createCDATASection(value)
        else:
            text = document.createTextNode(value)        

        element.appendChild(text)

        return element

    def _add_correct(self, document, invoice):
        """Export invoice correct"""
        invoiceElement = document.createElement('REJESTR_SPRZEDAZY_VAT')
        invoiceElement.appendChild(self._add_element(document, 'MODUL', 'Rejestr VAT'))
        invoiceElement.appendChild(self._add_element(document, 'REJESTR', u'SPRZEDAŻ', True))
        invoiceElement.appendChild(self._add_element(document, 'DATA_WYSTAWIENIA', str(invoice.correct_date), True))
        invoiceElement.appendChild(self._add_element(document, 'DATA_SPRZEDAZY', str(invoice.sell_date), True))
        invoiceElement.appendChild(self._add_element(document, 'TERMIN', str(invoice.payment_date), True))
        invoiceElement.appendChild(self._add_element(document, 'NUMER', invoice.number, True))
        invoiceElement.appendChild(self._add_element(document, 'KOREKTA', 'Nie'))
        invoiceElement.appendChild(self._add_element(document, 'FISKALNA', 'Nie'))
        invoiceElement.appendChild(self._add_element(document, 'DETALICZNA', 'Nie'))
        invoiceElement.appendChild(self._add_element(document, 'TYP_PODMIOTU', 'kontrahent', True))
        invoiceElement.appendChild(self._add_element(document, 'PODMIOT', invoice.company.shortName, True))
        invoiceElement.appendChild(self._add_element(document, 'NOTOWANIE_WALUTY_ILE', '1', True))
        invoiceElement.appendChild(self._add_element(document, 'NOTOWANIE_WALUTY_ZA_ILE', '1', True))
        invoiceElement.appendChild(self._add_element(document, 'KATEGORIA', u'SPRZEDAŻ', True))

        invoiceElement.appendChild(self._add_element(document, 'OPIS', invoice.number, True))
        invoiceElement.appendChild(self._add_element(document, 'FORMA_PLATNOSCI', invoice.company.payment.value, True))

        if invoice.company.tax.name == 'NPO':
            invoiceElement.appendChild(self._add_element(document, 'EKSPORT', u'Wewnątrzunijny', False))
            invoiceElement.appendChild(self._add_element(document, 'DEKLARACJA_VATUE', 'Tak', True))

        positions = document.createElement('POZYCJE')
        for position in invoice.positions:
            positionElement = document.createElement('POZYCJA')
            positionElement.appendChild(self._add_element(document, 'STAWKA_VAT', str(position.tax.value)))

            if invoice.company.tax.name == 'NPO':
                #add currency value
                positionElement.appendChild(self._add_element(document, 'NETTO', str(position.netto_value * (invoice.currency_value or 1))))
                positionElement.appendChild(self._add_element(document, 'VAT', str(position.tax_value * (invoice.currency_value or 1))))
                positionElement.appendChild(self._add_element(document, 'NETTO_SYS', str(position.netto_value * (invoice.currency_value or 1))))
                positionElement.appendChild(self._add_element(document, 'VAT_SYS', str(position.tax_value * (invoice.currency_value or 1))))
                positionElement.appendChild(self._add_element(document, 'NETTO_SYS2', str(position.netto_value * (invoice.currency_value or 1))))
                positionElement.appendChild(self._add_element(document, 'VAT_SYS2', str(position.tax_value * (invoice.currency_value or 1))))
                positionElement.appendChild(self._add_element(document, 'STATUS_VAT', 'nie podlega'))

            else:
                positionElement.appendChild(self._add_element(document, 'NETTO', str(position.netto_value)))
                positionElement.appendChild(self._add_element(document, 'VAT', str(position.tax_value)))
                positionElement.appendChild(self._add_element(document, 'NETTO_SYS', str(position.netto_value)))
                positionElement.appendChild(self._add_element(document, 'VAT_SYS', str(position.tax_value)))
                positionElement.appendChild(self._add_element(document, 'NETTO_SYS2', str(position.netto_value)))
                positionElement.appendChild(self._add_element(document, 'VAT_SYS2', str(position.tax_value)))
                positionElement.appendChild(self._add_element(document, 'STATUS_VAT', 'opodatkowana'))

            positions.appendChild(positionElement)

        if invoice.invoice.tax.name == 'NPO':
            payment = document.createElement('PLATNOSCI')
            paymentElement = document.createElement('PLATNOSC')
            paymentElement.appendChild(self._add_element(document, 'TERMIN_PLAT', str(invoice.payment_date), True))
            paymentElement.appendChild(self._add_element(document, 'FORMA_PLATNOSCI_PLAT', str(invoice.company.payment.value), True))
            paymentElement.appendChild(self._add_element(document, 'KWOTA_PLN_PLAT', str(invoice.brutto_value), True))
            paymentElement.appendChild(self._add_element(document, 'KWOTA_PLAT', str(invoice.brutto_value * invoice.currency_value), True))
            paymentElement.appendChild(self._add_element(document, 'KIERUNEK', u'przychód', True))
            paymentElement.appendChild(self._add_element(document, 'WALUTA_PLAT', invoice.currency_symbol, True))
            paymentElement.appendChild(self._add_element(document, 'NOTOWANIE_WALUTY_ILE_PLAT', str(invoice.currency_value), True))
            paymentElement.appendChild(self._add_element(document, 'DATA_KURSU', str(invoice.currency_date), True))
            payment.appendChild(paymentElement)
        else:
            payment = document.createElement('PLATNOSCI')
            paymentElement = document.createElement('PLATNOSC')
            paymentElement.appendChild(self._add_element(document, 'TERMIN_PLAT', str(invoice.payment_date), True))
            paymentElement.appendChild(self._add_element(document, 'FORMA_PLATNOSCI_PLAT', str(invoice.company.payment.value), True))
            paymentElement.appendChild(self._add_element(document, 'KWOTA_PLN_PLAT', str(invoice.brutto_value), True))
            paymentElement.appendChild(self._add_element(document, 'KWOTA_PLAT', str(invoice.brutto_value), True))
            paymentElement.appendChild(self._add_element(document, 'KIERUNEK', u'przychód', True))
            payment.appendChild(paymentElement)


        invoiceElement.appendChild(payment)
        invoiceElement.appendChild(positions)

        return invoiceElement

    def _add_invoice(self, document, invoice):
        """Export invoice"""
        invoiceElement = document.createElement('REJESTR_SPRZEDAZY_VAT')
        invoiceElement.appendChild(self._add_element(document, 'MODUL', 'Rejestr VAT'))
        invoiceElement.appendChild(self._add_element(document, 'REJESTR', u'SPRZEDAŻ', True))
        invoiceElement.appendChild(self._add_element(document, 'DATA_WYSTAWIENIA', str(invoice.issueDate), True))
        invoiceElement.appendChild(self._add_element(document, 'DATA_SPRZEDAZY', str(invoice.sellDate), True))
        invoiceElement.appendChild(self._add_element(document, 'TERMIN', str(invoice.payment_date), True))
        invoiceElement.appendChild(self._add_element(document, 'NUMER', invoice.number, True))
        invoiceElement.appendChild(self._add_element(document, 'KOREKTA', 'Nie'))
        invoiceElement.appendChild(self._add_element(document, 'FISKALNA', 'Nie'))
        invoiceElement.appendChild(self._add_element(document, 'DETALICZNA', 'Nie'))
        invoiceElement.appendChild(self._add_element(document, 'TYP_PODMIOTU', 'kontrahent', True))
        invoiceElement.appendChild(self._add_element(document, 'PODMIOT', invoice.company.shortName, True))

        if invoice.tax.name == 'NPO':
            if invoice.elements[0].currency.value == 'EUR':
                invoiceElement.appendChild(self._add_element(document, 'WALUTA', invoice.elements[0].currency.value, True))
                invoiceElement.appendChild(self._add_element(document, 'NOTOWANIE_WALUTY_ILE', str(invoice.currencyValue or 1), True))
                invoiceElement.appendChild(self._add_element(document, 'NOTOWANIE_WALUTY_ZA_ILE', u'1', True))
                invoiceElement.appendChild(self._add_element(document, 'KURS_WALUTY', u'NBP', True))
                invoiceElement.appendChild(self._add_element(document, 'DATA_KURSU', str(invoice.currencyDate or ''), True))
            invoiceElement.appendChild(self._add_element(document, 'KATEGORIA', u'EKSPORT USŁUG PRZEWO', True))
        else:
            invoiceElement.appendChild(self._add_element(document, 'NOTOWANIE_WALUTY_ILE', '1', True))
            invoiceElement.appendChild(self._add_element(document, 'NOTOWANIE_WALUTY_ZA_ILE', '1', True))
            invoiceElement.appendChild(self._add_element(document, 'KATEGORIA', u'SPRZEDAŻ USŁUG KRAJ', True))

        invoiceElement.appendChild(self._add_element(document, 'FORMA_PLATNOSCI', invoice.company.payment.value, True))
        
        if invoice.tax.name == 'NPO':
            invoiceElement.appendChild(self._add_element(document, 'EKSPORT', u'Wewnątrzunijny', False))
            invoiceElement.appendChild(self._add_element(document, 'DEKLARACJA_VATUE', 'Tak', True))

        positions = document.createElement('POZYCJE')
        for position in invoice.elements:
            positionElement = document.createElement('POZYCJA')
            positionElement.appendChild(self._add_element(document, 'STAWKA_VAT', str(position.tax.value)))

            if invoice.tax.name == 'NPO':
                positionElement.appendChild(self._add_element(document, 'NETTO', str(position.netto_value)))
                positionElement.appendChild(self._add_element(document, 'VAT', str(position.tax_value)))
                positionElement.appendChild(self._add_element(document, 'NETTO_SYS', str(position.netto_value)))
                positionElement.appendChild(self._add_element(document, 'VAT_SYS', str(position.tax_value)))
                #positionElement.appendChild(self._add_element(document, 'NETTO_SYS2', str(position.netto_value)))
                positionElement.appendChild(self._add_element(document, 'NETTO_SYS2', str(position.netto_value * Decimal(repr((invoice.currencyValue or 1))))))
                #positionElement.appendChild(self._add_element(document, 'VAT_SYS2', str(position.tax_value)))
                positionElement.appendChild(self._add_element(document, 'VAT_SYS2', str(position.tax_value * Decimal(repr((invoice.currencyValue or 1))))))
            else:
                positionElement.appendChild(self._add_element(document, 'NETTO', str(position.netto_value)))
                positionElement.appendChild(self._add_element(document, 'VAT', str(position.tax_value)))
                positionElement.appendChild(self._add_element(document, 'NETTO_SYS', str(position.netto_value)))
                positionElement.appendChild(self._add_element(document, 'VAT_SYS', str(position.tax_value)))
                #positionElement.appendChild(self._add_element(document, 'NETTO_SYS2', str(position.netto_value)))
                positionElement.appendChild(self._add_element(document, 'NETTO_SYS2', str(position.netto_value)))
                positionElement.appendChild(self._add_element(document, 'VAT_SYS2', str(position.tax_value)))

            if invoice.company.tax.name == 'NPO':
                positionElement.appendChild(self._add_element(document, 'STATUS_VAT', 'nie podlega'))
                positionElement.appendChild(self._add_element(document, 'KATEGORIA_POS', u'EKSPORT USŁUG PRZEWO', True))
            else:
                positionElement.appendChild(self._add_element(document, 'STATUS_VAT', 'opodatkowana'))
                positionElement.appendChild(self._add_element(document, 'KATEGORIA_POS', u'SPRZEDAŻ USŁUG KRAJ', True))
            
            positions.appendChild(positionElement)

        if invoice.tax.name == 'NPO':
            payment = document.createElement('PLATNOSCI')
            paymentElement = document.createElement('PLATNOSC')
            paymentElement.appendChild(self._add_element(document, 'TERMIN_PLAT', str(invoice.payment_date), True))
            paymentElement.appendChild(self._add_element(document, 'FORMA_PLATNOSCI_PLAT', str(invoice.company.payment.value), True))
            paymentElement.appendChild(self._add_element(document, 'KWOTA_PLN_PLAT', str(invoice.brutto_value * Decimal(repr(invoice.currencyValue or 1))), True))
            paymentElement.appendChild(self._add_element(document, 'KWOTA_PLAT', str(invoice.brutto_value), True))
            paymentElement.appendChild(self._add_element(document, 'KIERUNEK', u'przychód', True))
            paymentElement.appendChild(self._add_element(document, 'WALUTA_PLAT', invoice.currencySymbol or '', True))
            paymentElement.appendChild(self._add_element(document, 'NOTOWANIE_WALUTY_ILE_PLAT', str(invoice.currencyValue), True))
            paymentElement.appendChild(self._add_element(document, 'DATA_KURSU', str(invoice.currencyDate), True))
            payment.appendChild(paymentElement)
        else:
            payment = document.createElement('PLATNOSCI')
            paymentElement = document.createElement('PLATNOSC')
            paymentElement.appendChild(self._add_element(document, 'TERMIN_PLAT', str(invoice.payment_date), True))
            paymentElement.appendChild(self._add_element(document, 'FORMA_PLATNOSCI_PLAT', str(invoice.company.payment.value), True))
            paymentElement.appendChild(self._add_element(document, 'KWOTA_PLN_PLAT', str(invoice.brutto_value), True))
            paymentElement.appendChild(self._add_element(document, 'KWOTA_PLAT', str(invoice.brutto_value), True))
            paymentElement.appendChild(self._add_element(document, 'KIERUNEK', u'przychód', True))
            payment.appendChild(paymentElement)

        invoiceElement.appendChild(payment)
        invoiceElement.appendChild(positions)

        return invoiceElement

    def _add_company(self, document, company):
        element = document.createElement('KONTRAHENT')

        element.appendChild(self._add_element(document, 'AKRONIM', company.shortName, True))
        element.appendChild(self._add_element(document, 'RODZAJ', 'odbiorca dostawca', True))
        element.appendChild(self._add_element(document, 'PLATNIK_VAT', 'Tak', True))
        element.appendChild(self._add_element(document, 'ODBIORCA', company.shortName, True))
        element.appendChild(self._add_element(document, 'INDYWIDUALNY_TERMIN', 'Tak'))
        element.appendChild(self._add_element(document, 'TERMIN', company.paymentForm.value.split()[0], True))
        element.appendChild(self._add_element(document, 'MAX_ZWLOKA', '5', True))
        element.appendChild(self._add_element(document, 'FORMA_PLATNOSCI', company.payment.value, True))        

        addressElement = document.createElement('ADRESY')
        addElement = document.createElement('ADRES')
        addElement.appendChild(self._add_element(document, 'STATUS', 'aktualny'))
        addElement.appendChild(self._add_element(document, 'NAZWA1', company.name, True))
        addElement.appendChild(self._add_element(document, 'ULICA', company.address, True))
        addElement.appendChild(self._add_element(document, 'NR_DOMU', '', True))
        addElement.appendChild(self._add_element(document, 'MIASTO', company.city, True))
        addElement.appendChild(self._add_element(document, 'KOD_POCZTOWY', company.zip, True))
        addElement.appendChild(self._add_element(document, 'REGON', company.regon, True))
        addElement.appendChild(self._add_element(document, 'NIP', company.nip, True))
        addElement.appendChild(self._add_element(document, 'NIP_KRAJ', company.nip_code, True))
        addressElement.appendChild(addElement)
        
        element.appendChild(addressElement)

        return element

    def export_companies(self):
        """Export companies to OPTIMA"""
        doc = Document()
        companies = Company.query.all()
        buffer = StringIO.StringIO()

        root = doc.createElement('ROOT')
        root.setAttribute('xmlns', 'http://www.cdn.com.pl/optima/offline')
        doc.appendChild(root)

        companiesElement = doc.createElement('KONTRAHENCI')
        companiesElement.appendChild(self._add_element(doc, 'WERSJA', '2.00'))
        companiesElement.appendChild(self._add_element(doc, 'BAZA_ZRD_ID', 'SPRZ'))
        companiesElement.appendChild(self._add_element(doc, 'BAZA_DOC_ID', 'SPRZ'))

        for company in companies:
            companiesElement.appendChild(self._add_company(doc, company))

        root.appendChild(companiesElement)

        buffer.write(doc.toprettyxml(indent='', newl=''))        
        return buffer

    def export_to_cdn(self, date_from, date_to):
        """Export invoices to OPTIMA"""
        doc = Document()
        from pytis.model import meta
        buffer = StringIO.StringIO()
        
        invoices = Invoice.query.options(eagerload('elements')).filter(Invoice.issueDate.between(date_from , date_to)).order_by(Invoice.series_number).all()
        corrects = InvoiceCorrect.query.options(eagerload('positions')).filter(InvoiceCorrect.correct_date.between(date_from, date_to)).order_by(InvoiceCorrect.series_number).all()

        root = doc.createElement('ROOT')
        root.setAttribute('xmlns', 'http://www.cdn.com.pl/optima/offline')
        doc.appendChild(root)

        companiesElement = doc.createElement('KONTRAHENCI')
        companiesElement.appendChild(self._add_element(doc, 'WERSJA', '2.00'))
        companiesElement.appendChild(self._add_element(doc, 'BAZA_ZRD_ID', 'SPRZ'))
        companiesElement.appendChild(self._add_element(doc, 'BAZA_DOC_ID', 'SPRZ'))
        root.appendChild(companiesElement)

        companies = []
        for invoice in invoices:
            """fetch sets of companies"""
            if invoice.company not in companies:
                companies.append(invoice.company)

        for correct in corrects:
            """fetch sets of companies"""
            if correct.company not in companies:
                companies.append(correct.company)

        for company in companies:            
            companiesElement.appendChild(self._add_company(doc, company))
        root.appendChild(companiesElement)

        invoicesElement = doc.createElement('REJESTRY_SPRZEDAZY_VAT')
        invoicesElement.appendChild(self._add_element(doc, 'WERSJA', '2.00'))
        invoicesElement.appendChild(self._add_element(doc, 'BAZA_ZRD_ID', 'SPRZ'))
        invoicesElement.appendChild(self._add_element(doc, 'BAZA_DOC_ID', 'SPRZ'))
        for invoice in invoices:
            invoicesElement.appendChild(self._add_invoice(doc, invoice))

            if not invoice.is_exported:
                invoice.mark_as_exported()
        meta.Session.commit()
        
        for correct in corrects:
            invoicesElement.appendChild(self._add_correct(doc, correct))

        root.appendChild(invoicesElement)

        buffer.write(doc.toprettyxml(indent='', newl=''))        
        return buffer
