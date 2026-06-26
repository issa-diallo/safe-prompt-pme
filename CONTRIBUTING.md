# Contribution

## Principe clé

Chaque ligne de code métier doit être justifiée par un test.

## Workflow recommandé

1. Créer ou mettre à jour un test.
2. Vérifier que le test échoue si le comportement n'existe pas encore.
3. Implémenter le minimum de code.
4. Vérifier que le test passe.
5. Lancer toute la suite de tests.
6. Lancer lint et typage.
7. Mettre à jour la documentation.

## Commandes

```bash
pytest
ruff check .
mypy src
```

## Patterns attendus

- Constantes dans `constants.py`.
- Interfaces dans `interfaces.py`.
- Fonctions pures dès que possible.
- Tests unitaires dans `tests/`.
- Pas de secrets dans le dépôt.
- Pas de vraies données clients dans les fixtures.

## Nommage

- Tokens : `[TYPE_1]`, `[TYPE_2]`, etc.
- Branches : `feat/...`, `fix/...`, `docs/...`, `test/...`.
- Commits : Conventional Commits.
