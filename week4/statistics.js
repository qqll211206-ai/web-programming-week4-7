const tabs = [...document.querySelectorAll('[role=tab]')], charts = [];
function selectTab(index, focus=false) {
 tabs.forEach((tab,i)=>{tab.setAttribute('aria-selected',String(i===index));tab.tabIndex=i===index?0:-1;document.getElementById(`panel-${i}`).hidden=i!==index;});
 if(focus) tabs[index].focus(); requestAnimationFrame(()=>charts[index]?.resize());
}
tabs.forEach((tab,i)=>{tab.addEventListener('click',()=>selectTab(i));tab.addEventListener('keydown',e=>{if(['ArrowRight','ArrowLeft'].includes(e.key)){e.preventDefault();selectTab((i+(e.key==='ArrowRight'?1:tabs.length-1))%tabs.length,true);}})});
async function loadData(){
 const status=document.getElementById('status');
 try {
  const response=await fetch('data/iris.csv'); if(!response.ok) throw new Error(`CSV 요청 실패 (${response.status})`);
  const lines=(await response.text()).trim().split(/\r?\n/), headers=lines.shift().replace(/^\uFEFF/,'').split(',');
  const required=['sepal_length','sepal_width','petal_length','petal_width','species'];
  if(required.some(k=>!headers.includes(k))||new Set(headers).size!==headers.length)throw new Error('필수 열이 없거나 중복되었습니다.');
  const groups=Object.fromEntries(['setosa','versicolor','virginica'].map(k=>[k,[]]));
  lines.forEach((line,i)=>{const cells=line.split(',');if(cells.length!==headers.length)throw new Error(`${i+2}행의 열 개수가 올바르지 않습니다.`);const row=Object.fromEntries(headers.map((h,j)=>[h,cells[j].trim()]));if(required.some(k=>!row[k]))throw new Error(`${i+2}행에 빈 값이 있습니다.`);if(!Object.hasOwn(groups,row.species))throw new Error(`${i+2}행의 종 이름이 올바르지 않습니다.`);for(const key of required.slice(0,4)){if(!/^(?:\d+\.?\d*|\.\d+)$/.test(row[key])||!Number.isFinite(Number(row[key]))||Number(row[key])<=0)throw new Error(`${i+2}행의 수치가 올바르지 않습니다.`);row[key]=Number(row[key]);}groups[row.species].push(row);});
  const labels=Object.keys(groups);if(labels.some(k=>!groups[k].length))throw new Error('표본이 없는 종이 있습니다.');if(typeof Chart==='undefined')throw new Error('차트 라이브러리를 불러오지 못했습니다. 네트워크 연결을 확인해 주세요.');
  ['sepal_length','petal_length'].forEach((key,i)=>{const means=labels.map(k=>groups[k].reduce((sum,row)=>sum+row[key],0)/groups[k].length);charts[i]=new Chart(document.getElementById(`chart-${i}`),{type:'bar',data:{labels,datasets:[{label:'평균 길이 (cm)',data:means,backgroundColor:['#87aa82','#d9ad6a','#688f9b']}]},options:{responsive:true,maintainAspectRatio:false,scales:{x:{title:{display:true,text:'붓꽃 종'}},y:{beginAtZero:true,title:{display:true,text:'평균 길이 (cm)'}}}}});document.getElementById(`explain-${i}`).textContent=`표본에서 ${labels.map((k,j)=>`${k}의 평균은 ${means[j].toFixed(2)}cm`).join(', ')}입니다. 종별 평균을 비교하기 위해 막대그래프를 사용했습니다. 이 표본의 평균은 개체별 분포나 모든 붓꽃의 특성을 나타내지는 않습니다.`;});
  status.textContent=`${lines.length}개 표본을 불러왔습니다. 각 종: ${labels.map(k=>`${k} ${groups[k].length}개`).join(', ')}.`;
 }catch(e){status.textContent=`데이터를 표시할 수 없습니다: ${e.message}`;}
}
loadData();
