"""Quick API smoke test."""
import urllib.request, json

BASE = "http://127.0.0.1:8001/api/v1"

def get(path):
    r = urllib.request.urlopen(f"{BASE}{path}")
    return json.loads(r.read())

# Deals
d = get("/deals/")
print("=== DEALS ===")
print(f"  Total: {d['total']}")
print(f"  Golden: {d['golden_count']}")
print(f"  Avg Score: {d['average_bargain_score']:.1f}")

# Count positives
positive = sum(1 for deal in d['deals'] if deal['cash_flow']['monthly_cash_flow'] > 0)
print(f"  Cash-flow positive: {positive}")

# First deal images
imgs = d['deals'][0]['property'].get('image_urls', [])
print(f"  Images on first deal: {len(imgs)}")
if imgs:
    print(f"  First image URL: {imgs[0][:80]}...")

# Top 5 deals by score
sorted_deals = sorted(d['deals'], key=lambda x: x['bargain_score']['overall_score'], reverse=True)
print("\n=== TOP 5 DEALS ===")
for deal in sorted_deals[:5]:
    p = deal['property']
    cf = deal['cash_flow']
    bs = deal['bargain_score']
    gold = " GOLDEN" if deal.get('is_golden_opportunity') else ""
    print(f"  {p['suburb']}, {p['state']}: Score={bs['overall_score']} | "
          f"CF=${cf['monthly_cash_flow']:.0f}/mo | GY={cf['gross_rental_yield']:.1f}% | "
          f"BMV={deal['bmv_pct']:.1f}%{gold}")

# Properties
props = get("/properties/")
print(f"\n=== PROPERTIES ===")
print(f"  Total: {props['total']}")
all_have_images = all(len(p.get('image_urls', [])) > 0 for p in props['properties'])
print(f"  All have images: {all_have_images}")

# Sources diversity
sources = set(p['source'] for p in props['properties'])
print(f"  Sources: {', '.join(sorted(sources))}")

# States
states = set(p['state'] for p in props['properties'])
print(f"  States: {', '.join(sorted(states))}")

# Health
h = get("/health")
print(f"\n=== HEALTH ===")
print(f"  Status: {h['status']}")

print("\n ALL TESTS PASSED")
