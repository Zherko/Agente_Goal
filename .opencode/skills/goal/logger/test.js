const fs=require('fs'), path=require('path'), os=require('os');
const {append, verify, validateOrder}=require('./index.js');
const slug='test-logger-'+Date.now();
const base=path.join('C:/Users/user/Documents/Default Project/.opencode/goals',slug);
fs.mkdirSync(base,{recursive:true});
// 1. append 3 logs verifica hash chain
append(slug,{step:1,status:'ok',msg:'inicio'});
append(slug,{step:2,status:'ok',msg:'medio'});
append(slug,{step:3,status:'fail',msg:'fallo'});
let v=verify(slug); console.log('verify 3 ok?', v.ok, v.gaps, 'count',v.count);
if(!v.ok) throw new Error('verify fail '+v.gaps);
// 2. rotacion 250 -> 200 activas + 50 archivadas
for(let i=4;i<=250;i++) append(slug,{step:i%5+1,status:'ok',msg:'bulk'+i});
v=verify(slug); console.log('post 250 verify', v.ok, 'count',v.count, 'gaps',v.gaps.slice(0,3));
if(v.count!==200) throw new Error('cap 200 fail '+v.count);
const arch=fs.readdirSync(path.join(base,'archive')); console.log('arch files',arch.length, arch[0]);
if(arch.length===0) throw new Error('no archive');
// 3. validador orden: ok vs permutado
const plan=[{n:1,dependsOn:[]},{n:2,dependsOn:[1]},{n:3,dependsOn:[2]}];
const slug2='test-order-'+Date.now(); fs.mkdirSync(path.join('C:/Users/user/Documents/Default Project/.opencode/goals',slug2),{recursive:true});
append(slug2,{step:1,status:'ok',msg:'1'});
append(slug2,{step:2,status:'ok',msg:'2'});
append(slug2,{step:3,status:'ok',msg:'3'});
let o=validateOrder(slug2, plan); console.log('order ok?', o.ok, o.errors);
if(!o.ok) throw new Error('order ok should pass');
const slug3='test-order-bad-'+Date.now(); fs.mkdirSync(path.join('C:/Users/user/Documents/Default Project/.opencode/goals',slug3),{recursive:true});
append(slug3,{step:2,status:'ok',msg:'2 antes'});
append(slug3,{step:1,status:'ok',msg:'1 despues'});
append(slug3,{step:3,status:'ok',msg:'3'});
o=validateOrder(slug3, plan); console.log('order bad detect?', !o.ok, o.errors[0]);
if(o.ok) throw new Error('order bad should fail');
// 4. corrupcion hash
const p=path.join('C:/Users/user/Documents/Default Project/.opencode/goals',slug,'LOG.jsonl');
let lines=fs.readFileSync(p,'utf8').split('\n').filter(Boolean); let j=JSON.parse(lines[0]); j.hash='ffff'; lines[0]=JSON.stringify(j); fs.writeFileSync(p, lines.join('\n')+'\n');
v=verify(slug); console.log('corrupt detect?', !v.ok, v.gaps[0]); if(v.ok) throw new Error('corrupt should fail');
console.log('ALL GREEN');
