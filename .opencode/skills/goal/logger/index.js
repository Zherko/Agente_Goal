const fs=require('fs'), path=require('path'), crypto=require('crypto');
const LOG_DIR = 'C:/Users/user/Documents/Default Project/.opencode/goals';
function hashEntry(e){ return crypto.createHash('sha256').update(JSON.stringify({seq:e.seq, ts:e.ts, slug:e.slug, step:e.step, status:e.status, prev_hash:e.prev_hash, msg:e.msg})).digest('hex').slice(0,16); }
function logPath(slug){ return path.join(LOG_DIR, slug, 'LOG.jsonl'); }
function archivePath(slug, seq){ return path.join(LOG_DIR, slug, `archive/LOG-${String(seq).padStart(4,'0')}.jsonl`); }

function append(slug, {step, status, msg}){
  const dir=path.join(LOG_DIR, slug); fs.mkdirSync(dir,{recursive:true}); fs.mkdirSync(path.join(dir,'archive'),{recursive:true});
  const p=logPath(slug);
  let lines=[]; if(fs.existsSync(p)) lines=fs.readFileSync(p,'utf8').split('\n').filter(Boolean);
  let prev_hash='0000000000000000'; let seq=1;
  if(lines.length){ const last=JSON.parse(lines[lines.length-1]); prev_hash=last.hash; seq=last.seq+1; }
  const entry={seq, ts:new Date().toISOString(), slug, step, status, prev_hash, msg: msg||''};
  entry.hash=hashEntry(entry);
  const content=(lines.length? lines.join('\n')+'\n':'') + JSON.stringify(entry)+'\n';
  fs.writeFileSync(p, content);
  try{ const fd=fs.openSync(p,'r'); fs.fsyncSync(fd); fs.closeSync(fd);}catch{}
  // rotacion 200
  lines=fs.readFileSync(p,'utf8').split('\n').filter(Boolean);
  if(lines.length>200){
    const overflow=lines.length-200;
    const toArchive=lines.slice(0,overflow);
    const remain=lines.slice(overflow);
    const ap=archivePath(slug, JSON.parse(toArchive[0]).seq);
    fs.writeFileSync(ap, toArchive.join('\n')+'\n');
    fs.writeFileSync(p, remain.join('\n')+'\n');
  }
  return entry;
}
function verify(slug){
  const p=logPath(slug); if(!fs.existsSync(p)) return {ok:true, gaps:[]};
  const lines=fs.readFileSync(p,'utf8').split('\n').filter(Boolean).map(JSON.parse);
  let gaps=[];
  const archDir=path.join(LOG_DIR, slug, 'archive');
  let prev='0000000000000000'; let expected=1;
  if(fs.existsSync(archDir)){
    const files=fs.readdirSync(archDir).filter(f=>f.startsWith('LOG-')).sort();
    for(const f of files){
      const ls=fs.readFileSync(path.join(archDir,f),'utf8').split('\n').filter(Boolean).map(JSON.parse);
      for(const e of ls){ if(e.seq!==expected) gaps.push(`archive seq gap ${e.seq} exp ${expected}`); expected=e.seq+1; if(e.hash!==hashEntry(e)) gaps.push(`archive hash corrupt ${e.seq}`); if(e.prev_hash!==prev) gaps.push(`archive hash gap seq ${e.seq}`); prev=e.hash; }
    }
  }
  for(let i=0;i<lines.length;i++){
    const e=lines[i];
    if(e.seq !== expected) gaps.push(`seq gap at ${e.seq} exp ${expected}`);
    if(e.prev_hash!==prev) gaps.push(`hash gap seq ${e.seq}: prev ${e.prev_hash} != ${prev}`);
    if(e.hash!==hashEntry(e)) gaps.push(`hash corrupt seq ${e.seq}`);
    prev=e.hash; expected=e.seq+1;
  }
  return {ok:gaps.length===0, gaps, count:lines.length};
}
function validateOrder(slug, planSteps){
  // planSteps: [{n, dependsOn:[]}]
  const p=logPath(slug); if(!fs.existsSync(p)) return {ok:true};
  const lines=fs.readFileSync(p,'utf8').split('\n').filter(Boolean).map(JSON.parse);
  const done=new Set(); let errors=[];
  for(const e of lines){
    if(e.status!=='ok' && e.status!=='fail') continue;
    const stepDef=planSteps.find(s=>s.n===e.step);
    if(!stepDef) continue;
    for(const dep of (stepDef.dependsOn||[])){
      if(!done.has(dep)) errors.push(`orden roto: paso ${e.step} ejecutado antes de ${dep} (seq ${e.seq})`);
    }
    if(e.status==='ok') done.add(e.step);
  }
  return {ok:errors.length===0, errors};
}
module.exports={append, verify, validateOrder, hashEntry, logPath};
