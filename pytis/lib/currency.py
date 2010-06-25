## -*- coding: utf-8 -*-

from xml.dom import minidom
import urllib
import re
import datetime

import logging
log = logging.getLogger(__name__)

one_day = datetime.timedelta(days = 1)

def getCurrencyValue(dateString, symbol):
    """
    Funkcja zwraca słownik z informacja o symbolu waluty, wartości, dacie kursu oraz numerze tabeli
    Jesli dla danego dnia nie ma kursu bierzemy dzień wcześniej. Funkcja rekurencyjna
    """
    result = {}
    currencyValue = None #wartośc waluty
    
    #Konwersja stringa na datetime    
    date = datetime.datetime.strptime(dateString, "%Y-%m-%d")    
    
    if date.weekday() == 0 and date.weekday() == 7:
        date = date - one_day
        result = getCurrencyValue(date.strftime('%Y-%m-%d'), symbol)
    
    year = date.strftime('%y')
    month = date.strftime('%m')
    formatDate = date.strftime('%y%m%d')
    
    page = urllib.urlopen('http://nbp.pl/transfer.aspx?c=/ascx/listaabch.ascx&Typ=a&p=rok;mies&navid=archa',
                            data=urllib.urlencode({'mies': month, 'rok': year})).read()            

    pattern = re.compile(r'[a-z0-9]{5}' + formatDate, re.DOTALL)
    tt = re.findall(pattern, page)    
    if tt:        
        page = 'http://www.nbp.pl/kursy/xml/' + tt[0] + '.xml'
        document = urllib.urlopen(page) 
        xmldoc = minidom.parse(document)         
        currencies = xmldoc.childNodes
        for i in currencies[0].getElementsByTagName("pozycja"):
            currencySymbol = i.getElementsByTagName("kod_waluty")[0].childNodes[0].toxml()
            currencyValue = i.getElementsByTagName("kurs_sredni")[0].childNodes[0].toxml()
            if currencySymbol == symbol:
                #Zastąpienie znaku przecinka kropką
                currencyValue = currencyValue.replace(',', '.')
                
                result['tableNumber'] = xmldoc.getElementsByTagName("numer_tabeli")[0].childNodes[0].toxml()
                result['date'] = dateString
                result['value'] = currencyValue
                result['symbol'] = symbol

                return result
    else:
        date = date - one_day
        result = getCurrencyValue(date.strftime('%Y-%m-%d'), symbol)

    return result