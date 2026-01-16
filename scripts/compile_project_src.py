import py_compile
import glob
import os
import json
import sys

root = r"c:\Users\nabhi\Downloads\python_elinity-main\python_elinity-main"
errs = []

venv_segment = os.path.normcase(os.path.join(root, '.venv'))
for p in glob.glob(os.path.join(root, '**', '*.py'), recursive=True):
    ap = os.path.normcase(os.path.abspath(p))
    # skip any files inside a .venv directory
    if venv_segment in ap:
        continue
    try:
        py_compile.compile(p, doraise=True)
    except Exception as e:
        errs.append({"path": p, "error": str(e)})

print('COMPILE_ERRORS:')
print(json.dumps(errs, indent=2))
if errs:
    sys.exit(2)
else:
    print('COMPILE_OK')
    sys.exit(0)
