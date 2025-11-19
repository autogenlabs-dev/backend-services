#!/usr/bin/env python3
"""
Statically scan Python files under app/ for APIRouter usages and @router.<method> decorators.
Produces a CSV with: file, prefix, decorator_path, method, auth dependencies found in function body/signature.
"""
import re
import os
import csv

root = 'app'
pattern_router = re.compile(r"APIRouter\(([^)]*)\)")
pattern_prefix = re.compile(r"prefix\s*=\s*[\"']([^\"']+)[\"']")
pattern_decorator = re.compile(r"@router\.(get|post|put|delete|patch)\(([^)]*)\)")
pattern_depends = re.compile(r"Depends\(([^)]+)\)")
pattern_func = re.compile(r"def\s+(\w+)\s*\(")

rows = []
for dirpath, dirnames, filenames in os.walk(root):
    for fn in filenames:
        if not fn.endswith('.py'):
            continue
        path = os.path.join(dirpath, fn)
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        # find prefix if any
        prefix = ''
        for m in pattern_router.finditer(text):
            # naive: take first occurrence in file
            args = m.group(1)
            p = pattern_prefix.search(args)
            if p:
                prefix = p.group(1)
                break
        # scan decorators
        for m in pattern_decorator.finditer(text):
            method = m.group(1).upper()
            raw_args = m.group(2)
            # extract path string if present
            path_match = re.search(r"[\"']([^\"']+)[\"']", raw_args)
            dec_path = path_match.group(1) if path_match else ''
            # locate function definition after decorator
            idx = m.end()
            snippet = text[idx: idx+400]
            func_match = pattern_func.search(snippet)
            func_name = func_match.group(1) if func_match else ''
            # search for Depends in the function signature lines around
            # get a larger context
            context = text[max(0, m.start()-200): m.end()+800]
            deps = set()
            for d in pattern_depends.finditer(context):
                deps.add(d.group(1).strip())
            rows.append((path, prefix, dec_path, method, func_name, ';'.join(sorted(deps))))

out = 'static_endpoint_report.csv'
with open(out, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['file','prefix','decorator_path','method','function','dependencies'])
    for r in rows:
        w.writerow(r)

print(f"Wrote {out} with {len(rows)} entries")
