"""Phone-friendly lead cards: one self-contained HTML file per run (no external scripts or fonts)."""

from __future__ import annotations

import datetime as dt
import html
import json
import re
from urllib.parse import quote

BAND_LABEL = {"Hot": "🔥 Hot", "Warm": "Warm", "Cold": "Cold"}


def phone_e164(phone: str) -> str:
    """Israeli phone -> digits in international form without '+', e.g. '0546559181' -> '972546559181'."""
    digits = re.sub(r"\D", "", phone or "")
    if digits.startswith("00972"):
        digits = digits[2:]
    if digits.startswith("972"):
        pass
    elif digits.startswith("0"):
        digits = "972" + digits[1:]
    elif len(digits) in (8, 9):
        digits = "972" + digits
    else:
        return ""
    return digits if 11 <= len(digits) <= 12 else ""


def is_mobile(e164: str) -> bool:
    """Israeli mobile numbers are 05x locally, i.e. 9725x internationally. Landlines can't get WhatsApp."""
    return e164.startswith("9725") and len(e164) == 12


def _safe_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    if not re.match(r"^https?://", url, re.I):
        if re.match(r"^[\w.-]+\.[a-z]{2,}(/|$)", url, re.I):
            url = "https://" + url
        else:
            return ""
    return url


def _social_url(value: str, host: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    if value.lower().startswith("http") or host in value.lower():
        return _safe_url(value)
    return f"https://www.{host}/{quote(value.lstrip('@'))}"


def _e(text) -> str:
    return html.escape("" if text is None else str(text))


_RANGE = re.compile(r"\d{2}:\d{2}-\d{2}:\d{2}")


def _times(text) -> str:
    """Escape, and keep each time range on one line."""
    return _RANGE.sub(lambda m: f'<span class="nw">{m.group(0)}</span>', _e(text))


def _attr_json(obj) -> str:
    return html.escape(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), quote=True)


LOG_BUTTONS = [("answered", "ענה"), ("no_answer", "לא ענה"), ("call_back", "לחזור ב…"),
               ("meeting", "פגישה"), ("not_interested", "לא מעוניין"), ("won", "נסגר ✓")]


def _card(lead: dict, slot: str = "", kind: str = "") -> str:
    from .scripts_he import objections_for
    band = lead.get("band", "Cold")
    e164 = phone_e164(lead.get("phone", ""))
    buttons = []
    if e164:
        buttons.append(f'<a class="btn call" href="tel:+{e164}">📞 {_e(lead.get("phone"))}</a>')
        if is_mobile(e164):
            wa = f"https://wa.me/{e164}"
            if lead.get("outreach_he"):
                wa += "?text=" + quote(str(lead["outreach_he"]))
            buttons.append(f'<a class="btn wa" href="{_e(wa)}" target="_blank" rel="noopener">WhatsApp</a>')
            if lead.get("missed_he"):
                missed = f"https://wa.me/{e164}?text=" + quote(str(lead["missed_he"]))
                buttons.append(f'<a class="btn wa2" href="{_e(missed)}" target="_blank" rel="noopener">'
                               f'💬 ניסיתי להתקשר…</a>')
    links = [
        ("Website", _safe_url(lead.get("website", ""))),
        ("Facebook", _social_url(lead.get("facebook", ""), "facebook.com")),
        ("Instagram", _social_url(lead.get("instagram", ""), "instagram.com")),
        ("Listing", _safe_url(lead.get("directory_page", ""))),
        ("Map", _safe_url(lead.get("maps_link", ""))),
    ]
    buttons += [f'<a class="btn" href="{_e(u)}" target="_blank" rel="noopener">{n}</a>' for n, u in links if u]

    category = (lead.get("category", "").split("=")[-1] or "").replace("_", " ")
    meta = " · ".join(_e(x) for x in [category, lead.get("address", "")] if x)
    reasons = "".join(f"<li>{_e(r.strip())}</li>" for r in str(lead.get("why_he", "")).split(";") if r.strip())
    opener = ""
    if lead.get("outreach_he"):
        opener = (f'<div class="opener"><div class="label">הודעת פתיחה · Opener</div>'
                  f'<p dir="rtl">{_e(lead["outreach_he"])}</p>'
                  f'<button type="button" class="copy">Copy</button></div>')
    verified = '<span class="tag ok">✓ verified online</span>' if lead.get("enriched") else \
        '<span class="tag">not verified yet</span>'
    notes = f'<p class="notes" dir="auto">{_e(lead["notes"])}</p>' if lead.get("notes") else ""

    hours = _times(lead.get("opening_he") or lead.get("opening_hours") or "לא ידוע")
    personal = f'<div class="personal">📊 {_e(lead["call_personal"])}</div>' if lead.get("call_personal") else ""
    when = (f'<div class="when" dir="rtl">'
            f'<div class="live" data-live>…</div>'
            f'<div><b>🕐 מתי להתקשר:</b> {_times(lead.get("call_best", ""))}</div>'
            f'<div><b>⛔ שעות עומס:</b> {_times(lead.get("call_avoid", ""))}</div>'
            f'<div class="small"><b>שעות פתיחה:</b> {hours}</div>'
            f'<div class="small">💡 {_e(lead.get("call_tip", ""))}</div>{personal}</div>')
    log = ("<div class=\"log\" dir=\"rtl\"><div class=\"fu\" data-fu></div><div class=\"logbtns\">"
           + "".join(f'<button type="button" data-result="{r}">{label}</button>' for r, label in LOG_BUTTONS)
           + '<button type="button" class="undo" data-undo hidden>↩︎ בטל</button></div></div>')
    script = ""
    if lead.get("call_script_he"):
        auto = " (תבנית)" if lead.get("call_script_auto") else ""
        script = (f'<details dir="rtl"><summary>📋 תסריט שיחה{auto}</summary>'
                  f'<p class="pre">{_e(lead["call_script_he"])}</p></details>')
    objections = "".join(f"<dt>“{_e(q)}”</dt><dd>{_e(a)}</dd>" for q, a in objections_for(lead))
    objections = f'<details dir="rtl"><summary>💬 תשובות להתנגדויות</summary><dl>{objections}</dl></details>'
    slot_html = ""
    if slot:
        kind_he = {"callback": "🔁 חזרה שביקשו", "retry": "ניסיון נוסף", "new": "חדש"}.get(kind, "")
        slot_html = f'<div class="slot"><span class="time">{_e(slot)}</span> <span>{_e(kind_he)}</span></div>'

    data = {"lead_id": lead["lead_id"], "name": lead.get("name", ""), "profile": lead.get("call_profile", ""),
            "schedule": lead.get("call_schedule") or {}, "log": lead.get("call_log") or []}
    return f"""
<article class="card" data-band="{_e(band)}" data-lead="{_attr_json(data)}">
  {slot_html}
  <header>
    <h2 dir="auto">{_e(lead.get("name"))}</h2>
    <span class="badge {_e(band.lower())}">{_e(BAND_LABEL.get(band, band))} · {_e(lead.get("success_pct"))}%</span>
  </header>
  <p class="meta" dir="auto">{meta}</p>
  <p class="sell"><span class="pill">{_e(lead.get("sell") or lead.get("lead_type"))}</span> {verified}</p>
  {when}
  <ul class="why" dir="rtl">{reasons}</ul>
  {notes}
  {opener}
  <nav class="actions">{"".join(buttons) or '<span class="muted">No contact details found yet</span>'}</nav>
  {log}
  {script}
  {objections}
</article>"""


CSS = """
:root{--bg:#f6f7f9;--card:#fff;--text:#111827;--muted:#6b7280;--line:#e5e7eb;--accent:#1d4ed8;
--hot:#fde2e1;--hot-t:#991b1b;--warm:#fef3c7;--warm-t:#92400e;--cold:#eef0f3;--cold-t:#374151;
--wa:#16a34a;--chip:#fff;--chip-on:#111827;--chip-on-t:#fff;--opener:#f1f5ff;
--good:#dcfce7;--good-t:#166534;--rush:#ffedd5;--rush-t:#9a3412;--off:#eef0f3;--off-t:#4b5563;--when:#fafafa}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0f1115;--card:#181b21;--text:#e5e7eb;
--muted:#9ca3af;--line:#2a2f37;--accent:#93b4ff;--hot:#4a1d1d;--hot-t:#fecaca;--warm:#45330f;--warm-t:#fde68a;
--cold:#262a31;--cold-t:#d1d5db;--wa:#22c55e;--chip:#181b21;--chip-on:#e5e7eb;--chip-on-t:#111827;--opener:#1c2433;
--good:#123821;--good-t:#bbf7d0;--rush:#45240f;--rush-t:#fed7aa;--off:#262a31;--off-t:#d1d5db;--when:#1d2027}}
:root[data-theme="dark"]{--bg:#0f1115;--card:#181b21;--text:#e5e7eb;--muted:#9ca3af;--line:#2a2f37;--accent:#93b4ff;
--hot:#4a1d1d;--hot-t:#fecaca;--warm:#45330f;--warm-t:#fde68a;--cold:#262a31;--cold-t:#d1d5db;--wa:#22c55e;
--chip:#181b21;--chip-on:#e5e7eb;--chip-on-t:#111827;--opener:#1c2433;--good:#123821;--good-t:#bbf7d0;
--rush:#45240f;--rush-t:#fed7aa;--off:#262a31;--off-t:#d1d5db;--when:#1d2027}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:16px/1.45 system-ui,-apple-system,"Segoe UI",Arial,sans-serif}
main{max-width:720px;margin:0 auto;padding:16px}
h1{font-size:1.3rem;margin:4px 0}
.sub,.muted,.meta{color:var(--muted);font-size:.9rem}
.note{font-size:.85rem;color:var(--muted);border-left:3px solid var(--line);padding-left:10px;margin:10px 0}
.daynote{background:var(--rush);color:var(--rush-t);border-radius:10px;padding:10px 12px;margin:10px 0}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 16px;position:sticky;top:0;background:var(--bg);padding:8px 0;z-index:1}
.chips button{border:1px solid var(--line);background:var(--chip);color:var(--text);border-radius:999px;padding:8px 14px;font:inherit;font-size:.9rem}
.chips button[aria-pressed="true"]{background:var(--chip-on);color:var(--chip-on-t);border-color:var(--chip-on)}
.toolbar{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.toolbar button,.toolbar a{font:inherit;font-size:.85rem;border:1px solid var(--line);background:var(--card);color:var(--text);border-radius:10px;padding:8px 12px;text-decoration:none}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px;margin-bottom:12px}
.card.done{opacity:.55}
.card header{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}
.card h2{font-size:1.1rem;margin:0;overflow-wrap:anywhere}
.badge{white-space:nowrap;font-weight:700;font-size:.85rem;padding:4px 10px;border-radius:999px}
.badge.hot{background:var(--hot);color:var(--hot-t)}.badge.warm{background:var(--warm);color:var(--warm-t)}
.badge.cold{background:var(--cold);color:var(--cold-t)}
.meta{margin:4px 0 8px;overflow-wrap:anywhere}
.pill{display:inline-block;background:var(--cold);border-radius:6px;padding:2px 8px;font-size:.85rem}
.tag{font-size:.8rem;color:var(--muted);margin-left:6px}.tag.ok{color:var(--wa)}
.when{background:var(--when);border:1px solid var(--line);border-radius:10px;padding:10px 12px;margin:10px 0;font-size:.92rem}
.when > div{margin:2px 0}.nw{white-space:nowrap}.small{font-size:.85rem;color:var(--muted)}
.live{display:inline-block;font-weight:600;border-radius:8px;padding:3px 10px;margin-bottom:6px;background:var(--off);color:var(--off-t)}
.live.good{background:var(--good);color:var(--good-t)}.live.rush{background:var(--rush);color:var(--rush-t)}
.personal{margin-top:4px;font-size:.85rem}
.why{margin:8px 0;padding-right:20px;padding-left:0}
.notes{font-size:.9rem;color:var(--muted);margin:6px 0}
.opener{background:var(--opener);border-radius:10px;padding:10px 12px;margin:10px 0}
.opener .label{font-size:.75rem;color:var(--muted);margin-bottom:4px}
.opener p{margin:0 0 8px;white-space:pre-wrap}
.copy{font:inherit;font-size:.85rem;border:1px solid var(--line);background:var(--card);color:var(--text);border-radius:8px;padding:6px 12px}
.actions{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
.btn{display:inline-block;text-decoration:none;color:var(--accent);border:1px solid var(--line);border-radius:10px;padding:9px 12px;font-size:.9rem}
.btn.call{background:var(--accent);color:var(--card);border-color:var(--accent);font-weight:600}
.btn.wa{background:var(--wa);color:#fff;border-color:var(--wa);font-weight:600}
.btn.wa2{color:var(--wa);border-color:var(--wa)}
.log{border-top:1px dashed var(--line);margin-top:12px;padding-top:10px}
.fu{font-size:.9rem;margin-bottom:6px;min-height:1em}
.logbtns{display:flex;flex-wrap:wrap;gap:6px}
.logbtns button{font:inherit;font-size:.85rem;border:1px solid var(--line);background:var(--card);color:var(--text);border-radius:8px;padding:7px 10px}
.logbtns .undo{color:var(--muted)}
details{margin-top:8px;border-top:1px solid var(--line);padding-top:8px}
summary{cursor:pointer;font-weight:600;font-size:.92rem}
.pre{white-space:pre-wrap;font-size:.92rem}
dl{margin:6px 0}dt{font-weight:600;margin-top:8px;font-size:.9rem}dd{margin:2px 0 0;font-size:.9rem}
.slot{display:flex;gap:8px;align-items:center;margin-bottom:6px;color:var(--muted);font-size:.9rem}
.slot .time{font-weight:700;font-size:1.05rem;color:var(--text)}
.block{font-weight:700;margin:18px 0 8px}
footer{font-size:.8rem;color:var(--muted);margin:20px 0 40px}
"""

JS = r"""
const DAY=['ראשון','שני','שלישי','רביעי','חמישי','שישי','שבת'];
const KEY='lead_agent_calls_v1';
const p2=n=>String(n).padStart(2,'0'), hhmm=m=>p2(Math.floor(m/60)%24)+':'+p2(m%60);
function ilNow(){
  const parts=Object.fromEntries(new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Jerusalem',year:'numeric',
    month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hourCycle:'h23',weekday:'short'})
    .formatToParts(new Date()).map(p=>[p.type,p.value]));
  const dow=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].indexOf(parts.weekday);
  return {date:`${parts.year}-${parts.month}-${parts.day}`,dow,min:(+parts.hour)*60+(+parts.minute)};
}
function addDays(date,n){const d=new Date(date+'T12:00:00Z');d.setUTCDate(d.getUTCDate()+n);return d.toISOString().slice(0,10)}
function dowOf(date){return new Date(date+'T12:00:00Z').getUTCDay()}
const inR=(r,m)=>(r||[]).some(([s,e])=>s<=m&&m<e);
function dayInfo(S,date){
  const dow=dowOf(date),h=HOL[date];
  if(h&&(h.kind==='closed'||h.kind==='sensitive'))return{none:true,note:h.name_he+' – לא מתקשרים היום'};
  if(dow===6)return{none:true,note:'שבת – לא מתקשרים'};
  const k=String(h&&h.kind==='eve'?5:dow);
  let best=(S.best||{})[k]||[],note='';
  const ma=S.month_avoid,dom=+date.slice(8,10);
  if(ma&&dom>=ma[0]&&dom<=ma[1]){best=[];note='ימי דיווח מע"מ – עדיף אחרי ה-15'}
  if(h&&h.kind==='eve')note=h.name_he+' – רק עד 11:00';
  if(h&&h.kind==='low')note=h.name_he+' – הרבה לא זמינים';
  return{best,avoid:(S.avoid||{})[k]||[],open:S.open?(S.open[k]||[]):null,note};
}
function nextGood(S,now,fromMin,skip){
  for(let i=0;i<10;i++){
    const date=addDays(now.date,i),di=dayInfo(S,date);
    if(di.none)continue;
    for(const [s,e] of di.best){
      if(skip&&skip===date+'|'+s)continue;
      const floor=i===0?fromMin:0;
      if(e-10<=floor)continue;
      return{i,date,min:Math.max(s,floor)};
    }
  }
  return null;
}
function label(n,now){
  if(!n)return'אין חלון בשבוע הקרוב';
  if(n.i===0)return n.min<=now.min?'עכשיו':'היום ב-'+hhmm(n.min);
  if(n.i===1)return'מחר ב-'+hhmm(n.min);
  return'ביום '+DAY[dowOf(n.date)]+' ב-'+hhmm(n.min);
}
function status(S,now){
  const di=dayInfo(S,now.date),nx=()=>label(nextGood(S,now,now.min),now);
  if(di.none)return{cls:'off',text:'⚪ '+di.note+' · הבא: '+nx()};
  if(now.min<450||now.min>=1230)return{cls:'off',text:'⚪ מחוץ לשעות שיחה · הבא: '+nx()};
  if(di.open&&!inR(di.open,now.min))return{cls:'off',text:'⚪ סגור עכשיו · הבא: '+nx()};
  if(inR(di.avoid,now.min))return{cls:'rush',text:'🟠 שעת עומס · עדיף '+nx()};
  if(inR(di.best,now.min))return{cls:'good',good:true,text:'🟢 זמן טוב להתקשר עכשיו'+(di.note?' · '+di.note:'')};
  return{cls:'',text:'אפשר להתקשר · הכי טוב '+nx()+(di.note?' · '+di.note:'')};
}
function local(){try{return JSON.parse(localStorage.getItem(KEY)||'[]')}catch(e){return[]}}
function saveLocal(a){try{localStorage.setItem(KEY,JSON.stringify(a));return true}catch(e){return false}}
function history(L){
  const all=(L.log||[]).concat(local().filter(r=>r.lead_id===L.lead_id)),seen=new Set(),out=[];
  for(const r of all){const k=r.at+'|'+r.result;if(!seen.has(k)){seen.add(k);out.push(r)}}
  return out.sort((a,b)=>a.at<b.at?-1:1);
}
const HE={answered:'ענה',no_answer:'לא ענה',call_back:'לחזור',not_interested:'לא מעוניין',meeting:'פגישה',won:'נסגר ✓',lost:'לא נסגר'};
function followUp(L,now){
  const h=history(L);
  if(!h.length)return{text:'',done:false};
  const res=h.map(r=>r.result),last=h[h.length-1],n=h.length;
  const fin=[...res].reverse().find(r=>['not_interested','won','lost'].includes(r));
  if(fin)return{text:'✔ '+HE[fin]+' · '+n+' שיחות',done:true};
  if(last.result==='meeting')return{text:'📅 נקבעה פגישה',done:true};
  if(last.result==='call_back'&&last.callback_at)return{text:'🔁 לחזור ב-'+last.callback_at.slice(8,10)+'/'+last.callback_at.slice(5,7)+' '+last.callback_at.slice(11,16)};
  const na=res.filter(r=>r==='no_answer').length;
  if(na>=4)return{text:'✋ '+na+' ניסיונות בלי מענה – לשלוח וואטסאפ "ניסיתי להתקשר" ולעצור'};
  const lm=(+last.at.slice(11,13))*60+(+last.at.slice(14,16)),ld=last.at.slice(0,10);
  let skip=null;for(const [s,e] of (dayInfo(L.schedule,ld).best||[]))if(s<=lm&&lm<e)skip=ld+'|'+s;
  let from=now.min;if(ld===now.date)from=Math.max(from,lm+120);
  const S=L.schedule,nx=nextGood(S,now,from,skip);
  return{text:'ניסיונות: '+n+' (אחרון: '+HE[last.result]+') · ניסיון הבא: '+label(nx,now)};
}
function refresh(){
  const now=ilNow();
  document.querySelectorAll('.card').forEach(c=>{
    const L=JSON.parse(c.dataset.lead),fu=followUp(L,now),live=c.querySelector('[data-live]');
    const st=fu.done?{cls:'off',text:'✔ לא צריך להתקשר'}:status(L.schedule,now);
    live.textContent=st.text;live.className='live '+st.cls;c.dataset.good=st.good?'1':'0';
    c.querySelector('[data-fu]').textContent=fu.text;c.classList.toggle('done',!!fu.done);
    const mine=local().filter(r=>r.lead_id===L.lead_id);c.querySelector('[data-undo]').hidden=!mine.length;
  });
  applyFilter();
}
let filter='all';
function applyFilter(){document.querySelectorAll('.card').forEach(c=>{
  c.hidden=!(filter==='all'||(filter==='good'?c.dataset.good==='1':c.dataset.band===filter))})}
const chips=[...document.querySelectorAll('.chips button')];
chips.forEach(b=>b.addEventListener('click',()=>{chips.forEach(x=>x.setAttribute('aria-pressed',String(x===b)));
  filter=b.dataset.filter;applyFilter()}));
function nowStamp(){const n=ilNow();return n.date+' '+hhmm(n.min)}
document.querySelectorAll('.card').forEach(c=>{
  const L=JSON.parse(c.dataset.lead);
  c.querySelectorAll('[data-result]').forEach(b=>b.addEventListener('click',()=>{
    const result=b.dataset.result;let cb='';
    if(result==='call_back'){
      const t=prompt('מתי לחזור? (למשל 15:30, או 2026-11-17 10:00)');if(!t)return;
      cb=/^\d{1,2}:\d{2}$/.test(t.trim())?ilNow().date+' '+t.trim().padStart(5,'0'):t.trim().replace('T',' ');
    }
    if(result==='not_interested'&&!confirm('לסמן "לא מעוניין"? העסק לא יופיע יותר ברשימות.'))return;
    const a=local();a.push({lead_id:L.lead_id,at:nowStamp(),result,callback_at:cb,note:'',name:L.name,profile:L.profile});
    if(!saveLocal(a))alert('לא הצלחתי לשמור בטלפון. רשום ידנית או שלח ל-Claude.');
    refresh();
  }));
  c.querySelector('[data-undo]').addEventListener('click',()=>{
    const a=local();for(let i=a.length-1;i>=0;i--)if(a[i].lead_id===L.lead_id){a.splice(i,1);break}
    saveLocal(a);refresh();
  });
});
document.querySelectorAll('.copy').forEach(b=>b.addEventListener('click',async()=>{
  const t=b.previousElementSibling.textContent;
  try{await navigator.clipboard.writeText(t);b.textContent='Copied ✓'}
  catch(e){const r=document.createRange();r.selectNodeContents(b.previousElementSibling);
    const s=getSelection();s.removeAllRanges();s.addRange(r);b.textContent='Selected, now copy'}
  setTimeout(()=>b.textContent='Copy',2000);
}));
const exp=document.querySelector('[data-export]');
if(exp)exp.addEventListener('click',async()=>{
  const rows=local();if(!rows.length){alert('עוד לא נרשמו שיחות בטלפון הזה.');return}
  const f=['lead_id','at','result','callback_at','note','name','profile'],q=v=>'"'+String(v??'').replace(/"/g,'""')+'"';
  const csv=[f.join(',')].concat(rows.map(r=>f.map(k=>q(r[k])).join(','))).join('\n');
  const name='calls-'+ilNow().date+'.csv',file=new File(['﻿'+csv],name,{type:'text/csv'});
  try{if(navigator.canShare&&navigator.canShare({files:[file]})){await navigator.share({files:[file],title:name});return}}catch(e){}
  const a=document.createElement('a');a.href=URL.createObjectURL(file);a.download=name;a.click();
});
refresh();setInterval(refresh,60000);
"""


def _page(title: str, intro: str, body: str, leads: list[dict]) -> str:
    counts = {b: sum(1 for l in leads if l.get("band") == b) for b in ("Hot", "Warm", "Cold")}
    chips = "".join(
        f'<button type="button" data-filter="{f}" aria-pressed="{str(f == "all").lower()}">{label}</button>'
        for f, label in [("all", f"All {len(leads)}"), ("good", "📞 טוב עכשיו"), ("Hot", f"🔥 Hot {counts['Hot']}"),
                         ("Warm", f"Warm {counts['Warm']}"), ("Cold", f"Cold {counts['Cold']}")])
    from .holidays import upcoming
    hol = json.dumps(upcoming(dt.date.today() - dt.timedelta(days=1)), ensure_ascii=False)
    return f"""<!doctype html>
<html lang="he" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_e(title)}</title>
<style>{CSS}</style>
</head>
<body>
<main>
  {intro}
  <div class="chips" role="group" aria-label="Filter">{chips}</div>
  {body}
  <footer>Made by lead_agent from free OpenStreetMap data and website checks. Call times are estimates by type of
  business (see RESEARCH.md); they learn from your logged calls. Leads marked “not verified yet” haven't been checked
  online. Calls you log here stay on this phone until you press “ייצוא יומן שיחות” and send the file to Claude
  (/find-leads log &lt;file&gt;).</footer>
</main>
<script>const HOL={hol};{JS}</script>
</body>
</html>
"""


TOOLBAR = ('<div class="toolbar" dir="rtl"><button type="button" data-export>⬇︎ ייצוא יומן שיחות</button>'
           '{extra}</div>')


def render_cards(leads: list[dict], meta: dict) -> str:
    city = str(meta.get("city", "")).title()
    created = str(meta.get("created", ""))[:10]
    intro = f"""<h1>Leads · {_e(city)}</h1>
  <p class="sub">{_e(meta.get("category", ""))} · {_e(created)} · {len(leads)} businesses</p>
  <p class="note">The % is an <b>estimate</b> of the chance a business becomes a paying client after one personal
  message or call (Hot ≥ 7%, Warm ≥ 3.5%). The green badge shows who is good to call <b>right now</b> (Israel time).
  Send messages yourself, one at a time, and stop if they say no.</p>
  {TOOLBAR.format(extra="")}"""
    return _page(f"Leads · {city}", intro, "".join(_card(l) for l in leads), leads)


def render_plan(result: dict) -> str:
    day: dt.date = result["date"]
    dow = (day.weekday() + 1) % 7
    from .call_times import DAY_NAMES
    leads = [e["lead"] for e in result["entries"]]
    note = f'<p class="daynote" dir="rtl">{_e(result["day_note"])}</p>' if result.get("day_note") else ""
    blocks = ""
    for b in result["blocks"]:
        n = len(b["entries"])
        blocks += (f'<h3 class="block" dir="rtl">{b["start"]:%H:%M}-{b["end"]:%H:%M} · {n} '
                   f'{"שיחה" if n == 1 else "שיחות"}</h3>')
        blocks += "".join(_card(e["lead"], slot=f"{e['time']:%H:%M}", kind=e["kind"]) for e in b["entries"])
    if not result["entries"]:
        blocks = '<p class="note" dir="rtl">אין שיחות מתוכננות ליום הזה.</p>'
    ics = f"plan-{day.isoformat()}.ics"
    intro = f"""<h1 dir="rtl">תוכנית שיחות · יום {DAY_NAMES[dow]} {day:%d/%m}</h1>
  <p class="sub" dir="rtl">{len(result["entries"])} שיחות ב-{len(result["blocks"])} בלוקים ·
  קודם מי שביקשו שנחזור, אחר כך ניסיונות חוזרים, ואז Hot ו-Warm – כל אחד בשעה הכי טובה שלו.</p>
  {note}
  {TOOLBAR.format(extra=f'<a href="{_e(ics)}" download>📅 הוסף ליומן</a>')}"""
    return _page(f"Call plan · {day.isoformat()}", intro, blocks, leads)
