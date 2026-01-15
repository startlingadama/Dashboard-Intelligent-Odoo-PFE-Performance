# -*- coding: utf-8 -*-
{
    'name': 'PFE Performance Dashboard',
    'version': '17.0.1.0.0',
    'category': 'Project',
    'summary': 'Dashboard interactif de suivi des performances projets PFE',
    'description': """
        Module Odoo pour le suivi en temps réel des performances des projets:
        - Suivi avancement, budget, délais
        - KPIs et indicateurs financiers
        - Visualisation interactive (Kanban, Gantt, Graph)
        - Alertes et notifications automatiques
    """,
    'author': 'Adama COULIBALY',
    'email': 'startlingadama@gmail.com',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'project',
        'hr_timesheet',
        'account',
        'mail',
    ],
    'data': [
        'security/pfe_security.xml',
        'security/ir.model.access.csv',
        'views/pfe_project_views.xml',
        'views/pfe_kpi_views.xml',
        'views/pfe_dashboard_views.xml',
        'views/pfe_menu.xml',
        'data/pfe_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pfe_performance/static/src/css/dashboard.css',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
