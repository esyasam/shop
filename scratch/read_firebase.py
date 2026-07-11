import urllib.request
import json

url = "https://esyasam77-default-rtdb.europe-west1.firebasedatabase.app/products.json"

try:
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
        print("Firebase products database structure:")
        for key, value in data.items():
            print(f"\nProduct ID: {value.get('id')} - {value.get('name')}")
            for k, v in value.items():
                if k not in ['id', 'name']:
                    # truncate long values for clear printing
                    v_str = str(v)
                    if len(v_str) > 60:
                        v_str = v_str[:60] + "..."
                    print(f"  - {k}: {v_str}")
except Exception as e:
    print("Error:", e)
