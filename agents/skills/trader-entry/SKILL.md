---
name: trader-entry
description: "Vérifier un déclencheur d’entrée sur bougies américaines de 1 ou 5 minutes, après clôture au-dessus de la plage d’ouverture ou d’un seuil. Utiliser pour « vérifie mon entrée », « préviens-moi à la cassure » ou « la plage d’ouverture est-elle cassée ? ». Positions longues et données potentiellement retardées. Aucun ordre."
---

# trader-entry

Exécuter [le script `scripts/entry.py`](scripts/entry.py) avec Python 3.8 ou plus récent. Remplacer `<DOSSIER_DU_SKILL>` par le dossier du `SKILL.md` effectivement chargé. Utiliser le chemin absolu du script et conserver la racine du projet utilisateur comme répertoire de travail pour partager `trader/` entre skills. Sous Windows, employer `python` si `python3` est absent.

## Langue et format de restitution

Répondre en français naturel, avec le tutoiement. Expliquer brièvement les termes techniques utiles ; garder les noms de commandes, chemins, clés JSON, symboles, statuts et paramètres tels quels. Les diagnostics bruts des scripts sont en anglais : en restituer le sens en français sans changer les nombres ni masquer une limite ou un refus. Les prix et budgets restent en USD ; ne pas les convertir en euros sans demande et taux sourcé. Les horaires techniques restent ceux de New York, indiqués explicitement. Si une heure locale est demandée, convertir pour la date concernée, sans décalage fixe avec Paris. Les exemples historiques de l'auteur ne sont pas des résultats personnels de Dan AI Lab ni des données actuelles.

Ce skill attend une confirmation à la clôture d'une bougie. Un prix qui dépasse le niveau pendant une bougie ne suffit pas. Une fois la clôture confirmée au-dessus, il enregistre l'heure et le prix pour le plan de sortie, puis s'arrête. Il n'achète rien et un signal ne garantit aucun résultat.


```bash
python3 "<DOSSIER_DU_SKILL>/scripts/entry.py" check TSLA
python3 "<DOSSIER_DU_SKILL>/scripts/entry.py" check TSLA --write
python3 "<DOSSIER_DU_SKILL>/scripts/entry.py" check TSLA --setup level --level 371.20
python3 "<DOSSIER_DU_SKILL>/scripts/entry.py" check TSLA --interval 1m --min-volume-x 1.5
python3 "<DOSSIER_DU_SKILL>/scripts/entry.py" watch TSLA --until 15:30
python3 "<DOSSIER_DU_SKILL>/scripts/entry.py" watchlist
```

Paramètres supplémentaires : `--or-minutes N` (15 par défaut), `--json`, `--offline FILE` (JSON Yahoo, `.json.gz` ou dossier de fichiers `<TICKER>.json`), `--now "2026-10-19 10:15"` pour une horloge de New York figée. `watch` avec `--now` ou `--offline` rejoue la journée sans attendre sur une horloge simulée.

## Entrées et sorties

| Source | Usage |
| --- | --- |
| `trader/watchlist.json` | `hits[].symbol` du scanner pour `watchlist`. |
| `trader/config.json` | Fenêtre `no_entries_before` / `no_entries_after`, 09:45 / 15:30 par défaut à New York. Facultatif. |
| API de graphiques Yahoo | Bougies du jour, `range=1d&interval=5m`, ou `1m`. Données non officielles et potentiellement retardées. |
| `trader/entry.json` | Avec `check --write` ou au déclenchement de `watch` : symbole, configuration, statut, heure, bougie, prix, niveau et plage d'ouverture. |

## Règle

- `orb` : plus haut et plus bas des 15 premières minutes. En 5 minutes : bougies de 9 h 30, 9 h 35, 9 h 40. En 1 minute : les 15 premières bougies. Le seuil est le plus haut de la plage.
- `level` : niveau donné par l'utilisateur, par exemple un plus haut 20 jours issu du scanner.
- Déclenchement : première bougie terminée après la plage qui **clôture strictement au-dessus** du niveau. Ni une mèche au-dessus ni une clôture exactement au niveau ne suffisent.
- L'heure annoncée est la clôture de la bougie. Celle de 10 h 10 clôture à 10 h 15 en intervalle 5 minutes. Le prix est celui de clôture, au cent près.
- Une bougie est terminée quand l'horloge dépasse son début + 1 ou 5 minutes et que Yahoo a rattrapé cet instant, avec une attente maximale d'une minute. Un tick comme 10:49:45 n'est pas une bougie.
- `--min-volume-x 1.5` exige un volume de déclenchement d'au moins 1,5 fois la moyenne de la plage. La bougie de 9 h 30 contient l'enchère d'ouverture ; même 1,0 est exigeant.
- Pas d'entrée avant 9 h 45 ni après 15 h 30 par défaut. Lors d'une clôture à 13 h, la limite devient 12 h 30.
- États possibles : attente avec distance au niveau, déclenché, expiré, absence de données. Avant 9 h 30 : marché pas encore ouvert. Avant 9 h 45 : plage en formation. Week-ends et jours fériés NYSE : fermé.

## Déroulement

1. Obtenir le symbole auprès de l'utilisateur, ou lancer `entry.py watchlist` après le scanner. Examiner d'abord `$trader-news`.
2. Lancer `entry.py check SYMBOL` et donner le statut en une ligne : attente et distance, déclenchement avec heure/prix, ou expiration.
3. Si une surveillance est demandée, utiliser `watch SYMBOL --until 15:30`, ou `check SYMBOL --write` toutes les 5 minutes avec un mécanisme de boucle disponible. `watch` vérifie après chaque clôture, écrit une ligne par bougie, sort avec 0 au déclenchement et écrit `trader/entry.json`, ou avec 1 à l'expiration. Un ordinateur en veille suspend le processus et peut produire un signal tardif au réveil ; ne pas prétendre que la surveillance continue lorsqu'il dort.
4. Au déclenchement, annoncer l'heure, le prix et l'absence d'ordre passé. Si le signal a plus d'une bougie de retard, le dire : une entrée tardive correspond à un autre trade.
5. Passer à `$trader-exit` pour fixer stop et objectif **avant tout achat**.

## Exemple historique de l'auteur

TSLA, 19 octobre 2026, bougies de 5 minutes : plage 354,47–362,18. À 10 h 12, la bougie de 10 h 10 n'est pas terminée. La dernière clôture connue est 361,68, à 0,50 USD sous le seuil. Le prix de 364,18 dans la bougie en cours ne compte pas encore.

À 10 h 15, la clôture 364,18 confirme une cassure de +0,55 %. Le fichier d'entrée est prêt pour `exit.py plan --from trader/entry.json`. Avec `--min-volume-x 1`, le volume de cette bougie ne représente que 0,60 fois la moyenne et le signal se décale à 10 h 35, à 365,75, avec un volume de 7,98 fois la moyenne. Ce sont les résultats des fixtures d'origine, pas des signaux actuels.

## Limites

- Données Yahoo gratuites, non officielles, retard possible. Les signaler quand une minute compte.
- Un seul déclenchement par configuration et par jour : la première clôture au-dessus. Les clôtures suivantes ne le réinitialisent pas.
- Positions longues uniquement ; ne pas prétendre que le moteur planifie une vente à découvert.
- Ne jamais anticiper une clôture parce qu'une bougie « semble » devoir finir au-dessus.
- Ne pas modifier le niveau après coup, dimensionner une position ou définir le stop ici.
- Ne jamais appeler `$trader-broker` depuis une surveillance en arrière-plan : personne n'est présent pour confirmer l'ordre.

## Sécurité

- Usage éducatif, pas un conseil financier personnalisé. `PASS` indique un contrôle technique.
- Travailler en simulation (`"paper": true`). Le plugin n’installe ni n’appelle aucun connecteur de courtage. Aucun ordre réel ou simulé n’est transmis. Ne jamais demander, lire, afficher ou enregistrer une clé de courtage.
- Avant toute transmission en simulation hors plugin, trois validations restent obligatoires pour le même ticket : `PASS` du jour de `$trader-risk` sur son empreinte exacte, accord explicite de l’utilisateur pour ce seul ticket, puis validation séparée par l’utilisateur dans l’interface du connecteur externe réglé pour demander une autorisation à chaque action. Dans Codex, laisser cette troisième validation en attente.
- Conserver la réponse originale. `oui`, `oui.` et `oui!` sont acceptés, ainsi que les confirmations anglaises prises en charge comme `yes`. Refuser les réponses conditionnelles, ambiguës ou collectives.
- Aucun ordre depuis une surveillance en arrière-plan ou une tâche planifiée. Les instructions du skill n’étendent pas les autorisations de l’environnement hôte.
- Options, marge, vente à découvert et levier désactivés par défaut. L’entrée, la sortie et la taille de ce pack planifient des positions longues.
- Une alerte ou une écriture dans le journal local ne prouve aucune exécution. Le prix d’un stop peut être dépassé.

Adaptation française : Dan AI Lab. Original : [Jake Schincariol](https://github.com/Jakeschincariol/day-trader-skill), licence MIT conservée dans [LICENSE](LICENSE).
