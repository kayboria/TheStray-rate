import{s as y,Y as _,Z as g,$ as h,Q as P,q as x,z as b,a0 as w,a1 as C}from"./entry.37e139cb.js";const O=()=>null;function M(...i){const l=typeof i[i.length-1]=="string"?i.pop():void 0;typeof i[0]!="string"&&i.unshift(l);let[a,c,r={}]=i;if(typeof a!="string")throw new TypeError("[nuxt] [asyncData] key must be a string.");if(typeof c!="function")throw new TypeError("[nuxt] [asyncData] handler must be a function.");r.server=r.server??!0,r.default=r.default??O,r.lazy=r.lazy??!1,r.immediate=r.immediate??!0;const e=x(),f=()=>e.isHydrating?e.payload.data[a]:e.static.data[a],d=()=>f()!==void 0;(!e._asyncData[a]||!r.immediate)&&(e._asyncData[a]={data:y(f()??r.default()),pending:y(!d()),error:_(e.payload._errors,a),status:y("idle")});const t={...e._asyncData[a]};t.refresh=t.execute=(n={})=>{if(e._asyncDataPromises[a]){if(n.dedupe===!1)return e._asyncDataPromises[a];e._asyncDataPromises[a].cancelled=!0}if((n._initial||e.isHydrating&&n._initial!==!1)&&d())return f();t.pending.value=!0,t.status.value="pending";const u=new Promise((s,o)=>{try{s(c(e))}catch(D){o(D)}}).then(s=>{if(u.cancelled)return e._asyncDataPromises[a];let o=s;r.transform&&(o=r.transform(s)),r.pick&&(o=k(o,r.pick)),t.data.value=o,t.error.value=null,t.status.value="success"}).catch(s=>{if(u.cancelled)return e._asyncDataPromises[a];t.error.value=s,t.data.value=b(r.default()),t.status.value="error"}).finally(()=>{u.cancelled||(t.pending.value=!1,e.payload.data[a]=t.data.value,t.error.value&&(e.payload._errors[a]=w(t.error.value)),delete e._asyncDataPromises[a])});return e._asyncDataPromises[a]=u,e._asyncDataPromises[a]};const p=()=>t.refresh({_initial:!0}),v=r.server!==!1&&e.payload.serverRendered;{const n=C();if(n&&!n._nuxtOnBeforeMountCbs){n._nuxtOnBeforeMountCbs=[];const s=n._nuxtOnBeforeMountCbs;n&&(g(()=>{s.forEach(o=>{o()}),s.splice(0,s.length)}),h(()=>s.splice(0,s.length)))}v&&e.isHydrating&&d()?(t.pending.value=!1,t.status.value=t.error.value?"error":"success"):n&&(e.payload.serverRendered&&e.isHydrating||r.lazy)&&r.immediate?n._nuxtOnBeforeMountCbs.push(p):r.immediate&&p(),r.watch&&P(r.watch,()=>t.refresh());const u=e.hook("app:data:refresh",s=>{if(!s||s.includes(a))return t.refresh()});n&&h(u)}const m=Promise.resolve(e._asyncDataPromises[a]).then(()=>t);return Object.assign(m,t),m}function k(i,l){const a={};for(const c of l)a[c]=i[c];return a}export{M as u};
