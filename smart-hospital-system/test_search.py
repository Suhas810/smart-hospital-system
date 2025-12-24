from backend.database.db_adapter import get_db_backend

db = get_db_backend()
print("--- All Doctors ---")
all_docs = db.get_doctors()
for d in all_docs:
    print(f"Name: {d['name']}, Spec: {d['spec']}")

print("\n--- Search 'dentist' ---")
results = db.search_doctors('dentist')
print(f"Found {len(results)} matches.")
for d in results:
    print(d)

print("\n--- Search 'Dentist' ---")
results = db.search_doctors('Dentist')
print(f"Found {len(results)} matches.")
for d in results:
    print(d)
