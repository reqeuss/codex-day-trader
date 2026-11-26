# Day Trader FR pour Codex

Onze skills natifs en français pour analyser des actions américaines, préparer des scénarios intraday, les rejouer sur des données historiques et contrôler le risque. Le plugin `day-trader-fr` regroupe ces mêmes skills pour les installer ensemble. Le flux de courtage s’arrête au ticket de simulation et au journal local.

## Deux modes d’utilisation

### Skills natifs dans le projet

Ouvre ce dossier dans Codex, ou lance `codex` depuis sa racine. Dans Codex CLI ou l’extension IDE, tape `$` pour sélectionner un skill. `/skills` affiche aussi la liste dans la CLI. Dans le composeur ChatGPT qui propose les mentions, tape `@` et sélectionne le skill. [Documentation sur les skills](https://learn.chatgpt.com/docs/build-skills)

Exemple à envoyer depuis ce projet, sans réseau ni écriture de watchlist :

```text
$trader-scanner Analyse la cassure de TSLA à 10 h 15, heure de New York, le 19 octobre 2026. Utilise uniquement tests/fixtures/trader-scanner et indique que c’est une relecture historique.
```

### Plugin installable depuis la marketplace locale

Depuis la racine du dossier, exécute ces commandes dans le terminal avec la CLI Codex :

```sh
codex plugin marketplace add .
codex plugin add day-trader-fr@day-trader-fr-local
```

Si ta version de la CLI gère uniquement l’ajout de la marketplace, redémarre l’application ChatGPT pour ordinateur. Ouvre **Plugins**, sélectionne la source **Day Trader FR (local)**, puis installe **Day Trader FR**. Dans une nouvelle session Codex, tape `$` et sélectionne le skill du plugin. Les noms sont préfixés, par exemple `$day-trader-fr:trader-scanner`. [Documentation sur les marketplaces et plugins Codex](https://developers.openai.com/plugins/build/plugins)

Pour distinguer les deux modes, utilise les skills natifs depuis ce dossier ou le plugin depuis un autre projet. Si les deux modes sont actifs pour le même dossier, les skills peuvent apparaître en double dans le sélecteur. Les fichiers d’état `trader/` sont créés dans le projet de travail, où tu lances Codex. Les fixtures de test sont dans ce dossier de distribution. Pour les utiliser avec le plugin depuis un autre projet, fournis leur chemin absolu.

## Les 11 skills

| Mention Codex | Script | Fonction |
| --- | --- | --- |
| `$trader-scanner` | `scan.py` | Filtre l’univers US et construit une liste de surveillance selon les configurations détectées. |
| `$trader-news` | `news.py` | Regroupe les titres, dépôts SEC et mouvements des valeurs surveillées. |
| `$trader-entry` | `entry.py` | Vérifie la confirmation d’une cassure par une bougie clôturée. |
| `$trader-exit` | `exit.py` | Calcule un stop, un objectif et une heure limite de sortie. |
| `$trader-timemachine` | `timemachine.py` | Rejoue les séances historiques et simule la fin de séance. |
| `$trader-budget` | `size.py` | Dimensionne la position selon le budget et la perte maximale configurés. |
| `$trader-risk` | `check.py` | Émet `PASS` ou `BLOCK` pour l’empreinte du ticket. |
| `$trader-broker` | `ticket.py` | Prépare un ticket et consigne une réponse explicite en simulation. |
| `$trader-alerts` | `alerts.py` | Vérifie les seuils et heures fixés dans les règles d’alerte. |
| `$trader-analyst` | `facts.py` | Compare des résultats et marges publiés auprès de la SEC. |
| `$trader-pelosi` | `ptr.py` | Lit les déclarations publiques PTR et distingue dépôt et transaction. |

## Arborescence

| Chemin | Contenu |
| --- | --- |
| `.agents/skills/trader-*/` | Sources natives. Chaque dossier contient `SKILL.md`, `scripts/`, `agents/openai.yaml`, la licence MIT et, selon le skill, des exemples dans `references/`. |
| `.agents/plugins/marketplace.json` | Catalogue local `day-trader-fr-local`. |
| `plugins/day-trader-fr/` | Plugin autonome avec `plugin.json`, `.codex-plugin/plugin.json` et les 11 skills dans `skills/`. |
| `tests/` | Tests unitaires et données historiques enregistrées. |
| `tools/sync_plugin_skills.py` | Copie les skills natifs vers le plugin après une mise à jour. |

Après une modification d’un skill, exécute `python3 tools/sync_plugin_skills.py` depuis la racine pour mettre à jour le plugin. Si un fichier a été retiré du skill natif, retire aussi sa copie dans le plugin. La suite teste l’identité des deux distributions.

## Les trois validations du courtier

1. `$trader-risk` doit produire un `PASS` du jour, heure de New York, pour l’empreinte du ticket exact.
2. L’utilisateur confirme explicitement ce seul ticket. Le script journalise la réponse mot pour mot en mode simulation, puis affiche la validation externe en attente. Un `oui` conditionnel ou collectif est refusé.
3. La confirmation distincte dans un connecteur de simulation externe appartient à l’utilisateur. Le connecteur doit demander une autorisation à chaque action. Cette validation ne se fait pas dans le plugin.

Le plugin ne déclare aucun connecteur de courtage ni hook. Il ne demande aucune clé API et n’envoie aucun ordre. Le journal peut importer une issue de simulation déjà obtenue en dehors du plugin sur la base de faits fournis par l’utilisateur. Le fichier `claude_desktop_config.example.json` conservé dans les références du courtier est un exemple de l’amont, inactif dans Codex.

## Tests hors ligne

Python 3.8 ou plus récent suffit pour les scripts et la suite de tests. Sous Windows, remplace `python3` par `python` si nécessaire. Pour convertir les PDF du House Clerk, `trader-pelosi` peut utiliser `pdftotext` de Poppler. Le parseur accepte aussi le texte déjà extrait.

```sh
python3 -m unittest discover -s tests -v
```

Les outils de marché disposent de leurs options `--offline` pour les données locales. Les sous-commandes, positions d’options et formats sont dans les `SKILL.md` et l’aide `--help`. Les commandes en ligne peuvent consulter des sources publiques et écrire sous `trader/`. Pour la SEC en ligne, l’utilisateur renseigne lui-même un User-Agent de contact dans `trader/config.json` ou `SEC_USER_AGENT`.

## Limites à connaître

- Couverture des actions américaines et des montants en USD. Les heures de marché sont indiquées en heure de New York. Le calendrier NYSE intégré à l’amont couvre 2026 et 2027.
- Les cours publics peuvent être retardés. Les alertes informent. Les scénarios rééchantillonnent un historique et les prix au stop restent des hypothèses de calcul.
- Les chiffres des fixtures sont historiques. Les outils servent à l’analyse et à la simulation éducatives.

## Audit et provenance

Adaptation Codex de [dan-ai-lab/day-trader-fr](https://github.com/dan-ai-lab/day-trader-fr) d’après le [commit `756e4f5`](https://github.com/dan-ai-lab/day-trader-fr/commit/756e4f53cc1e79032ea7e1961c9e5589ae6477e0). Jake Schincariol a créé le [projet d’origine](https://github.com/Jakeschincariol/day-trader-skill) et Dan AI Lab a réalisé l’adaptation française. La [licence MIT](LICENSE) d’origine est incluse.

| Script audité | Entrées, sorties et dépendances |
| --- | --- |
| `scan.py` | Listes Nasdaq Trader, séries Yahoo ou fixtures. Classement des symboles, scan quotidien, cassures de plage d’ouverture et écriture de `universe.txt` ou `watchlist.json`. |
| `news.py` | Flux Yahoo RSS et SEC, mouvements Yahoo, filtres temporels et dédoublonnage dans le fichier d’état. |
| `entry.py` | Bougies en ligne ou locales. Écarte la bougie en cours et enregistre le déclenchement dans `entry.json`. |
| `exit.py` | Lit le déclenchement ou le prix saisi. Peut lire les bougies pour l’ATR. Calcule les niveaux et produit `plan.json`. |
| `timemachine.py` | Lit `plan.json` et jusqu’à 60 jours de bougies. Rejeux historiques et simulation reproductible, avec rapport JSON optionnel. |
| `size.py` | Lit le plan, la configuration, les cours éventuels et le portefeuille local. Écrit les propositions sous `orders.json`. |
| `check.py` | Contrôles locaux de session, capital, stops, risque, positions et journal. Écrit les verdicts et empreintes sous `state/risk.json`. |
| `ticket.py` | Lit et écrit tickets, portefeuille et journal locaux. Validation du jour, refus des réponses conditionnelles, empreinte du ticket affiché et garde de simulation. Aucun appel réseau. |
| `alerts.py` | Lit les prix publics Yahoo/Stooq ou des fixtures. Gère les règles, leur état et les cours partagés par les autres skills. |
| `facts.py` | SEC XBRL et métadonnées des dépôts, ou données locales. Calcule comparaisons et marges, puis exporte les métriques sur demande. |
| `ptr.py` | Index et rapports du House Clerk ou fichiers locaux. Parse le texte et calcule les délais de publication. `pdftotext` est optionnel pour les PDF. |

L’amont ne comporte aucun module Python partagé à installer. Les scripts sont autonomes et le flux partage des fichiers sous `trader/`. Le chargeur commun `tests/_load.py` et les assertions de distribution pointent vers la nouvelle arborescence. Les dix scripts hors courtage et les fixtures sont conservés à l’identique. `ticket.py` conserve le format d’origine, les contrôles du risque et le journal, avec des messages adaptés à Codex et une vérification de l’empreinte présentée au moment de l’accord.
