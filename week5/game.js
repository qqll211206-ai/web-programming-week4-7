'use strict';
// 각 질문의 A는 조용한 선택, B는 활동적인 선택입니다.
const questions = [
 {id:'study', text:'공부를 시작할 때 더 끌리는 곳은?', options:['조용한 스터디룸','친구와 함께하는 열린 공간']},
 {id:'lunch', text:'점심시간, 오늘의 식사는?', options:['혼자 천천히 식사하기','친구들과 함께 메뉴 고르기']},
 {id:'break', text:'수업 사이에 한 시간이 생겼다면?', options:['좋아하는 책 읽기','캠퍼스 행사 구경하기']},
 {id:'walk', text:'잔디밭을 지나는 방법은?', options:['벤치에 앉아 풍경 감상하기','친구와 새 산책길 찾아보기']},
 {id:'project', text:'팀 과제에서 맡고 싶은 역할은?', options:['자료를 차분히 정리하기','아이디어를 발표하고 토론하기']},
 {id:'rain', text:'비가 오는 공강 시간에는?', options:['창가에서 음악 듣기','친구와 실내 전시 보러 가기']},
 {id:'dinner', text:'하루를 마친 저녁에는?', options:['따뜻한 음료와 혼자 쉬기','친구들과 새로운 식당 가기']},
 {id:'weekend', text:'주말 캠퍼스에서 하고 싶은 일은?', options:['한적한 곳에서 일기 쓰기','동아리 활동에 참여하기']}
];
const VERSION=1, DRAFT='week5.balance.draft', HISTORY='week5.balance.history', LIMIT=20;
const game=document.getElementById('game'), notice=document.getElementById('notice');
let draft=null, currentResult=null, messages=[], completedIds=new Set();
// 접근 자체가 차단된 브라우저에서도 저장 오류를 화면에 표시합니다.
function storageOrFallback(name){try{return window[name]}catch(e){return {getItem(){throw e},setItem(){throw e},removeItem(){throw e}}}}
const sessionStore=storageOrFallback('sessionStorage'), localStore=storageOrFallback('localStorage');
function warn(message){if(!messages.includes(message))messages.push(message);notice.textContent=messages.join('\n');}
function readStorage(storage,key,validator,fallback){
 try {const raw=storage.getItem(key);if(raw===null)return fallback;const value=JSON.parse(raw);if(!validator(value))throw new Error('shape');return value;}
 catch(e){warn(key===DRAFT?'진행 기록을 읽을 수 없어 새 게임을 준비했어요. 저장 데이터 삭제 버튼으로 정리할 수 있어요.':'완료 기록을 읽을 수 없어요. 손상된 기록을 삭제하거나 저장 설정을 확인해 주세요.');return fallback;}
}
function writeStorage(storage,key,value){try{storage.setItem(key,JSON.stringify(value));return true}catch(e){warn('브라우저 저장 공간을 사용할 수 없어 새로고침 후 기록이 남지 않을 수 있어요.');return false}}
function removeStorage(storage,key){try{storage.removeItem(key);return true}catch(e){warn('저장 데이터를 삭제하지 못했어요. 브라우저 저장 설정을 확인해 주세요.');return false}}
function validAnswers(a,complete=false){return Array.isArray(a)&&a.length<=(complete?questions.length:questions.length)&&(!complete||a.length===questions.length)&&a.every((v,i)=>v&&typeof v==='object'&&!Array.isArray(v)&&v.id===questions[i].id&&(v.choice===0||v.choice===1));}
function validBase(v){return v&&typeof v==='object'&&!Array.isArray(v)&&v.version===VERSION&&typeof v.id==='string'&&v.id.length>0&&v.id.length<=100&&typeof v.nickname==='string'&&v.nickname.length>0&&v.nickname.length<=30;}
function validDraft(v){return !!(validBase(v)&&validAnswers(v.answers)&&Number.isInteger(v.index)&&v.index===v.answers.length);}
function resultFor(answers){const active=answers.filter(a=>a.choice===1).length;return active<=2?'quiet':active>=6?'active':'balanced';}
const types={
 quiet:{title:'고요한 충전형',icon:'🌿',description:'차분한 순간에서 에너지를 얻는 당신. 나만의 속도로 캠퍼스를 즐겨요.',tip:'오늘의 제안: 좋아하는 자리에서 잠깐 숨을 고르세요.'},
 active:{title:'활동 탐험형',icon:'☀️',description:'사람과 새로운 경험에서 에너지를 얻는 당신. 캠퍼스의 새로운 장면을 만나 보세요.',tip:'오늘의 제안: 가 보지 않은 산책길을 친구에게 소개해 보세요.'},
 balanced:{title:'느긋한 균형형',icon:'🍀',description:'혼자만의 시간과 함께하는 시간을 골고루 즐기는 당신. 그날의 기분을 따라가 보세요.',tip:'오늘의 제안: 오늘 필요한 휴식과 만남을 하나씩 골라 보세요.'}
};
function validRecord(v){return !!(validBase(v)&&validAnswers(v.answers,true)&&typeof v.result==='string'&&v.result===resultFor(v.answers)&&typeof v.completedAt==='string'&&!Number.isNaN(Date.parse(v.completedAt)));}
function validHistory(v){return Array.isArray(v)&&v.length<=LIMIT&&v.every(validRecord)&&new Set(v.map(x=>x.id)).size===v.length;}
function getDraft(){return readStorage(sessionStore,DRAFT,validDraft,null)}
function getHistory(){return readStorage(localStore,HISTORY,validHistory,[])}
function makeId(){return globalThis.crypto?.randomUUID?.() || Date.now().toString(36)+'-'+Math.random().toString(36).slice(2)+'-'+Math.random().toString(36).slice(2)}
function node(tag,text,cls){const el=document.createElement(tag);if(text!==undefined)el.textContent=text;if(cls)el.className=cls;return el}
function button(text,fn,cls){const b=node('button',text,cls);b.type='button';b.addEventListener('click',fn);return b}
function clear(node){node.replaceChildren()}
function showStart(saved){
 currentResult=null;clear(game);game.append(node('p','YOUR DAY, YOUR CHOICE','eyebrow'),node('h2','나의 캠퍼스 하루 시작하기'),node('p','실명, 학번, 연락처 대신 가벼운 별명을 사용해 주세요.','hint'));
 if(saved){const p=node('p',saved.nickname+'님의 진행 기록: '+saved.index+' / '+questions.length+'문항','tag');game.append(p,button('이어서 하기',()=>{draft=saved;renderQuestion()},'primary'));const actions=node('div',undefined,'actions');actions.append(button('새로 시작',()=>startForm()));game.append(actions);}
 else startForm();
}
function startForm(){draft=null;clear(game);game.append(node('p','YOUR DAY, YOUR CHOICE','eyebrow'),node('h2','나의 캠퍼스 하루 시작하기'),node('p','실명, 학번, 연락처 대신 가벼운 별명을 사용해 주세요.','hint'));const label=node('label','별명 (선택)');label.htmlFor='nickname';const input=node('input');input.id='nickname';input.maxLength=30;input.placeholder='예: 초록별';input.autocomplete='off';const actions=node('div',undefined,'actions');actions.append(button('게임 시작',()=>{const nickname=input.value.trim().slice(0,30)||'캠퍼스 친구';draft={version:VERSION,id:makeId(),nickname,index:0,answers:[]};writeStorage(sessionStore,DRAFT,draft);renderQuestion();refreshStorage()},'primary'));game.append(label,input,actions)}
function renderQuestion(){
 if(!draft)return;clear(game);const n=draft.index;game.append(node('p',draft.nickname+'님의 선택 · '+n+' / '+questions.length,'tag'));const bar=node('div',undefined,'progress');bar.setAttribute('aria-label','진행률 '+n+' / '+questions.length);const fill=node('span');fill.style.width=(n/questions.length*100)+'%';bar.append(fill);game.append(bar);
 if(n===questions.length){game.append(node('h2','모든 선택을 마쳤어요!'),node('p','결과를 확인하고 이 기기에 기록을 남겨 보세요.'),button('결과 확인하기',finish,'primary'));return}
 const q=questions[n];game.append(node('p','QUESTION '+String(n+1).padStart(2,'0'),'eyebrow'),node('h2',q.text));const choices=node('div',undefined,'choices');q.options.forEach((option,i)=>choices.append(button((i===0?'A  ':'B  ')+option,()=>{if(!draft||draft.index!==n)return;draft.answers.push({id:q.id,choice:i});draft.index++;writeStorage(sessionStore,DRAFT,draft);renderQuestion();refreshStorage()},'choice')));game.append(choices,node('p','선택하면 다음 질문으로 넘어갑니다.','hint'));
}
function finish(){
 if(!draft||draft.index!==questions.length||completedIds.has(draft.id))return;
 const record={version:VERSION,id:draft.id,nickname:draft.nickname,answers:draft.answers.map(a=>({...a})),result:resultFor(draft.answers),completedAt:new Date().toISOString()};
 const history=getHistory();if(!history.some(r=>r.id===record.id)){if(!writeStorage(localStore,HISTORY,[record,...history].slice(0,LIMIT))){warn('완료 결과를 저장하지 못해 진행 기록을 유지합니다.');return}}
 completedIds.add(record.id);removeStorage(sessionStore,DRAFT);draft=null;currentResult=record;renderResult(record);refreshStorage();
}
function renderResult(record){
 clear(game);const type=types[record.result];game.append(node('p','YOUR CAMPUS TYPE','eyebrow'),node('div',type.icon,'result-icon'),node('h2',record.nickname+'님은 '+type.title+'!'),node('p',type.description),node('p',type.tip,'tag'));
 const previous=getHistory().find(r=>r.id!==record.id);if(previous){const same=record.answers.filter((a,i)=>a.choice===previous.answers[i].choice).length;game.append(node('p',previous.nickname+'님과 같은 선택 '+same+'개, 다른 선택 '+(questions.length-same)+'개예요.','hint'))}
 const actions=node('div',undefined,'actions');actions.append(button('다음 친구 도전하기',()=>{currentResult=null;startForm()},'primary'));game.append(actions);
}
function refreshStorage(){
 const storedDraft=getDraft(),history=getHistory(),summary=document.getElementById('draft-summary'),list=document.getElementById('history');summary.textContent=storedDraft?'진행 중: '+storedDraft.nickname+' · '+storedDraft.index+' / '+questions.length:'저장된 진행 기록이 없습니다.';clear(list);
 if(!history.length){list.append(node('li','저장된 완료 기록이 없습니다.','empty'));return}
 history.forEach(record=>{const item=node('li');item.append(node('strong',record.nickname+' · '+types[record.result].title),node('p',new Date(record.completedAt).toLocaleString('ko-KR'),'small'),button('이 기록 삭제',()=>{const now=getHistory();if(writeStorage(localStore,HISTORY,now.filter(r=>r.id!==record.id)))refreshStorage()},'danger'));list.append(item)});
}
document.getElementById('refresh-storage').addEventListener('click',refreshStorage);
document.getElementById('delete-draft').addEventListener('click',()=>{if(removeStorage(sessionStore,DRAFT)){draft=null;currentResult=null;showStart(null);refreshStorage()}});
document.getElementById('clear-history').addEventListener('click',()=>{if(removeStorage(localStore,HISTORY))refreshStorage()});
draft=getDraft();showStart(draft);refreshStorage();
