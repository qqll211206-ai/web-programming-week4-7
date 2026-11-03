'use strict';
const form=document.querySelector('#image-form'), file=form.elements.image, button=document.querySelector('#fetch-button'), status=document.querySelector('#status'), times=document.querySelector('#times'), original=document.querySelector('#original'), result=document.querySelector('#result');
let originalUrl=null,resultUrl=null;
file.addEventListener('change',()=>{if(originalUrl)URL.revokeObjectURL(originalUrl);originalUrl=null;original.hidden=true;if(file.files[0]){originalUrl=URL.createObjectURL(file.files[0]);original.src=originalUrl;original.hidden=false}});
button.addEventListener('click',async()=>{
 if(!form.reportValidity())return;
 button.disabled=true;status.textContent='처리 중입니다…';times.textContent='';
 try {const started=performance.now();const response=await fetch(form.action,{method:'POST',body:new FormData(form)});if(!response.ok){let message='이미지를 처리하지 못했습니다.';try{message=(await response.json()).error||message}catch{}throw new Error(message)}const blob=await response.blob();const elapsed=performance.now()-started;if(resultUrl)URL.revokeObjectURL(resultUrl);resultUrl=URL.createObjectURL(blob);result.src=resultUrl;result.hidden=false;times.textContent='알고리즘 '+response.headers.get('X-Compute-Ms')+' ms · 서버 '+response.headers.get('X-Processing-Ms')+' ms · 왕복 '+elapsed.toFixed(1)+' ms';status.textContent='처리가 완료되었습니다.'}
 catch(error){status.textContent=error.message||'요청에 실패했습니다.'}finally{button.disabled=false}
});
window.addEventListener('pagehide',()=>{if(originalUrl)URL.revokeObjectURL(originalUrl);if(resultUrl)URL.revokeObjectURL(resultUrl)});
