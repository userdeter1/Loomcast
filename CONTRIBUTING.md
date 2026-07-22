# Guide de Contribution - Loomcast

Bienvenue dans le projet Loomcast ! Merci d'adapter ces règles pour contribuer à notre base de code.

## 1. Installation et Exécution des Tests en Local

Avant de soumettre vos modifications, installez le projet avec les dépendances de développement et exécutez la suite de tests :

```bash
# Installation en mode éditable avec les dépendances dev
pip install -e ".[dev]"

# Exécution des tests unitaires par défaut (les tests d'intégration sont ignorés automatiquement)
pytest -v

# Exécution manuelle des tests d'intégration (nécessite un runtime local actif)
pytest -m integration

# Vérification du style de code avec Ruff
ruff check .
```

> **Remarque** : La commande `pytest` sans l'option `-m` ignore automatiquement les tests d'intégration grâce à la configuration `addopts = "-m 'not integration'"` présente dans `pyproject.toml`.


## 2. Convention de Nommage des Branches

Veuillez utiliser un nom de branche explicite lié à l'issue ou la fonctionnalité traitée :

- Format : `issue-<numéro>-<description-courte>`
- Exemple : `issue-1-cache-content-addressed` ou `issue-4-fix-cli-documentation`

## 3. Workflow de Pull Request

- **Branche cible** : Toutes les Pull Requests doivent être ouvertes vers la branche `main`.
- **Passage de la CI** : Le workflow CI (tests unitaires sur Python 3.9 à 3.12 et lint Ruff) doit valider la PR avant qu'elle puisse être fusionnée.
- **Revue de code** : Les PRs sont revues par le mainteneur du projet avant fusion. Si le projet accueille plusieurs contributeurs à l'avenir, un fichier CODEOWNERS pourra être ajouté pour formaliser une revue croisée.
- **Mise à jour de la documentation** : Si une commande CLI est modifiée ou ajoutée, mettez à jour le fichier `README.md`.

## 4. Gestion des Versions et Procédure de Release

Loomcast suit la spécification [Semantic Versioning (SemVer 2.0.0)](https://semver.org/).

Lors de la préparation d'une nouvelle version :
1. Mettez à jour le numéro de version dans `pyproject.toml` (`version = "X.Y.Z"`).
2. Documentez les changements dans `CHANGELOG.md` sous une nouvelle section `[X.Y.Z]`.
3. Soumettez une PR de release vers `main`.
4. Une fois la PR fusionnée, créez et poussez le tag Git correspondant :
   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```
5. **Publication automatique sur TestPyPI** : Le workflow GitHub Action `.github/workflows/release.yml` se déclenche automatiquement pour générer les paquets `sdist` / `wheel`, créer la release sur GitHub et publier les paquets sur **TestPyPI**.
6. **Vérification de l'installation depuis TestPyPI** : Dans un environnement virtuel temporaire isolé (`venv`), testez l'installation du package publié :
   ```bash
   python -m venv .venv-test
   # Sous Linux/macOS : source .venv-test/bin/activate
   # Sous Windows : .venv-test\Scripts\Activate.ps1
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ loomcast
   python -c "import loomcast"
   loomcast --help
   ```
7. **Publication manuelle sur le vrai PyPI** : Une fois la version validée sur TestPyPI, déclenchez le workflow manuellement depuis GitHub (Onglet *Actions* -> *Release* -> *Run workflow* -> cocher `Publish package to production PyPI`).

