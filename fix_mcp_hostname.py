import sys

with open('/home/brrr/flux/packages/mcp/src/index.ts', 'r') as f:
    lines = f.readlines()

inserted = False
for i, line in enumerate(lines):
    if not inserted and '      port: HTTP_PORT,' in line:
        lines.insert(i+1, '      hostname: "0.0.0.0",\n')
        inserted = True
        break

with open('/home/brrr/flux/packages/mcp/src/index.ts', 'w') as f:
    f.writelines(lines)

print('done, inserted:', inserted)
