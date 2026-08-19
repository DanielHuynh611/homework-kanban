(() => {
'use strict';
const config={"actions":[{"authentication":"required","function_id":"capability_drag_and_drop_task_movement_a0308110.function.get_all_card_statuses","id":"capability_drag_and_drop_task_movement_a0308110.screen-action.load_board","method":"GET","request_schema":{"properties":{"column_status":{"description":"Optional filter to retrieve only cards in a specific column","enum":["to_do","in_progress","done"],"type":"string"}},"type":"object"},"response_schema":{"properties":{"statuses":{"description":"Array of all card statuses for the authenticated user, ordered by position_in_column within each column","items":{"properties":{"column_status":{"description":"The current column where the card resides","enum":["to_do","in_progress","done"],"type":"string"},"homework_card_id":{"description":"The homework card whose status is being retrieved","format":"uuid","type":"string"},"id":{"description":"Unique identifier for the status record","format":"uuid","type":"string"},"position_in_column":{"description":"The current position within the column","minimum":0,"type":"integer"},"updated_at":{"description":"Timestamp when the status was last updated","format":"date-time","type":"string"}},"required":["id","homework_card_id","column_status","position_in_column","updated_at"],"type":"object"},"type":"array"}},"required":["statuses"],"type":"object"},"route":"/api/capability_drag_and_drop_task_movement_a0308110/cards/statuses","success_route":null},{"authentication":"required","function_id":"capability_drag_and_drop_task_movement_a0308110.function.update_card_status","id":"capability_drag_and_drop_task_movement_a0308110.screen-action.drag_card_to_column","method":"PATCH","request_schema":{"properties":{"column_status":{"description":"The target column where the card is being dropped","enum":["to_do","in_progress","done"],"type":"string"},"position_in_column":{"description":"The zero-based vertical position within the target column","minimum":0,"type":"integer"}},"required":["column_status","position_in_column"],"type":"object"},"response_schema":{"properties":{"column_status":{"description":"The updated column status","enum":["to_do","in_progress","done"],"type":"string"},"homework_card_id":{"description":"The homework card whose status was updated","format":"uuid","type":"string"},"id":{"description":"Unique identifier for the status record","format":"uuid","type":"string"},"position_in_column":{"description":"The updated position within the column","minimum":0,"type":"integer"},"updated_at":{"description":"Timestamp when the status was last updated","format":"date-time","type":"string"}},"required":["id","homework_card_id","column_status","position_in_column","updated_at"],"type":"object"},"route":"/api/capability_drag_and_drop_task_movement_a0308110/cards/{homework_card_id}/status","success_route":null},{"authentication":"required","function_id":"capability_drag_and_drop_task_movement_a0308110.function.update_card_status","id":"capability_drag_and_drop_task_movement_a0308110.screen-action.reposition_card_within_column","method":"PATCH","request_schema":{"properties":{"column_status":{"description":"The target column where the card is being dropped","enum":["to_do","in_progress","done"],"type":"string"},"position_in_column":{"description":"The zero-based vertical position within the target column","minimum":0,"type":"integer"}},"required":["column_status","position_in_column"],"type":"object"},"response_schema":{"properties":{"column_status":{"description":"The updated column status","enum":["to_do","in_progress","done"],"type":"string"},"homework_card_id":{"description":"The homework card whose status was updated","format":"uuid","type":"string"},"id":{"description":"Unique identifier for the status record","format":"uuid","type":"string"},"position_in_column":{"description":"The updated position within the column","minimum":0,"type":"integer"},"updated_at":{"description":"Timestamp when the status was last updated","format":"date-time","type":"string"}},"required":["id","homework_card_id","column_status","position_in_column","updated_at"],"type":"object"},"route":"/api/capability_drag_and_drop_task_movement_a0308110/cards/{homework_card_id}/status","success_route":null}],"screen_route":"/board"};
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
  let draggedCardId = null;
  let sourceColumn = null;
  let sourcePosition = null;

  function initializeDragAndDrop() {
    const board = document.querySelector('.kanban-board');
    if (!board) return;

    // Delegate drag events
    board.addEventListener('dragstart', handleDragStart);
    board.addEventListener('dragend', handleDragEnd);
    board.addEventListener('dragover', handleDragOver);
    board.addEventListener('drop', handleDrop);
    board.addEventListener('dragleave', handleDragLeave);

    // Make cards draggable
    updateDraggableCards();
  }

  function updateDraggableCards() {
    const cards = document.querySelectorAll('.kanban-card');
    cards.forEach(card => {
      card.setAttribute('draggable', 'true');
    });
  }

  function handleDragStart(e) {
    if (!e.target.classList.contains('kanban-card')) return;
    
    draggedCard = e.target;
    draggedCardId = e.target.getAttribute('data-card-id');
    sourceColumn = e.target.closest('.kanban-column').getAttribute('data-column');
    sourcePosition = parseInt(e.target.getAttribute('data-position'), 10);
    
    e.target.setAttribute('data-dragging', 'true');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', e.target.innerHTML);
  }

  function handleDragEnd(e) {
    if (!e.target.classList.contains('kanban-card')) return;
    
    e.target.removeAttribute('data-dragging');
    
    // Remove all drag-over states
    document.querySelectorAll('[data-drag-over]').forEach(el => {
      el.removeAttribute('data-drag-over');
    });
    
    draggedCard = null;
    draggedCardId = null;
    sourceColumn = null;
    sourcePosition = null;
  }

  function handleDragOver(e) {
    e.preventDefault();
    
    const dropZone = e.target.closest('[data-drop-zone]');
    if (!dropZone) return;
    
    dropZone.setAttribute('data-drag-over', 'true');
    e.dataTransfer.dropEffect = 'move';
  }

  function handleDragLeave(e) {
    const dropZone = e.target.closest('[data-drop-zone]');
    if (!dropZone) return;
    
    // Only remove if we're actually leaving the drop zone
    if (!dropZone.contains(e.relatedTarget)) {
      dropZone.removeAttribute('data-drag-over');
    }
  }

  function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    
    const dropZone = e.target.closest('[data-drop-zone]');
    if (!dropZone || !draggedCardId) return;
    
    dropZone.removeAttribute('data-drag-over');
    
    const targetColumn = dropZone.getAttribute('data-drop-zone');
    const cardsInColumn = dropZone.querySelectorAll('.kanban-card');
    
    // Calculate position based on drop location
    let targetPosition = 0;
    const dropY = e.clientY;
    
    for (let i = 0; i < cardsInColumn.length; i++) {
      const card = cardsInColumn[i];
      if (card === draggedCard) continue;
      
      const rect = card.getBoundingClientRect();
      const cardMiddle = rect.top + rect.height / 2;
      
      if (dropY > cardMiddle) {
        targetPosition = i + 1;
      }
    }
    
    // Adjust position if moving within same column
    if (targetColumn === sourceColumn && targetPosition > sourcePosition) {
      targetPosition--;
    }
    
    // Only make API call if position or column changed
    if (targetColumn !== sourceColumn || targetPosition !== sourcePosition) {
      updateCardStatus(draggedCardId, targetColumn, targetPosition);
    }
  }

  function updateCardStatus(cardId, columnStatus, position) {
    const actionId = columnStatus === sourceColumn 
      ? 'capability_drag_and_drop_task_movement_a0308110.screen-action.reposition_card_within_column'
      : 'capability_drag_and_drop_task_movement_a0308110.screen-action.drag_card_to_column';
    
    // Trigger the action through the runtime
    const form = document.createElement('form');
    form.setAttribute('data-action-id', actionId);
    form.style.display = 'none';
    
    const columnInput = document.createElement('input');
    columnInput.name = 'column_status';
    columnInput.value = columnStatus;
    form.appendChild(columnInput);
    
    const positionInput = document.createElement('input');
    positionInput.name = 'position_in_column';
    positionInput.value = position;
    form.appendChild(positionInput);
    
    document.body.appendChild(form);
    
    // Dispatch submit event for runtime to handle
    const event = new Event('submit', { bubbles: true, cancelable: true });
    form.dispatchEvent(event);
    
    // Clean up
    setTimeout(() => form.remove(), 100);
  }

  // Initialize on load and after data updates
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeDragAndDrop);
  } else {
    initializeDragAndDrop();
  }

  // Re-initialize after data binding updates
  document.addEventListener('data-bind-complete', updateDraggableCards);
})();