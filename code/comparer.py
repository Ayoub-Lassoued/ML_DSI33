# code/comparer.py
import csv, glob, json, os

DOSSIER_CODE = os.path.dirname(os.path.abspath(__file__))
DOSSIER_RESULTATS = os.path.join(DOSSIER_CODE, "..", "resultats")
CSV_TICKETS = os.path.join(DOSSIER_CODE, "..", "data", "tickets.csv")
SEUIL_TICKETS = 5  # règle de la séance


def charger_resultats():
    resultats = []
    for chemin in sorted(glob.glob(os.path.join(DOSSIER_RESULTATS, "*.json"))):
        with open(chemin, encoding="utf-8") as f:
            r = json.load(f)
        r["bons"] = sum(1 for v, p in zip(r["vrais"], r["predits"]) if v == p)
        resultats.append(r)
    return resultats


def charger_tickets():
    with open(CSV_TICKETS, encoding="utf-8", newline="") as f:
        return {l["id"]: l for l in csv.DictReader(f)}


def tableau(resultats):
    resultats = sorted(resultats, key=lambda r: r["macro_f1"], reverse=True)
    meilleur = max(r["bons"] for r in resultats)
    largeur = max(len(r["etiquette"]) for r in resultats)

    print(f"{'Modèle':<{largeur}}  {'accuracy':>8}  {'macro-F1':>8}  "
          f"{'bons':>5}  {'Écart (tickets)':>15}  {'invalides':>9}  {'Durée':>7}")
    for r in resultats:
        ecart = meilleur - r["bons"]
        marque = "  <- différence mesurable" if ecart >= SEUIL_TICKETS else ""
        print(f"{r['etiquette']:<{largeur}}  {r['accuracy']:>8.3f}  "
              f"{r['macro_f1']:>8.3f}  {r['bons']:>3}/{len(r['vrais'])}  "
              f"{ecart:>15}  {r['taux_invalides']:>9.3f}  "
              f"{r['duree_s']:>6.0f}s{marque}")
    print(f"\nÉcart = nombre de tickets corrects en moins par rapport au meilleur. "
          f"Seuil de la séance : {SEUIL_TICKETS} tickets.")
    return resultats


def desaccords(resultats):
    # Les résultats doivent porter sur les mêmes tickets, dans le même ordre.
    ids = resultats[0]["ids"]
    if any(r["ids"] != ids for r in resultats):
        print("\nAttention : les évaluations ne portent pas sur les mêmes tickets.")
        return
    tickets = charger_tickets()

    divergents, tous_faux = [], []
    for i, tid in enumerate(ids):
        vrai = resultats[0]["vrais"][i]
        preds = [r["predits"][i] for r in resultats]
        if len(set(preds)) > 1:
            divergents.append((tid, vrai, preds))
        elif preds[0] != vrai:
            tous_faux.append((tid, vrai, preds[0]))

    print(f"\n=== {len(divergents)} tickets où les modèles divergent ===")
    for tid, vrai, preds in divergents:
        t = tickets.get(tid, {})
        ambigu = " [ambigu]" if t.get("ambigu") == "1" else ""
        print(f"\n{tid}  vérité : {vrai}{ambigu}")
        print(f"  « {t.get('texte', '')[:110]} »")
        for r, p in zip(resultats, preds):
            statut = "ok " if p == vrai else "ERR"
            print(f"  {statut} {r['etiquette']:<{max(len(x['etiquette']) for x in resultats)}}  -> {p}")

    print(f"\n=== {len(tous_faux)} tickets où tous les modèles se trompent "
          f"de la même façon ===")
    for tid, vrai, pred in tous_faux:
        t = tickets.get(tid, {})
        ambigu = " [ambigu]" if t.get("ambigu") == "1" else ""
        print(f"{tid}  vérité : {vrai:<12} prédit : {pred:<12}{ambigu}  "
              f"« {t.get('texte', '')[:70]} »")


if __name__ == "__main__":
    res = charger_resultats()
    if not res:
        raise SystemExit("Aucun fichier dans resultats/ : lancez d'abord evaluer.py")
    res = tableau(res)
    if len(res) > 1:
        desaccords(res)