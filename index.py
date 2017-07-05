from flask import Flask, request, render_template
from Bio import Entrez

#Het identificieren, om informatie op te halen
Entrez.email = "history.user@example.com"

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template( '/index.html' )

#Deze functie maakt van de zoek resultaten een json bestand en schrijft deze weg als resultaten,json op de server.
#Met behulp van dit json bestand wordt het netwerk/graaf gegenereerd.
@app.route("/results", methods=["POST"])
def results():
    query = request.form["query"]
    date1 = request.form["date1"]
    date2 = request.form["date2"]

    bestand = open("static/namen_planten.txt", mode="r")

    bl = makeList(bestand)
    makeJson(bl, query, date1, date2)

    return render_template('/results.html', query=query, date1=date1, date2=date2)

def makeList(bestand):
    begripLijst = []

    for regel in bestand:
        if regel in ("\n", "\r\n"):
            None
        else:
            regel = regel.strip()
            begripLijst.append(regel)
            
    return begripLijst
#Deze functie maakt van de zoek resultaten een json bestand en schrijft deze weg als resultaten.json
#op de server. Met behulp van dit json bestand wordt het netwerk/graaf gegenereerd.
def makeJson(bl, query, date1, date2):
    output = open("static/resultaten.json",'w', newline="\r\n")
    count2 = 0
    count3 = 0
    length = len(bl)-1

    output.write("""{ "nodes":[""")
    output.write("""{"id":"n", "loaded":true, "style":{ "fillColor": "rgba(236,46,46,0.8)", "label":\""""+query+"\"""}},\n""")

    for res in range(len(bl)):
        search_results = Entrez.read(Entrez.esearch(db="pubmed", term= query+" AND "+bl[count2]+" "+str(date1)+":"+str(date2)+" [PDAT]", datetype="pdat", usehistory="y"))
        count = int(search_results["Count"])

        if count2 == length:
            output.write("""{"id":"n"""+str(count2)+"""", "loaded":true, "style":{ "fillColor": "rgba(47,195,47,0.8)", "label":\""""+bl[count2]+""" """+str(count)+""" resultaten\"}}\n""")
        else:
            output.write("""{"id":"n"""+str(count2)+"""", "loaded":true, "style":{ "fillColor": "rgba(47,195,47,0.8)", "label":\""""+bl[count2]+""" """+str(count)+""" resultaten\"}},\n""")
			
        count2+=1
    output.write("],")

    output.write("""\"links\":[""")
    for sco in range(len(bl)):
        if count3 == length:
            output.write("""{"id":"e"""+str(count3)+"""", "from":"n", "to":"n"""+str(count3)+"""", "style":{"fillColor":"rgba(236,46,46,1)", "toDecoration":"arrow"}}\n""")
        else:
            output.write("""{"id":"e"""+str(count3)+"""", "from":"n", "to":"n"""+str(count3)+"""", "style":{"fillColor":"rgba(236,46,46,1)", "toDecoration":"arrow"}},\n""")
        count3+=1
    output.write("]}")

if __name__ == "__main__":
    app.run()