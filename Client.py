#ADVANCE LEVEL
#API FOTMATION
import requests

#For all the the URL(ENDPOINTS) in json
host = "http://localhost:8000"
URLS = ["/listSpecies?limit=10&json=1", "/listSpecies?json=1", "karyotipe?specie=human&json=1"
    "/karyotype?specie=mouse&json=1", "/chromosomeLength?specie=mouse&chromo=18&json=1", "/geneSeq?gene=FRAT1&json=1",
    "/geneInfo?gene=FRAT1&json=1", "/geneCalc?gene=FRAT1&json=1", "/geneList?chromo=1&start=0&end=30000&json=1"]
for i in URLS:
    link = host + i
    r = requests.get(link, headers={"Content-Type": "application/json"})
    json_code = r.json()

    print(json_code)
