#!/usr/bin/env python3
import os
import sys
out=[]
for root,dirs,files in os.walk(os.getcwd()):
    if '.git' in root:
        continue
    for f in files:
        if f.endswith(('.py','.md','.txt','.json','.yaml','.yml')):
            p=os.path.join(root,f)
            try:
                with open(p,'rb') as fh:
                    s=fh.read()
            except Exception:
                continue
            for b in s:
                if b>127:
                    out.append(p)
                    break
if out:
    print('\n'.join(sorted(set(out))))
    sys.exit(0)
print('NO_NONASCII')
sys.exit(0)
