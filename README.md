# Safe Prompt PME

**Safe Prompt PME** est un projet Python open source pour expliquer et prototyper un workflow d'**anonymisation locale avant appel à un LLM**.

Objectif : aider les PME à utiliser l'IA sur des emails, documents, devis, factures ou données CRM **sans envoyer les données sensibles sous leur forme réelle au modèle**.

> Le chiffrement protège le trajet.  
> L'anonymisation protège le contenu avant même qu'il parte vers l'IA.

---

## À quoi sert ce module ?

Ce module sert de **sas de sécurité entre les données métier et le LLM**.

Il permet de :

1. recevoir un texte original : email, note CRM, relance, facture, document ;
2. détecter les informations sensibles ;
3. remplacer ces informations par des étiquettes temporaires ;
4. envoyer uniquement le texte anonymisé au LLM ;
5. récupérer la réponse du LLM ;
6. réinjecter les vraies données localement ;
7. laisser un humain valider avant envoi ou action.

Exemple :

```text
Sophie Martin demande la facture F-2025-1842 de 3 480 €
à sophie.martin@abc-transport.fr.
```

Devient avant envoi à l'IA :

```text
[PERSONNE_1] demande la facture [FACTURE_1] de [MONTANT_1]
à [EMAIL_1].
```

Le LLM comprend la demande, mais ne reçoit pas les vraies données sensibles.

---

## Workflow expliqué à une personne non technique

```text
Email ou document original
        ↓
Détection des données sensibles
        ↓
Remplacement par des étiquettes
        ↓
Texte anonymisé envoyé au LLM
        ↓
Réponse générée par le LLM
        ↓
Réinjection locale des vraies valeurs
        ↓
Validation humaine
        ↓
Envoi ou action métier
```

Phrase simple :

> Avant d'envoyer vos données à l'IA, on masque les noms, emails, téléphones, montants et références sensibles. L'IA travaille sur une version anonymisée. Les vraies informations sont remises uniquement chez vous, avant validation humaine.

---

## Différence avec une société de chiffrement

| Sujet | Chiffrement d'inférence | Anonymisation avant LLM |
|---|---|---|
| Ce qui est protégé | Le transport et les intermédiaires | Le contenu envoyé au modèle |
| Ce que voit le LLM | Souvent le texte réel | Une version masquée |
| Compréhension par une PME | Technique | Très concrète |
| Démo commerciale | Difficile à montrer | Facile à montrer |
| Exemple | Enveloppe scellée | Document avec données masquées |

Les deux approches sont complémentaires :

```text
Anonymisation locale + transport chiffré + validation humaine
```

---

## Cas d'usage PME

- Réponses aux emails clients
- Relances commerciales
- Relances de factures impayées
- Résumés de documents
- Préparation de rendez-vous
- Mise à jour CRM
- Support client assisté
- Préqualification de demandes de devis
- Tri de candidatures RH

---

## Données sensibles à traiter

Le MVP démarre avec des règles simples :

- emails ;
- téléphones français ;
- IBAN français ;
- SIRET ;
- numéros de facture ;
- numéros de devis ;
- montants en euros.

La suite du projet pourra ajouter :

- noms de personnes ;
- noms d'entreprises ;
- adresses postales ;
- numéros de contrat ;
- références client ;
- règles métier spécifiques par secteur.

---

## Étapes du MVP

### MVP 1 — Démo texte / email

Objectif : prouver le workflow sur un email collé dans une interface simple.

Fonctions attendues :

- [x] anonymiser un texte ;
- [x] créer une table locale token -> valeur réelle ;
- [x] réinjecter les vraies valeurs dans une réponse ;
- [x] tester automatiquement les comportements critiques ;
- [ ] ajouter une interface Streamlit ;
- [ ] connecter un premier LLM ;
- [ ] afficher les 4 zones de démonstration : original, données détectées, version LLM, réponse finale.

### MVP 2 — Interface de validation humaine

- [ ] afficher la réponse finale à valider ;
- [ ] permettre d'accepter, modifier ou rejeter ;
- [ ] garder un journal local des décisions sans exposer les données inutilement.

### MVP 3 — Intégration email / CRM

- [ ] lire une boîte email ou un export ;
- [ ] générer un brouillon ;
- [ ] créer une tâche CRM ;
- [ ] envoyer uniquement après validation humaine.

---

## Exigence qualité : chaque ligne de code doit être testable

Règle du projet : **aucun code métier sans test associé**.

Principes :

- écrire les tests avant le code métier quand c'est possible ;
- tester chaque comportement public ;
- éviter les fonctions trop longues ;
- éviter les valeurs magiques ;
- centraliser les constantes ;
- utiliser des interfaces claires ;
- privilégier les fonctions pures ;
- séparer anonymisation, appel LLM, réinjection et validation ;
- ne jamais mélanger logique métier et interface utilisateur.

Commandes qualité :

```bash
pytest
ruff check .
mypy src
```

---

## Patterns de code retenus

| Pattern | Pourquoi |
|---|---|
| `constants.py` | Centraliser les regex et labels |
| `interfaces.py` | Définir les contrats pour anonymiseur et client LLM |
| Fonctions pures | Plus facile à tester |
| Dataclasses immuables | Résultats explicites et sûrs |
| Tests unitaires | Vérifier chaque étape du workflow |
| CI GitHub Actions | Tester automatiquement chaque changement |

---

## Installation locale

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
```

---

## Exemple d'utilisation

```python
from safe_prompt_pme import anonymize_text, deanonymize_text

original = "Bonjour, pouvez-vous envoyer la facture F-2025-1842 de 3 480 € à sophie.martin@abc-transport.fr ?"

result = anonymize_text(original)
print(result.text)
# Bonjour, pouvez-vous envoyer la facture [FACTURE_1] de [MONTANT_1] à [EMAIL_1] ?

llm_answer = "Bien sûr, la facture [FACTURE_1] sera envoyée à [EMAIL_1]."
final_answer = deanonymize_text(llm_answer, result.mapping)
print(final_answer)
```

---

## Limites assumées du MVP

Ce projet n'est pas encore une solution RGPD complète.

Le MVP sert à démontrer :

- le principe ;
- la valeur métier ;
- la faisabilité technique ;
- la différence entre texte original et texte envoyé au LLM.

Pour un usage client réel, il faudra ajouter :

- revue juridique/RGPD ;
- gestion des droits ;
- stockage chiffré du mapping si persistance ;
- suppression automatique des mappings temporaires ;
- journalisation sobre ;
- tests de fuite de données ;
- règles spécifiques par métier.

---

## Licence

MIT — à confirmer selon la stratégie du projet.
