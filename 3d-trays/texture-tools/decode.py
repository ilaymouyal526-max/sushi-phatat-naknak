import json,base64,glob,os,sys
d='/root/.claude/projects/-home-user-sushi-phatat-naknak/f008169a-e3fe-5e15-a4e1-236ae64ffc3e/tool-results/'
for f in glob.glob(d+'mcp-Google_Drive-download_file_content-*.txt'):
    j=json.load(open(f)); out='raw/'+os.path.basename(j['title'])
    if not os.path.exists(out): open(out,'wb').write(base64.b64decode(j['content'])); print(out)
