from pathlib import Path
p=Path('Momentum/Python/tools')
imgs=list(p.glob('*.png'))
print('png_count=',len(imgs))
for x in sorted(imgs)[:40]:
    print(x)
