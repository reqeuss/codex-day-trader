---
name: trader-exit
description: "Préparer le stop, l’objectif et l’heure limite d’un scénario intraday long à partir d’un prix ou du déclencheur d’entrée. Utiliser pour « calcule mon stop », « prépare ma sortie » ou « quel objectif à 2R ? ». Refuser les niveaux incohérents. Produit un plan local sans ordre ni garantie de prix exécuté."
---

# trader-exit

Exécuter [le script `scripts/exit.py`](scripts/exit.py) avec Python 3.8 ou plus récent. Remplacer `<DOSSIER_DU_SKILL>` par le dossier du `SKILL.md` effectivement chargé. Utiliser le chemin absolu du script et conserver la racine du projet utilisateur comme répertoire de travail pour partager `trader/` entre skills. Sous Windows, employer `python` si `python3` est absent.

## Langue et format de restitution

Répondre en français naturel, avec le tutoiement. Expliquer brièvement les termes techniques utiles ; garder les noms de commandes, chemins, clés JSON, symboles, statuts et paramètres tels quels. Les diagnostics bruts des scripts sont en anglais : en restituer le sens en français sans changer les nombres ni masquer une limite ou un refus. Les prix et budgets restent en USD ; ne pas les convertir en euros sans demande et taux sourcé. Les horaires techniques restent ceux de New York, indiqués explicitement. Si une heure locale est demandée, convertir pour la date concernée, sans décalage fixe avec Paris. Les exemples historiques de l'auteur ne sont pas des résultats personnels de Dan AI Lab ni des données actuelles.

Définir la sortie avant d'entrer : niveau d'invalidation, objectif et heure limite. Un stop ne garantit pas son prix d'exécution : un gap ou un marché rapide peut le dépasser. Le skill propose un plan pour une position longue ; il ne passe aucun ordre.

```bash
python3 "<DOSSIER_DU_SKILL>/scripts/exit.py" plan
python3 "<DOSSIER_DU_SKILL>/scripts/exit.py" plan --stop or-mid --target 1R --write
python3 "<DOSSIER_DU_SKILL>/scripts/exit.py" plan --stop atr:1.5
python3 "<DOSSIER_DU_SKILL>/scripts/exit.py" plan --symbol TSLA --entry 364.18 --or-high 362.18 --or-low 354.47
python3 "<DOSSIER_DU_SKILL>/scripts/exit.py" show
```

Autres paramètres : `--flat-by 15:55`, `--json`, `--now "2026-10-19 10:15"` (New York), `--entry PRICE` pour préparer un plan avant déclenchement, `--setup level`, `--offline FILE` pour les bougies nécessaires à l'ATR. 

## Fichiers

| Source | Usage |
| --- | --- |
| `trader/entry.json` | Symbole, prix d'entrée, heure, bougie, plage d'ouverture. |
| `trader/config.json` | `flat_by` (15:55), `min_reward_risk` (1.0 ; indiqué ici, imposé par trader-risk). |
| Yahoo | Seulement pour `atr:K` : bougies de la séance jusqu'à la bougie d'entrée. |
| `trader/plan.json` | Avec `--write` : entrée, stop/règle, objectif/R, risque par action, ratio et heure limite ; lu par timemachine, budget et alerts. |

## Choix du stop

| Paramètre | Niveau |
| --- | --- |
| `or-mid` | Milieu de la plage d'ouverture ; choix par défaut pour une cassure de cette plage. |
| `or-low` | Plus bas de la plage : plus éloigné, donc moins d'actions au même risque maximal. |
| `price:X` | Prix fourni. |
| `pct:X` | X % sous le prix d'entrée. |
| `atr:K` | K fois l'ATR 14 bougies sous l'entrée ; uniquement les bougies déjà connues à l'entrée. S'il y en a moins de 14, moyenne de celles disponibles avec mention explicite. |

Une configuration `level` n'a pas de plage d'ouverture : demander à l'utilisateur le stop souhaité.

## Calcul et refus

- Arrondir le stop au centime en l'éloignant de l'entrée : vers le bas pour un long. Risque par action = entrée − stop.
- Objectif = entrée + R × risque, arrondi au centime avec demi-arrondi vers le haut. `2R` par défaut ; `1R`, `1.5R` et `price:X` sont possibles.
- Refuser un stop supérieur ou égal à l'entrée, un objectif inférieur ou égal à l'entrée, ou un risque inférieur à 0,05 % du prix, trop serré face au spread.
- Refuser une entrée non déclenchée sans `--entry`, ainsi qu'une position courte.
- `flat_by` vaut 15 h 55 par défaut : sortir avant cette heure, quel que soit le résultat. Lors d'une clôture anticipée à 13 h, la limite devient 12 h 55. Refuser une entrée à cette heure ou plus tard.

## Déroulement

1. Après le déclenchement de `$trader-entry`, lancer le plan. Avant, `--entry PRICE` permet une préparation au prix attendu.
2. Pour une cassure de plage, garder le stop par défaut sauf autre choix explicite. Pour `level`, demander le niveau.
3. Lancer `exit.py plan --write` et restituer entrée, stop et règle, objectif et règle, risque par action, ratio et heure de sortie.
4. En cas de refus, expliquer pourquoi et ce qui doit être revu. Ne jamais élargir un stop, éloigner un objectif ou assouplir un critère sans décision de l'utilisateur.
5. Préciser que le prix du stop ne garantit pas le prix d'exécution.
6. Passer à `$trader-timemachine`, puis `$trader-budget`. Proposer les trois alertes de `$trader-alerts` pour le stop, l'objectif et l'heure de sortie.

Une surveillance `entry.py watch` ou une boucle disponible peut attendre le signal en arrière-plan, mais elle ne passe pas d'ordre. Le plan et sa validation restent nécessaires ensuite.

## Exemple historique de l'auteur

TSLA le 19 octobre 2026 : entrée 364,18 à 10 h 15, bougie 8, plage 354,47–362,18. Avec `--stop or-mid --target 1R` :

| Élément | Valeur en USD |
| --- | --- |
| Stop | 358,32 : (362,18 + 354,47) / 2 = 358,325, arrondi vers le bas. |
| Risque par action | 5,86, soit 1,61 % de l'entrée. |
| Objectif 1R | 370,04. |
| Objectif 2R par défaut | 375,90. |
| Sortie | Au plus tard 15 h 55 à New York. |

Avec un risque maximal d'exemple de 50 USD, trader-budget calcule ensuite `floor(50 / 5.86) = 8` actions. L'exemple n'est pas une recommandation actuelle.

## Limites

- Stop et objectif fixés avant l'entrée, jamais après.
- Ne jamais éloigner le stop une fois la position ouverte.
- Afficher les niveaux, le risque et le ratio ; ne pas présenter de rendement ou P&L attendu.
- Un objectif 1R ou 2R est une règle de planification, pas une prévision de prix.
- Ce skill ne dimensionne, ne place aucun ordre et ne modifie pas le plan pour forcer son acceptation.

## Sécurité

- Usage éducatif, pas un conseil financier personnalisé. `PASS` indique un contrôle technique.
- Travailler en simulation (`"paper": true`). Le plugin n’installe ni n’appelle aucun connecteur de courtage. Aucun ordre réel ou simulé n’est transmis. Ne jamais demander, lire, afficher ou enregistrer une clé de courtage.
- Avant toute transmission en simulation hors plugin, trois validations restent obligatoires pour le même ticket : `PASS` du jour de `$trader-risk` sur son empreinte exacte, accord explicite de l’utilisateur pour ce seul ticket, puis validation séparée par l’utilisateur dans l’interface du connecteur externe réglé pour demander une autorisation à chaque action. Dans Codex, laisser cette troisième validation en attente.
- Conserver la réponse originale. `oui`, `oui.` et `oui!` sont acceptés, ainsi que les confirmations anglaises prises en charge comme `yes`. Refuser les réponses conditionnelles, ambiguës ou collectives.
- Aucun ordre depuis une surveillance en arrière-plan ou une tâche planifiée. Les instructions du skill n’étendent pas les autorisations de l’environnement hôte.
- Options, marge, vente à découvert et levier désactivés par défaut. L’entrée, la sortie et la taille de ce pack planifient des positions longues.
- Une alerte ou une écriture dans le journal local ne prouve aucune exécution. Le prix d’un stop peut être dépassé.

Adaptation française : Dan AI Lab. Original : [Jake Schincariol](https://github.com/Jakeschincariol/day-trader-skill), licence MIT conservée dans [LICENSE](LICENSE).
