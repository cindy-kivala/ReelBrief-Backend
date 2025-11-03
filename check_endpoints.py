from app import create_app

app = create_app()

print("🚀 BACKEND ENDPOINTS STRUCTURE")
print("=" * 50)

# List all registered blueprints and routes
for rule in app.url_map.iter_rules():
    if rule.endpoint != 'static':
        methods = ','.join(sorted(rule.methods - {'OPTIONS', 'HEAD'}))
        print(f"{methods:15} {rule.rule:40} -> {rule.endpoint}")

print(f"\n📊 Total endpoints: {len([r for r in app.url_map.iter_rules() if r.endpoint != 'static'])}")
