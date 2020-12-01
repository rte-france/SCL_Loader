# RTE - scd_manager

## Installation

### Installation du package Python

Si la machine cible a accès au réseau RTE et si Python 3.8 y est déjà installé, il suffit d'exécuter la commande
suivante pour installer l'application :

```bash
pip3 install scd_manager -U --user
```

Ou, pour installer une version en particulier (notée ci-dessous `X.Y.Z`), il suffit d'exécuter :

```bash
pip3 install scd_manager==X.Y.Z -U --user
```

**Remarque** :
Ne pas oublier de configurer `pip` pour qu'il recherche les packages sur Nexus. Dans `~/.pip/pip.conf` :

```bash
[global]
index = https://devin-depot.rte-france.com/repository/pypi-all
index-url = https://devin-depot.rte-france.com/repository/pypi-all/simple
trusted-host = devin-depot.rte-france.com
```

Pour vérifier que l'installation est correcte, il suffit d'exécuter la commande suivante :

```bash
pip3 show scd_manager | grep -i version
```

Elle doit afficher la version du projet qui a été installée.

### USAGE

Ouvrir une console dans le répertoire racine du projet
lancer la commande py -3-32 -m venv straton_python32_env
lancer la commande : pip install -r .\requirements-dev.txt
lancer la commande : pip install --editable .   (ne pas oublier le point qui indique le répertoire courant)
Dans Visual Code, faire Ctrl+Shift+P et taper la commande "Python: Discover Tests" afin de détecter les tests unitaires

## Licence

Ce projet est destiné uniquement à un usage interne à RTE.
