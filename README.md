<p align="center">
  <img src="static/description/icon.png" width="128" alt="PFE Performance Dashboard Logo">
</p>

<h1 align="center">PFE Performance Dashboard</h1>

<p align="center">
  <a href="https://www.odoo.com/">
    <img src="https://img.shields.io/badge/Odoo-17.0-875A7B.svg?style=for-the-badge&logo=odoo&logoColor=white" alt="Odoo">
  </a>
  <a href="https://www.gnu.org/licenses/lgpl-3.0.en.html">
    <img src="https://img.shields.io/badge/License-LGPL--3-blue.svg?style=for-the-badge&logo=gnu&logoColor=white" alt="License">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  </a>
</p>

<br />

## <img src="https://api.iconify.design/material-symbols:info-outline.svg?color=%23875a7b" width="24" height="24"> Présentation

Le module **PFE Performance Dashboard** est une solution complète développée pour Odoo 17 permettant le suivi dynamique et en temps réel des performances des projets PFE. Il offre aux chefs de projets et à la direction une visibilité à 360° sur l'avancement technique et financier.

## <img src="https://api.iconify.design/material-symbols:featured-play-list-outline.svg?color=%23875a7b" width="24" height="24"> Fonctionnalités Clés

- **Gestion de Projet Avancée** : Suivi des cycles de vie (Brouillon ➜ Planification ➜ Développement ➜ Test ➜ Livraison ➜ Terminé).
- **Contrôle Budgétaire** : Comparaison en temps réel entre le budget alloué et consommé avec calcul automatique du reste à dépenser.
- **Tableaux de Bord Interactifs** : Visualisation via des vues Kanban, Gantt et Graphiques pour une analyse rapide des KPIs.
- **Indicateurs de Performance (KPIs)** : Monitoring précis de l'avancement (%) et de la santé financière des projets.
- **Système d'Alertes Intelligent** : Notifications automatiques en cas de dépassement de budget ou de retard sur les échéances.

## <img src="https://api.iconify.design/material-symbols:psychology-outline.svg?color=%23875a7b" width="24" height="24"> Intelligence Artificielle

Le module intègre une couche de Machine Learning pour transformer les données historiques en outils d'aide à la décision :

- **Prédiction des Alertes** : Algorithmes prédictifs analysant les tendances passées pour anticiper les risques de dérive budgétaire ou de retard de livraison.
- **Recommandations de Gestion** : Moteur de recommandation suggérant des actions correctives (réallocation de ressources, ajustement de planning) pour optimiser la réussite des projets.
- **Analyse de Santé des Projets** : Score de santé global calculé par ML basé sur la corrélation entre les multiples indicateurs du projet.

## <img src="https://api.iconify.design/material-symbols:terminal-outline.svg?color=%23875a7b" width="24" height="24"> Spécifications Techniques

Ce module s'intègre nativement avec l'écosystème Odoo et utilise les modèles suivants :

- `pfe.project` : Cœur du système gérant les métadonnées et indicateurs du projet.
- `pfe.budget.line` : Détail des lignes budgétaires.
- `pfe.kpi` : Définition et calcul des indicateurs clés.
- `pfe.task` & `pfe.milestone` : Gestion granulaire de l'exécution.

### Dépendances

- `base`, `project`, `hr_timesheet`, `account`, `mail`

## <img src="https://api.iconify.design/material-symbols:download-for-offline-outline.svg?color=%23875a7b" width="24" height="24"> Procédure d'Installation

1. Copiez le dossier `pfe_performance` dans votre répertoire `addons`.
2. Redémarrez votre serveur Odoo.
3. Activez le **Mode Développeur**.
4. Allez dans **Applications** > **Mettre à jour la liste des applications**.
5. Recherchez "PFE Performance Dashboard" et cliquez sur **Installer**.

## <img src="https://api.iconify.design/material-symbols:folder-open-outline.svg?color=%23875a7b" width="24" height="24"> Structure du Projet

```text
pfe_performance/
├── data/               # Données de configuration et séquences
├── models/             # Logique métier (Projets, Budgets, KPIs)
├── security/           # Droits d'accès et règles de record
├── static/             # Assets CSS, JS et Images pour le Dashboard
├── views/              # Définition des interfaces (XML)
├── __init__.py
└── __manifest__.py     # Métadonnées du module
```

## <img src="https://api.iconify.design/material-symbols:alternate-email.svg?color=%23875a7b" width="24" height="24" alt="Contact"> Contact Développeur

**Adama COULIBALY**  
📧 [startlingadama@gmail.com](mailto:startlingadama@gmail.com)  
*Ingénieur en Intelligence Artificielle*

---

<p align="center">© 2026. Tous droits réservés.</p>

