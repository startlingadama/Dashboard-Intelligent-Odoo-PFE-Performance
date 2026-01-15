# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PfeBudgetLine(models.Model):
    _name = 'pfe.budget.line'
    _description = 'Ligne de Budget PFE'
    _order = 'date desc, id desc'

    name = fields.Char(string='Description', required=True)
    project_id = fields.Many2one('pfe.project', string='Projet', required=True, ondelete='cascade')
    
    category = fields.Selection([
        ('personnel', 'Personnel'),
        ('equipment', 'Équipement'),
        ('software', 'Logiciel'),
        ('travel', 'Déplacements'),
        ('consulting', 'Consulting'),
        ('infrastructure', 'Infrastructure'),
        ('other', 'Autre'),
    ], string='Catégorie', required=True, default='other')
    
    amount_planned = fields.Float(string='Montant Planifié')
    amount_spent = fields.Float(string='Montant Dépensé')
    amount_remaining = fields.Float(string='Montant Restant', compute='_compute_amount_remaining', store=True)
    
    date = fields.Date(string='Date', default=fields.Date.today)
    user_id = fields.Many2one('res.users', string='Responsable', default=lambda self: self.env.user)
    
    notes = fields.Text(string='Notes')
    
    account_move_id = fields.Many2one('account.move', string='Pièce Comptable')

    @api.depends('amount_planned', 'amount_spent')
    def _compute_amount_remaining(self):
        for line in self:
            line.amount_remaining = line.amount_planned - line.amount_spent


class PfeBudgetReport(models.Model):
    _name = 'pfe.budget.report'
    _description = 'Rapport Budget PFE'
    _auto = False
    _order = 'project_id, category'

    project_id = fields.Many2one('pfe.project', string='Projet', readonly=True)
    project_name = fields.Char(string='Nom Projet', readonly=True)
    category = fields.Selection([
        ('personnel', 'Personnel'),
        ('equipment', 'Équipement'),
        ('software', 'Logiciel'),
        ('travel', 'Déplacements'),
        ('consulting', 'Consulting'),
        ('infrastructure', 'Infrastructure'),
        ('other', 'Autre'),
    ], string='Catégorie', readonly=True)
    
    total_planned = fields.Float(string='Total Planifié', readonly=True)
    total_spent = fields.Float(string='Total Dépensé', readonly=True)
    total_remaining = fields.Float(string='Total Restant', readonly=True)
    line_count = fields.Integer(string='Nombre de Lignes', readonly=True)

    def init(self):
        self.env.cr.execute("""
            DROP VIEW IF EXISTS pfe_budget_report;
            CREATE OR REPLACE VIEW pfe_budget_report AS (
                SELECT
                    ROW_NUMBER() OVER() AS id,
                    bl.project_id,
                    p.name AS project_name,
                    bl.category,
                    SUM(bl.amount_planned) AS total_planned,
                    SUM(bl.amount_spent) AS total_spent,
                    SUM(bl.amount_planned - bl.amount_spent) AS total_remaining,
                    COUNT(bl.id) AS line_count
                FROM pfe_budget_line bl
                JOIN pfe_project p ON bl.project_id = p.id
                GROUP BY bl.project_id, p.name, bl.category
            )
        """)
