import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,readFile,rm} from 'node:fs/promises';
import path from 'node:path';
import {createAssetStore} from './assets.mjs';
import {listVideoSources,importVideoSource} from './video-import.mjs';
test('chép đúng một dự án cùng media, không sửa dữ liệu và khóa Studio gốc',async()=>{
 await mkdir('tmp',{recursive:true});const dir=await mkdtemp(path.resolve('tmp/video-import-'));
 try{const source=path.join(dir,'old'),dest=path.join(dir,'new');await mkdir(source);
 const media=await createAssetStore(path.join(source,'assets')).put('data:image/png;base64,aGVsbG8=');
 const state={channels:[{id:'c',name:'Kênh',characters:[],type:'faceless'}],projects:[{id:'p',channelId:'c',topic:'Đức',narration:'Lời kể.',scenes:[{index:1,narration:'Lời kể.',prompt:'Mô tả.',image:media.url,duration:2}],renderJobId:'old-job',step:3},{id:'other',channelId:'c'}]};
 const before=JSON.stringify(state);await writeFile(path.join(source,'state.json'),before);
 assert.equal((await listVideoSources(source)).length,2);
 const result=await importVideoSource(source,dest,'p');assert.notEqual(result.project.id,'p');assert.equal(result.project.channelId,result.channel.id);assert.equal(result.project.step,5);assert.equal(result.project.renderJobId,undefined);assert.deepEqual(result.project.scenes,state.projects[0].scenes);assert.equal(result.project.narration,state.projects[0].narration);
 assert.equal(createAssetStore(path.join(dest,'assets')).read(media.url).bytes.toString(),'hello');assert.equal(await readFile(path.join(source,'state.json'),'utf8'),before);
 await assert.rejects(importVideoSource(source,dest,'missing'),/Không tìm/);
 }finally{await rm(dir,{recursive:true,force:true});}
});
