(() => {
'use strict';
const config={"actions":[{"authentication":"required","function_id":"capability_responsive_design_8e006bb8.function.get_user_viewport_preferences","id":"capability_responsive_design_8e006bb8.screen-action.view_preferences","method":"GET","request_schema":{"properties":{},"required":[],"type":"object"},"response_schema":{"properties":{"preferences":{"items":{"properties":{"created_at":{"format":"date-time","type":"string"},"device_category":{"enum":["desktop","tablet","mobile"],"type":"string"},"id":{"format":"uuid","type":"string"},"layout_mode":{"enum":["side_by_side","horizontal_scroll","vertical_stack","tabs"],"type":"string"},"updated_at":{"format":"date-time","type":"string"},"user_id":{"format":"uuid","type":"string"}},"required":["id","user_id","device_category","layout_mode","created_at","updated_at"],"type":"object"},"type":"array"}},"required":["preferences"],"type":"object"},"route":"/api/capability_responsive_design_8e006bb8/viewport-preferences","success_route":null},{"authentication":"required","function_id":"capability_responsive_design_8e006bb8.function.update_viewport_preference","id":"capability_responsive_design_8e006bb8.screen-action.update_preference","method":"PATCH","request_schema":{"properties":{"layout_mode":{"enum":["side_by_side","horizontal_scroll","vertical_stack","tabs"],"type":"string"}},"required":["layout_mode"],"type":"object"},"response_schema":{"properties":{"preference":{"properties":{"created_at":{"format":"date-time","type":"string"},"device_category":{"enum":["desktop","tablet","mobile"],"type":"string"},"id":{"format":"uuid","type":"string"},"layout_mode":{"enum":["side_by_side","horizontal_scroll","vertical_stack","tabs"],"type":"string"},"updated_at":{"format":"date-time","type":"string"},"user_id":{"format":"uuid","type":"string"}},"required":["id","user_id","device_category","layout_mode","created_at","updated_at"],"type":"object"}},"required":["preference"],"type":"object"},"route":"/api/capability_responsive_design_8e006bb8/viewport-preferences/{preference_id}","success_route":"/board/responsive"},{"authentication":"required","function_id":"capability_responsive_design_8e006bb8.function.create_viewport_preference","id":"capability_responsive_design_8e006bb8.screen-action.create_new_preference","method":"POST","request_schema":{"properties":{"device_category":{"enum":["desktop","tablet","mobile"],"type":"string"},"layout_mode":{"enum":["side_by_side","horizontal_scroll","vertical_stack","tabs"],"type":"string"}},"required":["device_category","layout_mode"],"type":"object"},"response_schema":{"properties":{"preference":{"properties":{"created_at":{"format":"date-time","type":"string"},"device_category":{"enum":["desktop","tablet","mobile"],"type":"string"},"id":{"format":"uuid","type":"string"},"layout_mode":{"enum":["side_by_side","horizontal_scroll","vertical_stack","tabs"],"type":"string"},"updated_at":{"format":"date-time","type":"string"},"user_id":{"format":"uuid","type":"string"}},"required":["id","user_id","device_category","layout_mode","created_at","updated_at"],"type":"object"}},"required":["preference"],"type":"object"},"route":"/api/capability_responsive_design_8e006bb8/viewport-preferences","success_route":"/board/responsive"}],"screen_route":"/board/responsive/preferences"};
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