"""Quick data audit."""
import json, urllib.request

r = urllib.request.urlopen('http://127.0.0.1:8001/api/v1/deals/')
data = json.loads(r.read())

print('=== DEALS BY STATE ===')
states = {}
for d in data['deals']:
    s = d['property']['state']
    states[s] = states.get(s, 0) + 1
for s in sorted(states.keys()):
    print(f'  {s}: {states[s]} deals')

print()
print('=== DEALS BY TYPE ===')
types = {}
for d in data['deals']:
    t = d['property']['property_type']
    types[t] = types.get(t, 0) + 1
for t in sorted(types.keys()):
    print(f'  {t}: {types[t]}')

print()
print('=== DEALS BY STRATEGY ===')
strats = {}
for d in data['deals']:
    t = d['deal_type']
    strats[t] = strats.get(t, 0) + 1
for s in sorted(strats.keys()):
    print(f'  {s}: {strats[s]}')

print()
print('=== VIC DEALS (default filter) ===')
vic = [d for d in data['deals'] if d['property']['state'] == 'VIC']
for d in sorted(vic, key=lambda x: x['bargain_score']['overall_score'], reverse=True):
    p = d['property']
    cf = d['cash_flow']
    suburb = p['suburb']
    score = d['bargain_score']['overall_score']
    cashflow = cf['monthly_cash_flow']
    ptype = p['property_type']
    print(f'  {suburb}: Score={score}, CF={cashflow:.0f}/mo, Type={ptype}')

print()
print('=== STRATEGY DISTRIBUTION ===')
for d in sorted(data['deals'], key=lambda x: x['bargain_score']['overall_score'], reverse=True)[:15]:
    p = d['property']
    suburb = p['suburb']
    state = p['state']
    strat = d['deal_type']
    strategies = d.get('recommended_strategies', [])
    print(f'  {suburb} {state}: Primary={strat}, All={strategies}')
