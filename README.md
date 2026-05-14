# Employee Work Tracker

**Version:** 1.0  
**Category:** Human Resources  
**License:** LGPL-3  
**Author:** Custom Development

## Description

Track employee tasks and work performance

Custom module to manage employee work tasks and summaries

## Features

- Odoo 19.0 compatible
- Standalone application
- Track employee tasks and work performance

## Dependencies

This module depends on the following Odoo modules:

- `base`
- `mail`
- `hr`
- `approvals`
- `product`
- `sale`
- `web`

## Installation

1. Clone this repository into your Odoo addons directory:
   ```bash
   git clone https://github.com/tejas7287/employee_work_tracker.git
   ```

2. Add the module path to your Odoo configuration file (`odoo.conf`):
   ```
   addons_path = /path/to/odoo/addons,/path/to/employee_work_tracker
   ```

3. Restart the Odoo server:
   ```bash
   sudo systemctl restart odoo
   ```

4. Go to **Apps** → **Update Apps List** → Search for **"Employee Work Tracker"** → Click **Install**

## Module Structure

```
employee_work_tracker/
├── __init__.py
├── __manifest__.py
├── controllers/
├── data/
├── models/
├── report/
├── security/
├── static/
├── views/
```

## Configuration

After installation, configure the module through Odoo's Settings menu or the module's specific configuration options.

## License

This project is licensed under the LGPL-3 License.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
