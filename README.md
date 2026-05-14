# Employee Work Tracker

![Version](https://img.shields.io/badge/version-1.0-blue)
![Category](https://img.shields.io/badge/category-Human%20Resources-green)
![License](https://img.shields.io/badge/license-LGPL-3-orange)
![Type](https://img.shields.io/badge/type-Application-purple)

| | |
|---|---|
| **Name** | Employee Work Tracker |
| **Version** | 1.0 |
| **Category** | Human Resources |
| **Author** | Custom Development |
| **License** | LGPL-3 |
| **Application** | Yes |

## Description

Track employee tasks and work performance

Custom module to manage employee work tasks and summaries

## Functionality

### Models & Fields

#### Extends `approval.request`

**File:** `models/approval_request.py`

**Inherits:** `approval.request`

**Key Methods:**

- `action_approve()` — Action/workflow method
- `action_refuse()` — Action/workflow method

#### Extends `crm.lead`

**File:** `models/crm_lead.py`

**Inherits:** `crm.lead`

**Fields:**

| Field | Type |
|-------|------|
| `task_ids` | `Many2many` |
| `task_count` | `Integer` |

**Key Methods:**

- `_compute_task_count()` — Computed field
- `action_view_tasks()` — Action/workflow method

#### `work.department` — Work Department

**File:** `models/department.py`

**Fields:**

| Field | Type |
|-------|------|
| `name` | `Char` |
| `partner_id` | `Many2one` |
| `employee_ids` | `Many2many` |

#### Extends `mrp.production`

**File:** `models/manufcature_order.py`

**Inherits:** `mrp.production`

**Fields:**

| Field | Type |
|-------|------|
| `task_ids` | `Many2many` |
| `task_count` | `Integer` |

**Key Methods:**

- `_compute_task_count()` — Computed field
- `action_view_tasks()` — Action/workflow method

#### Extends `product.product, product.template`

**File:** `models/product.py`

**Inherits:** `product.product`, `product.template`

**Fields:**

| Field | Type |
|-------|------|
| `task_count` | `Integer` |

**Key Methods:**

- `action_view_tasks()` — Action/workflow method
- `_compute_task_count()` — Computed field
- `action_view_tasks()` — Action/workflow method

#### Extends `purchase.order`

**File:** `models/purchase_order.py`

**Inherits:** `purchase.order`

**Fields:**

| Field | Type |
|-------|------|
| `task_ids` | `Many2many` |
| `task_count` | `Integer` |

**Key Methods:**

- `_compute_task_count()` — Computed field
- `action_view_tasks()` — Action/workflow method

#### Extends `sale.order`

**File:** `models/sales_order.py`

**Inherits:** `sale.order`

**Fields:**

| Field | Type |
|-------|------|
| `task_ids` | `Many2many` |
| `task_count` | `Integer` |

**Key Methods:**

- `_compute_task_count()` — Computed field
- `action_view_tasks()` — Action/workflow method

#### `employee.work.subtask` — Employee Work Subtask

**File:** `models/subtask.py`

**Inherits:** `mail.thread`, `mail.activity.mixin`

**Fields:**

| Field | Type |
|-------|------|
| `name` | `Char` |
| `task_id` | `Many2one` |
| `employee_id` | `Many2one` |
| `start_date` | `Date` |
| `end_date` | `Date` |
| `hours_spent` | `Float` |
| `state` | `Selection` |
| `approval_request_id` | `Many2one` |

**Key Methods:**

- `action_send_for_approval()` — Action/workflow method
- `action_send_for_approval()` — Action/workflow method

#### `task.document` — Task Documents

**File:** `models/task_document.py`

**Inherits:** `mail.thread`, `mail.activity.mixin`

**Fields:**

| Field | Type |
|-------|------|
| `task_id` | `Many2one` |
| `document_file` | `Binary` |
| `file_name` | `Char` |
| `uploaded_by` | `Many2one` |
| `upload_date` | `Datetime` |

**Key Methods:**

- `create()` — Overridden ORM method
- `unlink()` — Overridden ORM method

#### `employee.work.task.line` — Task Product Line

**File:** `models/task_product_line.py`

**Fields:**

| Field | Type |
|-------|------|
| `task_id` | `Many2one` |
| `product_id` | `Many2one` |
| `quantity` | `Float` |
| `price_unit` | `Float` |

#### `employee.work.summary` — Employee Work Summary

**File:** `models/work_summary.py`

**Fields:**

| Field | Type |
|-------|------|
| `employee_id` | `Many2one` |
| `total_tasks` | `Integer` |
| `total_hours` | `Float` |

#### `employee.work.task` — Employee Work Task

**File:** `models/work_task.py`

**Inherits:** `mail.thread`, `mail.activity.mixin`

**Fields:**

| Field | Type |
|-------|------|
| `reference` | `Char` |
| `department_id` | `Many2one` |
| `employee_ids` | `Many2many` |
| `partner_id` | `Many2one` |
| `sale_order_id` | `Many2one` |
| `order_line_ids` | `One2many` |
| `name` | `Char` |
| `employee_id` | `Many2one` |
| `description` | `Text` |
| `start_date` | `Date` |
| `end_date` | `Date` |
| `hours_spent` | `Float` |
| `manager_id` | `Many2one` |
| `password` | `Char` |
| `state` | `Selection` |
| `reminder_7_sent` | `Boolean` |
| `reminder_3_sent` | `Boolean` |
| `reminder_1_sent` | `Boolean` |
| `subtask_ids` | `One2many` |
| `subtask_count` | `Integer` |
| `sale_order_count` | `Integer` |
| `product_ids` | `Many2many` |
| `product_count` | `Integer` |
| `sale_order_ids` | `Many2many` |
| `purchase_order_ids` | `Many2many` |
| `mrp_ids` | `Many2many` |
| `crm_ids` | `Many2many` |
| `sale_count` | `Integer` |
| `purchase_count` | `Integer` |
| `mrp_count` | `Integer` |
| `crm_count` | `Integer` |
| `qr_code` | `Binary` |
| `qr_url` | `Char` |
| `document_ids` | `One2many` |
| `document_count` | `Integer` |
| `allowed_employee_ids` | `Many2many` |

**Key Methods:**

- `action_approve()` — Action/workflow method
- `action_reject()` — Action/workflow method
- `create()` — Overridden ORM method
- `write()` — Overridden ORM method
- `unlink()` — Overridden ORM method
- `_cron_send_deadline_reminder()` — Scheduled action
- `action_print_task_report()` — Action/workflow method
- `_compute_subtask_count()` — Computed field
- `action_view_subtasks()` — Action/workflow method
- `_compute_sale_order_count()` — Computed field
- `action_view_sale_order()` — Action/workflow method
- `_compute_products()` — Computed field
- `_compute_products()` — Computed field
- `action_view_products()` — Action/workflow method
- `_compute_link_counts()` — Computed field
- `_onchange_sale_order()` — Onchange handler
- `action_confirm_sale()` — Action/workflow method
- `action_view_sales()` — Action/workflow method
- `action_view_purchase()` — Action/workflow method
- `action_view_mrp()` — Action/workflow method
- `action_view_crm()` — Action/workflow method
- `_compute_qr_url()` — Computed field
- `_compute_qr_code()` — Computed field
- `_compute_document_count()` — Computed field
- `action_view_documents()` — Action/workflow method
- `_compute_allowed_employees()` — Computed field
- `_onchange_employee_ids()` — Onchange handler
- `action_reset_to_draft()` — Action/workflow method

#### `mrp.workorder.line` — Workorder Serial Tracking

**File:** `models/workorder.py`

**Inherits:** `mrp.production`, `mrp.workorder`, `quality.check`, `product.product`, `product.template`, `stock.lot`, `mrp.workcenter`, `mrp.bom.line`, `mrp.production`, `stock.move`

**Fields:**

| Field | Type |
|-------|------|
| `workorder_id` | `Many2one` |
| `production_id` | `Many2one` |
| `lot_id` | `Many2one` |
| `employee_ids` | `Many2many` |
| `workcenter_id` | `Many2one` |
| `workorder_line_count` | `Integer` |
| `history_count` | `Integer` |
| `workorder_line_ids` | `One2many` |
| `final_image` | `Binary` |
| `final_image_filename` | `Char` |
| `employee_history` | `Text` |
| `product_barcode` | `Char` |
| `faulty_component_id` | `Many2many` |
| `worksheet_document` | `Binary` |
| `instruction_note` | `Html` |
| `faulty_lot_id` | `Many2many` |
| `location_id` | `Many2one` |
| `operation_id` | `Many2one` |
| `serial_input` | `Char` |

**Key Methods:**

- `_compute_workorder_line_count()` — Computed field
- `_compute_history_count()` — Computed field
- `action_confirm()` — Action/workflow method
- `action_view_serials()` — Action/workflow method
- `action_view_history()` — Action/workflow method
- `button_start()` — Button handler
- `button_finish()` — Button handler
- `_compute_employee_history()` — Computed field
- `_onchange_faulty_component()` — Onchange handler
- `create()` — Overridden ORM method
- `_compute_employee_ids()` — Computed field
- `write()` — Overridden ORM method
- `create()` — Overridden ORM method
- `create()` — Overridden ORM method
- `action_scan_serial()` — Action/workflow method

### Views & UI

**Form Views:** `department_views.xml`, `extra_menu.xml`, `menu.xml`, `portal_templates.xml`, `subtask_views.xml`, `task_document_views.xml`, `task_views.xml`

**List/Tree Views:** `department_views.xml`, `subtask_views.xml`, `summary_views.xml`, `task_document_views.xml`, `task_views.xml`

**Kanban Views:** `summary_views.xml`, `task_views.xml`

**Menus:** `extra_menu.xml`, `menu.xml`

**Website/Portal Templates:**

- `report_lot_barcode` (`lot_barcode_report.xml`)
- `portal.portal_my_home` (`portal_templates.xml`)
- `portal_my_tasks` (`portal_templates.xml`)
- `portal_task_detail` (`portal_templates.xml`)
- `task_qr_page` (`task_qr_template.xml`)
- `traceability_template` (`traceability.xml`)

### Security

**Security Groups:**

- Work Tracker Employee
- Work Tracker Manager
- Work Tracker Administrator
- Employee Own Tasks
- Manager All Tasks
- Admin All Tasks
- Portal Task Access

**Access Rights:** 8 model access rules defined

| Model |
|-------|
| `access.employee.work.summary` |
| `access.employee.work.task` |
| `access.employee.work.subtask` |
| `access.employee.work.task.line` |
| `access.task.document` |
| `work.department` |
| `access_mrp_workorder_line_user` |
| `access.mrp.workorder.history.user` |

**Record Rules:** `security.xml`, `task_rules.xml`

### Web Controllers & Routes

| Route | Controller |
|-------|------------|
| `/traceability/<string:serial>` | `main.py` |
| `/my/task/reset/<int:task_id>` | `main.py` |
| `/my/tasks` | `portal.py` |
| `/my/task/<int:task_id>` | `portal.py` |
| `/my/task/approve/<int:task_id>` | `portal.py` |
| `/my/task/reject/<int:task_id>` | `portal.py` |
| `/my/task/print/<int:task_id>` | `portal.py` |
| `/my/tasks` | `portal.py` |
| `/task/details/<int:task_id>` | `task_qr_controller.py` |

### Data & Automation

**Sequences:** `sequence.xml`

**Scheduled Actions (Cron):** `cron.xml`

**Email Templates:** `mail_template.xml`

**Other Data:** `approval_category.xml`

### Reports

- `task_report.xml`

### Frontend Assets

**JavaScript:**

- `static/src/js/serial_enter.js`

## Dependencies

| Module | Type |
|--------|------|
| `base` | Odoo Core |
| `mail` | Odoo Core |
| `hr` | Odoo Core |
| `approvals` | Odoo Core |
| `product` | Odoo Core |
| `sale` | Odoo Core |
| `web` | Odoo Core |

## File Structure

```
employee_work_tracker/
├── LICENSE
├── README.md
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   ├── main.py
│   ├── portal.py
│   └── task_qr_controller.py
├── data/
│   ├── approval_category.xml
│   ├── cron.xml
│   ├── mail_template.xml
│   └── sequence.xml
├── models/
│   ├── __init__.py
│   ├── approval_request.py
│   ├── crm_lead.py
│   ├── department.py
│   ├── manufcature_order.py
│   ├── product.py
│   ├── purchase_order.py
│   ├── sales_order.py
│   ├── subtask.py
│   ├── task_document.py
│   ├── task_product_line.py
│   ├── work_summary.py
│   ├── work_task.py
│   └── workorder.py
├── report/
│   └── task_report.xml
├── security/
│   ├── ir.model.access.csv
│   ├── security.xml
│   └── task_rules.xml
├── static/
│   ├── description/
│   │   └── icon.png
│   └── src/
│       ├── img/
│       └── js/
└── views/
    ├── crm_lead_views.xml
    ├── department_views.xml
    ├── extra_menu.xml
    ├── lot_barcode_report.xml
    ├── manufacture_order_views.xml
    ├── menu.xml
    ├── portal_templates.xml
    ├── product_views.xml
    ├── purchase_order_views.xml
    ├── sales_order_views.xml
    ├── subtask_views.xml
    ├── summary_views.xml
    ├── task_document_views.xml
    ├── task_qr_template.xml
    ├── task_views.xml
    ├── traceability.xml
    └── workorder.xml
```

## Installation

This module is part of the **[odoo-hr-education-finance-suite](https://github.com/tejas7287/odoo-hr-education-finance-suite)** suite.

1. Place this module in your Odoo addons directory
2. Update the apps list: **Settings** → **Apps** → **Update Apps List**
3. Search for **"Employee Work Tracker"** and click **Install**

## License

LGPL-3
