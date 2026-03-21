import sys
sys.path.insert(0, '/home/brrr/brrr-printer2')
from src.api.topstepx_api import TopStepXClient

c = TopStepXClient()
c.authenticate()
accounts = c.get_accounts(only_active=True)
for a in accounts:
    print(f"ID: {a['id']}  Name: {a.get('name', '?')}  Balance: {a.get('balance', '?')}")
