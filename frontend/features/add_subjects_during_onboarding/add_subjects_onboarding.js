(() => {
'use strict';
const config={"actions":[{"authentication":"required","function_id":"capability_add_subjects_during_onboarding_c90dae67.function.create_subject","id":"capability_add_subjects_during_onboarding_c90dae67.screen-action.add_subject","method":"POST","request_schema":{"properties":{"name":{"description":"The subject name entered by the student (e.g., Maths, English, Science)","maxLength":100,"minLength":1,"type":"string"}},"required":["name"],"type":"object"},"response_schema":{"properties":{"created_at":{"description":"Timestamp when the subject was created","format":"date-time","type":"string"},"id":{"description":"Unique identifier for the created subject","format":"uuid","type":"string"},"name":{"description":"The subject name","type":"string"},"student_id":{"description":"The authenticated student's ID","format":"uuid","type":"string"}},"required":["id","name","student_id","created_at"],"type":"object"},"route":"/api/capability_add_subjects_during_onboarding_c90dae67/subjects","success_route":null},{"authentication":"required","function_id":"capability_add_subjects_during_onboarding_c90dae67.function.list_subjects","id":"capability_add_subjects_during_onboarding_c90dae67.screen-action.load_subjects","method":"GET","request_schema":{"properties":{},"type":"object"},"response_schema":{"properties":{"subjects":{"items":{"properties":{"created_at":{"description":"Timestamp when the subject was created","format":"date-time","type":"string"},"id":{"description":"Unique identifier for the subject","format":"uuid","type":"string"},"name":{"description":"The subject name","type":"string"},"student_id":{"description":"The student's ID","format":"uuid","type":"string"}},"required":["id","name","student_id","created_at"],"type":"object"},"type":"array"}},"required":["subjects"],"type":"object"},"route":"/api/capability_add_subjects_during_onboarding_c90dae67/subjects","success_route":null}],"screen_route":"/onboarding/subjects"};
const actionById=new Map(config.actions.map(action=>[action.id,action]));
const routeNames=template=>[...String(template||'').matchAll(/\{([A-Za-z_]\w*)\}/g)].map(match=>match[1]);
const previewValue=name=>name.endsWith('_id')||name==='id'?'example-id':'example';
const routeValues=()=>{
  const names=routeNames(config.screen_route);
  const pattern='^'+String(config.screen_route||'/').replace(/[.*+?^${}()|[\]\\]/g,'\\$&').replace(/\\\{([A-Za-z_]\w*)\\\}/g,'([^/]+)')+'$';
  const match=location.pathname.match(new RegExp(pattern));
  return Object.fromEntries(names.map((name,index)=>[name,match?decodeURIComponent(match[index+1]||''):previewValue(name)]));
};
const materialize=(template,values)=>String(template||'').replace(/\{([A-Za-z_]\w*)\}/g,(_,name)=>encodeURIComponent(values[name]??previewValue(name)));
const valueAt=(value,path)=>String(path||'').split('.').reduce((current,key)=>current&&typeof current==='object'?current[key]:undefined,value);
const display=value=>value==null?'—':typeof value==='object'?JSON.stringify(value):String(value);
const render=(payload,scope=document)=>scope.querySelectorAll('[data-bind]').forEach(node=>{
  const value=valueAt(payload,node.dataset.bind);
  if(value===undefined)return;
  if(Array.isArray(value)){
    const template=node.firstElementChild?.cloneNode(true);node.replaceChildren();
    value.forEach(item=>{if(template){const child=template.cloneNode(true);render(item,child);node.append(child);}else{const child=document.createElement('div');child.className='generated-item';child.textContent=display(item);node.append(child);}});
  }else node.textContent=display(value);
});
const region=(root,name)=>root.querySelector(`[data-${name}-region]`)||document.querySelector(`[data-${name}-region]`);
const show=(root,name,message)=>{const target=region(root,name);if(target){target.hidden=false;if(message)target.textContent=message;}};
const loading=(root,value)=>{root.dataset.loading=String(Boolean(value));root.querySelectorAll('button,input,textarea,select').forEach(node=>node.disabled=Boolean(value));};
const valuesFrom=root=>{const form=root.tagName==='FORM'?root:root.querySelector('form');return form?Object.fromEntries(new FormData(form).entries()):{};};
const coerce=(values,schema)=>Object.fromEntries(Object.entries(values).map(([key,value])=>{const rules=schema?.properties?.[key]||{};if(rules.type==='integer')return[key,Number.parseInt(value,10)];if(rules.type==='number')return[key,Number(value)];if(rules.type==='boolean')return[key,['true','1','on','yes'].includes(String(value).toLowerCase())];return[key,value];}));
const execute=async(root,action)=>{
  const requestSchema=action.request_schema||{};const requestValues=coerce(valuesFrom(root),requestSchema);const values={...routeValues(),...requestValues};let url=materialize(action.route,values);
  for(const name of requestSchema.required||[]){if(requestValues[name]===''||requestValues[name]===undefined){show(root,'error',`${name.replaceAll('_',' ')} is required.`);return;}}
  const pathNames=new Set(routeNames(action.route));const allowed=new Set(Object.keys(requestSchema.properties||{}));const body=Object.fromEntries(Object.entries(requestValues).filter(([key,value])=>allowed.has(key)&&!pathNames.has(key)&&value!==''));
  const headers={Accept:'application/json'};const token=localStorage.getItem('zorentia_access_token');if(action.authentication==='required'&&!token&&!window.__ZORENTIA_PREVIEW__){show(root,'error','Please sign in before using this action.');return;}if(token)headers.Authorization=`Bearer ${token}`;
  const options={method:action.method,headers};
  if(['GET','HEAD'].includes(action.method)){const query=new URLSearchParams(Object.entries(body));if(query.size)url+=`${url.includes('?')?'&':'?'}${query}`;}
  else{headers['Content-Type']='application/json';options.body=JSON.stringify(body);}
  loading(root,true);const errorRegion=region(root,'error');if(errorRegion)errorRegion.hidden=true;
  try{const response=await fetch(url,options);const payload=await response.json().catch(()=>({}));if(!response.ok)throw new Error(payload.message||payload.error||`Request failed (${response.status})`);if(payload.token)localStorage.setItem('zorentia_access_token',payload.token);render(payload,root);show(root,'success');if(action.success_route&&!window.__ZORENTIA_PREVIEW__)location.href=materialize(action.success_route,{...values,...payload});}
  catch(error){show(root,'error',error?.message||'Something went wrong. Please try again.');}
  finally{loading(root,false);}
};
document.querySelectorAll('[data-action-id]').forEach(root=>{
  const action=actionById.get(root.dataset.actionId);if(!action)return;
  if(root.tagName==='FORM')root.addEventListener('submit',event=>{event.preventDefault();execute(root,action);});
  else root.addEventListener('click',event=>{if(event.target.closest('button,[data-trigger]'))execute(root,action);});
  if(['GET','HEAD'].includes(action.method)&&root.dataset.autoload==='true')execute(root,action);
});
})();

// Enable continue button when subjects are loaded and at least one exists
document.addEventListener('data-loaded', function(e) {
  if (e.detail.actionId === 'capability_add_subjects_during_onboarding_c90dae67.screen-action.load_subjects') {
    const subjects = e.detail.data?.subjects || [];
    const continueBtn = document.querySelector('[data-continue-button]');
    if (continueBtn) {
      continueBtn.disabled = subjects.length === 0;
    }
  }
});

// After successful subject addition, clear the input and reload subjects
document.addEventListener('action-success', function(e) {
  if (e.detail.actionId === 'capability_add_subjects_during_onboarding_c90dae67.screen-action.add_subject') {
    const input = document.getElementById('subject-name');
    if (input) {
      input.value = '';
      input.focus();
    }
    // Trigger reload of subjects list
    const loadSection = document.querySelector('[data-action-id="capability_add_subjects_during_onboarding_c90dae67.screen-action.load_subjects"]');
    if (loadSection) {
      loadSection.dispatchEvent(new CustomEvent('reload-data'));
    }
  }
});

// Continue button navigation
document.querySelector('[data-continue-button]')?.addEventListener('click', function() {
  if (!this.disabled) {
    window.location.href = '/';
  }
});