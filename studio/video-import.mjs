import {readFile,mkdir,copyFile} from 'node:fs/promises';
import path from 'node:path';
import {randomUUID} from 'node:crypto';
import {createAssetStore} from './assets.mjs';
async function sourceState(directory){
  try{return JSON.parse(await readFile(path.join(directory,'state.json'),'utf8'));}
  catch(e){if(e.code==='ENOENT')return {projects:[],channels:[]};throw e;}
}
export async function listVideoSources(directory){
  return ((await sourceState(directory)).projects||[]).map(p=>({id:p.id,topic:p.topic,scenes:p.scenes?.length||0}));
}
export async function importVideoSource(source,destination,id){
  const state=await sourceState(source),original=state.projects?.find(p=>p.id===id);
  if(!original)throw Object.assign(Error('Không tìm thấy dự án gốc.'),{status:404});
  const channel=structuredClone(state.channels?.find(c=>c.id===original.channelId)||{name:'Video nhập',type:'faceless',characters:[],identity:{}});
  const project=structuredClone(original);
  channel.id=randomUUID();delete channel.surveyId;delete channel.nicheLock;
  project.id=randomUUID();project.channelId=channel.id;project.step=5;
  project.approved=(project.approved||[]).filter(n=>n!==5);project.done=false;
  for(const key of ['renderJobId','buildResult','buildError','nicheLock'])delete project[key];
  const from=createAssetStore(path.join(source,'assets')),to=createAssetStore(path.join(destination,'assets'));
  const refs=new Set();
  function walk(value){if(typeof value==='string'&&value.startsWith('/api/assets/'))refs.add(value);else if(value&&typeof value==='object')Object.values(value).forEach(walk);}
  walk({channel,project});await mkdir(path.join(destination,'assets'),{recursive:true});
  for(const url of refs){const origin=from.info(url),target=to.info(url);try{await copyFile(origin.file,target.file);}catch(e){if(e.code==='ENOENT')throw Object.assign(Error('Media của dự án gốc không còn trên máy. Hãy nhập lại ảnh/voice trong Studio gốc trước.'),{status:422});throw e;}}
  // Import nhúng cũ cũng dùng kho media của app mới.
  await to.externalize({channel,project});
  return {channel,project};
}
