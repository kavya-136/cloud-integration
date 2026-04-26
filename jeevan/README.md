# AI Cloud Cost Optimizer - Day 1 Foundation

Production-ready Django foundation for the AI Cloud Cost Optimizer backend.

## Project Structure

- `cloud_optimizer/` - Main Django project config
- `accounts/` - Authentication and security app
- `ml/` - ML model integration app (Day 3)
- `optimizer/` - Cost optimization logic app (Day 4+)
- `dashboard/` - Dashboard routes and views
- `templates/` - Shared template skeletons
- `static/` - CSS/JS/image static assets

## Requirements

- Python 3.10+
- pip

## Team Quick Start

```bash
git clone https://github.com/Jeevangowda05/cost-optimizer.git
cd cost-optimizer
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open: http://127.0.0.1:8000/

## URLs

- `/` - Index page
- `/dashboard/` - Dashboard page
- `/accounts/login/` - Login skeleton
- `/accounts/signup/` - Signup skeleton
- `/accounts/logout/` - Logout endpoint
- `/ml/predict/` - ML placeholder endpoint
- `/ml/anomaly/` - ML anomaly detection endpoint
- `/optimizer/recommendations/` - Optimizer recommendations endpoint
- `/optimizer/budget/set/` - Set budget threshold
- `/optimizer/budget/status/` - Get budget status
- `/optimizer/budget/alerts/check/` - Check budget alerts
- `/optimizer/scheduler/set/` - Create/update shutdown schedule
- `/optimizer/scheduler/list/` - List active shutdown schedules
- `/optimizer/scheduler/{id}/toggle/` - Enable/disable schedule
- `/optimizer/simulator/` - Run what-if simulation
- `/optimizer/carbon/` - Calculate carbon footprint
- `/optimizer/sustainability/` - Get sustainability score
- `/optimizer/region-advisor/` - Region recommendation
- `/optimizer/kubernetes/simulate/` - Kubernetes simulation
- `/optimizer/chatbot/` - Chatbot query endpoint
- `/admin/` - Django admin

## Day 1 Deliverables Included

- Django 4.2 project and 4 configured apps
- Custom user model (`accounts.CustomUser`)
- Project-level and app-level URL routing with namespaces
- SQLite database configuration
- Templates + static assets setup
- WSGI and ASGI configuration
- Initial model migrations
