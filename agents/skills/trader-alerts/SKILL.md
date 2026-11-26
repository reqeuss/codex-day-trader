---
name: trader-alerts
description: "Vérifier des seuils de prix, un stop, un objectif, une variation en pourcentage ou une heure de marché NYSE. Utiliser pour « surveille mon stop », « rappelle-moi de sortir », « quel est le cours ? » ou « le NYSE est-il ouvert ? ». Données potentiellement retardées et alertes informatives. Aucune exécution d’ordre."
---

# trader-alerts

Exécuter [le script `scripts/alerts.py`](scripts/alerts.py) avec Python 3.8 ou plus récent. Remplacer `<DOSSIER_DU_SKILL>` par le dossier du `SKILL.md` effectivement chargé. Utiliser le chemin absolu du script et conserver la racine du projet utilisateur comme répertoire de travail pour partager `trader/` entre skills. Sous Windows, employer `python` si `python3` est absent.

## Langue et format de restitution

Répondre en français naturel, avec le tutoiement. Expliquer brièvement les termes techniques utiles ; garder les noms de commandes, chemins, clés JSON, symboles, statuts et paramètres tels quels. Les diagnostics bruts des scripts sont en anglais : en restituer le sens en français sans changer les nombres ni masquer une limite ou un refus. Les prix et budgets restent en USD ; ne pas les convertir en euros sans demande et taux sourcé. Les horaires techniques restent ceux de New York, indiqués explicitement. Si une heure locale est demandée, convertir pour la date concernée, sans décalage fixe avec Paris. Les exemples historiques de l'auteur ne sont pas des résultats personnels de Dan AI Lab ni des données actuelles.

Une alerte informe ; elle ne vend ni n'achète rien. Avec un bracket, le stop et l'objectif sont des ordres placés chez le courtier. Les alertes locales indiquent qu'un niveau ou une heure a été atteint ; vérifier l'état réel de la position chez le courtier.

```bash
python3 "<DOSSIER_DU_SKILL>/scripts/alerts.py" clock
python3 "<DOSSIER_DU_SKILL>/scripts/alerts.py" add --from-plan
python3 "<DOSSIER_DU_SKILL>/scripts/alerts.py" add --opening-bell
python3 "<DOSSIER_DU_SKILL>/scripts/alerts.py" add --symbol TSLA --stop 358.32
python3 "<DOSSIER_DU_SKILL>/scripts/alerts.py" add --symbol TSLA --target 370.04
python3 "<DOSSIER_DU_SKILL>/scripts/alerts.py" add --at 15:55 --label "Sortie avant clôture" --before-close
python3 "<DOSSIER_DU_SKILL>/scripts/alerts.py" add --symbol KO --pct 3
python3 "<DOSSIER_DU_SKILL>/scripts/alerts.py" check
python3 "<DOSSIER_DU_SKILL>/scripts/alerts.py" quote TSLA --write
python3 "<DOSSIER_DU_SKILL>/scripts/alerts.py" quote --holdings --write
python3 "<DOSSIER_DU_SKILL>/scripts/alerts.py" list
python3 "<DOSSIER_DU_SKILL>/scripts/alerts.py" reset tsla-plan-stop
```

`--now "2026-10-19 15:55"` fige l’heure à New York. `--offline DIR` lit des fichiers sauvegardés. `check` renvoie un code 0 lorsqu’au moins une alerte a sonné.

## Fichiers

| Fichier | Usage |
| --- | --- |
| `trader/plan.json` | Plan de trader-exit pour `add --from-plan`. |
| `trader/alerts.json` | Règles ; voir [`alerts.example.json`](references/alerts.example.json). |
| `trader/state/alerts.json` | Déclenchements précédents pour éviter les doublons. |
| `trader/prices.json` | Derniers cours fusionnés avec horodatage, pour budget et risk. |
| `trader/portfolio.json` | Symboles détenus pour `quote --holdings`. |

## Types de règle

| Type | Déclenchement | Réarmement |
| --- | --- | --- |
| `above` / `target` | Prix supérieur ou égal à `price`. | Après `reset`, ou automatiquement si `rearm: true` et retour préalable sous le seuil. |
| `below` / `stop` | Prix inférieur ou égal à `price`. | Même logique, dans l'autre sens. |
| `pct_move` | Écart de `pct` % à la clôture précédente ou à `ref`, avec direction up/down facultative. | Une fois par jour au maximum. |
| `time` | Heure `at` dépassée à New York un jour de bourse. | Une fois par séance. |
| `opening_bell` | NYSE ouvert. | Une fois par séance. |

Une règle avec `date` ne s'applique qu'à ce jour de New York. Celles issues du plan portent sa date : le stop d'hier ne sonne pas aujourd'hui. `before_close: true` avance une règle horaire de 3 heures quand le NYSE ferme à 13 h : 15 h 55 devient 12 h 55.

## Cours

- Yahoo, choix par défaut : `query2.finance.yahoo.com/v8/finance/chart/<TICKER>`, endpoint gratuit non officiel, une requête par symbole et une pause de 0,5 seconde. Sur 429 : attente et nouvelle tentative ; puis repli query1 après 429 ou 5xx. Le User-Agent du moteur reste `day-trader-skill/2.0`.
- Stooq : `stooq.com/q/l/?s=tsla.us&f=sd2t2ohlcv&h&e=csv`. L'auteur a observé une réponse 404 le 13 octobre 2026 ; le parseur est conservé, sans promettre la disponibilité actuelle.
- Les cours gratuits peuvent convenir à une alerte ou un contrôle de taille, pas à une promesse d'entrée instantanée. Le courtier fixe le prix effectivement exécuté. trader-risk utilise seulement un prix de moins de 15 minutes.
- Si les deux sources échouent, signaler le cours indisponible ou utiliser un relevé fourni par l’utilisateur avec son horodatage réel. Ne pas appeler de connecteur de courtage.

## Horloge NYSE

Séance régulière de 9 h 30 à 16 h à New York. Le moteur gère le changement d'heure sans dépendre du fuseau de l'ordinateur. Calendrier conservé de l'amont, consulté par l'auteur le 13 octobre 2026 sur [NYSE](https://www.nyse.com/markets/hours-calendars) :

- 2026 : 1 et 19 janvier, 16 février, 3 avril, 25 mai, 19 juin, 3 juillet, 7 septembre, 26 novembre, 25 décembre. Clôture à 13 h les 27 novembre et 24 décembre.
- 2027 : 1 et 18 janvier, 15 février, 26 mars, 31 mai, 18 juin, 5 juillet, 6 septembre, 25 novembre, 24 décembre. Clôture à 13 h le 26 novembre.

Pour une autre année, annoncer que la liste des jours fériés est inconnue. Ne pas présenter un calendrier historique comme une vérification du jour.

## Déroulement

1. Après le plan, lancer `add --from-plan` et confirmer à l'utilisateur les trois alertes : stop, objectif, heure de sortie.
2. Pendant la position, lancer `check` à la fréquence demandée via une boucle ou une tâche réellement disponible. Chaque passage lit seulement les symboles des règles du jour. Une vérification ponctuelle n'est pas une surveillance continue ; un prix peut franchir le seuil entre deux passages.
3. Décrire chaque déclenchement en une ligne. Après un stop ou objectif, demander une preuve du résultat simulé à l’utilisateur avant de journaliser avec trader-broker.
4. À l'heure limite, si une position reste ouverte, préparer `trader-broker flatten`, puis trader-risk et le oui propre à cet ordre. Ne pas exécuter automatiquement depuis l'alerte.

## Exemple historique de l'auteur

TSLA le 19 octobre 2026 : entrée 364,18, stop 358,32, objectif 370,04, sortie à 15 h 55. `add --from-plan` écrit `tsla-plan-stop`, `tsla-plan-target`, `tsla-flat-by` pour cette journée.

À 10 h 53, le cours de 10 h 52 vaut 366,48 : aucun seuil atteint, trois règles surveillées. À 15 h 55, l'alerte demande de vérifier et fermer ce qui reste ouvert selon le parcours broker → risk → oui. Elle ne sonne qu'une fois. Le lendemain, les trois règles datées ne sont plus surveillées ; l'alerte `opening_bell` peut sonner à 9 h 30.

## Limites

Une alerte décrit un prix observé ou une heure. Confirmer chaque nouvelle règle : symbole, type, seuil et date. Ne jamais présenter un cours retardé comme temps réel, prédire une direction, ou placer, modifier ou annuler un ordre depuis ce skill.

## Sécurité

- Usage éducatif, pas un conseil financier personnalisé. `PASS` indique un contrôle technique.
- Travailler en simulation (`"paper": true`). Le plugin n’installe ni n’appelle aucun connecteur de courtage. Aucun ordre réel ou simulé n’est transmis. Ne jamais demander, lire, afficher ou enregistrer une clé de courtage.
- Avant toute transmission en simulation hors plugin, trois validations restent obligatoires pour le même ticket : `PASS` du jour de `$trader-risk` sur son empreinte exacte, accord explicite de l’utilisateur pour ce seul ticket, puis validation séparée par l’utilisateur dans l’interface du connecteur externe réglé pour demander une autorisation à chaque action. Dans Codex, laisser cette troisième validation en attente.
- Conserver la réponse originale. `oui`, `oui.` et `oui!` sont acceptés, ainsi que les confirmations anglaises prises en charge comme `yes`. Refuser les réponses conditionnelles, ambiguës ou collectives.
- Aucun ordre depuis une surveillance en arrière-plan ou une tâche planifiée. Les instructions du skill n’étendent pas les autorisations de l’environnement hôte.
- Options, marge, vente à découvert et levier désactivés par défaut. L’entrée, la sortie et la taille de ce pack planifient des positions longues.
- Une alerte ou une écriture dans le journal local ne prouve aucune exécution. Le prix d’un stop peut être dépassé.

Adaptation française : Dan AI Lab. Original : [Jake Schincariol](https://github.com/Jakeschincariol/day-trader-skill), licence MIT conservée dans [LICENSE](LICENSE).
