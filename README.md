# Calculateur de Drop Dofus Rétro

Ce dépôt contient `test-cody.py`, un petit utilitaire graphique pour estimer les probabilités de drop sur Dofus Rétro.

## Installation

Python 3 est nécessaire. Depuis ce dossier, installez les dépendances du projet en mode développement&nbsp;:

```bash
python -m pip install -e .
```

Pour générer un exécutable Windows, installez également `pyinstaller` :

```bash
python -m pip install pyinstaller
```

## Utilisation avec PyCharm

1. Ouvrez PyCharm et choisissez **Open** pour sélectionner le dossier du projet.
2. Assurez-vous que l'interpréteur Python configuré dispose des dépendances ci-dessus.
3. Ouvrez `test-cody.py` puis exécutez le script (clic droit &rarr; **Run** ou via la flèche verte).

L'interface s'ouvrira et vous pourrez faire vos calculs de drop.

## Lancement depuis un terminal

Si vous préférez exécuter le programme sans IDE, placez un terminal dans ce répertoire puis lancez :

```bash
python test-cody.py
```

L'interface graphique s'ouvrira et vous permettra de réaliser vos calculs.


## Génération d'un exécutable Windows

Après avoir installé `pyinstaller`, lancez depuis un terminal dans le dossier du projet :

```bash
pyinstaller --onefile --windowed test-cody.py
```

Le programme sera compilé dans `dist/test-cody.exe`. Vous pourrez alors lancer l'application sans avoir Python installé sur la machine cible.

