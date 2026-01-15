# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date, timedelta


class PfeProject(models.Model):
    _name = 'pfe.project'
    _description = 'Projet PFE avec suivi de performance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, date_start desc'

    name = fields.Char(string='Nom du Projet', required=True, tracking=True)
    code = fields.Char(string='Code Projet', required=True, copy=False)
    description = fields.Html(string='Description')
    
    # Dates
    date_start = fields.Date(string='Date de début', required=True, tracking=True)
    date_end = fields.Date(string='Date de fin prévue', required=True, tracking=True)
    date_end_actual = fields.Date(string='Date de fin réelle', tracking=True)
    
    # Responsables
    manager_id = fields.Many2one('res.users', string='Chef de Projet', tracking=True)
    team_ids = fields.Many2many('res.users', string='Équipe Projet')
    department_id = fields.Many2one('hr.department', string='Département')
    partner_id = fields.Many2one('res.partner', string='Client')
    
    # État et phase
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('planning', 'Planification'),
        ('development', 'Développement'),
        ('testing', 'Test'),
        ('delivery', 'Livraison'),
        ('done', 'Terminé'),
        ('cancelled', 'Annulé'),
    ], string='État', default='draft', tracking=True, group_expand='_expand_states')
    
    priority = fields.Selection([
        ('0', 'Basse'),
        ('1', 'Normale'),
        ('2', 'Haute'),
        ('3', 'Urgente'),
    ], string='Priorité', default='1')
    
    color = fields.Integer(string='Couleur')
    
    # Budget
    budget_allocated = fields.Float(string='Budget Alloué', tracking=True)
    budget_consumed = fields.Float(string='Budget Consommé', compute='_compute_budget_consumed', store=True)
    budget_remaining = fields.Float(string='Budget Restant', compute='_compute_budget_remaining', store=True)
    budget_percentage = fields.Float(string='% Budget Consommé', compute='_compute_budget_percentage')
    
    # Avancement
    progress = fields.Float(string='Avancement (%)', compute='_compute_progress', store=True)
    
    # Relations
    task_ids = fields.One2many('pfe.task', 'project_id', string='Tâches')
    milestone_ids = fields.One2many('pfe.milestone', 'project_id', string='Jalons')
    budget_line_ids = fields.One2many('pfe.budget.line', 'project_id', string='Lignes de Budget')
    kpi_ids = fields.One2many('pfe.kpi', 'project_id', string='KPIs')
    
    # Compteurs
    task_count = fields.Integer(string='Nombre de Tâches', compute='_compute_task_count')
    task_done_count = fields.Integer(string='Tâches Terminées', compute='_compute_task_count')
    milestone_count = fields.Integer(string='Nombre de Jalons', compute='_compute_milestone_count')
    
    # Alertes
    is_budget_exceeded = fields.Boolean(string='Budget Dépassé', compute='_compute_alerts', store=True)
    is_delayed = fields.Boolean(string='En Retard', compute='_compute_alerts', store=True)
    alert_message = fields.Char(string='Message d\'alerte', compute='_compute_alerts')

    @api.model
    def _expand_states(self, states, domain, order):
        """Retourne tous les états pour la vue Kanban"""
        return [key for key, val in type(self).state.selection]

    @api.depends('task_ids', 'task_ids.state')
    def _compute_task_count(self):
        for project in self:
            project.task_count = len(project.task_ids)
            project.task_done_count = len(project.task_ids.filtered(lambda t: t.state == 'done'))

    @api.depends('milestone_ids')
    def _compute_milestone_count(self):
        for project in self:
            project.milestone_count = len(project.milestone_ids)

    @api.depends('budget_line_ids', 'budget_line_ids.amount_spent')
    def _compute_budget_consumed(self):
        for project in self:
            project.budget_consumed = sum(project.budget_line_ids.mapped('amount_spent'))

    @api.depends('budget_allocated', 'budget_consumed')
    def _compute_budget_remaining(self):
        for project in self:
            project.budget_remaining = project.budget_allocated - project.budget_consumed

    @api.depends('budget_allocated', 'budget_consumed')
    def _compute_budget_percentage(self):
        for project in self:
            if project.budget_allocated:
                project.budget_percentage = (project.budget_consumed / project.budget_allocated) * 100
            else:
                project.budget_percentage = 0

    @api.depends('task_ids', 'task_ids.progress')
    def _compute_progress(self):
        for project in self:
            tasks = project.task_ids
            if tasks:
                project.progress = sum(tasks.mapped('progress')) / len(tasks)
            else:
                project.progress = 0

    @api.depends('budget_allocated', 'budget_consumed', 'date_end')
    def _compute_alerts(self):
        today = date.today()
        for project in self:
            project.is_budget_exceeded = project.budget_consumed > project.budget_allocated if project.budget_allocated else False
            project.is_delayed = project.date_end and project.date_end < today and project.state not in ['done', 'cancelled']
            
            alerts = []
            if project.is_budget_exceeded:
                alerts.append('⚠️ Budget dépassé!')
            if project.is_delayed:
                alerts.append('⚠️ Projet en retard!')
            project.alert_message = ' | '.join(alerts) if alerts else ''

    def action_start_planning(self):
        self.write({'state': 'planning'})

    def action_start_development(self):
        self.write({'state': 'development'})

    def action_start_testing(self):
        self.write({'state': 'testing'})

    def action_start_delivery(self):
        self.write({'state': 'delivery'})

    def action_done(self):
        self.write({'state': 'done', 'date_end_actual': date.today()})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_view_tasks(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tâches du Projet',
            'res_model': 'pfe.task',
            'view_mode': 'tree,form,kanban',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def action_view_milestones(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Jalons du Projet',
            'res_model': 'pfe.milestone',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }


class PfeTask(models.Model):
    _name = 'pfe.task'
    _description = 'Tâche de Projet PFE'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, date_deadline'

    name = fields.Char(string='Nom de la Tâche', required=True)
    description = fields.Html(string='Description')
    project_id = fields.Many2one('pfe.project', string='Projet', required=True, ondelete='cascade')
    milestone_id = fields.Many2one('pfe.milestone', string='Jalon', domain="[('project_id', '=', project_id)]")
    
    user_id = fields.Many2one('res.users', string='Assigné à', tracking=True)
    
    date_start = fields.Date(string='Date de début')
    date_deadline = fields.Date(string='Échéance', tracking=True)
    
    state = fields.Selection([
        ('todo', 'À faire'),
        ('in_progress', 'En cours'),
        ('review', 'En revue'),
        ('done', 'Terminé'),
        ('cancelled', 'Annulé'),
    ], string='État', default='todo', tracking=True, group_expand='_expand_task_states')
    
    priority = fields.Selection([
        ('0', 'Basse'),
        ('1', 'Normale'),
        ('2', 'Haute'),
        ('3', 'Urgente'),
    ], string='Priorité', default='1')
    
    progress = fields.Float(string='Avancement (%)', default=0)
    hours_planned = fields.Float(string='Heures Planifiées')
    hours_spent = fields.Float(string='Heures Passées', compute='_compute_hours_spent', store=True)
    
    timesheet_ids = fields.One2many('pfe.timesheet', 'task_id', string='Feuilles de temps')
    
    sequence = fields.Integer(string='Séquence', default=10)
    color = fields.Integer(string='Couleur')
    
    is_critical = fields.Boolean(string='Tâche Critique', compute='_compute_is_critical', store=True)

    @api.model
    def _expand_task_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.depends('timesheet_ids', 'timesheet_ids.hours')
    def _compute_hours_spent(self):
        for task in self:
            task.hours_spent = sum(task.timesheet_ids.mapped('hours'))

    @api.depends('date_deadline', 'state')
    def _compute_is_critical(self):
        today = date.today()
        for task in self:
            if task.date_deadline and task.state not in ['done', 'cancelled']:
                days_remaining = (task.date_deadline - today).days
                task.is_critical = days_remaining <= 3
            else:
                task.is_critical = False

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_review(self):
        self.write({'state': 'review'})

    def action_done(self):
        self.write({'state': 'done', 'progress': 100})

    def action_cancel(self):
        self.write({'state': 'cancelled'})


class PfeMilestone(models.Model):
    _name = 'pfe.milestone'
    _description = 'Jalon de Projet PFE'
    _order = 'date_target'

    name = fields.Char(string='Nom du Jalon', required=True)
    project_id = fields.Many2one('pfe.project', string='Projet', required=True, ondelete='cascade')
    date_target = fields.Date(string='Date Cible', required=True)
    date_achieved = fields.Date(string='Date Atteinte')
    
    state = fields.Selection([
        ('pending', 'En attente'),
        ('achieved', 'Atteint'),
        ('missed', 'Manqué'),
    ], string='État', default='pending')
    
    task_ids = fields.One2many('pfe.task', 'milestone_id', string='Tâches')
    
    is_overdue = fields.Boolean(string='En retard', compute='_compute_is_overdue', store=True)

    @api.depends('date_target', 'state')
    def _compute_is_overdue(self):
        today = date.today()
        for milestone in self:
            milestone.is_overdue = milestone.date_target < today and milestone.state == 'pending'


class PfeTimesheet(models.Model):
    _name = 'pfe.timesheet'
    _description = 'Feuille de temps PFE'
    _order = 'date desc'

    task_id = fields.Many2one('pfe.task', string='Tâche', required=True, ondelete='cascade')
    project_id = fields.Many2one('pfe.project', string='Projet', related='task_id.project_id', store=True)
    user_id = fields.Many2one('res.users', string='Utilisateur', default=lambda self: self.env.user, required=True)
    date = fields.Date(string='Date', default=fields.Date.today, required=True)
    hours = fields.Float(string='Heures', required=True)
    description = fields.Text(string='Description')
