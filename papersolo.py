from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import re

#########################################################################
######################Levenshtein Distance Implementation################
#########################################################################

def LD(s,t):
    s = ' ' + s
    t = ' ' + t
    d = {}
    S = len(s)
    T = len(t)
    for i in range(S):
        d[i, 0] = i
    for j in range (T):
        d[0, j] = j
    for j in range(1,T):
        for i in range(1,S):
            if s[i] == t[j]:
                d[i, j] = d[i-1, j-1]
            else:
                d[i, j] = min(d[i-1, j], d[i, j-1], d[i-1, j-1]) + 1
    return d[S-1, T-1]

#########################################################################
#########################################################################

my_url = 'https://ideas.repec.org/a/aea/aecrev/v80y1990i1p204-17.html'

# opening up connection, grabbing the page
uClient = uReq(my_url)
page_html = uClient.read()
uClient.close()

# html parsing
sopa = soup(page_html, "html.parser")

#-------------------------------------------------------------------------------
#--- (1) out
#-------------------------------------------------------------------------------


PapersFile = open('Papers2.txt', 'w')
headers = "Journal | Year | Issue | Volume | Title | Author | Affiliation | Citations\n"
PapersFile.write(headers)

# getting paper info
info = sopa.find_all("meta")

# Journal name
journa = info[19].get("content")
journal = str(journa)

# Year
yea = info[25].get("content")
year = str(yea)

# Issue
issu = info[27].get("content")
issue = str(issu)

# Volume
volum = info[26].get("content")
volume = str(volum)

# Paper name
nam = info[16].get("content")
name = str(nam)

# Authors
authors = info[15].get("content")
autores = authors.split("; ")

# Citations
citations = sopa.find("a", {"aria-controls":"cites"})
try:
    citas = citations.text
except:
    citas= "."

# Affiliations
# Páginas de autores registrados
registrados = sopa.find("ul", {"id":"authorregistered"})
links = registrados.find_all("a")
aa=[]
lnk=[]
autrs=[]
base2 = 'https://ideas.repec.org'

for link in links:
    aa.append(link.text)
    lnk.append(link['href'])

for a in aa:
    autrs.append(a.replace("  "," ").rstrip( ))

print(autores)
print(autrs)
print(lnk)

bienasignados=[]
for c in autrs:
    pos = autrs.index(c)
    pagc = lnk[pos]
    dismin = 20
    distancia = []
    atr = []
    for d in autores:
        dist = LD(c,d)
        distancia += [dist]
        atr += [d]
    minimo = min(distancia)
    posicion = distancia.index(minimo)

    if minimo < dismin:
        print("Se encontró afiliación para " + atr[posicion])
        try:
            a = re.sub('[^ a-zA-Z0-9 ]', '', atr[posicion])
        except:
            a = "problema!"
    else: a = "No hizo match!"
    bienasignados += [a]

    """Para sacar la afiliación del autor que estamos revisando"""

    dadd = base2 + pagc
    # Vamos a la página del autor
    cliente2 = uReq(dadd)
    pagehtml1 = cliente2.read()
    cliente2.close()

    # html parsing
    sopa3 = soup(pagehtml1, "html.parser")

    # affiliation
    aut = sopa3.find("div", {"id": "title"})
    autho = aut.h1.text
    author = re.sub('[^ a-zA-Z0-9]', '', autho)
    affi = sopa3.find("div", {"id": "affiliation"})
    try:
        affiliation = affi.h3.text
    except:
        affiliation = "."

    print("Journal: " + journal)
    print("Year: " + year)
    print("Issue: " + issue)
    print("Volume: " + volume)
    print("Title: " + name)
    print("Author: " + author)
    print("Affiliation: " + affiliation)
    print("Citations: " + citas)
    PapersFile.write(
        journal + ' | ' + year + ' | ' + issue + ' | ' + volume + ' | ' + name + ' | ' + author + ' | ' + affiliation + ' | ' + citas + '\n')

print(bienasignados)
print(autores)

"""ahora vemos los autores que no están registrados"""

for autore in autores:
    try:
        autor = re.sub('[^ a-zA-Z0-9 ]', '', autore)
    except:
        autor = "."

    fot = autor in bienasignados
    if fot == False:
        print("Journal: " + journal)
        print("Year: " + year)
        print("Issue: " + issue)
        print("Volume: " + volume)
        print("Title: " + name)
        print("Authors: " + autor)
        print("Affiliation: Sin afiliación")
        print("Citations: " + citas)
        PapersFile.write(journal + ' | ' + year + ' | ' + issue + ' | ' + volume + ' | ' + name + ' | ' + autor + ' | ' + "." + ' | ' + citas + '\n')

    else:
        print("Se encontró afiliación")

""" Este es el código que se usa actualmente. Funciona, pero con errores de reconocimiento

for autore in autores:
    tof = autore in autrs
    try:
        autor = re.sub('[^ a-zA-Z0-9 ]', '', autore)
    except:
        autor = "."
    print(tof)

    if tof==False:
        print("Journal: " + journal)
        print("Year: " + year)
        print("Issue: " + issue)
        print("Volume: " + volume)
        print("Title: " + name)
        print("Authors: " + autor)
        print("Affiliation: Sin afiliación")
        print("Citations: " + citas)
        PapersFile.write(journal + ' | ' + year + ' | ' + issue + ' | ' + volume + ' | ' + name + ' | ' + autor + ' | ' + "." + ' | ' + citas + '\n')

    else:
        print("Se encontró afiliación")

for link in links:
    d = link['href']
    dadd = base2 + d
    # Vamos a la página del autor
    cliente2 = uReq(dadd)
    pagehtml1 = cliente2.read()
    cliente2.close()

    # html parsing
    sopa3 = soup(pagehtml1, "html.parser")

    # affiliation
    aut = sopa3.find("div", {"id": "title"})
    autho = aut.h1.text
    author = re.sub('[^ a-zA-Z0-9]', '', autho)
    affi = sopa3.find("div", {"id":"affiliation"})
    try:
        affiliation = affi.h3.text
    except:
        affiliation = "."

    print("Journal: " + journal)
    print("Year: " + year)
    print("Issue: " + issue)
    print("Volume: " + volume)
    print("Title: " + name)
    print("Authors: " + author)
    print("Affiliation: " + affiliation)
    print("Citations: " + citas)
    PapersFile.write(journal + ' | ' + year + ' | ' + issue + ' | ' + volume + ' | ' + name + ' | ' + author + ' | ' + affiliation + ' | ' + citas + '\n')
"""
