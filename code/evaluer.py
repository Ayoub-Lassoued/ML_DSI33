# code/evaluer.py
import csv, json, os, re, sys, time
from classifieur import CONSIGNE, classer
from evaluation import afficher_rapport

PAUSE = 2.1  # 30 requêtes/minute au maximum

DOSSIER_CODE = os.path.dirname(os.path.abspath(__file__))
CSV_PAR_DEFAUT = os.path.join(DOSSIER_CODE, "..", "data", "tickets.csv")
DOSSIER_RESULTATS = os.path.join(DOSSIER_CODE, "..", "resultats")


def charger(chemin=CSV_PAR_DEFAUT):
    """Lit le CSV et renvoie une liste de dictionnaires (une par ticket)."""
    with open(chemin, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def nom_fichier(etiquette):
    """'openai/gpt-oss-20b' -> 'openai_gpt-oss-20b.json'."""
    return re.sub(r"[^\w.-]+", "_", etiquette).strip("_") + ".json"


def evaluer(modele, lignes, consigne=CONSIGNE, etiquette=None):
    etiquette = etiquette or modele
    vrais, predits, debut = [], [], time.time()
    for ligne in lignes:
        predits.append(classer(ligne["texte"], modele, consigne=consigne))
        vrais.append(ligne["categorie"])
        time.sleep(PAUSE)
    resume = afficher_rapport(etiquette, vrais, predits)
    resume.update(modele=modele, etiquette=etiquette,
                  duree_s=round(time.time() - debut, 1),
                  predits=predits, vrais=vrais,
                  ids=[l["id"] for l in lignes])

    os.makedirs(DOSSIER_RESULTATS, exist_ok=True)
    chemin = os.path.join(DOSSIER_RESULTATS, nom_fichier(etiquette))
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(resume, f, ensure_ascii=False, indent=2)
    print(f"\nRésultats enregistrés : {os.path.normpath(chemin)}")
    return resume


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage : python evaluer.py <modele>")
    evaluer(sys.argv[1], charger())