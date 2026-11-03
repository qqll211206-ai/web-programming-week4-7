// Requires the Week 7 local server on 8769 and Chrome DevTools on 9225.
const fs=require('node:fs'),assert=require('node:assert/strict');
(async()=>{
 const target=await (await fetch('http://127.0.0.1:9225/json/new?'+encodeURIComponent('http://127.0.0.1:8769/comments'),{method:'PUT'})).json();
 const ws=new WebSocket(target.webSocketDebuggerUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j});let id=0;const pending=new Map(),errors=[];
 ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result)}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text)};
 const send=(method,params={})=>new Promise((resolve,reject)=>{const n=++id;pending.set(n,{resolve,reject});ws.send(JSON.stringify({id:n,method,params}))});
 const ev=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
 await send('Runtime.enable');await send('Page.enable');await send('Emulation.setDeviceMetricsOverride',{width:1280,height:900,deviceScaleFactor:1,mobile:false});
 for(let i=0;i<100;i++){if(await ev("document.readyState==='complete' && !!document.querySelector('.hero')"))break;await new Promise(r=>setTimeout(r,50))}
 const photo=await send('Page.captureScreenshot',{format:'png'});fs.mkdirSync('week7/screenshots',{recursive:true});fs.writeFileSync('week7/screenshots/board.png',Buffer.from(photo.data,'base64'));
 await send('Emulation.setDeviceMetricsOverride',{width:375,height:800,deviceScaleFactor:1,mobile:true});
 assert.equal(await ev("document.documentElement.scrollWidth<=innerWidth"),true);
 assert.equal(await ev("(async()=> (await fetch('/admin')).status)()"),403);
 assert.equal(await ev("(async()=> (await fetch('/comments',{method:'POST',body:new URLSearchParams({content:'test'})})).status)()"),400);
 assert.deepEqual(errors,[]);console.log('PASS real browser: anonymous board, 375px no overflow, admin 403, CSRF 400; screenshot saved');
 await send('Page.close');ws.close();
})().catch(e=>{console.error(e);process.exitCode=1});
