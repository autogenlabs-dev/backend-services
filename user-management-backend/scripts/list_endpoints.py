#!/usr/bin/env python3
"""
List FastAPI routes with methods and dependency names.
Run from project root: python3 scripts/list_endpoints.py
"""
import csv
import sys
from importlib import import_module

try:
    app_mod = import_module('app.main')
    app = getattr(app_mod, 'app')
except Exception as e:
    print(f"Failed to import app.main.app: {e}", file=sys.stderr)
    sys.exit(1)

rows = []
for route in app.routes:
    try:
        path = getattr(route, 'path', '')
        methods = getattr(route, 'methods', None)
        methods = ",".join(sorted(methods)) if methods else ''
        name = getattr(route, 'name', '')
        # Dependencies: try to extract from route.dependant
        deps = []
        dependant = getattr(route, 'dependant', None)
        if dependant:
            for d in getattr(dependant, 'dependencies', []) or []:
                call = getattr(d, 'call', None)
                if call:
                    deps.append(getattr(call, '__name__', str(call)))
        deps_str = ";".join(deps)
        rows.append((path, methods, name, deps_str))
    except Exception as e:
        rows.append((getattr(route,'path','err'), '', 'error', str(e)))

out_path = 'endpoint_report.csv'
with open(out_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['path','methods','name','dependencies'])
    for r in rows:
        writer.writerow(r)

print(f"Wrote {out_path} with {len(rows)} routes")
