# copy transferred blobs whose md5 matches an expected piece into q/
import hashlib, glob, os, shutil, sys
exp = {}
for line in open(sys.argv[1]):
    n, h = line.split(); exp[h] = n
T = '/root/.claude/projects/-home-user-sushi-phatat-naknak/f008169a-e3fe-5e15-a4e1-236ae64ffc3e/tool-results/'
out = sys.argv[2]; os.makedirs(out, exist_ok=True)
for f in glob.glob(T + 'mcp-Higgsfield-blob-*'):
    h = hashlib.md5(open(f, 'rb').read()).hexdigest()
    if h in exp and not os.path.exists(os.path.join(out, exp[h])): shutil.copy(f, os.path.join(out, exp[h]))
have = set(os.listdir(out)); miss = [n for n in exp.values() if n not in have]
print('have', len(have & set(exp.values())), 'missing', len(miss), ' '.join(miss[:40]))
