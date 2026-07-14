import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from resolve_core import ResolveConnection

engine = ResolveConnection()
success, msg = engine.connect()
if not success:
    print(f"Failed to connect: {msg}")
    sys.exit(1)

output_path = "/Users/audiovisual/Desktop/test_shotlist.csv"
success, msg = engine.export_shotlist_doc('csv', output_path, "")

print(msg)
if success and os.path.exists(output_path):
    print("\n--- CSV CONTENT ---")
    with open(output_path, 'r') as f:
        print(f.read())
