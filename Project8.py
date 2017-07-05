from Bio import Entrez, Medline
from flask import Flask, request, render_template, json
from datetime import date

app = Flask(__name__)

#Mainflow door het programma
#Als eerst word de email vastgesteld, door de email adres
#parst csv query naar de dictionary {dutch:'', english:'', latin:''} in een lijst
#gebruikt querys om gerelateerde papers op te halen



#de index pagina ophalen uit de templates map
@app.route("/", methods=["GET"])
def index():
    return render_template("/index.html")

def Main(queryFilePath, Entrez=None):
    papers = []
    #Entrez.email = "aditi.ch2@gmail.com"  # Jezelf identificeren bij NCBI
    querysAsDicInList = CsvFileToList(queryFilePath)
    paperResult = RelatedPapers(querysAsDicInList)
    for query in paperResult:
        papers = paperResult[query]

#Kijkt of alle papers wel de juiste informatie bevateen en zet ze allemaal in een dictionary
def PaperInformation(paper, datetime=None, namen_planten=None, organismen=None, begripLijst=None):
    paperInformation = {}
    """
        for number in range (0,10):
            hit = idsHit[number]
            result = fetch_article(hit)
            for result in results:
                papers.append(result)
    """
    paperKeys = paper.keys()
    if 'AU' in paperKeys:
        author = paper['AU']
    else:
        author = "missing"
    if 'PMID' in paperKeys:
        link = 'https://www.ncbi.nlm.nih.gov/pubmed/?term=' + paper['PMID']
        pmid = paper['PMID']
    else:
        link = "missing"
        pmid = "missing"
    if 'DP' in paperKeys:
        date = paper['DP']
    else:
        date = 'missing'
    if 'AB' in paperKeys:
        summary = paper['AB']
    else:
        summary = 'missing'
    paperInformation["Author"] = "".join(author)
    paperInformation["Url"] = link
    try:
        paperInformation["PublicationDate"] = datetime.strptime(date, '%Y %b %d')
    except:
        try:
            paperInformation["PublicationDate"] = datetime.strptime(date, '%Y')
        except:
            paperInformation["PublicationDate"] = None
    paperInformation["PubMedId"] = pmid
# Maakt een dictionary aan die alle organismen laat zien met de pubmedcode erbij
# In begripLijst staan dus alle organismen in
    for organismen in begripLijst:
        paperInformation[organismen]=pmid
# Schrijft dictionary weg met json.dump, zodat sunburst het kan inlezen en aantonen
# Sunburst leest dit door de functie flare.json waardoor de geneste dictionary [paperInformation] word aangetoont in de sunburst
    with open("flare.json","w") as f:
        json.dump(paperInformation,f)

#Haalt papers op met id als json en geeft een lijst terug met alle papers
def FetchPaper(idToFetch):
    articles = []
    handle = Entrez.efetch(db="pubmed", id=idToFetch, rettype="medline", retmode="json",retmax=100000)
    try:
        article = Medline.parse(handle)
    except:
        print("Error can't retrieve: "+idToFetch)
        article = None
    #TODO find out why for loop is slow, prob pubmed thing
    for results in article:
        articles.append(results)
    print("Done retrieving")
    handle.close()
    return articles

#Parst csv file naar list
#Splitst op elke line, en zet informatie in de dictionary
#Eerste woord is Nederlands, tweede woord is Engels en derde woord is Latijns
def CsvFileToList(filePath):
    querys = []
    fileToUse = open(filePath,'r')
    for line in fileToUse:
        query = {}
        items = line.replace('\n','').split(',')
        query["Dutch"] = items[0]
        query["Englis"] = items[1]
        query["Latin"] = items[2]
        querys.append(query)
    return querys

#Loops through list and parses to csv format
def ListToCsv(items):
    line = ''
    for item in items:
        line += item + ','
    return line[:-1]

#Loopt door alle query dictionary en haalt alle papers op met engelse of latijnse naam
#Zet de resultaten in de dictionary met Engelse naam als key
def RelatedPapers(Entrez=None, queryAsDicInList=None):
    paperResults={}
    for query in queryAsDicInList:
        englishQuery = query["English"]
        latinQuery = query["Latin"]
        dutchQuery = query["Dutch"]
        handle = Entrez.esearch(db="pubmed", term="("+englishQuery+")OR("+latinQuery+")", retmode='xml', retmax=100000)
        records = Entrez.read(handle)
        handle.close()
        idsHit = records["IdList"]
        paperResults[englishQuery] = idsHit
    return paperResults


if __name__ == '__main__':
    app.run()
