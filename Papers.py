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

JNam = ['JEuEconAsso1','JEuEconAsso2','JEuEconAsso3','SouEconJ']
Ref = ['https://ideas.repec.org/s/tpr/jeurec.html','https://ideas.repec.org/s/bla/jeurec.html','https://ideas.repec.org/s/oup/jeurec.html','https://ideas.repec.org/s/sej/ancoec.html']
FPag = [4,3,2,7]


for j in JNam:

    #-------------------------------------------------------------------------------
    #--- (1) out
    #-------------------------------------------------------------------------------

    PapersFile = open(j + 'Papers.txt', 'w')
    headers = "Journal | Year | Issue | Volume | Title | Author | Affiliation | Citations\n"
    PapersFile.write(headers)

    #-------------------------------------------------------------------------------
    #--- (2) dump
    #-------------------------------------------------------------------------------

    ubic = JNam.index(j)
    bas = Ref[ubic]
    base = bas.split('.html')
    addresses = [str(bas)]
    pfin = FPag[ubic]

    for page in range(2, pfin):
        addresses += [str(base[0]) + str(page) + '.html']

    for a in addresses:
        sour = uReq(a)
        source = sour.read()
        sour.close()
        sopa = soup(source, "html.parser")

        #print(sopa)

        pap = sopa.find_all("li", {"class": "list-group-item downgate"})
        papers = []

        for f in pap:
            papers += [f.a.get('href')]

        base1 = "https://ideas.repec.org"

        for p in papers:

            #p = p.split('.html')
            padd = base1 + p

            # Vamos a las páginas de los papers
            cliente = uReq(padd)
            pagehtml = cliente.read()
            cliente.close()

            # html parsing
            sopa1 = soup(pagehtml, "html.parser")

            # getting paper info
            info = sopa1.find_all("meta")

            # Journal name
            try:
                journal = info[19].get("content")
            except:
                journal = "."

            # Year
            try:
                year = info[25].get("content")
            except:
                year = "."

            # Issue
            try:
                issue = info[27].get("content")
            except:
                issue = "."

            # Volume
            try:
                volume = info[26].get("content")
            except:
                volume = "."

            # Paper name
            try:
                nam = info[16].get("content")
                name = re.sub('[^ a-zA-Z0-9 ]', '', nam)
            except:
                name = "."

            # Authors
            authors = info[15].get("content")
            autores = authors.split("; ")

            # Citations
            try:
                citations = sopa1.find("a", {"aria-controls":"cites"})
                citas = citations.text
            except:
                citas = "."

            # Affiliations
            # Páginas de autores registrados
            registrados = sopa1.find("ul", {"id": "authorregistered"})
            links = registrados.find_all("a")
            aa = []
            lnk = []
            autrs = []
            base2 = 'https://ideas.repec.org'

            for link in links:
                aa.append(link.text)
                lnk.append(link['href'])

            for a in aa:
                autrs.append(a.replace("  ", " ").rstrip())

            while '' in autrs:
                n = autrs.index('')
                lnk.remove(lnk[n])
                autrs.remove('')

            print(autores)
            print(autrs)
            print(lnk)

            bienasignados = []
            for c in autrs:
                pos = autrs.index(c)
                pagc = lnk[pos]
                dismax = 20
                distancia = []
                atr = []
                for d in autores:
                    dist = LD(c, d)
                    distancia += [dist]
                    atr += [d]
                minimo = min(distancia)
                posicion = distancia.index(minimo)

                if minimo < dismax:
                    print("Se encontró afiliación para " + atr[posicion])
                    try:
                        a = re.sub('[^ a-zA-Z0-9 ]', '', atr[posicion])
                    except:
                        a = "problema!"
                else:
                    a = "No hizo match!"
                bienasignados += [a]

                """Para sacar la afiliación del autor que estamos revisando"""

                dadd = base2 + pagc
                # Vamos a la página del autor
                try:
                    cliente2 = uReq(dadd)
                    pagehtml1 = cliente2.read()
                    cliente2.close()

                    # html parsing
                    sopa2 = soup(pagehtml1, "html.parser")

                    # affiliation
                    aut = sopa2.find("div", {"id": "title"})
                    autho = aut.h1.text
                    author = re.sub('[^ a-zA-Z0-9]', '', autho)
                    affi = sopa2.find("div", {"id": "affiliation"})
                    try:
                        affiliatio = affi.h3.text
                        affiliation = re.sub('[^ a-zA-Z0-9]', '', affiliatio)
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
                except:
                    print("upsi")

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
                    PapersFile.write(
                        journal + ' | ' + year + ' | ' + issue + ' | ' + volume + ' | ' + name + ' | ' + autor + ' | ' + "." + ' | ' + citas + '\n')

                else:
                    print("Se encontró afiliación")
    print("Done!")




