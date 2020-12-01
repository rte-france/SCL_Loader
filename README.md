# RTE - scl_loader

## Installation

### Installation du package Python

Si la machine cible a accès au réseau RTE et si Python 3.8 y est déjà installé, il suffit d'exécuter la commande
suivante pour installer l'application :

```bash
pip3 install scl_loader -U --user
```

Ou, pour installer une version en particulier (notée ci-dessous `X.Y.Z`), il suffit d'exécuter :

```bash
pip3 install scl_loader==X.Y.Z -U --user
```

Pour vérifier que l'installation est correcte, il suffit d'exécuter la commande suivante :

```bash
pip3 show scl_loader | grep -i version
```

Elle doit afficher la version du projet qui a été installée.

### USAGE

Ouvrir une console dans le répertoire racine du projet
lancer la commande py -m venv my_venv
lancer la commande : pip install -r .\requirements-dev.txt
lancer la commande : pip install --editable .   (ne pas oublier le point qui indique le répertoire courant)
Dans Visual Code, faire Ctrl+Shift+P et taper la commande "Python: Discover Tests" afin de détecter les tests unitaires

## Licence

Apache 2.0
