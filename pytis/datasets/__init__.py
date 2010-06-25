## -*- coding: utf-8 -*-
from fixture import DataSet

class DictionaryData(DataSet):
    class pln:
        key = u'WAL'
        value = u'PLN'
        kind = 0

class GroupData(DataSet):
    class admin_group:
        name = u'Administratorzy'
    class default_group:
        name = u'Wszyscy'
        
class UserData(DataSet):
    class admin_user:
        login = u'admin'
        password = u'rafal1983'
        email = u'kosrafal@gmail.com'
        first_name = u'Rafal'
        last_name = u'Kos'
        phone = u'+48 602 326 653'
        groups = [GroupData.admin_group, GroupData.default_group]                