## -*- coding: utf-8 -*-

from webhelpers.html.builder import HTML, literal
from routes import url_for, request_config
from pylons import request

class Grid(object):

    def default_header_column_format(self, column_number, header_label):
        class_name = 'column%s' % (column_number)
        return HTML.tag('th', header_label, class_=class_name)

    def default_header_ordered_column_format(self, column_number, order, header_label):
        class_name = 'sorted %sending' % (order)
        return HTML.tag('th', header_label, class_=class_name)

    def default_header_link(self,url,content, onclick_action=None):
        if self.onclick:
            return HTML.tag('a', href=url, c=content, onclick = onclick_action)
        else:
            return HTML.tag('a', href=url, c=content)

    def default_header(self, header_label):
        return HTML.tag('th', header_label)
    
    def __init__(self, columns, onclick=None, order_by=None):
        self.columns = columns
        self.exclude_ordering = ['_numbered']
        self.labels = {}
        self.onclick = None
        self.order_column = order_by
        self.order_type = 'asc'

    def make_headers(self):
        header_columns = []
        new_order_type = {'asc': 'desc', 'desc': 'asc'}
        request_copy = request.copy()

        # Pobranie sortowanej kolumny
        if 'ob' in request_copy.GET:
            self.order_column = request_copy.GET.pop('ob')
        else:
            self.order_column = None

        # Pobranie kierunku sortowania
        if 'ot' in request_copy.GET:
            self.order_type = request_copy.GET.pop('ot')
        
        for i, column in enumerate(self.columns):
            label_text = ''            
            if column in self.labels:
                label_text = self.labels[column]
            else:
                label_text = column

            if column not in self.exclude_ordering:
                if self.order_column and column == self.order_column:
                    new_ordering = new_order_type[self.order_type]
                else:
                    new_ordering = 'asc'

                # Pobranie dodatkowych parametrów
                link_params = {}
                for k, v in request_copy.GET.items():
                    link_params[k] = v

                # Utworzenie linka dla AJAXA
                if self.onclick: 
                    link_params['partial'] = 1
                    onclick_action = self.onclick % url_for(ob=column, ot=new_ordering, **link_params)
                
                # Wyświetlenie prawidłowego linka
                label_text = self.default_header_link(url_for(ob=column, ot=new_ordering, **link_params), label_text, onclick_action)                
                if self.order_column and column == self.order_column:
                    header_columns.append(self.default_header_ordered_column_format(i+1,self.order_type, label_text))
                else:
                    header_columns.append(self.default_header(label_text))                    
                
            else:                
                header_columns.append(self.default_header_column_format(i + 1, label_text))

        return HTML(*header_columns)
