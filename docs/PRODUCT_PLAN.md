# Plan produit — Safe Prompt PME

## Vision

Créer une couche Python simple et explicable qui protège les données sensibles avant utilisation d'un LLM dans les workflows PME.

## Proposition de valeur

> Automatiser les emails, documents, relances et données CRM avec l'IA, sans exposer inutilement les données clients.

## Public cible

- dirigeants de PME ;
- responsables administratifs ;
- commerciaux ;
- équipes support ;
- consultants IA/automatisation.

## Modules prévus

### 1. `anonymizer`

Rôle : transformer le texte original en texte anonymisé.

Entrée : texte original.  
Sortie : texte anonymisé + mapping local.

### 2. `deanonymizer`

Rôle : remettre les vraies valeurs dans la réponse générée.

Entrée : réponse du LLM + mapping local.  
Sortie : réponse finale à valider.

### 3. `interfaces`

Rôle : définir les contrats entre les briques.

Exemples :

- anonymiseur ;
- client LLM ;
- validateur humain ;
- connecteur email ;
- connecteur CRM.

### 4. `rules`

Rôle : porter les règles françaises et métier.

Exemples :

- SIRET ;
- IBAN ;
- TVA intracommunautaire ;
- facture ;
- devis ;
- commande ;
- téléphone français ;
- montant en euros.

### 5. `ui`

Rôle : interface de démonstration.

Option MVP : Streamlit.

## Démo MVP recommandée

Interface avec 4 panneaux :

1. **Email original**
2. **Données détectées**
3. **Version envoyée à l'IA**
4. **Réponse finale après réinjection**

## Critères d'acceptation du MVP 1

- [ ] Un utilisateur colle un email.
- [ ] L'application affiche la version anonymisée.
- [ ] L'application affiche la table de correspondance localement.
- [ ] L'application envoie uniquement la version anonymisée au LLM.
- [ ] L'application réinjecte les vraies valeurs dans la réponse.
- [ ] L'utilisateur peut valider ou modifier avant envoi.
- [ ] Tous les comportements critiques sont couverts par des tests.

## Règles d'architecture

- La table de mapping ne part jamais au LLM.
- Le client LLM ne reçoit que du texte anonymisé.
- L'interface utilisateur ne contient pas de logique d'anonymisation.
- Les constantes et regex sont centralisées.
- Les intégrations externes passent par des interfaces.
- Les fonctions métier doivent rester testables sans réseau.

## Definition of Done

Une fonctionnalité est terminée uniquement si :

- [ ] elle a des tests unitaires ;
- [ ] les tests passent ;
- [ ] `ruff check .` passe ;
- [ ] `mypy src` passe ;
- [ ] la documentation est mise à jour ;
- [ ] aucun secret ni donnée client réelle n'est commitée.
