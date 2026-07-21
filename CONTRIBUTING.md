# Guide de Contribution - Loomcast

Bienvenue dans le projet Loomcast ! Merci d'adapter ces règles pour contribuer à notre base de code.

## 1. Installation et Exécution des Tests en Local

Avant de soumettre vos modifications, installez le projet avec les dépendances de développement et exécutez la suite de tests :

```bash
# Installation en mode éditable avec les dépendances dev
pip install -e ".[dev]"

# Exécution des tests pytest
pytest -v

# Vérification du style de code avec Ruff
ruff check .
```

## 2. Convention de Nommage des Branches

Veuillez utiliser un nom de branche explicite lié à l'issue ou la fonctionnalité traitée :

- Format : `issue-<numéro>-<description-courte>`
- Exemple : `issue-1-cache-content-addressed` ou `issue-4-fix-cli-documentation`

## 3. Workflow de Pull Request

- **Branche cible** : Toutes les Pull Requests doivent être ouvertes vers la branche `main`.
- **Passage de la CI** : Le workflow CI (tests unitaires sur Python 3.9 à 3.12 et lint Ruff) doit valider la PR avant qu'elle puisse être fusionnée.
- **Revue de code** : Chaque PR requiert l'approbation d'un autre développeur (revue croisée CODEOWNERS).
- **Mise à jour de la documentation** : Si une commande CLI est modifiée ou ajoutée, mettez à jour le fichier `README.md`.
