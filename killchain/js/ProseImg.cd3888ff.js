import{g as a,r as n,i as c,T as h,n as o,j as l,o as u,c as d,z as g}from"./entry.37e139cb.js";const f=["src","alt","width","height"],p=a({__name:"ProseImg",props:{src:{type:String,default:""},alt:{type:String,default:""},width:{type:[String,Number],default:void 0},height:{type:[String,Number],default:void 0}},setup(e){const t=e,r=n(()=>{var i;if((i=t.src)!=null&&i.startsWith("/")&&!t.src.startsWith("//")){const s=c(h(o().app.baseURL));if(s!=="/"&&!t.src.startsWith(s))return l(s,t.src)}return t.src});return(i,s)=>(u(),d("img",{src:g(r),alt:e.alt,width:e.width,height:e.height},null,8,f))}});export{p as default};
