## -*- coding: utf-8 -*-

def currency_spell_out(amount, currency=u'złoty', rest=u'groszy'):
    values = str("%7.2f" % amount).split('.')
    
    result = [slownie(int(value)) for value in values]
    
    return result[0] + ' ' + currency + ' ' + result[1] + ' ' + rest

pojedyncze = [u"jeden", u"dwa", u"trzy", u"cztery", u"pięć", u"sześć", u"siedem",
     u"osiem", u"dziewięć", u"dziesięć", u"jedenaście", u"dwanaście",
     u"trzynaście", u"czternaście", u"piętnaście", u"szesnaście", u"siedemnaście",
     u"osiemnaście", u"dziewiętnaście"]
dziesiatki = [u"dwadzieścia", u"trzydzieści", u"czterdzieści",
     u"pięćdziesiąt", u"sześćdziesiąt", u"siedemdziesiąt", u"osiemdziesiąt",
     u"dziewięćdziesiąt"]
setki = [u"sto", u"dwieście", u"trzysta", u"czterysta", u"pięćset", u"sześćset",
     u"siedemset", u"osiemset", u"dziewięćset"]
duze1 = [u"tysiąc", u"milion", u"miliard", u"bilion", u"biliard", u"trylion",
     u"tryliard"]
duze234 = [u"tysiące", u"miliony", u"miliardy", u"biliony", u"biliardy",
     u"tryliony", u"tryliardy"]
duze5 = [u"tysięcy", u"milionów", u"miliardów", u"bilionów", u"biliardów",
     u"trylionów", u"tryliardów"]

def slownie(n, separator=' '):
    tekst = []  # Składniki tekstu (lista stringów)
    duza = -1  # Wskazuje indeks w tablicy nazw dużych liczb
    append_minus = False
    
    if n == 0:  # Czy podano zero
        return 'zero'
    if n >= 1000 * 10**21:  # liczba musi być mniejsza od 1000 tryliardów
        raise ValueError(str(n) + "Zbyt duża liczba!")
    
    if str(n)[0] == '-':       
        append_minus = True
        n = int(str(n)[1:])
     
    while n > 0:
        nx = n % 1000  # Bierzemy 3 miejscową (0-999) część liczby
        n1 = nx % 10  # Jedności
        n10 = nx % 100 // 10  # Dziesiątki
        n100 = nx // 100  # Setki

        if n10 == 1:  # Specjalna obsługa liczb 10-19
            n10 = 0
            n1 += 10

        if nx != 0:  # Jeśli badana zcęść liczby jest niezerowa
            if duza >= 0:  # Potrzeba dodać nazwę dużej liczby
                if nx == 1:  # Część liczby == 1, to mianownik l.p.
                    tekst.insert(0, duze1[duza])
                elif 2 <= n1 <= 4:  # Ostatnia cyfra 2, 3 lub 4 mianownik l.mn.                        
                    tekst.insert(0, duze234[duza])
                else:  # Jeśli nic z powyższych, to używamy dopełniacz l.mn.
                    tekst.insert(0, duze5[duza])

            if n1 > 0 and not (nx == 1 and duza >= 0):  # Jedności
                tekst.insert(0, pojedyncze[n1-1])
            if n10 > 0:  # Dziesiątki
                tekst.insert(0, dziesiatki[n10-2])
            if n100 > 0:  # Setki
                tekst.insert(0, setki[n100-1])

        duza += 1  # Przesunięcie na następną nazwę w liście nazw dużych liczb

        n //= 1000  # "Odcięcie" już zamienionych cyfr
        
    if append_minus:
        tekst.insert(0, 'minus')

    return separator.join(tekst) 
 
def capfirst(text):
    """Capitalize first letter"""
    return text[0].upper() + text[1:]