'use strict';
let state=null, pending=false, timer=null, polling=null;
const $=id=>document.getElementById(id);
const outcomes={investigating:'Case open — investigation in progress',awaiting_rep_verification:'Case open — waiting for you to verify customer recovery',verified_open:'Success verified — case still open until you close it',closed:'Case closed by you'};
function modeHint(){ const hints={answer:'Answer the current question about the same case.',finding:'Keep earlier checked evidence and add what you learned. This does not confirm recovery.',note:'Use only when earlier scope or evidence is wrong. Earlier records will be retired, not silently reused.'};$('mode-hint').textContent=hints[$('mode').value]; }
function row(parent,label,text){const div=document.createElement('div'),head=document.createElement('div'),p=document.createElement('p');head.className='entry-label';head.textContent=label;p.textContent=text;div.append(head,p);parent.append(div);}
function render(){if(!state)return;const busy=pending||state.busy;
 $('family').value=state.family;$('step').textContent=`Example update ${state.step} of ${state.total_steps}`;
 $('customer').textContent=state.customer_update; $('account').textContent=state.account||'';
 $('next').hidden=['resolve_journey','escalate_journey'].includes(state.family);
 $('step').textContent=['resolve_journey','escalate_journey'].includes(state.family)?'Investigation starts with the complaint and account only':`Example update ${state.step} of ${state.total_steps}`;
 $('advice-text').textContent=state.advice?.message||'Read the customer update, then choose “Get advice”.';
 $('question').textContent=state.advice?.suggested_question||(state.advice?.decision?.next?.kind==='suggest_check'?state.advice.decision.next.reason:'');
 $('outcome-label').textContent='Can the customer now complete the original activity?';
 $('status').textContent=outcomes[state.progress.status]||'Case open';
 $('error').hidden=!state.last_error;$('error').textContent=state.last_error||'';
 $('busy').hidden=!busy;
 document.querySelectorAll('button,textarea,select').forEach(el=>el.disabled=busy);
 $('next').disabled=busy||state.step>=state.total_steps||state.progress.closed;
 $('advise').disabled=busy||state.progress.closed||state.progress.outcome==='worked';
 $('send').disabled=busy||state.progress.closed||!$('update').value.trim();
 document.querySelectorAll('[data-outcome]').forEach(el=>el.disabled=busy||!state.progress.proposal_id||state.progress.closed);
 $('close').disabled=busy||state.progress.outcome!=='worked'||state.progress.closed;
 $('mode').options[0].disabled=!state.pending_question;
 if(!state.pending_question)$('mode').value='finding';
 const handoff=state.advice?.handoff;
 $('handoff-section').hidden=!handoff;
 $('handoff-text').textContent=handoff?['Request: '+handoff.proposed_request,'','Known and reported:',...handoff.observations.map(f=>f.value),'','Still unknown:',...handoff.unknowns,'','What happened:',...handoff.history.filter(h=>['read','rep_report','rep_answer','private_advice','rep_control'].includes(h.type)).map(h=>h.text||h.message||JSON.stringify(h))].join('\n'):'';
 $('accept-handoff').disabled=busy||!handoff||!!handoff.accepted_by_rep;
 if(handoff?.accepted_by_rep){$('advise').disabled=true;$('status').textContent='Handoff accepted by you — not sent; recovery unverified';}
 $('checks').replaceChildren();state.checks.forEach(c=>row($('checks'),`${c.name} · ${c.status}`,c.result));
 if(!state.checks.length)row($('checks'),'No checks yet','Copilot has not requested a product record.');
 $('history').replaceChildren();state.notes.forEach(n=>row($('history'),n.kind==='private_advice'?'Private advice — not sent':'You',n.text));
 modeHint();
 if(state.busy&&!polling)polling=setTimeout(async()=>{polling=null;await refresh();},1000);
}
async function refresh(){try{const r=await fetch('/api/state');if(!r.ok)throw Error('Your local session is unavailable. Reload the page.');state=await r.json();render();}catch(e){$('error').hidden=false;$('error').textContent=e.message;}}
async function act(action,extra={}){if(pending||!state)return;pending=true;let started=Date.now();$('elapsed').textContent='';timer=setInterval(()=>$('elapsed').textContent=`${Math.floor((Date.now()-started)/1000)}s`,1000);render();
 try{const r=await fetch('/api/action',{method:'POST',headers:{'Content-Type':'application/json','X-Copilot-Action':'1'},body:JSON.stringify({action,version:state.version,proposal_id:state.progress.proposal_id,...extra})});const data=await r.json();if(data.progress){state=data;if(r.ok&&['answer','note','finding'].includes(action))$('update').value='';if(state.pending_question)$('mode').value='answer';}else throw Error(data.error||'The request could not finish.');}
 catch(e){state.last_error=e.message;}finally{pending=false;clearInterval(timer);timer=null;render();}}
$('accept-handoff').onclick=()=>act('accept_handoff');
$('advise').onclick=()=>act('advice');$('next').onclick=()=>act('next');$('family').onchange=()=>act('start',{family:$('family').value});
$('update-form').onsubmit=e=>{e.preventDefault();act($('mode').value,{text:$('update').value});};
$('mode').onchange=modeHint;$('update').oninput=render;
document.querySelectorAll('[data-outcome]').forEach(b=>b.onclick=()=>act(b.dataset.outcome));
refresh();
