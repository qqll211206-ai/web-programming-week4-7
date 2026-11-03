// Requires local TTS server on 8768 and Chrome DevTools on 9224.
const assert=require('node:assert/strict');
(async()=>{
 const target=await (await fetch('http://127.0.0.1:9224/json/new?'+encodeURIComponent('http://127.0.0.1:8768/tts'),{method:'PUT'})).json();
 const ws=new WebSocket(target.webSocketDebuggerUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j});let id=0;const pending=new Map(),errors=[];
 ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result)}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text)};
 const send=(method,params={})=>new Promise((resolve,reject)=>{let n=++id;pending.set(n,{resolve,reject});ws.send(JSON.stringify({id:n,method,params}))});
 const ev=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
 await send('Runtime.enable');await send('Emulation.setDeviceMetricsOverride',{width:375,height:800,deviceScaleFactor:1,mobile:true});
 for(let i=0;i<100;i++){if(await ev("document.readyState==='complete' && !!document.querySelector('.preset')"))break;await new Promise(r=>setTimeout(r,50))}
 await ev("document.querySelector('.preset').click();document.querySelector('#tts-form').requestSubmit()");
 for(let i=0;i<100;i++){await new Promise(r=>setTimeout(r,50));if(await ev("!document.querySelector('#tts-button').disabled"))break}
 assert.equal(await ev("document.querySelector('#status').textContent.includes('모델')"),true);
 assert.equal(await ev("document.documentElement.scrollWidth<=innerWidth"),true);assert.deepEqual(errors,[]);
 console.log('PASS preset, missing-model error, button recovery and 375px viewport');await send('Page.close');ws.close();
})().catch(e=>{console.error(e);process.exitCode=1});
