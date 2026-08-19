(() => {
'use strict';
const config={"actions":[{"authentication":"required","function_id":"capability_three_column_kanban_board_7897884e.function.get_kanban_board","id":"capability_three_column_kanban_board_7897884e.screen-action.load_board","method":"GET","request_schema":{},"response_schema":{"properties":{"columns":{"items":{"properties":{"cards":{"items":{"properties":{"homework_card_id":{"format":"uuid","type":"string"},"position":{"minimum":0,"type":"integer"},"status_id":{"format":"uuid","type":"string"},"updated_at":{"format":"date-time","type":"string"}},"required":["status_id","homework_card_id","position","updated_at"],"type":"object"},"type":"array"},"label":{"enum":["To Do","In Progress","Done"],"type":"string"},"name":{"enum":["to_do","in_progress","done"],"type":"string"}},"required":["name","label","cards"],"type":"object"},"type":"array"}},"required":["columns"],"type":"object"},"route":"/api/capability_three_column_kanban_board_7897884e/kanban/board","success_route":null},{"authentication":"required","function_id":"capability_three_column_kanban_board_7897884e.function.move_card","id":"capability_three_column_kanban_board_7897884e.screen-action.move_card_to_column","method":"PATCH","request_schema":{"properties":{"column_name":{"enum":["to_do","in_progress","done"],"type":"string"},"position":{"minimum":0,"type":"integer"}},"required":["column_name","position"],"type":"object"},"response_schema":{"properties":{"column_name":{"enum":["to_do","in_progress","done"],"type":"string"},"homework_card_id":{"format":"uuid","type":"string"},"id":{"format":"uuid","type":"string"},"position":{"minimum":0,"type":"integer"},"updated_at":{"format":"date-time","type":"string"},"user_id":{"format":"uuid","type":"string"}},"required":["id","homework_card_id","user_id","column_name","position","updated_at"],"type":"object"},"route":"/api/capability_three_column_kanban_board_7897884e/kanban/card-status/{status_id}/move","success_route":null}],"screen_route":"/board"};
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

(function() {
  let draggedCard = null;
  let draggedStatusId = null;
  let sourceColumn = null;

  document.addEventListener('dragstart', function(e) {
    if (e.target.classList.contains('kanban-card')) {
      draggedCard = e.target;
      draggedStatusId = e.target.getAttribute('data-bind-id');
      sourceColumn = e.target.closest('.kanban-column-body');
      e.target.style.opacity = '0.4';
    }
  });

  document.addEventListener('dragend', function(e) {
    if (e.target.classList.contains('kanban-card')) {
      e.target.style.opacity = '1';
      draggedCard = null;
      draggedStatusId = null;
      sourceColumn = null;
    }
  });

  document.addEventListener('dragover', function(e) {
    if (!draggedCard) return;
    
    const columnBody = e.target.closest('.kanban-column-body');
    if (columnBody && columnBody.hasAttribute('data-droppable')) {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
    }
  });

  document.addEventListener('dragenter', function(e) {
    if (!draggedCard) return;
    
    const columnBody = e.target.closest('.kanban-column-body');
    if (columnBody && columnBody.hasAttribute('data-droppable')) {
      columnBody.classList.add('kanban-column-drag-over');
    }
  });

  document.addEventListener('dragleave', function(e) {
    if (!draggedCard) return;
    
    const columnBody = e.target.closest('.kanban-column-body');
    if (columnBody && !columnBody.contains(e.relatedTarget)) {
      columnBody.classList.remove('kanban-column-drag-over');
    }
  });

  document.addEventListener('drop', function(e) {
    if (!draggedCard) return;
    
    const columnBody = e.target.closest('.kanban-column-body');
    if (columnBody && columnBody.hasAttribute('data-droppable')) {
      e.preventDefault();
      columnBody.classList.remove('kanban-column-drag-over');
      
      const columnName = columnBody.getAttribute('data-column-name');
      const cards = Array.from(columnBody.querySelectorAll('.kanban-card')).filter(c => c !== draggedCard);
      const position = cards.length;
      
      const form = document.querySelector('[data-action-id="capability_three_column_kanban_board_7897884e.screen-action.move_card_to_column"]');
      if (form) {
        const actionUrl = form.getAttribute('data-action-url') || '/api/capability_three_column_kanban_board_7897884e/kanban/card-status/' + draggedStatusId + '/move';
        form.querySelector('[name="column_name"]').value = columnName;
        form.querySelector('[name="position"]').value = position;
        
        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => {
          data[key] = key === 'position' ? parseInt(value, 10) : value;
        });
        
        fetch(actionUrl, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(data)
        }).then(response => {
          if (response.ok) {
            const loadSection = document.querySelector('[data-action-id="capability_three_column_kanban_board_7897884e.screen-action.load_board"]');
            if (loadSection && window.reloadSection) {
              window.reloadSection(loadSection);
            }
          }
        });
      }
    }
  });
})();