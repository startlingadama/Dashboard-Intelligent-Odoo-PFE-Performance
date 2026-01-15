# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date


class PfeKpi(models.Model):
    _name = 'pfe.kpi'
    _description = 'Indicateur de Performance PFE'
    _order = 'sequence, name'

    name = fields.Char(string='Nom du KPI', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description')
    
    project_id = fields.Many2one('pfe.project', string='Projet', ondelete='cascade')
    
    kpi_type = fields.Selection([
        ('budget', 'Budget'),
        ('time', 'Temps'),
        ('quality', 'Qualité'),
        ('performance', 'Performance'),
        ('resource', 'Ressources'),
    ], string='Type de KPI', required=True, default='performance')
    
    target_value = fields.Float(string='Valeur Cible')
    current_value = fields.Float(string='Valeur Actuelle', compute='_compute_current_value', store=True)
    unit = fields.Char(string='Unité', default='%')
    
    threshold_warning = fields.Float(string='Seuil d\'avertissement (%)', default=80)
    threshold_danger = fields.Float(string='Seuil de danger (%)', default=100)
    
    status = fields.Selection([
        ('good', 'Bon'),
        ('warning', 'Attention'),
        ('danger', 'Danger'),
    ], string='Statut', compute='_compute_status', store=True)
    
    color = fields.Integer(string='Couleur', compute='_compute_color')
    sequence = fields.Integer(string='Séquence', default=10)
    active = fields.Boolean(string='Actif', default=True)
    
    # Champs pour calcul automatique
    calculation_method = fields.Selection([
        ('manual', 'Manuel'),
        ('budget_consumed', 'Budget Consommé'),
        ('progress', 'Avancement Projet'),
        ('tasks_done', 'Tâches Terminées'),
        ('hours_ratio', 'Ratio Heures'),
        ('delay_days', 'Jours de Retard'),
    ], string='Méthode de calcul', default='manual')

    @api.depends('project_id', 'project_id.budget_percentage', 'project_id.progress', 
                 'project_id.task_done_count', 'project_id.task_count', 'calculation_method')
    def _compute_current_value(self):
        for kpi in self:
            if kpi.calculation_method == 'manual':
                continue
            elif kpi.calculation_method == 'budget_consumed' and kpi.project_id:
                kpi.current_value = kpi.project_id.budget_percentage
            elif kpi.calculation_method == 'progress' and kpi.project_id:
                kpi.current_value = kpi.project_id.progress
            elif kpi.calculation_method == 'tasks_done' and kpi.project_id:
                if kpi.project_id.task_count:
                    kpi.current_value = (kpi.project_id.task_done_count / kpi.project_id.task_count) * 100
                else:
                    kpi.current_value = 0
            elif kpi.calculation_method == 'delay_days' and kpi.project_id:
                if kpi.project_id.date_end:
                    delta = (date.today() - kpi.project_id.date_end).days
                    kpi.current_value = max(0, delta)
                else:
                    kpi.current_value = 0
            else:
                kpi.current_value = 0

    @api.depends('current_value', 'target_value', 'threshold_warning', 'threshold_danger')
    def _compute_status(self):
        for kpi in self:
            if kpi.target_value:
                percentage = (kpi.current_value / kpi.target_value) * 100
                if percentage >= kpi.threshold_danger:
                    kpi.status = 'danger'
                elif percentage >= kpi.threshold_warning:
                    kpi.status = 'warning'
                else:
                    kpi.status = 'good'
            else:
                kpi.status = 'good'

    @api.depends('status')
    def _compute_color(self):
        color_map = {'good': 10, 'warning': 3, 'danger': 1}
        for kpi in self:
            kpi.color = color_map.get(kpi.status, 0)


class PfeKpiReport(models.Model):
    _name = 'pfe.kpi.report'
    _description = 'Rapport KPI PFE'
    _auto = False
    _order = 'project_id'

    project_id = fields.Many2one('pfe.project', string='Projet', readonly=True)
    project_name = fields.Char(string='Nom Projet', readonly=True)
    manager_id = fields.Many2one('res.users', string='Chef de Projet', readonly=True)
    department_id = fields.Many2one('hr.department', string='Département', readonly=True)
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('planning', 'Planification'),
        ('development', 'Développement'),
        ('testing', 'Test'),
        ('delivery', 'Livraison'),
        ('done', 'Terminé'),
        ('cancelled', 'Annulé'),
    ], string='État', readonly=True)
    
    budget_allocated = fields.Float(string='Budget Alloué', readonly=True)
    budget_consumed = fields.Float(string='Budget Consommé', readonly=True)
    budget_percentage = fields.Float(string='% Budget', readonly=True)
    
    progress = fields.Float(string='Avancement (%)', readonly=True)
    task_count = fields.Integer(string='Nb Tâches', readonly=True)
    task_done_count = fields.Integer(string='Tâches Terminées', readonly=True)
    
    date_start = fields.Date(string='Date Début', readonly=True)
    date_end = fields.Date(string='Date Fin', readonly=True)
    
    is_delayed = fields.Boolean(string='En Retard', readonly=True)
    is_budget_exceeded = fields.Boolean(string='Budget Dépassé', readonly=True)

    def init(self):
        self.env.cr.execute("""
            DROP VIEW IF EXISTS pfe_kpi_report;
            CREATE OR REPLACE VIEW pfe_kpi_report AS (
                SELECT
                    p.id AS id,
                    p.id AS project_id,
                    p.name AS project_name,
                    p.manager_id,
                    p.department_id,
                    p.state,
                    p.budget_allocated,
                    COALESCE(p.budget_consumed, 0) AS budget_consumed,
                    CASE WHEN p.budget_allocated > 0 
                         THEN (COALESCE(p.budget_consumed, 0) / p.budget_allocated) * 100 
                         ELSE 0 END AS budget_percentage,
                    COALESCE(p.progress, 0) AS progress,
                    (SELECT COUNT(*) FROM pfe_task t WHERE t.project_id = p.id) AS task_count,
                    (SELECT COUNT(*) FROM pfe_task t WHERE t.project_id = p.id AND t.state = 'done') AS task_done_count,
                    p.date_start,
                    p.date_end,
                    CASE WHEN p.date_end < CURRENT_DATE AND p.state NOT IN ('done', 'cancelled') 
                         THEN true ELSE false END AS is_delayed,
                    CASE WHEN p.budget_allocated > 0 AND COALESCE(p.budget_consumed, 0) > p.budget_allocated 
                         THEN true ELSE false END AS is_budget_exceeded
                FROM pfe_project p
                WHERE p.state != 'cancelled'
            )
        """)
