# -*- coding: utf-8 -*-
"""Genera comuni_gg.js dalla tabella gradi giorno del DPR 412/93.
Uso: python build_comuni.py  (richiede il PDF DPR412 nel percorso indicato)."""
import fitz, json, collections, io

PDF = r"C:\Users\LucaCarbisiero\OneDrive - FBC Italia srl\ESCO FBC\01_Diagnosi Energetiche\DPR4121993_P01_merged.pdf"

# Provincia -> (nome, regione)  [codici DPR 412/1993, 96 province]
PROV = {
 "TO":("Torino","Piemonte"),"VC":("Vercelli","Piemonte"),"NO":("Novara","Piemonte"),"CN":("Cuneo","Piemonte"),
 "AT":("Asti","Piemonte"),"AL":("Alessandria","Piemonte"),"BI":("Biella","Piemonte"),
 "AO":("Aosta","Valle d'Aosta"),
 "VA":("Varese","Lombardia"),"CO":("Como","Lombardia"),"SO":("Sondrio","Lombardia"),"MI":("Milano","Lombardia"),
 "BG":("Bergamo","Lombardia"),"BS":("Brescia","Lombardia"),"PV":("Pavia","Lombardia"),"CR":("Cremona","Lombardia"),"MN":("Mantova","Lombardia"),
 "BZ":("Bolzano","Trentino-Alto Adige"),"TN":("Trento","Trentino-Alto Adige"),
 "VR":("Verona","Veneto"),"VI":("Vicenza","Veneto"),"BL":("Belluno","Veneto"),"TV":("Treviso","Veneto"),
 "VE":("Venezia","Veneto"),"PD":("Padova","Veneto"),"RO":("Rovigo","Veneto"),
 "UD":("Udine","Friuli-Venezia Giulia"),"GO":("Gorizia","Friuli-Venezia Giulia"),"TS":("Trieste","Friuli-Venezia Giulia"),"PN":("Pordenone","Friuli-Venezia Giulia"),
 "IM":("Imperia","Liguria"),"SV":("Savona","Liguria"),"GE":("Genova","Liguria"),"SP":("La Spezia","Liguria"),
 "PC":("Piacenza","Emilia-Romagna"),"PR":("Parma","Emilia-Romagna"),"RE":("Reggio Emilia","Emilia-Romagna"),"MO":("Modena","Emilia-Romagna"),
 "BO":("Bologna","Emilia-Romagna"),"FE":("Ferrara","Emilia-Romagna"),"RA":("Ravenna","Emilia-Romagna"),"FO":("Forlì-Cesena","Emilia-Romagna"),
 "MS":("Massa-Carrara","Toscana"),"LU":("Lucca","Toscana"),"PT":("Pistoia","Toscana"),"FI":("Firenze","Toscana"),
 "LI":("Livorno","Toscana"),"PI":("Pisa","Toscana"),"AR":("Arezzo","Toscana"),"SI":("Siena","Toscana"),"GR":("Grosseto","Toscana"),
 "PG":("Perugia","Umbria"),"TR":("Terni","Umbria"),
 "PS":("Pesaro e Urbino","Marche"),"AN":("Ancona","Marche"),"MC":("Macerata","Marche"),"AP":("Ascoli Piceno","Marche"),
 "VT":("Viterbo","Lazio"),"RI":("Rieti","Lazio"),"RM":("Roma","Lazio"),"LT":("Latina","Lazio"),"FR":("Frosinone","Lazio"),
 "AQ":("L'Aquila","Abruzzo"),"TE":("Teramo","Abruzzo"),"PE":("Pescara","Abruzzo"),"CH":("Chieti","Abruzzo"),
 "CB":("Campobasso","Molise"),"IS":("Isernia","Molise"),
 "CE":("Caserta","Campania"),"BN":("Benevento","Campania"),"NA":("Napoli","Campania"),"AV":("Avellino","Campania"),"SA":("Salerno","Campania"),
 "FG":("Foggia","Puglia"),"BA":("Bari","Puglia"),"TA":("Taranto","Puglia"),"BR":("Brindisi","Puglia"),"LE":("Lecce","Puglia"),
 "PZ":("Potenza","Basilicata"),"MT":("Matera","Basilicata"),
 "CS":("Cosenza","Calabria"),"CZ":("Catanzaro","Calabria"),"RC":("Reggio Calabria","Calabria"),
 "TP":("Trapani","Sicilia"),"PA":("Palermo","Sicilia"),"ME":("Messina","Sicilia"),"AG":("Agrigento","Sicilia"),
 "CL":("Caltanissetta","Sicilia"),"EN":("Enna","Sicilia"),"CT":("Catania","Sicilia"),"RG":("Ragusa","Sicilia"),"SR":("Siracusa","Sicilia"),
 "SS":("Sassari","Sardegna"),"NU":("Nuoro","Sardegna"),"CA":("Cagliari","Sardegna"),"OR":("Oristano","Sardegna"),
}

d = fitz.open(PDF)
lines=[]
for pg in d:
    for ln in pg.get_text().split("\n"):
        s=ln.strip()
        if s: lines.append(s)

recs=collections.defaultdict(list)
i=0; n=len(lines)
while i<n:
    tok=lines[i]
    if tok in PROV and i+4<n:
        z,gg,alt,com=lines[i+1],lines[i+2],lines[i+3],lines[i+4]
        if len(z)==1 and z in "ABCDEF" and gg.isdigit() and alt.lstrip("-").isdigit():
            recs[tok].append([com.strip(), int(gg)]); i+=5; continue
    i+=1

# ordina i comuni alfabeticamente per provincia
out={code:sorted(v, key=lambda x:x[0]) for code,v in recs.items()}
tot=sum(len(v) for v in out.values())
unknown=[c for c in recs if c not in PROV]
print("comuni:",tot,"province:",len(out),"sconosciute:",unknown)

prov_out={c:{"n":PROV[c][0],"r":PROV[c][1]} for c in sorted(out.keys())}

with io.open("comuni_gg.js","w",encoding="utf-8") as f:
    f.write("/* Gradi giorno per comune — fonte: DPR 412/1993 (allegato A). Generato da build_comuni.py */\n")
    f.write("window.PROVINCE_IT = "+json.dumps(prov_out, ensure_ascii=False)+";\n")
    f.write("window.COMUNI_GG = "+json.dumps(out, ensure_ascii=False)+";\n")
print("scritto comuni_gg.js")
