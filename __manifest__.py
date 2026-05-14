{
    'name': 'Employee Work Tracker',
    'version': '1.0',
    'summary': 'Track employee tasks and work performance',
    'description': 'Custom module to manage employee work tasks and summaries',
    'author': 'Custom Development',
    'category': 'Human Resources',
    'depends': ['base', 'mail', 'hr', 'approvals', 'product', 'sale','web'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/task_rules.xml',

        'views/task_views.xml',
        'views/summary_views.xml',
        'views/subtask_views.xml',
        'views/menu.xml',
        'views/sales_order_views.xml',
        'views/product_views.xml',
        'views/purchase_order_views.xml',
        'views/manufacture_order_views.xml',
        'views/crm_lead_views.xml',
        'views/task_document_views.xml',
        'views/task_qr_template.xml',
        'views/portal_templates.xml',
        'views/department_views.xml',
        'views/workorder.xml',
        'views/lot_barcode_report.xml',
        'views/traceability.xml',
        # 'views/subtask_portal_templates.xml',

        'report/task_report.xml',

        'data/mail_template.xml',
        'data/cron.xml',
        'data/approval_category.xml',
        'data/sequence.xml',

    ],
'assets': {
    'web.assets_backend': [
        'employee_work_tracker/static/src/js/serial_enter.js',
    ],
},
    'installable': True,
    'application': True,
}
