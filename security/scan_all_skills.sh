#!/bin/bash
# Static (free, --no-llm) SkillSpector scan of every installed skill. Usage: security/scan_all_skills.sh [out_dir]
S=${1:-./skill-audit-out}; mkdir -p "$S/reports"
P=$(ls -d "$HOME"/.claude/plugins/synced/*/ | head -1)
K=$(ls -d "$HOME"/.claude/skills/synced/*/ | head -1)
{
for d in $K/*/; do echo "skills|$(basename $d)|$d"; done
echo "skills|session-start-hook|$HOME/.claude/skills/session-start-hook"
for pl in adobe-for-creativity c21dd3e3-2c37-4d53-a75a-a465de3f3f6e canva design modern-web-guidance; do
  name=$pl; [ $pl = c21dd3e3-2c37-4d53-a75a-a465de3f3f6e ] && name=remotion
  for d in $P/$pl/skills/*/; do echo "$name|$(basename $d)|$d"; done
done
for d in $P/canva/inactive-skills/*/; do echo "canva-inactive|$(basename $d)|$d"; done
echo "repo|skill-inspector|$(git rev-parse --show-toplevel)/.claude/skills/skill-inspector"
} > $S/targets.txt
while IFS='|' read -r grp name dir; do
  out=$S/reports/${grp}__${name}.json
  timeout 300 skillspector scan "$dir" --no-llm --format json --output "$out" >/dev/null 2>$S/reports/${grp}__${name}.err
  echo "$grp/$name exit=$?"
done < $S/targets.txt
