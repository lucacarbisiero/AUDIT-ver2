# -*- coding: utf-8 -*-
"""Genera comuni_gg.js (province ATTUALI + gradi giorno/zona climatica DPR 412/93).

Fonte: dataset open "Italy.Core" (SQLite, auto-aggiornato da ISTAT; campi zona_climatica
e gradi_giorno dal DPR 412/93 - valori ENEA). Repo: github.com/N0T-A-NUMB3R/Italy.Core

Uso:  python build_comuni.py
- Se manca 'italy.db' nella cartella, viene scaricato dal repo.
- Scrive 'comuni_gg.js' con window.PROVINCE_IT e window.COMUNI_GG.
"""
import sqlite3, json, io, os, urllib.request

DB = "italy.db"
DB_URL = "https://github.com/N0T-A-NUMB3R/Italy.Core/raw/HEAD/src/Italy.Core/data/italy.db"

# Nomi regione esattamente come nel menu a tendina dell'app (index.html)
APP_REGIONS = {
    "Abruzzo","Basilicata","Calabria","Campania","Emilia-Romagna","Friuli-Venezia Giulia",
    "Lazio","Liguria","Lombardia","Marche","Molise","Piemonte","Puglia","Sardegna","Sicilia",
    "Toscana","Trentino-Alto Adige","Umbria","Valle d'Aosta","Veneto"
}

def main():
    if not os.path.exists(DB):
        print("Scarico italy.db (~20 MB)...")
        urllib.request.urlretrieve(DB_URL, DB)

    con = sqlite3.connect(DB)
    rows = con.execute("""
        select denominazione, sigla_provincia, nome_provincia, nome_regione, gradi_giorno
        from comuni
        where is_attivo=1 and gradi_giorno is not null and sigla_provincia is not null
    """).fetchall()

    prov, com = {}, {}
    for den, sig, pnome, reg, gg in rows:
        region = reg.split("/")[0].strip()      # "Trentino-Alto Adige/Suedtirol" -> "Trentino-Alto Adige"
        pn = pnome.split("/")[0].strip()
        prov.setdefault(sig, {"n": pn, "r": region})
        com.setdefault(sig, []).append([den, int(gg)])

    for s in com:
        com[s].sort(key=lambda x: x[0])
    prov = {s: prov[s] for s in sorted(prov)}
    com = {s: com[s] for s in sorted(com)}

    bad = {v["r"] for v in prov.values()} - APP_REGIONS
    assert not bad, f"Regioni non allineate al menu app: {bad}"

    with io.open("comuni_gg.js", "w", encoding="utf-8") as f:
        f.write("/* Gradi giorno e zona climatica per comune (DPR 412/93, valori ENEA) con province attuali.\n"
                "   Fonte: ISTAT via dataset Italy.Core. Rigenerare con build_comuni.py */\n")
        f.write("window.PROVINCE_IT = " + json.dumps(prov, ensure_ascii=False) + ";\n")
        f.write("window.COMUNI_GG = " + json.dumps(com, ensure_ascii=False) + ";\n")

    print(f"OK: {len(prov)} province, {sum(len(v) for v in com.values())} comuni -> comuni_gg.js")

if __name__ == "__main__":
    main()
