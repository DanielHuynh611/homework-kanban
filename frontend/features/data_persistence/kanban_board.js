(() => {
'use strict';
const config={"actions":[{"authentication":"required","function_id":"capability_data_persistence_8e00a8e9.function.list_tasks","id":"capability_data_persistence_8e00a8e9.screen-action.load_tasks","method":"GET","request_schema":{"properties":{},"type":"object"},"response_schema":{"properties":{"tasks":{"items":{"properties":{"created_at":{"format":"date-time","type":"string"},"due_date":{"format":"date","type":"string"},"id":{"format":"uuid","type":"string"},"priority":{"enum":["low","medium","high"],"type":"string"},"status":{"enum":["to_do","in_progress","done"],"type":"string"},"subject_id":{"format":"uuid","type":"string"},"title":{"type":"string"},"updated_at":{"format":"date-time","type":"string"},"user_id":{"format":"uuid","type":"string"}},"required":["id","title","subject_id","due_date","priority","status","user_id","created_at","updated_at"],"type":"object"},"type":"array"}},"required":["tasks"],"type":"object"},"route":"/api/capability_data_persistence_8e00a8e9/tasks","success_route":null},{"authentication":"required","function_id":"capability_data_persistence_8e00a8e9.function.list_subjects","id":"capability_data_persistence_8e00a8e9.screen-action.load_subjects","method":"GET","request_schema":{"properties":{},"type":"object"},"response_schema":{"properties":{"subjects":{"items":{"properties":{"created_at":{"format":"date-time","type":"string"},"id":{"format":"uuid","type":"string"},"name":{"type":"string"},"user_id":{"format":"uuid","type":"string"}},"required":["id","name","user_id","created_at"],"type":"object"},"type":"array"}},"required":["subjects"],"type":"object"},"route":"/api/capability_data_persistence_8e00a8e9/subjects","success_route":null},{"authentication":"required","function_id":"capability_data_persistence_8e00a8e9.function.update_task_status","id":"capability_data_persistence_8e00a8e9.screen-action.move_task","method":"PATCH","request_schema":{"properties":{"status":{"enum":["to_do","in_progress","done"],"type":"string"}},"required":["status"],"type":"object"},"response_schema":{"properties":{"created_at":{"format":"date-time","type":"string"},"due_date":{"format":"date","type":"string"},"id":{"format":"uuid","type":"string"},"priority":{"enum":["low","medium","high"],"type":"string"},"status":{"enum":["to_do","in_progress","done"],"type":"string"},"subject_id":{"format":"uuid","type":"string"},"title":{"type":"string"},"updated_at":{"format":"date-time","type":"string"},"user_id":{"format":"uuid","type":"string"}},"required":["id","title","subject_id","due_date","priority","status","user_id","created_at","updated_at"],"type":"object"},"route":"/api/capability_data_persistence_8e00a8e9/tasks/{task_id}/status","success_route":"/board#create-task"}],"screen_route":"/board"};
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

(function(){
  const API_BASE = '/api/capability_data_persistence_8e00a8e9';
  const statusMap = {
    to_do: 'col-to_do',
    in_progress: 'col-in_progress',
    done: 'col-done'
  };
  const priorityColors = {
    low: '#10B981',
    medium: '#6366F1',
    high: '#C0362C'
  };
  let subjects = {};

  function fetchSubjects(){
    return fetch(`${API_BASE}/subjects`, {credentials:'include'}).then(r=>r.json()).then(data=>{
      data.subjects.forEach(s=>{ subjects[s.id]=s.name; });
    });
  }

  function fetchTasks(){
    return fetch(`${API_BASE}/tasks`, {credentials:'include'}).then(r=>r.json()).then(data=>{
      renderTasks(data.tasks);
    });
  }

  function renderTasks(tasks){
    // Clear columns
    Object.values(statusMap).forEach(colId=>{ document.getElementById(colId).innerHTML=''; });
    const now = new Date();
    tasks.forEach(task=>{
      const card = document.createElement('div');
      card.className = 'data-card task-card';
      card.draggable = true;
      card.dataset.taskId = task.id;
      card.dataset.status = task.status;
      card.style.border = '1px solid #E2E8F0';
      card.style.borderRadius = '14px';
      card.style.padding = '12px';
      card.style.background = '#FFFFFF';
      card.style.boxShadow = '0 2px 6px rgba(0,0,0,0.05)';

      // Title and priority badge
      const header = document.createElement('div');
      header.style.display='flex';
      header.style.justifyContent='space-between';
      header.style.alignItems='center';
      const title = document.createElement('span');
      title.textContent = task.title;
      title.style.fontWeight='600';
      title.style.color='#1E293B';
      const priorityBadge = document.createElement('span');
      priorityBadge.className='badge';
      priorityBadge.textContent = task.priority.charAt(0).toUpperCase()+task.priority.slice(1);
      priorityBadge.style.backgroundColor = priorityColors[task.priority] || '#6366F1';
      priorityBadge.style.color = '#FFFFFF';
      priorityBadge.style.borderRadius='8px';
      priorityBadge.style.padding='2px 6px';
      header.appendChild(title);
      header.appendChild(priorityBadge);
      card.appendChild(header);

      // Body fields
      const body = document.createElement('div');
      body.style.marginTop='8px';
      const subjectField = document.createElement('div');
      subjectField.className='field';
      const subjectLabel = document.createElement('label');
      subjectLabel.className='label';
      subjectLabel.textContent='Subject';
      const subjectValue = document.createElement('span');
      subjectValue.textContent = subjects[task.subject_id] || '—';
      subjectField.appendChild(subjectLabel);
      subjectField.appendChild(subjectValue);

      const dueField = document.createElement('div');
      dueField.className='field';
      const dueLabel = document.createElement('label');
      dueLabel.className='label';
      dueLabel.textContent='Due';
      const dueValue = document.createElement('span');
      dueValue.textContent = task.due_date;
      dueField.appendChild(dueLabel);
      dueField.appendChild(dueValue);

      // Urgency badge
      const urgencyBadge = document.createElement('span');
      urgencyBadge.className='badge';
      const dueDate = new Date(task.due_date);
      const diffDays = Math.floor((dueDate - now)/(1000*60*60*24));
      if(diffDays < 0){
        urgencyBadge.textContent='Overdue';
        urgencyBadge.style.backgroundColor = '#C0362C';
      } else if(diffDays <= 2){
        urgencyBadge.textContent='Due Soon';
        urgencyBadge.style.backgroundColor = '#F59E0B';
      }
      if(urgencyBadge.textContent){
        urgencyBadge.style.color='#FFFFFF';
        urgencyBadge.style.borderRadius='8px';
        urgencyBadge.style.padding='2px 6px';
        urgencyBadge.style.marginLeft='8px';
        header.appendChild(urgencyBadge);
      }

      body.appendChild(subjectField);
      body.appendChild(dueField);
      card.appendChild(body);

      // Drag events
      card.addEventListener('dragstart', e=>{
        e.dataTransfer.setData('text/plain', task.id);
        e.dataTransfer.effectAllowed='move';
      });

      // Append to column
      const colId = statusMap[task.status];
      const col = document.getElementById(colId);
      if(col){ col.appendChild(card); }
    });
  }

  function setupDropZones(){
    Object.entries(statusMap).forEach(([status, colId])=>{
      const col = document.getElementById(colId);
      col.addEventListener('dragover', e=>{ e.preventDefault(); e.dataTransfer.dropEffect='move'; });
      col.addEventListener('drop', e=>{
        e.preventDefault();
        const taskId = e.dataTransfer.getData('text/plain');
        const card = document.querySelector(`.task-card[data-task-id="${taskId}"]`);
        if(!card) return;
        // Optimistic UI move
        col.appendChild(card);
        // Call API to update status
        fetch(`${API_BASE}/tasks/${taskId}/status`, {
          method:'PATCH',
          credentials:'include',
          headers:{'Content-Type':'application/json'},
          body:JSON.stringify({status: status})
        }).then(r=>{
          if(!r.ok){
            // revert UI on error
            const originalCol = document.getElementById(statusMap[card.dataset.status]);
            if(originalCol){ originalCol.appendChild(card); }
          } else {
            card.dataset.status = status;
          }
        }).catch(()=>{
          const originalCol = document.getElementById(statusMap[card.dataset.status]);
          if(originalCol){ originalCol.appendChild(card); }
        });
      });
    });
  }

  document.addEventListener('DOMContentLoaded',()=>{
    Promise.all([fetchSubjects(), fetchTasks()]).then(()=>{
      setupDropZones();
    });
  });
})();