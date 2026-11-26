---
name: trader-broker
description: "Préparer, afficher et journaliser un ticket d’ordre de simulation. Utiliser pour « montre le ticket », « prépare une clôture simulée » ou « enregistre mon oui pour ce ticket ». Exiger le PASS du jour sur l’empreinte exacte, un oui explicite et une validation indépendante du connecteur hors plugin. Aucun accès courtier, secret ni envoi d’ordre."
---

# trader-broker

Exécuter [le script `scripts/ticket.py`](scripts/ticket.py) avec Python 3.8 ou plus récent. Remplacer `<DOSSIER_DU_SKILL>` par le dossier du `SKILL.md` effectivement chargé. Utiliser le chemin absolu du script et conserver la racine du projet utilisateur comme répertoire de travail pour partager `trader/` entre skills. Sous Windows, employer `python` si `python3` est absent.

## Langue et format de restitution

Répondre en français naturel, avec le tutoiement. Expliquer brièvement les termes techniques utiles ; garder les noms de commandes, chemins, clés JSON, symboles, statuts et paramètres tels quels. Les diagnostics bruts des scripts sont en anglais : en restituer le sens en français sans changer les nombres ni masquer une limite ou un refus. Les prix et budgets restent en USD ; ne pas les convertir en euros sans demande et taux sourcé. Les horaires techniques restent ceux de New York, indiqués explicitement. Si une heure locale est demandée, convertir pour la date concernée, sans décalage fixe avec Paris. Les exemples historiques de l'auteur ne sont pas des résultats personnels de Dan AI Lab ni des données actuelles.

## Validations obligatoires

1. Obtenir un `PASS` du jour de `$trader-risk` sur le ticket exact, identifié par son empreinte.
2. Afficher un seul ticket et recueillir l’accord explicite de l’utilisateur pour cette empreinte. Vérifier de nouveau que le ticket est `READY`, `paper: true` et porte la même empreinte avant de journaliser la réponse, mot pour mot. Un ticket modifié, un accord pour un lot ou une confirmation antérieure impose de reprendre le contrôle et la confirmation.
3. La validation séparée dans le connecteur de simulation externe appartient à l’utilisateur. Ce plugin n’intègre aucun connecteur. Arrêter le flux Codex après le journal local et annoncer « validation externe en attente ». Une permission générale, un `oui` dans le chat ou le statut `approved` n’est pas une validation du connecteur.

```bash
python3 "<DOSSIER_DU_SKILL>/scripts/ticket.py" show --index 1 --json
python3 "<DOSSIER_DU_SKILL>/scripts/ticket.py" approve --index 1 --fingerprint EMPREINTE --reply "REPONSE_EXACTE"
python3 "<DOSSIER_DU_SKILL>/scripts/ticket.py" log
```

## Préparation et journal local

- Lire `trader/orders.json` et `trader/state/risk.json` via `show`. Présenter le symbole, le sens, la quantité, le prix ou le type d’ordre, le stop, l’objectif, la perte au stop et l’empreinte. Montrer les valeurs du ticket, sans appeler l’outil dont le nom figure éventuellement dans les champs historiques.
- En cas de `BLOCKED`, `NOT READY`, `paper: false` ou changement d’empreinte, stopper le flux. Ne jamais écrire un `PASS` à la main. Poursuivre la simulation seulement après un nouveau contrôle de la proposition, avec les paramètres validés par l’utilisateur.
- Journaliser dans `trader/state/broker.json` via `approve` uniquement après la réponse réelle dans la conversation. Passer la réponse comme argument littéral, sans interpolation de shell. `decline --index N` consigne un refus. Un `Not recorded` ne valide rien. Ne pas utiliser `--now` ni `--today` pour confirmer un ticket courant. Réserver ces options aux relectures historiques isolées.
- `result` et `fill` servent uniquement à importer dans le journal une issue de simulation déjà obtenue en dehors du plugin. Pour `result`, exiger une validation externe distincte attestée par l’utilisateur pour le même ticket. Pour `placed` ou `fill`, exiger un résultat de simulation explicite, avec l’identifiant externe si disponible et les quantités et prix réellement fournis. En leur absence, laisser la validation en attente. L’accord local ne constitue jamais une exécution.
- Pour préparer une réduction dans la simulation, lire la position locale `trader/portfolio.json` ou obtenir la quantité simulée auprès de l’utilisateur. `flatten --symbol TSLA --qty 8` remplace les propositions dans `trader/orders.json`. Prévenir avant ce remplacement et repasser par `$trader-risk`. La réduction et les alertes ne ferment aucune position chez un courtier.
- Le JSON conserve le format technique d’origine. Les champs `why` et `plan` restent internes.

## Exemple historique de l’auteur

Le ticket TSLA portait sur 8 actions, stop 358,32 USD, objectif 370,04 USD et perte au prix du stop de 46,88 USD. Après le `PASS`, le journal conserve le mot `oui` tel quel. La validation séparée du connecteur de simulation reste encore à effectuer hors Codex. Aucun ordre ne part du plugin, et une simulation n’établit aucun prix d’exécution réel.

## Sécurité

- Usage éducatif, pas un conseil financier personnalisé. `PASS` indique un contrôle technique.
- Travailler en simulation (`"paper": true`). Le plugin n’installe ni n’appelle aucun connecteur de courtage. Aucun ordre réel ou simulé n’est transmis. Ne jamais demander, lire, afficher ou enregistrer une clé de courtage.
- Avant toute transmission en simulation hors plugin, trois validations restent obligatoires pour le même ticket : `PASS` du jour de `$trader-risk` sur son empreinte exacte, accord explicite de l’utilisateur pour ce seul ticket, puis validation séparée par l’utilisateur dans l’interface du connecteur externe réglé pour demander une autorisation à chaque action. Dans Codex, laisser cette troisième validation en attente.
- Conserver la réponse originale. `oui`, `oui.` et `oui!` sont acceptés, ainsi que les confirmations anglaises prises en charge comme `yes`. Refuser les réponses conditionnelles, ambiguës ou collectives.
- Aucun ordre depuis une surveillance en arrière-plan ou une tâche planifiée. Les instructions du skill n’étendent pas les autorisations de l’environnement hôte.
- Options, marge, vente à découvert et levier désactivés par défaut. L’entrée, la sortie et la taille de ce pack planifient des positions longues.
- Une alerte ou une écriture dans le journal local ne prouve aucune exécution. Le prix d’un stop peut être dépassé.

Adaptation française : Dan AI Lab. Original : [Jake Schincariol](https://github.com/Jakeschincariol/day-trader-skill), licence MIT conservée dans [LICENSE](LICENSE).
