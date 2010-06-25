from wtforms import Form
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import ValidationError
from wtforms import widgets
from wtforms.widgets import html_params
from cgi import escape
from pylons import url
from wtforms.fields import Field
from operator import attrgetter

class PytisForm(Form):
    def populate_obj(self, obj, exclude=None):
        """
        Populates the attributes of the passed `obj` with data from the form's
        fields.
        
        **Note:** This is a destructive operation, any attribute with the same
        name as a field will be overridden. Use with caution.
        """
        if exclude is None:
            exclude = []           
        
        for name, field in self._fields.iteritems():            
            if field.name not in exclude:
                field.populate_obj(obj, name)                           

class PytisQuerySelectField(Field):
  
    widget = widgets.Select()

    def __init__(self, label=u'', validators=None, query_factory=None, pk_attr='id', 
                 label_attr='', allow_blank=False, coerce=int, blank_text=u'', **kwargs):
        super(PytisQuerySelectField, self).__init__(label, validators, **kwargs)
        self.query_factory = query_factory
        self.pk_attr = pk_attr
        self.label_attr = label_attr
        self.allow_blank = allow_blank
        self.blank_text = blank_text
        self.query = None
        self.coerce = coerce
        self._object_list = None

    def _get_data(self):
        if self._formdata is not None:
            for pk, obj in self._get_object_list():
                if pk == self._formdata:
                    self._set_data(obj)
                    break
        return self._data

    def _set_data(self, data):
        self._data = data
        self._formdata = None

    data = property(_get_data, _set_data)

    def _get_object_list(self):
        if self._object_list is None:
            query = self.query or self.query_factory()
            get_pk = attrgetter(self.pk_attr)
            self._object_list = list((get_pk(obj), obj) for obj in query)
        return self._object_list

    def iter_choices(self):
        if self.allow_blank:
            yield (u'__None', self.blank_text, self.data is None)

        for pk, obj in self._get_object_list():
            label = self.label_attr and getattr(obj, self.label_attr) or obj
            yield (pk, label, obj == self.data)

    def process_formdata(self, valuelist):
        if valuelist:
            if self.allow_blank and valuelist[0] == '__None':
                self.data = None
            else:
                self._data = None
                self._formdata = self.coerce(valuelist[0])

    def pre_validate(self, form):
        if not self.allow_blank or self.data is not None:
            for pk, obj in self._get_object_list():
                if self.data == obj:
                    break
            else:
                raise ValidationError('Not a valid choice')

class CountrySelect(widgets.Select):
    '''
    Select countries with flags
    '''
    def __init__(self, **kwargs):
        super(CountrySelect, self).__init__()
        
    def __call__(self, field, title='', **kwargs):
        kwargs.setdefault('id', field.id)
        if self.multiple:
            kwargs['multiple'] = 'multiple'
        html = [u'<select %s>' % html_params(name=field.name, **kwargs)]
        for val, label, selected in field.iter_choices():
            options = {'value': val}
            if selected:
                options['selected'] = u'selected'            
            if val is not None or val != '_None':
                options['title'] = url('/images/flags/%s.png' % str(val))
            html.append(u'<option %s>%s</option>' % (html_params(**options), escape(unicode(label))))
        html.append(u'</select>')
        return u''.join(html)        


def is_selected(message=u'Nie wybrano pola!', default_value = '-1'):
    
    def _is_selected(form, field):
        '''
        Sprawdzam czy wybrano pole z listy wybieralnej
        @param form:
        @param field:
        '''
        if not field.data or field.data == default_value:
            raise ValidationError(message)
    return _is_selected
