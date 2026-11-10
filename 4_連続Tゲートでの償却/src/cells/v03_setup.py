os.makedirs(OUT_DIR, exist_ok=True)
VAL = {}


def record(name, ok, detail=''):
    VAL[name] = dict(status='PASS' if ok else 'FAIL', detail=detail)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f' — {detail}' if detail else ''))
