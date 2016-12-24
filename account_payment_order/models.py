# -*- coding: utf-8 -*-

from openerp import models, fields, api, _, osv
from openerp.exceptions import except_orm
import math
from datetime import datetime
from dateutil import relativedelta


'''
Account Payment Order form   
'''
class account_payment_order(models.Model):
    _name = 'account.payment.order'
    _rec_name = 'partner_name'


    supplier_id = fields.Many2one('res.partner', 'Supplier', domain=[('supplier', '=', 'true')])
    date = fields.Date('Date', required = True)
    partner_name = fields.Char('Name', required=True)
    amount_text = fields.Char('Amount Text')
    cheque_no = fields.Char('Cheque No')
    payment_type = fields.Selection([('atm', 'ATM'), ('cash', 'Cash'), ('transfer', 'Transfer'), ('cheque', 'Cheque'),], 'Payment Type', required= True, default='cash')
    journal_id = fields.Many2one('account.journal', 'Payment Method', domain=[('type', 'in', ('bank', 'cash'))], required= True)
    cr_account_id = fields.Many2one('account.account', 'Credit account', required=True, domain=[('type', '=', 'payable')])
    note = fields.Char('Notes', required=True)
    state = fields.Selection([('draft', 'Draft'), ('cancel', 'Cancel'), ('post', 'Post')], string='Status', default='draft')
    number = fields.Char('Number', default='/')
    payment_line = fields.One2many('account.payment.order.line', 'account_payment_order_no', 'Payment Lines')
    total_amount = fields.Float('Total Aomunt', help='Summation of lines amount',  compute='_calc_all', store=True,multi=True)
    n_hidden = fields.Char('Number', default='/')

    def _create_payment_line(self, sup_obj):

        values = {}
        payment_line_obj = self.env['account.payment.order.line']
        values = {
                'memo': 'payment order line created',
                'amount': 0.0,
                'dr_account_id': sup_obj.property_account_receivable.id
        }
        obj = payment_line_obj.create(values)
        return obj
    
    '''
    Return the period as per payment order date 
    '''
    def _get_je_period(self, p_date):
    	p2_date = datetime.strptime(p_date, '%Y-%m-%d')
    	p3_date = p2_date.date()
    	peroid_obj = self.env['account.period']
    	period = peroid_obj.search([('date_start', '<=', str(p3_date)), ('date_stop', '>=', str(p3_date)) ])
    	return period.id
    	

    '''
    Onchange method which chnage partner name on change of supplier 
    '''
    @api.multi
    def onchange_supplier_id(self, supplier_id):
        n_payment_line = []
        sup_obj =  self.env['res.partner'].search([('id', '=', supplier_id)])
        if sup_obj:
            n_payment_line = self._create_payment_line(sup_obj)

        return {'value': {
            'partner_name': sup_obj.name,
            'payment_line': n_payment_line,
            'total_amount': 0.0
        }}  


    '''
	Calculate the total amount from payment order lines
    '''
    @api.depends('payment_line')
    def _calc_all(self):
    	total_amt = 0.0
        for payment in self.payment_line:
            total_amt += payment.amount
        self.total_amount = total_amt


    '''
    Change the Total amount on onchange of order to get the correct values. Onchange does not get the last payment order line so we write the lofic in dependss
    '''
    @api.multi
    def onchange_payment_line(self):
        total_amt =0.0
    	if self.payment_line:
    		lines = self.payment_line
    		for each in lines:
    			total_amt+=each.amount
        return {'value': {
            'total_amount': 0.0
        }}


    '''
    Draft button changed to status to draft 
    '''
    @api.multi
    def action_set_to_draft(self):
        self.write({'state': 'draft'})
        return True

    '''
    Cancel button changed to status to cancel  
    '''
    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel', 'number': '/'})
        return True

        '''
    Create Journal Entry on post button  
    '''
    def _create_journal_entry(self):
        # period_id = self.env['account.move.line']._get_period()
        period_id = self._get_je_period(self.date)
        account_move={
            'name': '/',
            'journal_id': self.journal_id.id,
            'date': self.date,
            'narration': self.note,
            'ref': self.partner_name,
            'period_id': period_id
            }
        move_id = self.env['account.move'].create(account_move)
        account_move_line=[]
        move_line = {
            'name': str(self.partner_name),
            'date': self.date, 
            'partner_id': self.supplier_id.id,
            'account_id': self.cr_account_id.id,
            'journal_id': self.journal_id.id,
            'credit': round(self.total_amount),
            'debit': round(0),
            'move_id': move_id.id,
            'period_id': period_id
        }
        self.env['account.move.line'].create(move_line)
        lines = self.payment_line
        for payment in lines:
            self.env['account.move'].browse(payment)
            move_line={
                'name': str(payment.memo),
                'date': self.date, 
                'partner_id': self.supplier_id.id,
                'account_id': payment.dr_account_id.id,
                'journal_id': self.journal_id.id,
                'credit': round(0), 
                'debit': round(payment.amount),
                'move_id': move_id.id,
                'period_id': period_id
            }

            self.env['account.move.line'].create(move_line)
        return True
        '''
    Post button changed to status to post and generate generate entry  
    '''
    @api.one
    def action_post(self):
        res = self.write({})
        if self.payment_line:
            if self.n_hidden != '/':
                self.write({'state': 'post', 'number': self.n_hidden})
            elif self.number == '/':
                self.write({'state': 'post', 'number': self.env['ir.sequence'].get('account.payment.order'),
                    'n_hidden': self.env['ir.sequence'].get('account.payment.order')
            })
            else:
                self.write({'state': 'post'})
        else:
            raise except_orm(_('Bad Input!'), _('There must be at least one Account Payment Order Line.'))
        self._create_journal_entry()
        return True
        '''
    Override the create button  
    '''
    @api.model
    def create(self, values):
        res = super(account_payment_order, self).create(values)
        if not res.payment_line:
            raise except_orm(_('Bad Input!'), _('There must be at least one Account Payment Order Line.'))
        line_obj = self.env['account.payment.order.line'].search([('account_payment_order_no', '=', self.id)])
        
        if self.payment_line:
            if 'number' in values:
                order_num = values['number']
                values.update({
                    'number_hidden': order_num,
            })
        return super(account_payment_order, self).create(values)

    '''
    SQL constraints on account payment order   
    '''
    _sql_constraints = [
        ('check_layers',
         'check (len(payment_line)>0)',
         'Payment Line should be greater than 0.'
         )]

    '''
    Override unlink method   
    '''
    @api.one
    def unlink(self):
        if self.state not in ('draft'):
            raise Warning(_('You cannot delete a Record which is in Post/Confirm state.'))
        return super(account_payment_order, self).unlink()
account_payment_order()


'''
Account Payment Order Lines, Account order can have multiple order lines  
'''
class account_payment_order_line(models.Model):
    _name = 'account.payment.order.line'
    _rec_name = 'account_payment_order_no'
    
    memo  = fields.Char('Memo ', default='/', required=True)
    dr_account_id = fields.Many2one('account.account', 'Debit account', required=True, domain=[('type', '=', 'receivable')])
    amount = fields.Float('Aomunt', required=True)
    account_payment_order_no = fields.Many2one('account.payment.order', 'Account Payment Order Reference', ondelete='cascade')

    @api.model
    def create(self, values):
        return super(account_payment_order_line, self).create(values)

account_payment_order_line()