#!/usr/bin/env python3
"""clean-lab: borra spikes >72h y reporta hit-rate. Uso: python clean-lab.py [--dry]"""
import os, time, pathlib, sys
ROOT = pathlib.Path(__file__).parent
BLOB_DIRS = [ROOT/"lab", ROOT/"research"/"probes", ROOT/"tests"/"_probe_"]
LEDGER = ROOT/"LEDGER.md"
TTL_S = 72*3600

# El proof de research es evidencia permanente: nunca vive en lab/ (TTL 72h).
if (ROOT/"lab"/"traces").exists():
    raise SystemExit("ERROR: lab/traces/ prohibido; el proof vive en research/<exp>/traces/<hash>.r1.proof")

def scan():
    now=time.time()
    to_del=[]
    for d in BLOB_DIRS:
        if not d.exists(): continue
        for p in d.rglob("*"):
            if p.is_file() and now - p.stat().st_mtime > TTL_S:
                to_del.append(p)
    return to_del

def hit_rate():
    if not LEDGER.exists(): return 0,0,0
    lines=[l for l in LEDGER.read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]
    hits=sum(1 for l in lines if 'promoted' in l)
    total=len(lines) or 1
    return hits, total, round(hits/total*100,1)

if __name__=='__main__':
    dry='--dry' in sys.argv
    dels=scan()
    h,tot,pct=hit_rate()
    print(f"hit-rate: {h}/{tot} ({pct}%)  TTL 72h  candidatos a borrar: {len(dels)}")
    if dry:
        for p in dels: print(" would del", p)
    else:
        for p in dels:
            try: p.unlink()
            except: pass
        # vacía dirs huérfanos
        for d in BLOB_DIRS:
            if d.exists():
                for q in sorted(d.rglob("*"), reverse=True):
                    if q.is_dir() and not any(q.iterdir()):
                        try: q.rmdir()
                        except: pass
        print("borrados:", len(dels))
