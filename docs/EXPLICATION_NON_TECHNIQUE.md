# Explication non technique

## Phrase courte

Safe Prompt PME masque les informations sensibles avant que l'IA les voie.

## Exemple

Message original :

```text
Bonjour, je suis Sophie Martin de ABC Transport.
Pouvez-vous me renvoyer la facture F-2025-1842 de 3 480 €
à sophie.martin@abc-transport.fr ?
```

Message envoyé à l'IA :

```text
Bonjour, je suis [PERSONNE_1] de [ENTREPRISE_1].
Pouvez-vous me renvoyer la facture [FACTURE_1] de [MONTANT_1]
à [EMAIL_1] ?
```

L'IA comprend qu'il faut préparer une réponse, mais elle ne reçoit pas les vraies données.

## Analogie

C'est comme envoyer un document à un assistant en masquant les noms, emails et montants au marqueur noir. L'assistant peut comprendre la tâche, mais il ne connaît pas les vraies identités.

## Différence avec le chiffrement

- Le chiffrement met le message dans une enveloppe fermée pendant le transport.
- L'anonymisation retire les informations sensibles du message avant le transport.

Le meilleur workflow peut combiner les deux.

## Pourquoi c'est utile pour une PME

- Moins de peur d'envoyer des données clients dans l'IA.
- Démonstration facile à comprendre.
- Compatible avec email, documents, CRM, relances et support.
- L'humain garde la validation finale.
