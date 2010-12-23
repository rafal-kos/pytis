## -*- coding: utf-8 -*-

'''
ALTER TABLE `dictionary` CHANGE `key` `key` VARCHAR( 20 ) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL 
'''

from pytis.lib.validators import PytisForm, is_selected, CountrySelect, PytisQuerySelectField
from pytis.model.dictionary import Dictionary, Tax, Country
from pytis.model.document import Document
from pytis.model.driver import Driver, Truck, Semitrailer
from pytis.model.user import User, Group, UserDoesntExistsException
from wtforms import validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField, \
    QuerySelectMultipleField
from wtforms.fields import HiddenField, TextField, SelectField, PasswordField, \
    DecimalField, FormField, FieldList, TextAreaField, BooleanField, DateField, \
    IntegerField, DateTimeField
from wtforms.validators import ValidationError
import pytis.lib.helpers as h

def get_groups():
    return Group.query

def get_payment():
    return Dictionary.query.filter(Dictionary.key == u'PAYMENT').order_by(Dictionary.value)

def get_payment_form():
    return Dictionary.query.filter(Dictionary.key == u'PAYFORM').order_by(Dictionary.value)

def get_tax_type():
    return [('0', '22%'), ('1', 'NPO'), ('2', '0%')]

def get_taxes():
    return Tax.query

def get_currencies():
    return Dictionary.query.filter(Dictionary.key == 'WAL').order_by(Dictionary.id)

def get_drivers():
    return Driver.query.filter(Driver.is_active == True)

def get_trucks():
    return Truck.query.filter(Truck.is_active == True)

def get_semitrailers():
    return Semitrailer.query.filter(Semitrailer.is_active == True)

def get_euro_norms():
    return Dictionary.query.filter(Dictionary.key == 'EURO_NORM').order_by(Dictionary.value)

def get_truck_models():
    return Dictionary.query.filter(Dictionary.key == 'TRUCK_MODEL').order_by(Dictionary.value)

def get_countries():
    return Country.query.order_by(Country.name)

def get_causes():
    return Dictionary.query.filter(Dictionary.key == 'HOLIDAY_CAUSE').order_by(Dictionary.value)

#------------------COMPANIES-----------------------
class CompanyForm(PytisForm):    
    name = TextField('Nazwa', [validators.required(message=u'Pole jest wymagane')])
    shortName = TextField('Akronim', [validators.required(message=u'Pole jest wymagane')])
    regon = TextField('REGON', [validators.required(message=u'Pole jest wymagane')])
    nip = TextField('NIP', [validators.required(message=u'Pole jest wymagane')])
    nip_code = SelectField('NIP Kraj', choices=[
        ('PL', 'PL'),
        ('DE', 'DE'),
        ('EN', 'EN'),
        ('FR', 'FR'),
        ('CZ', 'CZ'),
        ('EE', 'EE'),
        ('SK', 'SK'),
        ('NL', 'NL'),
        ('BE', 'BE'),
        ('LV', 'LV'),
        ('AT', 'AT'),
        ('EL', 'EL'),
        ('HU', 'HU'),
        ('ES', 'ES')
    ])
    address = TextField('Adres', [validators.required(message=u'Pole jest wymagane')])
    zip = TextField('Kod', [validators.required(message=u'Pole jest wymagane')])
    city = TextField('Miasto', [validators.required(message=u'Pole jest wymagane')])
    contact_phone = TextField(u'Tel. kontaktowy', [validators.required(message=u'Pole jest wymagange')])
    description = TextAreaField('Opis', [validators.length(max=255)])
    paymentForm = QuerySelectField(u'Forma płatności', query_factory=get_payment_form, allow_blank=False)
    payment = QuerySelectField(u'Termin płatności', query_factory=get_payment, allow_blank=False)    
    tax = QuerySelectField(u'Stawka VAT', query_factory=get_taxes, label_attr='name')

    def validate_nip(form, field):
        if '-' in form.nip.data or '.' in form.ni.data:
            raise ValidationError(u'NIP może zawierać tylko cyfry lub litery')

class PlaceForm(PytisForm):
    id = HiddenField()
    idCompany = HiddenField()
    name = TextField('Nazwa', [validators.required(message=u'Pole jest wymagane')])
    zip = TextField('Kod')
    street = TextField('Ulica')
    city = TextField(u'Miejscowość', [validators.required(message=u'Pole jest wymagane')])
    country = PytisQuerySelectField(u'Kraj', [validators.required(message=u'Pole jest wymagane')], 
                               query_factory=get_countries, allow_blank=True, 
                               blank_text="Wybierz...", pk_attr='code', coerce=unicode,
                               label_attr='name', widget=CountrySelect())

#------------------USERS-------------------
class UserForm(PytisForm):
    id = HiddenField()
    login = TextField(u'Login', [validators.required(message=u'Pole jest wymagane.')])
    email = TextField(u'Email', [validators.email(message=u'Nieprawidłowy email'), validators.required(message=u'Pole jest wymagane')])
    first_name = TextField(u'Imię', [validators.required(message=u'Pole jest wymagane')])
    last_name = TextField(u'Nazwisko', [validators.required(message=u'Pole jest wymagane')])
    phone = TextField('Telefon')    

class UserRegisterForm(UserForm):
    password = PasswordField(u'Hasło', [validators.required(message=u'Pole jest wymagane')])
    password_confirm = PasswordField(u'Hasło', [validators.required(message=u'Pole jest wymagane')])
    
    def validate_password(form, field):
        if form.password.data != form.password_confirm.data:
            raise ValidationError(u'Hasła muszą się zgadzać')

class UserEditForm(UserForm):
    groups = QuerySelectMultipleField(query_factory=get_groups, pk_attr='id', label_attr='name')

class ChangePasswordForm(PytisForm):
    old_password = PasswordField(u'Stare hasło', [validators.required(message=u'Pole jest wymagane')])
    password = PasswordField(u'Hasło', [validators.required(message=u'Pole jest wymagane')])
    password_confirm = PasswordField(u'Hasło', [validators.required(message=u'Pole jest wymagane')])
    
    def validate_old_password(form, field):
        user = User()
        user.id = h.auth.user_id()
        user.password = form.old_password.data
        
        try:
            user.exists()            
        except UserDoesntExistsException:
            raise ValidationError(u'Podano nieprawidłowe hasło')
        
#------------------CORRECTS-------------------
class InvoiceCorrectPositionForm(PytisForm):    
    position_id = HiddenField([validators.required(message=u'Pole jest wymagane.')])    
    number = TextField('Numer')    
    netto_value = TextField('Fracht', [validators.required(message=u'Pole jest wymagane.')])
    brutto_value = DecimalField(u'Wartośc brutto')
    tax_value = DecimalField('VAT')    
    tax = QuerySelectField('Podatek', query_factory=get_taxes, label_attr='name')

class InvoiceCorrectForm(PytisForm):
    id = HiddenField()
    number = TextField('Numer')
    company = TextField('Kontrahent')    
    correct_date = TextField(u'Data korekty', [validators.required(message=u'Pole jest wymagane.')])
    sell_date = TextField(u'Data sprzedaży', [validators.required(message=u'Pole jest wymagane.')])    
    positions = FieldList(FormField(InvoiceCorrectPositionForm))
    payment_form = QuerySelectField(u'Forma płatności', query_factory=get_payment, allow_blank=False)
    payment_date = TextField(u'Data płatności', [validators.required(message=u'Pole jest wymagane.')])
    description = TextAreaField(u'Opis', [validators.length(max=320, message=u'Maksymalna długość wynosi 320 znaków.')])
    
#------------------DICTIONARIES-------------------    
class DictionaryForm(PytisForm):
    id = HiddenField()
    kind = SelectField('Kategoria', coerce=int, choices=Dictionary.get_categories_list().items())
    key = TextField('Klucz', [validators.required(message=u'Pole jest wymagane.')])
    value = TextField(u'Wartość', [validators.required(message=u'Pole jest wymagane.')])
    enabled = BooleanField('Aktywny')
    
#------------------GROUPS-------------------    
class GroupForm(PytisForm):
    id = HiddenField()
    name = TextField('Kategoria', [validators.required(message=u'Pole jest wymagane.')])
    
#------------------INVOICES-------------------
class InvoiceForm(PytisForm):
    id = HiddenField()
    number = TextField('Numer')
    company = TextField('Kontrahent')
    issueDate = TextField(u'Data wystawienia', [validators.required(message=u'Pole jest wymagane.')])
    sellDate = TextField(u'Data sprzedaży', [validators.required(message=u'Pole jest wymagane.')])
    isBooked = BooleanField('Zafakturowana')
    tax = QuerySelectField(u'Stawka VAT', query_factory=get_taxes, label_attr='name')
    payment_date = TextField(u'Data płatności')
    
class NewInvoiceForm(PytisForm):
    year = TextField(u'Rok', [validators.required(message=u'Pole jest wymagane.')], default=str(h.today(0).year))
    months = SelectField(u'Miesiąc', coerce=int, choices=h.months_list(), default=str(h.today().month))

#------------------ORDERS-----------------------
class OrderPlaceForm(PytisForm):          
    idType = SelectField('Typ', [is_selected(), validators.required()], choices=[('-1', 'Wybierz...'), ('1', u'Załadunek'), ('2', u'Rozładunek')])
    idPlace = HiddenField()
    place = TextField('Miejsce', [validators.required(message=u'Pole jest wymagane.')])
    placeDate = TextField('Data', [validators.required(message=u'Pole jest wymagane.')])

class TransportOrderForm(PytisForm):
    id = HiddenField()    
    idCompany = HiddenField([validators.required(message=u'Pole jest wymagane')])
    company = TextField('Kontrahent', [validators.required(message=u'Pole jest wymagane')])
    number = TextField('Numer')
    freight = TextField('Fracht', [validators.required(message=u'Pole jest wymagane')])    
    currency = QuerySelectField(query_factory=get_currencies, allow_blank=False)
    driverName = TextField('Kierowca')
    tractorName = TextField(u'Ciągnik')
    description = TextField('Uwagi')
    currencyValue = TextField('Kurs')
    currencyDate = TextField('Z dnia')
    currencySymbol = TextField('Symbol waluty')
    currencyTableNumber = TextField('Tabela')
    

class OrderForm(PytisForm):
    id = HiddenField([validators.required()])
    number = TextField('Numer')
    idCompany = HiddenField()
    company = TextField('Kontrahent', [validators.required(message=u'Pole jest wymagane.')])
    freight = TextField('Fracht', [validators.required(message=u'Pole jest wymagane.')])        
    currency = QuerySelectField(query_factory=get_currencies, allow_blank=False)
    isCurrencyDate = SelectField(u'Kurs z daty załadunku?', choices=[('0', 'NIE'), ('1', 'TAK')])
    invoice = TextField('Faktura')
    description = TextAreaField(u'Dodatkowe uwagi', [validators.length(max=320, message=u'Maksymalna długość wynosi 320.')])
    foreignOrder = TextAreaField('Opis')
    currencyValue = TextField('Kurs')
    currencyDate = TextField('Z dnia')
    currencyTableNumber = TextField('Nr tabeli')    
    
#------------------SETTINGS-----------------------
class SettingsForm(PytisForm):             
    company_name = TextField(u'Nazwa firmy', 
                             [validators.required(message=u'Pole jest wymagane.')])
    company_city = TextField(u'Miasto', 
                             [validators.required(message=u'Pole jest wymagane.')])
    company_zip = TextField(u'Kod', 
                            [validators.required(message=u'Pole jest wymagane.')])
    company_street = TextField(u'Ulica', 
                               [validators.required(message=u'Pole jest wymagane.')])
    company_nip = TextField(u'NIP', 
                            [validators.required(message=u'Pole jest wymagane.')])
    company_regon = TextField(u'REGON', 
                              [validators.required(message=u'Pole jest wymagane.')])
    company_telfax = TextField(u'Tel./Fax', 
                               [validators.required(message=u'Pole jest wymagane.')])
    company_krs = TextField(u'KRS', 
                            [validators.required(message=u'Pole jest wymagane.')])
    company_bank_account_1 = TextField(u'Numer konta', 
                                       [validators.required(message=u'Pole jest wymagane.')])
    company_bank_account_2 = TextField(u'Numer konta 2')
    
#------------------DOCUMENTS-----------------------
class DocumentForm(PytisForm):
    name = TextField(u'Nazwa', [validators.required(message=u'Pole jest wymagane')])
    pattern = TextField(u'Wzorzec', [validators.required(message=u'Pole jest wymagane')])
    
    def validate_pattern(form, field):
        if not Document.is_pattern_valid(field.data):
            raise ValidationError(u'Podano nieprawidłowy wzorzec')
        
#------------------DRIVERS-----------------------
class DriverForm(PytisForm):
    first_name = TextField(u'Imię', [validators.required(message=u'Pole jest wymagane')])
    second_name = TextField(u'Drugie imię')
    last_name = TextField(u'Nazwisko', [validators.required(message=u'Pole jest wymagane')])
    identity_card_number = TextField(u'Numer dowodu osobistego', [validators.required(message=u'Pole jest wymagane')])
    phone = TextField(u'Telefon kontaktowy', [validators.required(message=u'Pole jest wymagane')])
    medical_tests_date = DateField(u'Termin ważności badań lekarskich')
    psychology_tests_date = DateField(u'Termin ważności badań psychologicznych')
    employment_date = DateField(u'Data zatrudnienia', [validators.required(message=u'Pole jest wymagane')])
    birthday_date = DateField(u'Data urodzenia', [validators.required(message=u'Pole jest wymagane')])
    is_active = BooleanField(u'Zatrudniony')
           
    
class TruckForm(PytisForm):
    registration = TextField(u'Rejestracja', [validators.required(message=u'Pole jest wymagane')])
    is_active = BooleanField(u'Aktywny')
    vignette_validity_date = DateField(u'Termin winiety', [validators.required(message=u'Pole jest wymagane')])
    oc_validity_date = DateField(u'Termin OC', [validators.required(message=u'Pole jest wymagane')])
    ac_validity_date = DateField(u'Termin AC', [validators.required(message=u'Pole jest wymagane')])
    technical_review_validity_date = DateField(u'Termin przeglądu technicznego', [validators.required(message=u'Pole jest wymagane')])
    vin_number = TextField(u'Numer VIN', [validators.required(message=u'Pole jest wymagane')])
    year_of_production = TextField(u'Rocznik', [validators.required(message=u'Pole jest wymagane')])
    euro_norm = QuerySelectField(u'Norma EURO', query_factory=get_euro_norms, allow_blank=True, blank_text="Wybierz...")
    model = QuerySelectField(u'Marka', query_factory=get_truck_models, allow_blank=True, blank_text="Wybierz...")    

class SemitrailerForm(PytisForm):
    registration = TextField(u'Rejestracja', [validators.required(message=u'Pole jest wymagane')])
    is_active = BooleanField(u'Aktywny')    
    oc_validity_date = DateField(u'Termin OC', [validators.required(message=u'Pole jest wymagane')])
    ac_validity_date = DateField(u'Termin AC', [validators.required(message=u'Pole jest wymagane')])
    technical_review_validity_date = DateField(u'Termin przeglądu technicznego', [validators.required(message=u'Pole jest wymagane')])
    vin_number = TextField(u'Numer VIN', [validators.required(message=u'Pole jest wymagane')])
    year_of_production = TextField(u'Rocznik', [validators.required(message=u'Pole jest wymagane')])        

class HolidayDocumentForm(PytisForm):
    issue_date = DateField(u'Data wystawienia', [validators.required(message=u'Pole jest wymagane')])
    from_date = DateField(u'Data od', [validators.required(message=u'Pole jest wymagane')])
    from_time = TextField(u'Czas od', [validators.required(message=u'Pole jest wymagane')])
    to_date = DateField(u'Data do', [validators.required(message=u'Pole jest wymagane')])
    to_time = TextField(u'Czas do', [validators.required(message=u'Pole jest wymagane')])
    driver = QuerySelectField(u'Kierowca', [validators.required(message=u'Pole jest wymagane')],
                              query_factory=get_drivers, allow_blank=True, blank_text="Wybierz...")       
    
    def validate_issue_date(form, field):
        if form.to_date.data and form.issue_date.data != form.to_date.data:
            raise ValidationError(u'Data wystawienia musi być równa dacie "Do"')

#------------------DELEGATIONS-----------------------
class DelegationForm(PytisForm):    
    driver = QuerySelectField(u'Kierowca', [validators.required(message=u'Pole jest wymagane')], query_factory=get_drivers, allow_blank=True, blank_text="Wybierz...")    
    truck = QuerySelectField(u'Ciągnik', [validators.required(message=u'Pole jest wymagane')], query_factory=get_trucks, allow_blank=True, blank_text="Wybierz...")    
    semitrailer = QuerySelectField(u'Naczepa', query_factory=get_semitrailers, allow_blank=True, blank_text="Wybierz...")
    start_counter = IntegerField(u'Początkowy stan licznika', default=0)