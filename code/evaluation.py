CATEGORIES = ["facturation", "technique", "compte", "commercial"]
INVALIDE = "invalide"

def accuracy(vrais, predits):
    return sum(1 for v, p in zip(vrais, predits) if v == p) / len(vrais)
def taux_invalides(predits, classes=CATEGORIES):
    """Part des réponses hors nomenclature (JSON cassé, catégorie inventée)."""
    if not predits:
        return 0.0
    return sum(1 for p in predits if p not in classes) / len(predits)


def matrice_confusion(vrais, predits, classes=CATEGORIES):
    """Lignes = vérité, colonnes = prédiction (+ une colonne 'invalide').

    Renvoie {vrai: {predit: nombre}}, facile à enregistrer en JSON.
    """
    colonnes = list(classes) + [INVALIDE]
    matrice = {v: {c: 0 for c in colonnes} for v in classes}
    for v, p in zip(vrais, predits):
        if v not in matrice:
            continue
        colonne = p if p in classes else INVALIDE
        matrice[v][colonne] += 1
    return matrice


def scores_par_classe(vrais, predits, classes=CATEGORIES):
    resultat = {}
    for c in classes:
        vp = sum(1 for v, p in zip(vrais, predits) if v == c and p == c)
        fp = sum(1 for v, p in zip(vrais, predits) if v != c and p == c)
        fn = sum(1 for v, p in zip(vrais, predits) if v == c and p != c)
        precision = vp / (vp + fp) if (vp + fp) else 0.0
        recall = vp / (vp + fn) if (vp + fn) else 0.0
        f1 = (2 * precision * recall / (precision + recall)
              if (precision + recall) else 0.0)
        resultat[c] = {"precision": precision, "recall": recall,
                       "f1": f1, "support": vp + fn}
    return resultat


def f1_macro(scores):
    return sum(d["f1"] for d in scores.values()) / len(scores)




def afficher_rapport(etiquette, vrais, predits, classes=CATEGORIES):
    """Imprime le résumé et renvoie un dictionnaire prêt pour json.dump."""
    scores = scores_par_classe(vrais, predits, classes)
    acc = accuracy(vrais, predits)
    macro = f1_macro(scores)
    inval = taux_invalides(predits, classes)
    matrice = matrice_confusion(vrais, predits, classes)

    print(f"=== {etiquette} ===")
    print(f"accuracy : {acc:.3f}")
    print(f"macro-F1 : {macro:.3f}")
    print(f"invalides : {inval:.3f}")
    print()
    print(f"{'categorie':<13}{'precision':>10}{'recall':>8}{'F1':>8}{'n':>5}")
    for c in classes:
        d = scores[c]
        print(f"{c:<13}{d['precision']:>10.3f}{d['recall']:>8.3f}"
              f"{d['f1']:>8.3f}{d['support']:>5}")

    colonnes = list(classes) + [INVALIDE]
    print("\nConfusion matrix (lignes = vérité, colonnes = prédiction)")
    print(" " * 13 + "".join(f"{c[:6]:>7}" for c in colonnes))
    for v in classes:
        print(f"{v:<13}" + "".join(f"{matrice[v][c]:>7}" for c in colonnes))

    return {
        "accuracy": acc,
        "macro_f1": macro,
        "taux_invalides": inval,
        "scores": scores,
        "matrice": matrice,
    }



