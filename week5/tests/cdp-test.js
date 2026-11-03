// 실행 전: 로컬 HTTP 서버(8766)와 Chrome DevTools 포트(9223)를 켭니다.
const assert=require('node:assert/strict');
const URL_BASE='http://127.0.0.1:8766/week5/';
async function connect(url){
 const target=await (await fetch('http://127.0.0.1:9223/json/new?'+encodeURIComponent(url),{method:'PUT'})).json();
 const ws=new WebSocket(target.webSocketDebuggerUrl);await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject});
 let seq=0,pending=new Map(),errors=[];ws.onmessage=e=>{const msg=JSON.parse(e.data);if(msg.id){const p=pending.get(msg.id);pending.delete(msg.id);if(msg.error)p.reject(Error(JSON.stringify(msg.error)));else p.resolve(msg.result)}else if(msg.method==='Runtime.exceptionThrown')errors.push(msg.params.exceptionDetails.text);else if(msg.method==='Runtime.consoleAPICalled'&&msg.params.type==='error')errors.push('console.error')};
 const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}))});
 await send('Runtime.enable');await send('Page.enable');await send('Emulation.setDeviceMetricsOverride',{width:375,height:800,deviceScaleFactor:1,mobile:true});
 async function evaluate(expression){const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text);return r.result.value}
 async function ready(){for(let i=0;i<100;i++){if(await evaluate("document.readyState==='complete' && !!document.querySelector('#refresh-storage')"))return;await new Promise(r=>setTimeout(r,50))}throw Error('page timeout')}
 async function reload(){await send('Page.reload');await new Promise(r=>setTimeout(r,150));await ready()}
 await ready();return {send,evaluate,reload,errors,ws,target};
}
(async()=>{
 const p=await connect(URL_BASE),e=p.evaluate;
 const click=text=>e("Array.from(document.querySelectorAll('button')).find(b=>b.textContent==="+JSON.stringify(text)+").click()");
 const q=async()=>await e("JSON.parse(sessionStorage.getItem('week5.balance.draft'))");
 await e("sessionStorage.removeItem('week5.balance.draft');localStorage.removeItem('week5.balance.history');localStorage.setItem('other.week','keep')");
 await p.reload();
 await e("document.querySelector('#nickname').value='<b>test</b>'");await click('게임 시작');
 await e("document.querySelector('.choice').click()");await e("document.querySelector('.choice').click()");
 assert.equal((await q()).index,2);await p.reload();assert.equal(await e("document.querySelector('#game').textContent.includes('<b>test</b>')"),true);assert.equal(await e("document.querySelector('#game b')===null"),true);
 await click('이어서 하기');assert.equal((await q()).index,2);console.log('PASS refresh/resume, answers, nickname and HTML injection');
 const second=await connect(URL_BASE);assert.equal(await second.evaluate("sessionStorage.getItem('week5.balance.draft')"),null);second.ws.close();console.log('PASS independent tab has no draft');
 for(let i=2;i<8;i++)await e("document.querySelector('.choice').click()");
 await e("const b=document.querySelector('#game .primary');b.click();b.click()");assert.equal(await e("JSON.parse(localStorage.getItem('week5.balance.history')).length"),1);
 await click('다음 친구 도전하기');assert.equal(await e("sessionStorage.getItem('week5.balance.draft')"),null);assert.equal(await e("JSON.parse(localStorage.getItem('week5.balance.history')).length"),1);
 const reopened=await connect(URL_BASE);assert.equal(await reopened.evaluate("JSON.parse(localStorage.getItem('week5.balance.history')).length"),1);reopened.ws.close();
 await p.reload();assert.equal(await e("JSON.parse(localStorage.getItem('week5.balance.history')).length"),1);console.log('PASS completion, duplicate click and reload persistence');
 await e("document.querySelector('#nickname').value='friend'");await click('게임 시작');for(let i=0;i<8;i++)await e("document.querySelectorAll('.choice')[1].click()");
 await click('결과 확인하기');assert.equal(await e("document.querySelector('#game').textContent.includes('같은 선택 0개, 다른 선택 8개')"),true);
 assert.equal(await e("JSON.parse(localStorage.getItem('week5.balance.history')).length"),2);console.log('PASS second participant and 0/8 comparison');
 await e("document.querySelector('#history button').click()");await p.reload();assert.equal(await e("JSON.parse(localStorage.getItem('week5.balance.history')).length"),1);
 await e("document.querySelector('#nickname').value='draft'");await click('게임 시작');await e("document.querySelector('.choice').click()");await click('진행 기록 삭제');await p.reload();assert.equal(await e("sessionStorage.getItem('week5.balance.draft')"),null);
 await click('완료 기록 모두 삭제');await p.reload();assert.equal(await e("localStorage.getItem('week5.balance.history')"),null);assert.equal(await e("localStorage.getItem('other.week')"),'keep');console.log('PASS individual, draft and all deletions across reload; other key preserved');
 for(const bad of ['{broken','123']){await e("sessionStorage.setItem('week5.balance.draft',"+JSON.stringify(bad)+");localStorage.setItem('week5.balance.history',"+JSON.stringify(bad)+")");await p.reload();assert.equal(await e("document.querySelector('#notice').textContent.length>0"),true);assert.equal(await e("!!document.querySelector('#nickname')"),true);await click('완료 기록 모두 삭제');await click('진행 기록 삭제');}console.log('PASS malformed JSON and invalid shape');
 await e("Storage.prototype.setItem=function(){throw new Error('blocked')}");await click('게임 시작');assert.equal(await e("document.querySelector('#notice').textContent.includes('저장 공간')"),true);assert.equal(await e("!!document.querySelector('.choice')"),true);await p.reload();console.log('PASS blocked storage write keeps page usable and displays warning');
 assert.equal(await e("document.documentElement.scrollWidth<=innerWidth"),true);assert.deepEqual(p.errors,[]);console.log('PASS 375px viewport without horizontal overflow and no console exceptions');
 await e("localStorage.removeItem('other.week')");await p.send('Page.close');p.ws.close();
})().catch(err=>{console.error(err);process.exitCode=1});
