var tt=Object.create;var Ce=Object.defineProperty;var at=Object.getOwnPropertyDescriptor;var Oo=Object.getOwnPropertyNames;var Do=Object.getPrototypeOf,qo=Object.prototype.hasOwnProperty;var ot=(t,e)=>(e=Symbol[t])?e:Symbol.for("Symbol."+t),Re=t=>{throw TypeError(t)};var it=(t,e,r)=>e in t?Ce(t,e,{enumerable:!0,configurable:!0,writable:!0,value:r}):t[e]=r;var Zr=(t,e)=>Ce(t,"name",{value:e,configurable:!0});var Ho=(t,e)=>()=>(e||t((e={exports:{}}).exports,e),e.exports);var Bo=(t,e,r,a)=>{if(e&&typeof e=="object"||typeof e=="function")for(let o of Oo(e))!qo.call(t,o)&&o!==r&&Ce(t,o,{get:()=>e[o],enumerable:!(a=at(e,o))||a.enumerable});return t};var Ge=(t,e,r)=>(r=t!=null?tt(Do(t)):{},Bo(e||!t||!t.__esModule?Ce(r,"default",{value:t,enumerable:!0}):r,t));var b=t=>[,,,tt(t?.[ot("metadata")]??null)],nt=["class","method","getter","setter","accessor","field","value","get","set"],ze=t=>t!==void 0&&typeof t!="function"?Re("Function expected"):t,jo=(t,e,r,a,o)=>({kind:nt[t],name:e,metadata:a,addInitializer:i=>r._?Re("Already initialized"):o.push(ze(i||null))}),Vo=(t,e)=>it(e,ot("metadata"),t[3]),s=(t,e,r,a)=>{for(var o=0,i=t[e>>1],n=i&&i.length;o<n;o++)e&1?i[o].call(r):a=i[o].call(r,a);return a},u=(t,e,r,a,o,i)=>{var n,v,c,d,y,p=e&7,k=!!(e&8),w=!!(e&16),T=p>3?t.length+1:p?k?1:2:0,D=nt[p+5],Xr=p>3&&(t[T-1]=[]),Uo=t[T]||(t[T]=[]),I=p&&(!w&&!k&&(o=o.prototype),p<5&&(p>3||!w)&&at(p<4?o:{get[r](){return et(this,i)},set[r](z){return rt(this,i,z)}},r));p?w&&p<4&&Zr(i,(p>2?"set ":p>1?"get ":"")+r):Zr(o,r);for(var fr=a.length-1;fr>=0;fr--)d=jo(p,r,c={},t[3],Uo),p&&(d.static=k,d.private=w,y=d.access={has:w?z=>Go(o,z):z=>r in z},p^3&&(y.get=w?z=>(p^1?et:Ko)(z,o,p^4?i:I.get):z=>z[r]),p>2&&(y.set=w?(z,br)=>rt(z,o,br,p^4?i:I.set):(z,br)=>z[r]=br)),v=(0,a[fr])(p?p<4?w?i:I[D]:p>4?void 0:{get:I.get,set:I.set}:o,d),c._=1,p^4||v===void 0?ze(v)&&(p>4?Xr.unshift(v):p?w?i=v:I[D]=v:o=v):typeof v!="object"||v===null?Re("Object expected"):(ze(n=v.get)&&(I.get=n),ze(n=v.set)&&(I.set=n),ze(n=v.init)&&Xr.unshift(n));return p||Vo(t,o),I&&Ce(o,r,I),w?p^4?i:I:o},l=(t,e,r)=>it(t,typeof e!="symbol"?e+"":e,r),xr=(t,e,r)=>e.has(t)||Re("Cannot "+r),Go=(t,e)=>Object(e)!==e?Re('Cannot use the "in" operator on this value'):t.has(e),et=(t,e,r)=>(xr(t,e,"read from private field"),r?r.call(t):e.get(t));var rt=(t,e,r,a)=>(xr(t,e,"write to private field"),a?a.call(t,r):e.set(t,r),r),Ko=(t,e,r)=>(xr(t,e,"access private method"),r);var He=Ho((rs,cr)=>{(function(){"use strict";var t={}.hasOwnProperty;function e(){for(var o="",i=0;i<arguments.length;i++){var n=arguments[i];n&&(o=a(o,r(n)))}return o}function r(o){if(typeof o=="string"||typeof o=="number")return o;if(typeof o!="object")return"";if(Array.isArray(o))return e.apply(null,o);if(o.toString!==Object.prototype.toString&&!o.toString.toString().includes("[native code]"))return o.toString();var i="";for(var n in o)t.call(o,n)&&o[n]&&(i=a(i,n));return i}function a(o,i){return i?o?o+" "+i:o+i:o}typeof cr<"u"&&cr.exports?(e.default=e,cr.exports=e):typeof define=="function"&&typeof define.amd=="object"&&define.amd?define("classnames",[],function(){return e}):window.classNames=e})()});var Ke=window,Fe=Ke.ShadowRoot&&(Ke.ShadyCSS===void 0||Ke.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,lt=Symbol(),st=new WeakMap,We=class{constructor(e,r,a){if(this._$cssResult$=!0,a!==lt)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=r}get styleSheet(){let e=this.o,r=this.t;if(Fe&&e===void 0){let a=r!==void 0&&r.length===1;a&&(e=st.get(r)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),a&&st.set(r,e))}return e}toString(){return this.cssText}},ct=t=>new We(typeof t=="string"?t:t+"",void 0,lt);var yr=(t,e)=>{Fe?t.adoptedStyleSheets=e.map(r=>r instanceof CSSStyleSheet?r:r.styleSheet):e.forEach(r=>{let a=document.createElement("style"),o=Ke.litNonce;o!==void 0&&a.setAttribute("nonce",o),a.textContent=r.cssText,t.appendChild(a)})},Ye=Fe?t=>t:t=>t instanceof CSSStyleSheet?(e=>{let r="";for(let a of e.cssRules)r+=a.cssText;return ct(r)})(t):t;var wr,Je=window,dt=Je.trustedTypes,Wo=dt?dt.emptyScript:"",ut=Je.reactiveElementPolyfillSupport,Er={toAttribute(t,e){switch(e){case Boolean:t=t?Wo:null;break;case Object:case Array:t=t==null?t:JSON.stringify(t)}return t},fromAttribute(t,e){let r=t;switch(e){case Boolean:r=t!==null;break;case Number:r=t===null?null:Number(t);break;case Object:case Array:try{r=JSON.parse(t)}catch{r=null}}return r}},vt=(t,e)=>e!==t&&(e==e||t==t),$r={attribute:!0,type:String,converter:Er,reflect:!1,hasChanged:vt},kr="finalized",oe=class extends HTMLElement{constructor(){super(),this._$Ei=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$El=null,this._$Eu()}static addInitializer(e){var r;this.finalize(),((r=this.h)!==null&&r!==void 0?r:this.h=[]).push(e)}static get observedAttributes(){this.finalize();let e=[];return this.elementProperties.forEach((r,a)=>{let o=this._$Ep(a,r);o!==void 0&&(this._$Ev.set(o,a),e.push(o))}),e}static createProperty(e,r=$r){if(r.state&&(r.attribute=!1),this.finalize(),this.elementProperties.set(e,r),!r.noAccessor&&!this.prototype.hasOwnProperty(e)){let a=typeof e=="symbol"?Symbol():"__"+e,o=this.getPropertyDescriptor(e,a,r);o!==void 0&&Object.defineProperty(this.prototype,e,o)}}static getPropertyDescriptor(e,r,a){return{get(){return this[r]},set(o){let i=this[e];this[r]=o,this.requestUpdate(e,i,a)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)||$r}static finalize(){if(this.hasOwnProperty(kr))return!1;this[kr]=!0;let e=Object.getPrototypeOf(this);if(e.finalize(),e.h!==void 0&&(this.h=[...e.h]),this.elementProperties=new Map(e.elementProperties),this._$Ev=new Map,this.hasOwnProperty("properties")){let r=this.properties,a=[...Object.getOwnPropertyNames(r),...Object.getOwnPropertySymbols(r)];for(let o of a)this.createProperty(o,r[o])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(e){let r=[];if(Array.isArray(e)){let a=new Set(e.flat(1/0).reverse());for(let o of a)r.unshift(Ye(o))}else e!==void 0&&r.push(Ye(e));return r}static _$Ep(e,r){let a=r.attribute;return a===!1?void 0:typeof a=="string"?a:typeof e=="string"?e.toLowerCase():void 0}_$Eu(){var e;this._$E_=new Promise(r=>this.enableUpdating=r),this._$AL=new Map,this._$Eg(),this.requestUpdate(),(e=this.constructor.h)===null||e===void 0||e.forEach(r=>r(this))}addController(e){var r,a;((r=this._$ES)!==null&&r!==void 0?r:this._$ES=[]).push(e),this.renderRoot!==void 0&&this.isConnected&&((a=e.hostConnected)===null||a===void 0||a.call(e))}removeController(e){var r;(r=this._$ES)===null||r===void 0||r.splice(this._$ES.indexOf(e)>>>0,1)}_$Eg(){this.constructor.elementProperties.forEach((e,r)=>{this.hasOwnProperty(r)&&(this._$Ei.set(r,this[r]),delete this[r])})}createRenderRoot(){var e;let r=(e=this.shadowRoot)!==null&&e!==void 0?e:this.attachShadow(this.constructor.shadowRootOptions);return yr(r,this.constructor.elementStyles),r}connectedCallback(){var e;this.renderRoot===void 0&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),(e=this._$ES)===null||e===void 0||e.forEach(r=>{var a;return(a=r.hostConnected)===null||a===void 0?void 0:a.call(r)})}enableUpdating(e){}disconnectedCallback(){var e;(e=this._$ES)===null||e===void 0||e.forEach(r=>{var a;return(a=r.hostDisconnected)===null||a===void 0?void 0:a.call(r)})}attributeChangedCallback(e,r,a){this._$AK(e,a)}_$EO(e,r,a=$r){var o;let i=this.constructor._$Ep(e,a);if(i!==void 0&&a.reflect===!0){let n=(((o=a.converter)===null||o===void 0?void 0:o.toAttribute)!==void 0?a.converter:Er).toAttribute(r,a.type);this._$El=e,n==null?this.removeAttribute(i):this.setAttribute(i,n),this._$El=null}}_$AK(e,r){var a;let o=this.constructor,i=o._$Ev.get(e);if(i!==void 0&&this._$El!==i){let n=o.getPropertyOptions(i),v=typeof n.converter=="function"?{fromAttribute:n.converter}:((a=n.converter)===null||a===void 0?void 0:a.fromAttribute)!==void 0?n.converter:Er;this._$El=i,this[i]=v.fromAttribute(r,n.type),this._$El=null}}requestUpdate(e,r,a){let o=!0;e!==void 0&&(((a=a||this.constructor.getPropertyOptions(e)).hasChanged||vt)(this[e],r)?(this._$AL.has(e)||this._$AL.set(e,r),a.reflect===!0&&this._$El!==e&&(this._$EC===void 0&&(this._$EC=new Map),this._$EC.set(e,a))):o=!1),!this.isUpdatePending&&o&&(this._$E_=this._$Ej())}async _$Ej(){this.isUpdatePending=!0;try{await this._$E_}catch(r){Promise.reject(r)}let e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var e;if(!this.isUpdatePending)return;this.hasUpdated,this._$Ei&&(this._$Ei.forEach((o,i)=>this[i]=o),this._$Ei=void 0);let r=!1,a=this._$AL;try{r=this.shouldUpdate(a),r?(this.willUpdate(a),(e=this._$ES)===null||e===void 0||e.forEach(o=>{var i;return(i=o.hostUpdate)===null||i===void 0?void 0:i.call(o)}),this.update(a)):this._$Ek()}catch(o){throw r=!1,this._$Ek(),o}r&&this._$AE(a)}willUpdate(e){}_$AE(e){var r;(r=this._$ES)===null||r===void 0||r.forEach(a=>{var o;return(o=a.hostUpdated)===null||o===void 0?void 0:o.call(a)}),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$Ek(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$E_}shouldUpdate(e){return!0}update(e){this._$EC!==void 0&&(this._$EC.forEach((r,a)=>this._$EO(a,this[a],r)),this._$EC=void 0),this._$Ek()}updated(e){}firstUpdated(e){}};oe[kr]=!0,oe.elementProperties=new Map,oe.elementStyles=[],oe.shadowRootOptions={mode:"open"},ut?.({ReactiveElement:oe}),((wr=Je.reactiveElementVersions)!==null&&wr!==void 0?wr:Je.reactiveElementVersions=[]).push("1.6.3");var _r,Qe=window,ge=Qe.trustedTypes,mt=ge?ge.createPolicy("lit-html",{createHTML:t=>t}):void 0,Xe="$lit$",j=`lit$${(Math.random()+"").slice(9)}$`,Sr="?"+j,Fo=`<${Sr}>`,se=document,Ne=()=>se.createComment(""),Me=t=>t===null||typeof t!="object"&&typeof t!="function",yt=Array.isArray,wt=t=>yt(t)||typeof t?.[Symbol.iterator]=="function",Ar=`[ 	
\f\r]`,Pe=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,ht=/-->/g,pt=/>/g,ie=RegExp(`>|${Ar}(?:([^\\s"'>=/]+)(${Ar}*=${Ar}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),gt=/'/g,ft=/"/g,$t=/^(?:script|style|textarea|title)$/i,Et=t=>(e,...r)=>({_$litType$:t,strings:e,values:r}),m=Et(1),or=Et(2),V=Symbol.for("lit-noChange"),$=Symbol.for("lit-nothing"),bt=new WeakMap,ne=se.createTreeWalker(se,129,null,!1);function kt(t,e){if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return mt!==void 0?mt.createHTML(e):e}var _t=(t,e)=>{let r=t.length-1,a=[],o,i=e===2?"<svg>":"",n=Pe;for(let v=0;v<r;v++){let c=t[v],d,y,p=-1,k=0;for(;k<c.length&&(n.lastIndex=k,y=n.exec(c),y!==null);)k=n.lastIndex,n===Pe?y[1]==="!--"?n=ht:y[1]!==void 0?n=pt:y[2]!==void 0?($t.test(y[2])&&(o=RegExp("</"+y[2],"g")),n=ie):y[3]!==void 0&&(n=ie):n===ie?y[0]===">"?(n=o??Pe,p=-1):y[1]===void 0?p=-2:(p=n.lastIndex-y[2].length,d=y[1],n=y[3]===void 0?ie:y[3]==='"'?ft:gt):n===ft||n===gt?n=ie:n===ht||n===pt?n=Pe:(n=ie,o=void 0);let w=n===ie&&t[v+1].startsWith("/>")?" ":"";i+=n===Pe?c+Fo:p>=0?(a.push(d),c.slice(0,p)+Xe+c.slice(p)+j+w):c+j+(p===-2?(a.push(void 0),v):w)}return[kt(t,i+(t[r]||"<?>")+(e===2?"</svg>":"")),a]},Le=class t{constructor({strings:e,_$litType$:r},a){let o;this.parts=[];let i=0,n=0,v=e.length-1,c=this.parts,[d,y]=_t(e,r);if(this.el=t.createElement(d,a),ne.currentNode=this.el.content,r===2){let p=this.el.content,k=p.firstChild;k.remove(),p.append(...k.childNodes)}for(;(o=ne.nextNode())!==null&&c.length<v;){if(o.nodeType===1){if(o.hasAttributes()){let p=[];for(let k of o.getAttributeNames())if(k.endsWith(Xe)||k.startsWith(j)){let w=y[n++];if(p.push(k),w!==void 0){let T=o.getAttribute(w.toLowerCase()+Xe).split(j),D=/([.?@])?(.*)/.exec(w);c.push({type:1,index:i,name:D[2],strings:T,ctor:D[1]==="."?er:D[1]==="?"?rr:D[1]==="@"?tr:ce})}else c.push({type:6,index:i})}for(let k of p)o.removeAttribute(k)}if($t.test(o.tagName)){let p=o.textContent.split(j),k=p.length-1;if(k>0){o.textContent=ge?ge.emptyScript:"";for(let w=0;w<k;w++)o.append(p[w],Ne()),ne.nextNode(),c.push({type:2,index:++i});o.append(p[k],Ne())}}}else if(o.nodeType===8)if(o.data===Sr)c.push({type:2,index:i});else{let p=-1;for(;(p=o.data.indexOf(j,p+1))!==-1;)c.push({type:7,index:i}),p+=j.length-1}i++}}static createElement(e,r){let a=se.createElement("template");return a.innerHTML=e,a}};function le(t,e,r=t,a){var o,i,n,v;if(e===V)return e;let c=a!==void 0?(o=r._$Co)===null||o===void 0?void 0:o[a]:r._$Cl,d=Me(e)?void 0:e._$litDirective$;return c?.constructor!==d&&((i=c?._$AO)===null||i===void 0||i.call(c,!1),d===void 0?c=void 0:(c=new d(t),c._$AT(t,r,a)),a!==void 0?((n=(v=r)._$Co)!==null&&n!==void 0?n:v._$Co=[])[a]=c:r._$Cl=c),c!==void 0&&(e=le(t,c._$AS(t,e.values),c,a)),e}var Ze=class{constructor(e,r){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=r}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){var r;let{el:{content:a},parts:o}=this._$AD,i=((r=e?.creationScope)!==null&&r!==void 0?r:se).importNode(a,!0);ne.currentNode=i;let n=ne.nextNode(),v=0,c=0,d=o[0];for(;d!==void 0;){if(v===d.index){let y;d.type===2?y=new fe(n,n.nextSibling,this,e):d.type===1?y=new d.ctor(n,d.name,d.strings,this,e):d.type===6&&(y=new ar(n,this,e)),this._$AV.push(y),d=o[++c]}v!==d?.index&&(n=ne.nextNode(),v++)}return ne.currentNode=se,i}v(e){let r=0;for(let a of this._$AV)a!==void 0&&(a.strings!==void 0?(a._$AI(e,a,r),r+=a.strings.length-2):a._$AI(e[r])),r++}},fe=class t{constructor(e,r,a,o){var i;this.type=2,this._$AH=$,this._$AN=void 0,this._$AA=e,this._$AB=r,this._$AM=a,this.options=o,this._$Cp=(i=o?.isConnected)===null||i===void 0||i}get _$AU(){var e,r;return(r=(e=this._$AM)===null||e===void 0?void 0:e._$AU)!==null&&r!==void 0?r:this._$Cp}get parentNode(){let e=this._$AA.parentNode,r=this._$AM;return r!==void 0&&e?.nodeType===11&&(e=r.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,r=this){e=le(this,e,r),Me(e)?e===$||e==null||e===""?(this._$AH!==$&&this._$AR(),this._$AH=$):e!==this._$AH&&e!==V&&this._(e):e._$litType$!==void 0?this.g(e):e.nodeType!==void 0?this.$(e):wt(e)?this.T(e):this._(e)}k(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}$(e){this._$AH!==e&&(this._$AR(),this._$AH=this.k(e))}_(e){this._$AH!==$&&Me(this._$AH)?this._$AA.nextSibling.data=e:this.$(se.createTextNode(e)),this._$AH=e}g(e){var r;let{values:a,_$litType$:o}=e,i=typeof o=="number"?this._$AC(e):(o.el===void 0&&(o.el=Le.createElement(kt(o.h,o.h[0]),this.options)),o);if(((r=this._$AH)===null||r===void 0?void 0:r._$AD)===i)this._$AH.v(a);else{let n=new Ze(i,this),v=n.u(this.options);n.v(a),this.$(v),this._$AH=n}}_$AC(e){let r=bt.get(e.strings);return r===void 0&&bt.set(e.strings,r=new Le(e)),r}T(e){yt(this._$AH)||(this._$AH=[],this._$AR());let r=this._$AH,a,o=0;for(let i of e)o===r.length?r.push(a=new t(this.k(Ne()),this.k(Ne()),this,this.options)):a=r[o],a._$AI(i),o++;o<r.length&&(this._$AR(a&&a._$AB.nextSibling,o),r.length=o)}_$AR(e=this._$AA.nextSibling,r){var a;for((a=this._$AP)===null||a===void 0||a.call(this,!1,!0,r);e&&e!==this._$AB;){let o=e.nextSibling;e.remove(),e=o}}setConnected(e){var r;this._$AM===void 0&&(this._$Cp=e,(r=this._$AP)===null||r===void 0||r.call(this,e))}},ce=class{constructor(e,r,a,o,i){this.type=1,this._$AH=$,this._$AN=void 0,this.element=e,this.name=r,this._$AM=o,this.options=i,a.length>2||a[0]!==""||a[1]!==""?(this._$AH=Array(a.length-1).fill(new String),this.strings=a):this._$AH=$}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(e,r=this,a,o){let i=this.strings,n=!1;if(i===void 0)e=le(this,e,r,0),n=!Me(e)||e!==this._$AH&&e!==V,n&&(this._$AH=e);else{let v=e,c,d;for(e=i[0],c=0;c<i.length-1;c++)d=le(this,v[a+c],r,c),d===V&&(d=this._$AH[c]),n||(n=!Me(d)||d!==this._$AH[c]),d===$?e=$:e!==$&&(e+=(d??"")+i[c+1]),this._$AH[c]=d}n&&!o&&this.j(e)}j(e){e===$?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}},er=class extends ce{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===$?void 0:e}},Yo=ge?ge.emptyScript:"",rr=class extends ce{constructor(){super(...arguments),this.type=4}j(e){e&&e!==$?this.element.setAttribute(this.name,Yo):this.element.removeAttribute(this.name)}},tr=class extends ce{constructor(e,r,a,o,i){super(e,r,a,o,i),this.type=5}_$AI(e,r=this){var a;if((e=(a=le(this,e,r,0))!==null&&a!==void 0?a:$)===V)return;let o=this._$AH,i=e===$&&o!==$||e.capture!==o.capture||e.once!==o.once||e.passive!==o.passive,n=e!==$&&(o===$||i);i&&this.element.removeEventListener(this.name,this,o),n&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){var r,a;typeof this._$AH=="function"?this._$AH.call((a=(r=this.options)===null||r===void 0?void 0:r.host)!==null&&a!==void 0?a:this.element,e):this._$AH.handleEvent(e)}},ar=class{constructor(e,r,a){this.element=e,this.type=6,this._$AN=void 0,this._$AM=r,this.options=a}get _$AU(){return this._$AM._$AU}_$AI(e){le(this,e)}},At={O:Xe,P:j,A:Sr,C:1,M:_t,L:Ze,R:wt,D:le,I:fe,V:ce,H:rr,N:tr,U:er,F:ar},xt=Qe.litHtmlPolyfillSupport;xt?.(Le,fe),((_r=Qe.litHtmlVersions)!==null&&_r!==void 0?_r:Qe.litHtmlVersions=[]).push("2.8.0");var St=(t,e,r)=>{var a,o;let i=(a=r?.renderBefore)!==null&&a!==void 0?a:e,n=i._$litPart$;if(n===void 0){let v=(o=r?.renderBefore)!==null&&o!==void 0?o:null;i._$litPart$=n=new fe(e.insertBefore(Ne(),v),v,void 0,r??{})}return n._$AI(t),n};var ir=window,nr=ir.ShadowRoot&&(ir.ShadyCSS===void 0||ir.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Tr=Symbol(),Tt=new WeakMap,Ie=class{constructor(e,r,a){if(this._$cssResult$=!0,a!==Tr)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=r}get styleSheet(){let e=this.o,r=this.t;if(nr&&e===void 0){let a=r!==void 0&&r.length===1;a&&(e=Tt.get(r)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),a&&Tt.set(r,e))}return e}toString(){return this.cssText}},zt=t=>new Ie(typeof t=="string"?t:t+"",void 0,Tr),f=(t,...e)=>{let r=t.length===1?t[0]:e.reduce((a,o,i)=>a+(n=>{if(n._$cssResult$===!0)return n.cssText;if(typeof n=="number")return n;throw Error("Value passed to 'css' function must be a 'css' function result: "+n+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(o)+t[i+1],t[0]);return new Ie(r,t,Tr)},zr=(t,e)=>{nr?t.adoptedStyleSheets=e.map(r=>r instanceof CSSStyleSheet?r:r.styleSheet):e.forEach(r=>{let a=document.createElement("style"),o=ir.litNonce;o!==void 0&&a.setAttribute("nonce",o),a.textContent=r.cssText,t.appendChild(a)})},sr=nr?t=>t:t=>t instanceof CSSStyleSheet?(e=>{let r="";for(let a of e.cssRules)r+=a.cssText;return zt(r)})(t):t;var Cr,lr=window,Ct=lr.trustedTypes,Jo=Ct?Ct.emptyScript:"",Rt=lr.reactiveElementPolyfillSupport,Pr={toAttribute(t,e){switch(e){case Boolean:t=t?Jo:null;break;case Object:case Array:t=t==null?t:JSON.stringify(t)}return t},fromAttribute(t,e){let r=t;switch(e){case Boolean:r=t!==null;break;case Number:r=t===null?null:Number(t);break;case Object:case Array:try{r=JSON.parse(t)}catch{r=null}}return r}},Pt=(t,e)=>e!==t&&(e==e||t==t),Rr={attribute:!0,type:String,converter:Pr,reflect:!1,hasChanged:Pt},Nr="finalized",G=class extends HTMLElement{constructor(){super(),this._$Ei=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$El=null,this._$Eu()}static addInitializer(e){var r;this.finalize(),((r=this.h)!==null&&r!==void 0?r:this.h=[]).push(e)}static get observedAttributes(){this.finalize();let e=[];return this.elementProperties.forEach((r,a)=>{let o=this._$Ep(a,r);o!==void 0&&(this._$Ev.set(o,a),e.push(o))}),e}static createProperty(e,r=Rr){if(r.state&&(r.attribute=!1),this.finalize(),this.elementProperties.set(e,r),!r.noAccessor&&!this.prototype.hasOwnProperty(e)){let a=typeof e=="symbol"?Symbol():"__"+e,o=this.getPropertyDescriptor(e,a,r);o!==void 0&&Object.defineProperty(this.prototype,e,o)}}static getPropertyDescriptor(e,r,a){return{get(){return this[r]},set(o){let i=this[e];this[r]=o,this.requestUpdate(e,i,a)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)||Rr}static finalize(){if(this.hasOwnProperty(Nr))return!1;this[Nr]=!0;let e=Object.getPrototypeOf(this);if(e.finalize(),e.h!==void 0&&(this.h=[...e.h]),this.elementProperties=new Map(e.elementProperties),this._$Ev=new Map,this.hasOwnProperty("properties")){let r=this.properties,a=[...Object.getOwnPropertyNames(r),...Object.getOwnPropertySymbols(r)];for(let o of a)this.createProperty(o,r[o])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(e){let r=[];if(Array.isArray(e)){let a=new Set(e.flat(1/0).reverse());for(let o of a)r.unshift(sr(o))}else e!==void 0&&r.push(sr(e));return r}static _$Ep(e,r){let a=r.attribute;return a===!1?void 0:typeof a=="string"?a:typeof e=="string"?e.toLowerCase():void 0}_$Eu(){var e;this._$E_=new Promise(r=>this.enableUpdating=r),this._$AL=new Map,this._$Eg(),this.requestUpdate(),(e=this.constructor.h)===null||e===void 0||e.forEach(r=>r(this))}addController(e){var r,a;((r=this._$ES)!==null&&r!==void 0?r:this._$ES=[]).push(e),this.renderRoot!==void 0&&this.isConnected&&((a=e.hostConnected)===null||a===void 0||a.call(e))}removeController(e){var r;(r=this._$ES)===null||r===void 0||r.splice(this._$ES.indexOf(e)>>>0,1)}_$Eg(){this.constructor.elementProperties.forEach((e,r)=>{this.hasOwnProperty(r)&&(this._$Ei.set(r,this[r]),delete this[r])})}createRenderRoot(){var e;let r=(e=this.shadowRoot)!==null&&e!==void 0?e:this.attachShadow(this.constructor.shadowRootOptions);return zr(r,this.constructor.elementStyles),r}connectedCallback(){var e;this.renderRoot===void 0&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),(e=this._$ES)===null||e===void 0||e.forEach(r=>{var a;return(a=r.hostConnected)===null||a===void 0?void 0:a.call(r)})}enableUpdating(e){}disconnectedCallback(){var e;(e=this._$ES)===null||e===void 0||e.forEach(r=>{var a;return(a=r.hostDisconnected)===null||a===void 0?void 0:a.call(r)})}attributeChangedCallback(e,r,a){this._$AK(e,a)}_$EO(e,r,a=Rr){var o;let i=this.constructor._$Ep(e,a);if(i!==void 0&&a.reflect===!0){let n=(((o=a.converter)===null||o===void 0?void 0:o.toAttribute)!==void 0?a.converter:Pr).toAttribute(r,a.type);this._$El=e,n==null?this.removeAttribute(i):this.setAttribute(i,n),this._$El=null}}_$AK(e,r){var a;let o=this.constructor,i=o._$Ev.get(e);if(i!==void 0&&this._$El!==i){let n=o.getPropertyOptions(i),v=typeof n.converter=="function"?{fromAttribute:n.converter}:((a=n.converter)===null||a===void 0?void 0:a.fromAttribute)!==void 0?n.converter:Pr;this._$El=i,this[i]=v.fromAttribute(r,n.type),this._$El=null}}requestUpdate(e,r,a){let o=!0;e!==void 0&&(((a=a||this.constructor.getPropertyOptions(e)).hasChanged||Pt)(this[e],r)?(this._$AL.has(e)||this._$AL.set(e,r),a.reflect===!0&&this._$El!==e&&(this._$EC===void 0&&(this._$EC=new Map),this._$EC.set(e,a))):o=!1),!this.isUpdatePending&&o&&(this._$E_=this._$Ej())}async _$Ej(){this.isUpdatePending=!0;try{await this._$E_}catch(r){Promise.reject(r)}let e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var e;if(!this.isUpdatePending)return;this.hasUpdated,this._$Ei&&(this._$Ei.forEach((o,i)=>this[i]=o),this._$Ei=void 0);let r=!1,a=this._$AL;try{r=this.shouldUpdate(a),r?(this.willUpdate(a),(e=this._$ES)===null||e===void 0||e.forEach(o=>{var i;return(i=o.hostUpdate)===null||i===void 0?void 0:i.call(o)}),this.update(a)):this._$Ek()}catch(o){throw r=!1,this._$Ek(),o}r&&this._$AE(a)}willUpdate(e){}_$AE(e){var r;(r=this._$ES)===null||r===void 0||r.forEach(a=>{var o;return(o=a.hostUpdated)===null||o===void 0?void 0:o.call(a)}),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$Ek(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$E_}shouldUpdate(e){return!0}update(e){this._$EC!==void 0&&(this._$EC.forEach((r,a)=>this._$EO(a,this[a],r)),this._$EC=void 0),this._$Ek()}updated(e){}firstUpdated(e){}};G[Nr]=!0,G.elementProperties=new Map,G.elementStyles=[],G.shadowRootOptions={mode:"open"},Rt?.({ReactiveElement:G}),((Cr=lr.reactiveElementVersions)!==null&&Cr!==void 0?Cr:lr.reactiveElementVersions=[]).push("1.6.3");var Mr,Lr;var g=class extends G{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var e,r;let a=super.createRenderRoot();return(e=(r=this.renderOptions).renderBefore)!==null&&e!==void 0||(r.renderBefore=a.firstChild),a}update(e){let r=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=St(r,this.renderRoot,this.renderOptions)}connectedCallback(){var e;super.connectedCallback(),(e=this._$Do)===null||e===void 0||e.setConnected(!0)}disconnectedCallback(){var e;super.disconnectedCallback(),(e=this._$Do)===null||e===void 0||e.setConnected(!1)}render(){return V}};g.finalized=!0,g._$litElement$=!0,(Mr=globalThis.litElementHydrateSupport)===null||Mr===void 0||Mr.call(globalThis,{LitElement:g});var Nt=globalThis.litElementPolyfillSupport;Nt?.({LitElement:g});((Lr=globalThis.litElementVersions)!==null&&Lr!==void 0?Lr:globalThis.litElementVersions=[]).push("3.3.3");var x=t=>e=>typeof e=="function"?((r,a)=>(customElements.define(r,a),a))(t,e):((r,a)=>{let{kind:o,elements:i}=a;return{kind:o,elements:i,finisher(n){customElements.define(r,n)}}})(t,e);var Qo=(t,e)=>e.kind==="method"&&e.descriptor&&!("value"in e.descriptor)?{...e,finisher(r){r.createProperty(e.key,t)}}:{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:e.key,initializer(){typeof e.initializer=="function"&&(this[e.key]=e.initializer.call(this))},finisher(r){r.createProperty(e.key,t)}},Xo=(t,e,r)=>{e.constructor.createProperty(r,t)};function h(t){return(e,r)=>r!==void 0?Xo(t,e,r):Qo(t,e)}function be(t){return h({...t,state:!0})}var Ir,mn=((Ir=window.HTMLSlotElement)===null||Ir===void 0?void 0:Ir.prototype.assignedElements)!=null?(t,e)=>t.assignedElements(e):(t,e)=>t.assignedNodes(e).filter(r=>r.nodeType===Node.ELEMENT_NODE);var Mt,Ur,Zo;Mt=[x("bp-blockquote")];var xe=class extends(Zo=g){render(){return m`
      <figure>
        <blockquote>
          <slot></slot>
        </blockquote>

        <slot name="caption"></slot>
      </figure>
    `}};Ur=b(Zo),xe=u(Ur,0,"BlockQuote",Mt,xe),l(xe,"styles",f`
    :host {
      display: block;
      margin: var(--size-2) 0;
    }

    figure {
      box-shadow: inset var(--size-1) 0 0 -5px var(--color-black);
      padding: 0 0 0 var(--size-2);
      margin: 0;
      line-height: var(--line-height-normal);
    }

    blockquote {
      margin: 0;
    }

    ::slotted(p) {
      margin: var(--size-2) 0;
    }

    figcaption ::slotted(*) {
      color: var(--color-gray);
      font-size: var(--font-size-xs);
    }
  `),s(Ur,1,xe);var ei=or`<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><path d="m256 0c-141.4 0-256 114.6-256 256s114.6 256 256 256 256-114.6 256-256-114.6-256-256-256zm0 400c-18 0-32-14-32-32s13.1-32 32-32c17.1 0 32 14 32 32s-14.9 32-32 32zm69.1-142-45.1 28v2c0 13-11 24-24 24s-24-11-24-24v-16c0-8 4-16 12-21l57-34c7-4 11-11 11-19 0-12-10.9-22-22.9-22h-51.1c-12.9 0-22 10-22 22 0 13-11 24-24 24s-24-11-24-24c0-39 31-70 69.1-70h51.1c40.8 0 71.8 31 71.8 70 0 24-13 47-34.9 60z"/></svg>`,Lt,It,Ut,ye;Ut=[x("bp-callout")];var de=class extends(It=g,Lt=[h()],It){constructor(){super(...arguments);l(this,"intent",s(ye,8,this,"question")),s(ye,11,this)}render(){return m`
      <div class="callout">
        ${ei}
        <aside>
          <slot></slot>
        </aside>
      </div>
    `}};ye=b(It),u(ye,5,"intent",Lt,de),de=u(ye,0,"Callout",Ut,de),l(de,"styles",f`
    :host {
      display: block;
      line-height: var(--line-height-normal);
      margin: var(--size-2) 0;
    }

    .callout {
      display: grid;
      grid-template-columns: var(--size-5) 1fr;
      column-gap: var(--size-1-5);
      align-items: center;
      border: 2px solid var(--color-black);
      border-radius: var(--radius-md);
      padding: var(--size-1-5);
    }
  `),s(ye,1,de);var Ot,Or,ri;Ot=[x("bp-caption")];var we=class extends(ri=g){handleLinkClick(e){globalThis.window.BibleProjectApp&&e.preventDefault(),document.dispatchEvent(new CustomEvent("bp:external_link",{detail:{href:e.currentTarget.href}}))}handleSlotChange(){this.querySelectorAll("a").forEach(e=>{e.setAttribute("target","_blank"),e.removeEventListener("click",this.handleLinkClick),e.addEventListener("click",this.handleLinkClick)})}render(){return m`
      <figcaption>
        <slot @slotchange=${this.handleSlotChange}></slot>
      </figcaption>
    `}};Or=b(ri),we=u(Or,0,"Caption",Ot,we),l(we,"styles",f`
    :host {
      color: var(--color-gray);
      font-size: var(--font-size-xs);
    }

    ::slotted(a) {
      color: inherit;
      text-decoration: underline;
    }
  `),s(Or,1,we);var Dt,qt,Ht,$e;Ht=[x("bp-cite")];var ue=class extends(qt=g,Dt=[h()],qt){constructor(){super(...arguments);l(this,"href",s($e,8,this)),s($e,11,this)}handleClick(r){globalThis.window.BibleProjectApp&&r.preventDefault(),document.dispatchEvent(new CustomEvent("bp:external_link",{detail:{href:this.href}}))}render(){let r=this.href?m`
          <a href="${this.href}" target="_blank" @click="${this.handleClick}">
            <slot></slot>
          </a>
        `:m`<slot></slot>`;return m`<cite>${r}</cite>`}};$e=b(qt),u($e,5,"href",Dt,ue),ue=u($e,0,"Cite",Ht,ue),l(ue,"styles",f`
    cite {
      color: var(--bp-cite-color, var(--color-gray));
      font-size: inherit;
    }

    a {
      color: inherit;
      text-decoration: underline;
    }
  `),s($e,1,ue);var ti=or`
  <svg height="31" viewBox="0 0 34 31" width="34" xmlns="http://www.w3.org/2000/svg"><path d="m0 4.5c0-2.05078 1.64062-3.75 3.75-3.75h15c2.0508 0 3.75 1.69922 3.75 3.75v7.9102c-4.3359 1.2304-7.5 5.2148-7.5 9.9023 0 3.5156 1.6992 6.5625 4.2773 8.4375-.1757 0-.3515 0-.5273 0h-15c-2.10938 0-3.75-1.6406-3.75-3.75zm4.6875 5.625h13.125c.4687 0 .9375-.41016.9375-.9375 0-.46875-.4688-.9375-.9375-.9375h-13.125c-.52734 0-.9375.46875-.9375.9375 0 .52734.41016.9375.9375.9375zm0 3.75c-.52734 0-.9375.4688-.9375.9375 0 .5273.41016.9375.9375.9375h9.375c.4687 0 .9375-.4102.9375-.9375 0-.4687-.4688-.9375-.9375-.9375zm0 5.625c-.52734 0-.9375.4688-.9375.9375 0 .5273.41016.9375.9375.9375h5.625c.4687 0 .9375-.4102.9375-.9375 0-.4687-.4688-.9375-.9375-.9375zm12.1875 2.8125c0-4.6289 3.75-8.4375 8.4375-8.4375 4.6289 0 8.4375 3.8086 8.4375 8.4375 0 4.6875-3.8086 8.4375-8.4375 8.4375-4.6875 0-8.4375-3.75-8.4375-8.4375zm8.4375-2.8125c.7617 0 1.4063-.5859 1.4063-1.4062 0-.7618-.6446-1.4063-1.4063-1.4063-.8203 0-1.4063.6445-1.4063 1.4063 0 .8203.586 1.4062 1.4063 1.4062zm-.9375 3.75v2.8125c-.5273 0-.9375.4687-.9375.9375 0 .5273.4102.9375.9375.9375h1.875c.4688 0 .9375-.4102.9375-.9375 0-.4688-.4687-.9375-.9375-.9375v-3.75c0-.4687-.4688-.9375-.9375-.9375h-.9375c-.5273 0-.9375.4688-.9375.9375 0 .5273.4102.9375.9375.9375z" /></svg>
`,Bt,Dr,ai;Bt=[x("bp-empty-state")];var Ee=class extends(ai=g){render(){return m`
      <div class="empty-state">
        ${ti}
        <slot></slot>
      </div>
    `}};Dr=b(ai),Ee=u(Dr,0,"EmptyState",Bt,Ee),l(Ee,"styles",f`
    :host {
      display: block;
      color: var(--color-gray);
    }

    .empty-state {
      background-color: var(--color-white);
      border-radius: var(--radius-md);
      border: 2px solid var(--color-neutral-10);
      padding: var(--size-4) var(--size-3);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: var(--size-1-5);
      font-weight: var(--font-weight-semibold);
      text-align: center;
    }

    svg {
      max-width: var(--size-5);
      max-height: var(--size-5);
      fill: currentColor;
    }
  `),s(Dr,1,Ee);var Oe={ATTRIBUTE:1,CHILD:2,PROPERTY:3,BOOLEAN_ATTRIBUTE:4,EVENT:5,ELEMENT:6},De=t=>(...e)=>({_$litDirective$:t,values:e}),ve=class{constructor(e){}get _$AU(){return this._$AM._$AU}_$AT(e,r,a){this._$Ct=e,this._$AM=r,this._$Ci=a}_$AS(e,r){return this.update(e,r)}update(e,r){return this.render(...r)}};var qe=class extends ve{constructor(e){if(super(e),this.et=$,e.type!==Oe.CHILD)throw Error(this.constructor.directiveName+"() can only be used in child bindings")}render(e){if(e===$||e==null)return this.ft=void 0,this.et=e;if(e===V)return e;if(typeof e!="string")throw Error(this.constructor.directiveName+"() called with a non-string value");if(e===this.et)return this.ft;this.et=e;let r=[e];return r.raw=r,this.ft={_$litType$:this.constructor.resultType,strings:r,values:[]}}};qe.directiveName="unsafeHTML",qe.resultType=1;var K=De(qe);var Yt=Ge(He(),1);var ke=f`
  .spotlight-container {
    --fade-amount: 0;
  }

  .spotlight-container-active {
    --fade-amount: 0.8;
  }

  .spotlight-container {
    --spotlight-transition-duration: var(--duration-long);

    /* Adjustable Vars */
    --inverse-fade-amount: calc(1 - var(--fade-amount));
    --mixed-red: calc(var(--fade-amount) * var(--background-red));
    --mixed-green: calc(var(--fade-amount) * var(--background-green));
    --mixed-blue: calc(var(--fade-amount) * var(--background-blue));

    /* Utility Colors */
    --color-white: rgb(
      calc(255 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(255 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(255 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-black: var(--color-neutral-90);
    --color-gray: var(--color-neutral-50);
    --color-brand: rgb(
      calc(0 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(179 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(229 * var(--inverse-fade-amount) + var(--mixed-blue))
    );

    /* Color Rainbow */
    --color-neutral-05: rgb(
      calc(249 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(250 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(252 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-neutral-10: rgb(
      calc(228 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(232 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(237 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-neutral-20: rgb(
      calc(193 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(201 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(208 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-neutral-30: rgb(
      calc(164 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(171 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(183 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-neutral-40: rgb(
      calc(137 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(146 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(158 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-neutral-50: rgb(
      calc(107 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(115 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(132 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-neutral-60: rgb(
      calc(79 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(86 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(105 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-neutral-70: rgb(
      calc(62 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(64 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(84 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-neutral-80: rgb(
      calc(42 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(47 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(68 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-neutral-90: rgb(
      calc(24 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(29 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(54 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-red-05: rgb(
      calc(254 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(248 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(244 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-red-10: rgb(
      calc(249 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(227 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(222 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-red-20: rgb(
      calc(241 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(184 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(181 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-red-30: rgb(
      calc(234 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(137 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(140 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-red-40: rgb(
      calc(220 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(104 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(120 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-red-50: rgb(
      calc(190 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(73 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(103 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-red-60: rgb(
      calc(151 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(42 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(78 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-red-70: rgb(
      calc(117 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(31 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(64 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-red-80: rgb(
      calc(86 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(23 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(57 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-red-90: rgb(
      calc(60 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(10 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(39 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-orange-05: rgb(
      calc(254 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(250 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(238 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-orange-10: rgb(
      calc(250 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(228 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(196 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-orange-20: rgb(
      calc(239 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(186 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(141 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-orange-30: rgb(
      calc(230 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(149 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(101 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-orange-40: rgb(
      calc(214 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(117 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(82 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-orange-50: rgb(
      calc(181 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(84 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(58 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-orange-60: rgb(
      calc(145 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(54 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(46 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-orange-70: rgb(
      calc(116 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(38 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(38 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-orange-80: rgb(
      calc(87 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(25 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(31 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-orange-90: rgb(
      calc(59 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(17 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(19 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-yellow-05: rgb(
      calc(251 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(249 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(235 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-yellow-10: rgb(
      calc(245 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(229 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(189 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-yellow-20: rgb(
      calc(232 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(194 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(129 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-yellow-30: rgb(
      calc(217 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(157 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(82 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-yellow-40: rgb(
      calc(203 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(125 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(51 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-yellow-50: rgb(
      calc(175 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(89 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(34 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-yellow-60: rgb(
      calc(141 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(61 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(23 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-yellow-70: rgb(
      calc(108 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(47 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(20 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-yellow-80: rgb(
      calc(80 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(34 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(17 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-yellow-90: rgb(
      calc(53 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(22 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(9 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-green-05: rgb(
      calc(242 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(254 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(240 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-green-10: rgb(
      calc(211 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(242 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(205 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-green-20: rgb(
      calc(151 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(214 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(156 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-green-30: rgb(
      calc(96 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(191 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(135 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-green-40: rgb(
      calc(79 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(164 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(120 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-green-50: rgb(
      calc(58 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(128 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(96 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-green-60: rgb(
      calc(43 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(97 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(70 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-green-70: rgb(
      calc(32 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(75 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(60 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-green-80: rgb(
      calc(23 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(54 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(52 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-green-90: rgb(
      calc(14 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(34 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(39 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-turquoise-05: rgb(
      calc(236 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(251 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(254 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-turquoise-10: rgb(
      calc(185 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(239 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(247 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-turquoise-20: rgb(
      calc(135 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(222 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(234 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-turquoise-30: rgb(
      calc(76 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(193 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(209 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-turquoise-40: rgb(
      calc(31 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(156 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(173 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-turquoise-50: rgb(
      calc(9 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(125 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(141 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-turquoise-60: rgb(
      calc(0 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(98 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(111 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-turquoise-70: rgb(
      calc(0 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(77 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(88 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-turquoise-80: rgb(
      calc(0 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(54 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(62 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-turquoise-90: rgb(
      calc(0 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(41 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(48 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-cyan-05: rgb(
      calc(239 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(252 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(252 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-cyan-10: rgb(
      calc(204 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(241 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(250 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-cyan-20: rgb(
      calc(145 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(209 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(234 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-cyan-30: rgb(
      calc(105 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(180 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(226 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-cyan-40: rgb(
      calc(84 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(150 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(207 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-cyan-50: rgb(
      calc(54 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(120 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(180 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-cyan-60: rgb(
      calc(36 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(87 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(145 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-cyan-70: rgb(
      calc(27 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(69 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(117 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-cyan-80: rgb(
      calc(21 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(49 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(79 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-cyan-90: rgb(
      calc(11 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(33 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(49 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-blue-05: rgb(
      calc(245 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(251 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(255 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-blue-10: rgb(
      calc(217 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(236 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(253 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-blue-20: rgb(
      calc(172 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(204 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(251 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-blue-30: rgb(
      calc(133 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(170 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(241 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-blue-40: rgb(
      calc(114 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(140 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(230 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-blue-50: rgb(
      calc(88 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(105 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(205 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-blue-60: rgb(
      calc(64 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(76 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(166 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-blue-70: rgb(
      calc(49 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(60 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(134 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-blue-80: rgb(
      calc(35 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(44 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(97 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-blue-90: rgb(
      calc(19 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(30 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(63 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-violet-05: rgb(
      calc(248 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(249 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(254 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-violet-10: rgb(
      calc(230 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(230 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(250 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-violet-20: rgb(
      calc(196 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(195 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(232 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-violet-30: rgb(
      calc(172 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(161 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(220 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-violet-40: rgb(
      calc(152 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(130 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(213 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-violet-50: rgb(
      calc(126 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(98 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(188 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-violet-60: rgb(
      calc(93 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(72 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(151 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-violet-70: rgb(
      calc(71 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(52 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(126 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-violet-80: rgb(
      calc(51 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(37 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(96 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-violet-90: rgb(
      calc(29 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(23 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(75 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-purple-05: rgb(
      calc(253 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(248 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(255 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-purple-10: rgb(
      calc(247 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(225 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(245 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-purple-20: rgb(
      calc(230 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(182 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(225 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-purple-30: rgb(
      calc(215 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(145 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(216 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-purple-40: rgb(
      calc(189 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(114 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(203 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-purple-50: rgb(
      calc(152 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(85 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(175 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-purple-60: rgb(
      calc(113 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(60 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(146 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-purple-70: rgb(
      calc(85 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(45 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(125 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-purple-80: rgb(
      calc(59 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(30 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(102 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-purple-90: rgb(
      calc(40 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(15 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(82 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-tan-05: rgb(
      calc(249 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(247 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(241 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-tan-10: rgb(
      calc(239 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(232 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(219 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-tan-20: rgb(
      calc(215 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(202 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(176 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-tan-30: rgb(
      calc(187 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(170 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(136 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-tan-40: rgb(
      calc(163 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(145 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(110 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-tan-50: rgb(
      calc(129 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(111 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(77 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-tan-60: rgb(
      calc(100 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(85 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(55 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-tan-70: rgb(
      calc(80 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(67 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(41 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-tan-80: rgb(
      calc(59 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(49 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(28 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-tan-90: rgb(
      calc(37 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(30 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(17 * var(--inverse-fade-amount) + var(--mixed-blue))
    );

    /* Highlight Colors */
    --color-highlight-yellow-1: rgb(
      calc(255 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(227 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(79 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-highlight-yellow-2: rgb(
      calc(255 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(247 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(44 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-highlight-pink-1: rgb(
      calc(255 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(61 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(201 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-highlight-pink-2: rgb(
      calc(230 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(128 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(255 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-highlight-orange-1: rgb(
      calc(255 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(140 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(57 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-highlight-orange-2: rgb(
      calc(255 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(192 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(70 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-highlight-blue-1: rgb(
      calc(79 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(223 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(255 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-highlight-blue-2: rgb(
      calc(84 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(255 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(214 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-highlight-green-1: rgb(
      calc(41 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(248 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(62 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-highlight-green-2: rgb(
      calc(175 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(255 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(44 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
  }

  .spotlighted {
    --fade-amount: 0;
    --inverse-fade-amount: 1;

    /* Utility Colors */
    --color-white: #ffffff;
    --color-black: var(--color-neutral-90);
    --color-gray: var(--color-neutral-50);
    --color-brand: #00b3e5;

    /* Color Rainbow */
    --color-neutral-05: #f9fafc;
    --color-neutral-10: #e4e8ed;
    --color-neutral-20: #c1c9d0;
    --color-neutral-30: #a4abb7;
    --color-neutral-40: #89929e;
    --color-neutral-50: #6b7384;
    --color-neutral-60: #4f5669;
    --color-neutral-70: #3e4054;
    --color-neutral-80: #2a2f44;
    --color-neutral-90: #181d36;
    --color-red-05: #fef8f4;
    --color-red-10: #f9e3de;
    --color-red-20: #f1b8b5;
    --color-red-30: #ea898c;
    --color-red-40: #dc6878;
    --color-red-50: #be4967;
    --color-red-60: #972a4e;
    --color-red-70: #751f40;
    --color-red-80: #561739;
    --color-red-90: #3c0a27;
    --color-orange-05: #fefaee;
    --color-orange-10: #fae4c4;
    --color-orange-20: #efba8d;
    --color-orange-30: #e69565;
    --color-orange-40: #d67552;
    --color-orange-50: #b5543a;
    --color-orange-60: #91362e;
    --color-orange-70: #742626;
    --color-orange-80: #57191f;
    --color-orange-90: #3b1113;
    --color-yellow-05: #fbf9eb;
    --color-yellow-10: #f5e5bd;
    --color-yellow-20: #e8c281;
    --color-yellow-30: #d99d52;
    --color-yellow-40: #cb7d33;
    --color-yellow-50: #af5922;
    --color-yellow-60: #8d3d17;
    --color-yellow-70: #6c2f14;
    --color-yellow-80: #502211;
    --color-yellow-90: #351609;
    --color-green-05: #f2fef0;
    --color-green-10: #d3f2cd;
    --color-green-20: #97d69c;
    --color-green-30: #60bf87;
    --color-green-40: #4fa478;
    --color-green-50: #3a8060;
    --color-green-60: #2b6146;
    --color-green-70: #204b3c;
    --color-green-80: #173634;
    --color-green-90: #0e2227;
    --color-turquoise-05: #ecfbfe;
    --color-turquoise-10: #b9eff7;
    --color-turquoise-20: #87deea;
    --color-turquoise-30: #4cc1d1;
    --color-turquoise-40: #1f9cad;
    --color-turquoise-50: #097d8d;
    --color-turquoise-60: #00626f;
    --color-turquoise-70: #004d58;
    --color-turquoise-80: #00363e;
    --color-turquoise-90: #002930;
    --color-cyan-05: #effcfc;
    --color-cyan-10: #ccf1fa;
    --color-cyan-20: #91d1ea;
    --color-cyan-30: #69b4e2;
    --color-cyan-40: #5496cf;
    --color-cyan-50: #3678b4;
    --color-cyan-60: #245791;
    --color-cyan-70: #1b4575;
    --color-cyan-80: #15314f;
    --color-cyan-90: #0b2131;
    --color-blue-05: #f5fbff;
    --color-blue-10: #d9ecfd;
    --color-blue-20: #acccfb;
    --color-blue-30: #85aaf1;
    --color-blue-40: #728ce6;
    --color-blue-50: #5869cd;
    --color-blue-60: #404ca6;
    --color-blue-70: #313c86;
    --color-blue-80: #232c61;
    --color-blue-90: #131e3f;
    --color-violet-05: #f8f9fe;
    --color-violet-10: #e6e6fa;
    --color-violet-20: #c4c3e8;
    --color-violet-30: #aca1dc;
    --color-violet-40: #9882d5;
    --color-violet-50: #7e62bc;
    --color-violet-60: #5d4897;
    --color-violet-70: #47347e;
    --color-violet-80: #332560;
    --color-violet-90: #1d174b;
    --color-purple-05: #fdf8ff;
    --color-purple-10: #f7e1f5;
    --color-purple-20: #e6b6e1;
    --color-purple-30: #d791d8;
    --color-purple-40: #bd72cb;
    --color-purple-50: #9855af;
    --color-purple-60: #713c92;
    --color-purple-70: #552d7d;
    --color-purple-80: #3b1e66;
    --color-purple-90: #280f52;
    --color-tan-05: #f9f7f1;
    --color-tan-10: #efe8db;
    --color-tan-20: #d7cab0;
    --color-tan-30: #bbaa88;
    --color-tan-40: #a3916e;
    --color-tan-50: #816f4d;
    --color-tan-60: #645537;
    --color-tan-70: #504329;
    --color-tan-80: #3b311c;
    --color-tan-90: #251e11;

    /* Highlight Colors */
    --color-highlight-yellow-1: #ffe34f;
    --color-highlight-yellow-2: #fff72c;
    --color-highlight-pink-1: #ff3dc9;
    --color-highlight-pink-2: #e680ff;
    --color-highlight-orange-1: #ff8c39;
    --color-highlight-orange-2: #ffc046;
    --color-highlight-blue-1: #4fdfff;
    --color-highlight-blue-2: #54ffd6;
    --color-highlight-green-1: #29f83e;
    --color-highlight-green-2: #afff2c;
  }
`;var jt,Vt,Gt,Kt,Wt,Ft,A;Ft=[x("bp-ephesians-literary-design")];var q=class extends(Wt=g,Kt=[h()],Gt=[h({attribute:"title"})],Vt=[h({attribute:"data"})],jt=[h({type:Boolean,attribute:"debug"})],Wt){constructor(){super(...arguments);l(this,"reference",s(A,8,this)),s(A,11,this);l(this,"designTitle",s(A,12,this)),s(A,15,this);l(this,"data",s(A,16,this)),s(A,19,this);l(this,"debug",s(A,20,this)),s(A,23,this)}annotateTags(r,a){let o=1,i=new RegExp(`<([^>]*)class="${r}"([^>]*)>`,"g");return a.replace(i,(n,v,c)=>{let d=`<${v}class="${r}" data-id="${r}-${o}"${c}>`;return this.debug&&(d+=`<div class="group-debug-label">Id: ${r}-${o}</div>`),o+=1,d})}get annotatedHtml(){let r=this.data??"";return r=this.annotateTags("group",r),r=this.annotateTags("group-title",r),r=r?.replace("<bp-mark","<bp-mark can-spotlight "),r}render(){if(!this.data)return;let r=(0,Yt.default)({debug:this.debug});return m`<div class="${r}">
      ${this.designTitle?m`<div class="title">${this.designTitle}</div>`:null}
      ${this.reference?m`<div class="reference">${this.reference}</div>`:null}
      <div class="design">${K(this.annotatedHtml)}</div>
    </div>`}};A=b(Wt),u(A,5,"reference",Kt,q),u(A,5,"designTitle",Gt,q),u(A,5,"data",Vt,q),u(A,5,"debug",jt,q),q=u(A,0,"EphesiansLiteraryDesign",Ft,q),l(q,"styles",[ke,f`
      :host {
        display: block;
        white-space: nowrap;
        --group-body-font-size: 16px;
        --group-title-font-size: 14px;
        --title-font-size: 22px;
        --reference-font-size: 18px;
      }

      .design {
        overflow-x: auto;
        padding-bottom: var(--size-1);
      }

      .title {
        font-size: var(--title-font-size);
        font-weight: var(--font-weight-normal);
        line-height: var(--line-height-snug);
      }

      .reference {
        font-size: var(--reference-font-size);
        font-weight: var(--font-weight-bold);
        margin-bottom: var(--size-3);
      }

      .group-title {
        font-size: var(--group-title-font-size);
        font-weight: var(--font-weight-semibold);
        margin: var(--size-3) 0 var(--size-1);
      }

      .group-title[data-id="group-title-1"] {
        margin-top: 0;
      }

      .group {
        align-items: flex-start;
        display: flex;
        flex-direction: column;
        font-size: var(--group-body-font-size);
        white-space: nowrap;
        position: relative;
        color: var(--color-black);
        transition: color var(--spotlight-transition-duration);
      }

      .arrow-bottom {
        background-color: var(--color-neutral-10);
        position: absolute;
        left: calc(var(--size-1) + 2px);
        top: var(--size-1);
        bottom: var(--size-0-5);
        width: 4px;
      }

      .arrow-top {
        position: absolute;
        left: var(--size-0-5);
        top: var(--size-0-5);
        bottom: var(--size-0-5);
        width: 0;
        height: 0;
        border-left: 8px solid transparent;
        border-right: 8px solid transparent;
        border-bottom: 8px solid var(--color-neutral-10);
      }

      .group:not(:has(.group)) {
        display: inline-block;
      }

      .group-debug-label {
        display: none;
      }
      .debug .group:hover {
        outline: 2px solid lightgrey;
      }
      .debug > .group:hover {
        outline: 2px solid white;
      }
      .debug .group:not(:has(.group:hover)):hover {
        outline: 2px solid red;
      }

      .debug .group:hover > .group-debug-label {
        font-size: 12px;
        font-weight: 700;
        z-index: 10;
        background-color: grey;
        color: white;
        display: block;
        position: absolute;
        left: 0;
        top: 0;
        padding: 2px;
      }
      .debug .group:not(:has(.group)):hover > .group-debug-label {
        left: calc(100% + 4px);
      }
      .debug .group:not(:has(.group:hover)):hover > .group-debug-label {
        background-color: red;
      }

      .group[indent="1"] {
        margin-inline-start: 10px;
      }
      .group[indent="2"] {
        margin-inline-start: 20px;
      }
      .group[indent="3"] {
        margin-inline-start: 30px;
      }
      .group[indent="4"] {
        margin-inline-start: 40px;
      }
      .group[indent="5"] {
        margin-inline-start: 50px;
      }
      .group[indent="6"] {
        margin-inline-start: 60px;
      }
      .group[indent="7"] {
        margin-inline-start: 70px;
      }
      .group[indent="8"] {
        margin-inline-start: 80px;
      }
      .group[indent="9"] {
        margin-inline-start: 90px;
      }
      .group[indent="10"] {
        margin-inline-start: 100px;
      }
      .group[indent="11"] {
        margin-inline-start: 110px;
      }
      .group[indent="12"] {
        margin-inline-start: 120px;
      }
      .group[indent="13"] {
        margin-inline-start: 130px;
      }
      .group[indent="14"] {
        margin-inline-start: 140px;
      }
      .group[indent="15"] {
        margin-inline-start: 150px;
      }
      .group[indent="16"] {
        margin-inline-start: 160px;
      }
      .group[indent="17"] {
        margin-inline-start: 170px;
      }
      .group[indent="18"] {
        margin-inline-start: 180px;
      }
      .group[indent="19"] {
        margin-inline-start: 190px;
      }
      .group[indent="20"] {
        margin-inline-start: 200px;
      }
      .group[indent="21"] {
        margin-inline-start: 210px;
      }
      .group[indent="22"] {
        margin-inline-start: 220px;
      }
      .group[indent="23"] {
        margin-inline-start: 230px;
      }
      .group[indent="24"] {
        margin-inline-start: 240px;
      }
      .group[indent="25"] {
        margin-inline-start: 250px;
      }
      .group[indent="26"] {
        margin-inline-start: 260px;
      }
      .group[indent="27"] {
        margin-inline-start: 270px;
      }
      .group[indent="28"] {
        margin-inline-start: 280px;
      }
      .group[indent="29"] {
        margin-inline-start: 290px;
      }
      .group[indent="30"] {
        margin-inline-start: 300px;
      }
      .group[indent="31"] {
        margin-inline-start: 310px;
      }
      .group[indent="32"] {
        margin-inline-start: 320px;
      }
      .group[indent="33"] {
        margin-inline-start: 330px;
      }
      .group[indent="34"] {
        margin-inline-start: 340px;
      }
      .group[indent="35"] {
        margin-inline-start: 350px;
      }
      .group[indent="36"] {
        margin-inline-start: 360px;
      }
      .group[indent="37"] {
        margin-inline-start: 370px;
      }
      .group[indent="38"] {
        margin-inline-start: 380px;
      }
      .group[indent="39"] {
        margin-inline-start: 390px;
      }
      .group[indent="40"] {
        margin-inline-start: 400px;
      }
      .group[indent="41"] {
        margin-inline-start: 410px;
      }
      .group[indent="42"] {
        margin-inline-start: 420px;
      }
      .group[indent="43"] {
        margin-inline-start: 430px;
      }
      .group[indent="44"] {
        margin-inline-start: 440px;
      }
      .group[indent="45"] {
        margin-inline-start: 450px;
      }
      .group[indent="46"] {
        margin-inline-start: 460px;
      }
      .group[indent="47"] {
        margin-inline-start: 470px;
      }
      .group[indent="48"] {
        margin-inline-start: 480px;
      }
      .group[indent="49"] {
        margin-inline-start: 490px;
      }
      .group[indent="50"] {
        margin-inline-start: 500px;
      }
    `]),s(A,1,q);var oa=Ge(He(),1);function Jt(t){let e=t.trim().match(/^((?<miliseconds>[0-9]+)ms)|((?<seconds>[0-9]+)s)$/)?.groups;return e?.miliseconds?Number(e?.miliseconds):e?.seconds?Number(e?.seconds)*1e3:0}var Qt,Xt,Zt,ea,ra,ta,aa,_;aa=[x("bp-highlight")];var U=class extends(ta=g,ra=[h({attribute:"color"})],ea=[h({type:Number,attribute:"reveal-time"})],Zt=[h({type:Boolean,attribute:"no-animation"})],Xt=[h({type:Boolean,attribute:"can-spotlight"})],Qt=[h({type:Boolean,attribute:"show"})],ta){constructor(){super(...arguments);l(this,"color",s(_,8,this,"yellow")),s(_,11,this);l(this,"userRevealTime",s(_,12,this,1)),s(_,15,this);l(this,"noAnimation",s(_,16,this,!1)),s(_,19,this);l(this,"canSpotlight",s(_,20,this)),s(_,23,this);l(this,"show",s(_,24,this,!1)),s(_,27,this);l(this,"revealTime",1);l(this,"shouldResetState",!1);l(this,"shownState","initHidden");l(this,"lastState");l(this,"resetStateTimeoutId",null)}resetShownState(){let r=Jt(globalThis.window.getComputedStyle(this).getPropertyValue("--duration-x-long")),a=this.revealTime*r+50;this.resetStateTimeoutId=setTimeout(()=>{this.shouldResetState=!0,this.requestUpdate()},a)}willUpdate(r){if(r.has("show")&&(this.shouldResetState=!1,this.resetStateTimeoutId&&clearTimeout(this.resetStateTimeoutId)),this.shouldResetState){this.revealTime=0,this.shownState="initHidden",this.shouldResetState=!1;return}this.noAnimation?this.revealTime=0:this.userRevealTime&&(this.revealTime=this.userRevealTime),this.shownState=this.show?"shown":this.lastState==="shown"?"hiddenAfterShown":"initHidden",this.shownState==="hiddenAfterShown"&&this.resetShownState()}render(){let r=(0,oa.default)("highlight",this.color,this.shownState,{"can-spotlight":this.canSpotlight}),a=`--reveal-time: calc(${this.revealTime} * var(--duration-x-long))`;return m`<span class="${r}" style="${a}"><slot></slot></span>`}updated(){this.lastState=this.shownState}};_=b(ta),u(_,5,"color",ra,U),u(_,5,"userRevealTime",ea,U),u(_,5,"noAnimation",Zt,U),u(_,5,"canSpotlight",Xt,U),u(_,5,"show",Qt,U),U=u(_,0,"Highlight",aa,U),l(U,"styles",f`
    :host {
      --reveal-time: var(--duration-x-long);
      --left-gradient-color: var(--color-highlight-yellow-1);
      --right-gradient-color: var(--color-highlight-yellow-2);
    }

    .highlight {
      transition: background-position var(--reveal-time);
      background-color: none;
      background: linear-gradient(
        90deg,
        var(--left-gradient-color) 1.46%,
        var(--right-gradient-color) 50%,
        rgba(255, 255, 255, 0) 50%
      );
      background-size: 201% 100%;
      background-position: 100% 0;
    }

    .can-spotlight {
      color: var(--color-black);
      transition:
        color var(--spotlight-transition-duration),
        background var(--spotlight-transition-duration);
    }

    .highlight.shown {
      background-position: 0 0;
    }

    .highlight.hiddenAfterShown {
      background-position: -99% 0;
    }

    .highlight.pink {
      --left-gradient-color: var(--color-highlight-pink-1);
      --right-gradient-color: var(--color-highlight-pink-2);
    }

    .highlight.orange {
      --left-gradient-color: var(--color-highlight-orange-1);
      --right-gradient-color: var(--color-highlight-orange-2);
    }

    .highlight.blue {
      --left-gradient-color: var(--color-highlight-blue-1);
      --right-gradient-color: var(--color-highlight-blue-2);
    }

    .highlight.green {
      --left-gradient-color: var(--color-highlight-green-1);
      --right-gradient-color: var(--color-highlight-green-2);
    }
  `),s(_,1,U);var ia="0.24.0";var na=ia;var xs=window.matchMedia("(min-width: 480px)"),ys=window.matchMedia("(min-width: 768px)"),ws=window.matchMedia("(min-width: 1024px)"),$s=window.matchMedia("(min-width: 1280px)"),Es=window.matchMedia("(prefers-reduced-motion: reduce)");var ii=(t,e)=>e.some(r=>t instanceof r),sa,la;function ni(){return sa||(sa=[IDBDatabase,IDBObjectStore,IDBIndex,IDBCursor,IDBTransaction])}function si(){return la||(la=[IDBCursor.prototype.advance,IDBCursor.prototype.continue,IDBCursor.prototype.continuePrimaryKey])}var ca=new WeakMap,Hr=new WeakMap,da=new WeakMap,qr=new WeakMap,jr=new WeakMap;function li(t){let e=new Promise((r,a)=>{let o=()=>{t.removeEventListener("success",i),t.removeEventListener("error",n)},i=()=>{r(H(t.result)),o()},n=()=>{a(t.error),o()};t.addEventListener("success",i),t.addEventListener("error",n)});return e.then(r=>{r instanceof IDBCursor&&ca.set(r,t)}).catch(()=>{}),jr.set(e,t),e}function ci(t){if(Hr.has(t))return;let e=new Promise((r,a)=>{let o=()=>{t.removeEventListener("complete",i),t.removeEventListener("error",n),t.removeEventListener("abort",n)},i=()=>{r(),o()},n=()=>{a(t.error||new DOMException("AbortError","AbortError")),o()};t.addEventListener("complete",i),t.addEventListener("error",n),t.addEventListener("abort",n)});Hr.set(t,e)}var Br={get(t,e,r){if(t instanceof IDBTransaction){if(e==="done")return Hr.get(t);if(e==="objectStoreNames")return t.objectStoreNames||da.get(t);if(e==="store")return r.objectStoreNames[1]?void 0:r.objectStore(r.objectStoreNames[0])}return H(t[e])},set(t,e,r){return t[e]=r,!0},has(t,e){return t instanceof IDBTransaction&&(e==="done"||e==="store")?!0:e in t}};function ua(t){Br=t(Br)}function di(t){return t===IDBDatabase.prototype.transaction&&!("objectStoreNames"in IDBTransaction.prototype)?function(e,...r){let a=t.call(dr(this),e,...r);return da.set(a,e.sort?e.sort():[e]),H(a)}:si().includes(t)?function(...e){return t.apply(dr(this),e),H(ca.get(this))}:function(...e){return H(t.apply(dr(this),e))}}function ui(t){return typeof t=="function"?di(t):(t instanceof IDBTransaction&&ci(t),ii(t,ni())?new Proxy(t,Br):t)}function H(t){if(t instanceof IDBRequest)return li(t);if(qr.has(t))return qr.get(t);let e=ui(t);return e!==t&&(qr.set(t,e),jr.set(e,t)),e}var dr=t=>jr.get(t);function ma(t,e,{blocked:r,upgrade:a,blocking:o,terminated:i}={}){let n=indexedDB.open(t,e),v=H(n);return a&&n.addEventListener("upgradeneeded",c=>{a(H(n.result),c.oldVersion,c.newVersion,H(n.transaction),c)}),r&&n.addEventListener("blocked",c=>r(c.oldVersion,c.newVersion,c)),v.then(c=>{i&&c.addEventListener("close",()=>i()),o&&c.addEventListener("versionchange",d=>o(d.oldVersion,d.newVersion,d))}).catch(()=>{}),v}var vi=["get","getKey","getAll","getAllKeys","count"],mi=["put","add","delete","clear"],Vr=new Map;function va(t,e){if(!(t instanceof IDBDatabase&&!(e in t)&&typeof e=="string"))return;if(Vr.get(e))return Vr.get(e);let r=e.replace(/FromIndex$/,""),a=e!==r,o=mi.includes(r);if(!(r in(a?IDBIndex:IDBObjectStore).prototype)||!(o||vi.includes(r)))return;let i=async function(n,...v){let c=this.transaction(n,o?"readwrite":"readonly"),d=c.store;return a&&(d=d.index(v.shift())),(await Promise.all([d[r](...v),o&&c.done]))[0]};return Vr.set(e,i),i}ua(t=>({...t,get:(e,r,a)=>va(e,r)||t.get(e,r,a),has:(e,r)=>!!va(e,r)||t.has(e,r)}));var ha="__bp__",Gr={env:{API_URL:process.env.API_URL??"/services/graphql/",DEBUG:!0,LANGUAGE:process.env.LANGUAGE??"en",USER_API_URL:process.env.USER_API_URL??"/services/current-user/",NEWSLETTER_API_URL:process.env.NEWSLETTER_API_URL??"/services/newsletter/",ROOT:process.env.ROOT}};function W(t,e){return Gr.env[t]??e}function hi(t,e){if(e){for(let[r,a]of Object.entries(t.env))typeof e.env[r]>"u"&&(e.env[r]=a);return e}return t}typeof window<"u"&&(Gr=window[ha]=hi(Gr,window[ha]));var pi="bp_web_components",gi=1,Kr="expires",fi=2,ur=class{constructor(e){l(this,"name");l(this,"debug",W("DEBUG"));l(this,"connection",null);this.name=e.name}async getDatabase(){return this.connection||(this.connection=ma(pi,gi,{upgrade:e=>{e.createObjectStore(this.name).createIndex(Kr,Kr)}})),this.connection.then(e=>this.cleanUp(e))}async cleanUp(e){let r=IDBKeyRange.upperBound(Date.now()),a=await e.transaction(this.name,"readwrite").store.index(Kr).openCursor(r);for(;a;)await a.delete(),a=await a.continue();return e}async attemptTransaction(e){let r=0,a=async(o,i)=>this.getDatabase().then(e).then(o).catch(async n=>{if(++r>fi){i(n);return}return this.getDatabase().then(v=>(v.close(),this.connection=null,a(o,i))).catch(i)});return new Promise(a)}async put(e,r){return this.attemptTransaction(a=>a.put(this.name,r,e)).catch(a=>{this.debug&&console.error(a)})}async get(e){return this.attemptTransaction(r=>r.get(this.name,e)).catch(r=>{this.debug&&console.error(r)})}async clear(){return this.attemptTransaction(e=>e.clear(this.name)).catch(e=>{this.debug&&console.error(e)})}};function bi(...t){return t.map(e=>e.replace(/^\/|\/$/g,"")).join("/")}function me(t,e=W("ROOT",import.meta.url)){let r=e?.replace(/[^/]+\/?$/,"")??"";return bi(r,t)}function pa(t=1e3){return new Promise(e=>{setTimeout(e,t)})}var Be={Timeout:"TIMEOUT",NetworkFailure:"NETWORK_FAILURE",Aborted:"ABORTED"},re=class extends Error{constructor(r,a,o){super(r);this.reason=a;this.detail=o;this.name="BpNetworkError"}};async function fa(t,e){return new Promise((r,a)=>{let o=me(t);fetch(o,{signal:e}).then(async i=>{let n=await i.text();i.ok||a(n),r(n)}).catch(i=>a(i))})}function ga(t,e){return e&&e.status>=400&&e.status<500?!1:e&&e.status>=500||t instanceof Error&&(t.name==="AbortError"||t.name==="TypeError")?!0:t instanceof re?t.reason===Be.Timeout||t.reason===Be.NetworkFailure:!0}async function Wr(t,e,r={}){let{retries:a=2,delay:o=1e3,timeout:i=3e4}=r,n=async()=>(await pa(o),Wr(t,e,{retries:a-1,delay:o*2,timeout:i})),v=new AbortController,c=setTimeout(()=>v.abort(),i);e?.signal&&e.signal.addEventListener("abort",()=>v.abort());try{let d=await fetch(t,{...e,signal:v.signal});return clearTimeout(c),!d.ok&&a>0&&ga(null,d)?n():d}catch(d){if(clearTimeout(c),d instanceof Error&&d.name==="AbortError"){if(e?.signal?.aborted)throw new re(`Request aborted: ${t}`,Be.Aborted);if(a>0)return n();throw new re(`Request timeout after ${i}ms: ${t}`,Be.Timeout)}if(a>0&&ga(d))return n();throw d instanceof Error?new re(d.message,Be.NetworkFailure,{url:t.toString()}):d}}var xi=1e3*60*60*24*90,vr=new Map,ba=new ur({name:"icons"});function yi(t){let{set:e="regular",name:r}=t.match(/((?<set>.+):)?(?<name>.+)/)?.groups??{};return{set:e,name:r}}async function xa(t){let{set:e,name:r}=yi(t),a=`${e}:${r}:${na}`,o=await ba.get(a);if(o)return o.value;let i,n=`/icons/${e}/${r}.svg`;return vr.has(n)?i=vr.get(n):(i=fa(n),vr.set(n,i)),i.then(v=>(ba.put(a,{expires:Date.now()+xi,value:v}).then(()=>{vr.delete(n)}).catch(()=>{}),v))}var ya,wa,$a,Ea,ka,R;ka=[x("bp-icon")];var F=class extends(Ea=g,$a=[h()],wa=[h()],ya=[be()],Ea){constructor(){super(...arguments);l(this,"icon",s(R,8,this)),s(R,11,this);l(this,"size",s(R,12,this)),s(R,15,this);l(this,"xml",s(R,16,this)),s(R,19,this)}updated(r){!r.has("icon")||!this.icon||xa(this.icon).then(a=>{this.xml=a})}render(){return this.xml?K(this.xml):m` <slot></slot> `}};R=b(Ea),u(R,5,"icon",$a,F),u(R,5,"size",wa,F),u(R,5,"xml",ya,F),F=u(R,0,"Icon",ka,F),l(F,"styles",f`
    :host {
      display: inline-flex;
      fill: var(--icon-color, currentColor);
      height: var(--icon-size, var(--size-2-5));
      width: var(--icon-size, var(--size-2-5));
    }

    :host([size="sm"]) {
      --icon-size: var(--size-2);
    }

    :host([size="lg"]) {
      --icon-size: var(--size-3);
    }

    :host([size="xl"]) {
      --icon-size: var(--size-4);
    }

    :host([size="2xl"]) {
      --icon-size: var(--size-5);
    }

    svg {
      display: block;
      width: 100%;
      height: 100%;
    }
  `),s(R,1,F);var{I:Qs}=At;var _a=t=>t.strings===void 0;var je=(t,e)=>{var r,a;let o=t._$AN;if(o===void 0)return!1;for(let i of o)(a=(r=i)._$AO)===null||a===void 0||a.call(r,e,!1),je(i,e);return!0},mr=t=>{let e,r;do{if((e=t._$AM)===void 0)break;r=e._$AN,r.delete(t),t=e}while(r?.size===0)},Aa=t=>{for(let e;e=t._$AM;t=e){let r=e._$AN;if(r===void 0)e._$AN=r=new Set;else if(r.has(t))break;r.add(t),Ei(e)}};function wi(t){this._$AN!==void 0?(mr(this),this._$AM=t,Aa(this)):this._$AM=t}function $i(t,e=!1,r=0){let a=this._$AH,o=this._$AN;if(o!==void 0&&o.size!==0)if(e)if(Array.isArray(a))for(let i=r;i<a.length;i++)je(a[i],!1),mr(a[i]);else a!=null&&(je(a,!1),mr(a));else je(this,t)}var Ei=t=>{var e,r,a,o;t.type==Oe.CHILD&&((e=(a=t)._$AP)!==null&&e!==void 0||(a._$AP=$i),(r=(o=t)._$AQ)!==null&&r!==void 0||(o._$AQ=wi))},hr=class extends ve{constructor(){super(...arguments),this._$AN=void 0}_$AT(e,r,a){super._$AT(e,r,a),Aa(this),this.isConnected=e._$AU}_$AO(e,r=!0){var a,o;e!==this.isConnected&&(this.isConnected=e,e?(a=this.reconnected)===null||a===void 0||a.call(this):(o=this.disconnected)===null||o===void 0||o.call(this)),r&&(je(this,e),mr(this))}setValue(e){if(_a(this._$Ct))this._$Ct._$AI(e,this);else{let r=[...this._$Ct._$AH];r[this._$Ci]=e,this._$Ct._$AI(r,this,0)}}disconnected(){}reconnected(){}};var Sa=()=>new Yr,Yr=class{},Fr=new WeakMap,Ta=De(class extends hr{render(t){return $}update(t,[e]){var r;let a=e!==this.G;return a&&this.G!==void 0&&this.ot(void 0),(a||this.rt!==this.lt)&&(this.G=e,this.dt=(r=t.options)===null||r===void 0?void 0:r.host,this.ot(this.lt=t.element)),$}ot(t){var e;if(typeof this.G=="function"){let r=(e=this.dt)!==null&&e!==void 0?e:globalThis,a=Fr.get(r);a===void 0&&(a=new WeakMap,Fr.set(r,a)),a.get(this.G)!==void 0&&this.G.call(this.dt,void 0),a.set(this.G,t),t!==void 0&&this.G.call(this.dt,t)}else this.G.value=t}get rt(){var t,e,r;return typeof this.G=="function"?(e=Fr.get((t=this.dt)!==null&&t!==void 0?t:globalThis))===null||e===void 0?void 0:e.get(this.G):(r=this.G)===null||r===void 0?void 0:r.value}disconnected(){this.rt===this.lt&&this.ot(void 0)}reconnected(){this.ot(this.lt)}});var O="bp-literary-design",ki=new Set(["book","cell","chapter","char","figure","group","note","optbreak","para","ref","row","sidebar","table","usx","verse"]),Ca,Ra,Pa,Na,Ma,La,S;La=[x(O)];var B=class extends(Ma=g,Na=[h()],Pa=[h({attribute:"title"})],Ra=[h({attribute:"excluded-key-paths"})],Ca=[h({attribute:"usx"})],Ma){constructor(){super(...arguments);l(this,"contentRef",Sa());l(this,"reference",s(S,8,this)),s(S,11,this);l(this,"designTitle",s(S,12,this)),s(S,15,this);l(this,"excludedKeyPaths",s(S,16,this,"[]")),s(S,19,this);l(this,"usx",s(S,20,this)),s(S,23,this)}parseScript(r){let i=new DOMParser().parseFromString(r??"","text/xml").firstElementChild;if(!i||i.tagName!=="usx")throw new Error(`${O}: Missing required <usx> tag`);let n=Ia(i,v=>v.nodeType===Node.ELEMENT_NODE&&ki.has(v.nodeName)?document.createElement(`${O}-${v.nodeName}`):v.cloneNode(),(v,c)=>c.name==="id"?za("data-id",c.value):c.name==="style"?za("data-style",c.value.split(" ").map(d=>`_${d}_`).join(" ")):c.cloneNode(!0));_i(n,`${O}-group`.toUpperCase()),this.contentRef?.value?.lastChild?.remove(),this.contentRef?.value?.appendChild(n)}firstUpdated(r){r.has("usx")&&this.usx&&this.parseScript(this.usx)}willUpdate(r){r.has("usx")&&this.parseScript(this.usx??"")}getElementById(r){return this.shadowRoot?.querySelector(`[data-id="${r}"]`)??null}getElementByKeyPath(r){return this.shadowRoot?.querySelector(`[data-key-path="${r}"]`)??null}removeElementByKeyPath(r){let a=this.shadowRoot?.querySelector(`[data-key-path="${r}"]`);a&&(a.classList.add("hidden-group"),a.nextElementSibling?.nodeName==="BP-LITERARY-DESIGN-OPTBREAK"&&a.nextElementSibling.classList.add("hidden-group"),a.previousElementSibling?.nodeName==="BP-LITERARY-DESIGN-OPTBREAK"&&a.previousElementSibling.classList.add("hidden-group"))}updated(){this.shadowRoot?.querySelectorAll(".hidden-group").forEach(a=>a.classList.remove("hidden-group")),console.log("Excluded paths",this.excludedKeyPaths),(this.excludedKeyPaths.match(/\[(?<stringArray>.*)\]/)?.groups?.stringArray.split(",").map(a=>a.trim())??[]).forEach(a=>this.removeElementByKeyPath(a))}render(){return m`
      <div>
        ${this.designTitle?m`<div class="title">${this.designTitle}</div>`:m`<div class="design-start"></div>`}
        ${this.reference?m`<div class="reference">${this.reference}</div>`:null}
        <div ${Ta(this.contentRef)}></div>
        <slot name="caption"></slot>
      </div>
    `}};S=b(Ma),u(S,5,"reference",Na,B),u(S,5,"designTitle",Pa,B),u(S,5,"excludedKeyPaths",Ra,B),u(S,5,"usx",Ca,B),B=u(S,0,"LiteraryDesign",La,B),l(B,"styles",[ke,f`
      :host {
        --title-font-size: 22px;
        --reference-font-size: 18px;
      }

      bp-literary-design-usx {
        --group-sidebar-color-offset: 6px;
        --group-sidebar-color-width: 4px;
        --group-sidebar-value-offset: 8px;
        --group-body-font-size: 16px;
        --group-title-font-size: 14px;
        --group-sidebar-font-size: 13px;
        --verse-font-size: 12px;
        line-height: var(--line-height-normal);
      }

      /* Used because otherwise pseudo-elements will not be included
        in height calculation when no title. */
      .design-start {
        height: 1px;
      }

      .title {
        font-size: var(--title-font-size);
        font-weight: var(--font-weight-normal);
        line-height: var(--line-height-snug);
      }

      .reference {
        font-size: var(--reference-font-size);
        font-weight: var(--font-weight-bold);
      }

      .hidden-group {
        display: none;
      }

      .hidden-optbreak {
        display: none;
      }

      bp-literary-design-para {
        display: block;
      }

      bp-literary-design-group {
        font-size: var(--group-body-font-size);
        border-radius: var(--radius-lg);
        display: block;
        padding: 0;
        position: relative;
      }

      bp-literary-design-group[title] {
        margin-top: var(--group-title-height);
      }

      bp-literary-design-group[type="primary"],
      bp-literary-design-group[type="primary-alt"],
      bp-literary-design-group[type="secondary"] {
        box-sizing: border-box;
        margin: var(--size-1-5) 0;
        padding: var(--size-1-5);
      }

      bp-literary-design-group[type="primary-alt"] {
        padding: var(--size-1-5) 0 0;
      }

      bp-literary-design-group
        > bp-literary-design-group:last-of-type[type="primary"],
      bp-literary-design-group
        > bp-literary-design-group:last-of-type[type="primary-alt"],
      bp-literary-design-group
        > bp-literary-design-group:last-of-type[type="secondary"] {
        margin-bottom: 0;
      }

      bp-literary-design-group[type="primary"][title],
      bp-literary-design-group[type="primary-alt"][title],
      bp-literary-design-group[type="secondary"][title] {
        border-radius: 0 var(--radius-lg) var(--radius-lg) var(--radius-lg);
        margin-top: calc(var(--group-title-height) + var(--size-1-5));
      }

      bp-literary-design-group
        > bp-literary-design-group:first-of-type[type="primary"][title],
      bp-literary-design-group
        > bp-literary-design-group:first-of-type[type="primary-alt"][title],
      bp-literary-design-group
        > bp-literary-design-group:first-of-type[type="secondary"][title] {
        margin-top: var(--group-title-height);
      }

      bp-literary-design-group[type="primary-alt"][title] {
        border-radius: 0;
      }

      bp-literary-design-group[type="primary"][title]::before,
      bp-literary-design-group[type="primary-alt"][title]::before,
      bp-literary-design-group[type="secondary"][title]::before,
      bp-literary-design-group[type="bare"][title]::before {
        border-radius: var(--radius-lg) var(--radius-lg) 0 0;
        bottom: 100%;
        box-sizing: border-box;
        content: attr(title);
        display: block;
        font-size: var(--group-title-font-size);
        font-weight: var(--font-weight-semibold);
        left: -2px;
        margin-right: var(--size-2);
        padding: var(--size-0-5) var(--size-1);
        position: absolute;
        z-index: 1;
      }

      bp-literary-design-group[type="bare"][title]::before {
        padding: var(--size-0-5) 0;
      }

      bp-literary-design-group::before {
        transition:
          color var(--spotlight-transition-duration),
          background-color var(--spotlight-transition-duration);
      }

      bp-literary-design-group[type="primary"][title]::before {
        color: white;
        background-color: var(--color-black);
      }

      bp-literary-design-group[type="primary-alt"][title]::before {
        color: var(--color-black);
        padding: var(--size-0-5) var(--size-0-5);
      }

      bp-literary-design-group[type="secondary"][title]::before {
        background-color: var(--color-neutral-10);
        color: var(--color-black);
      }

      bp-literary-design-group {
        color: var(--color-black);
        transition:
          color var(--spotlight-transition-duration),
          border var(--spotlight-transition-duration);
      }

      bp-literary-design-group[type="primary"] {
        border: 2px solid var(--color-black);
      }

      bp-literary-design-group[type="primary-alt"] {
        border-top: 2px solid var(--color-black);
        border-radius: 0px;
      }

      bp-literary-design-group[type="secondary"] {
        border: 2px solid var(--color-neutral-10);
      }

      bp-literary-design-group::after {
        transition: background var(--spotlight-transition-duration);
      }

      bp-literary-design-group[sidebar-color]::after {
        background: var(--color-black);
        border-radius: 100px;
        bottom: 0;
        content: "";
        display: block;
        inset-inline-start: 0;
        position: absolute;
        top: 0;
        transform: translateX(calc(-100% - var(--group-sidebar-color-offset)));
        width: var(--group-sidebar-color-width);
      }

      [dir="rtl"] bp-literary-design-group[sidebar-color]::after {
        transform: translateX(calc(100% + var(--group-sidebar-color-offset)));
      }

      bp-literary-design-group[sidebar-color="red"]::after {
        background: var(--color-red-50);
      }

      bp-literary-design-group[sidebar-color="orange"]::after {
        background: var(--color-orange-50);
      }

      bp-literary-design-group[sidebar-color="green"]::after {
        background: var(--color-green-50);
      }

      bp-literary-design-group[sidebar-color="turquoise"]::after {
        background: var(--color-turquoise-50);
      }

      bp-literary-design-group[sidebar-color="cyan"]::after {
        background: var(--color-cyan-50);
      }

      bp-literary-design-group[sidebar-color="blue"]::after {
        background: var(--color-blue-50);
      }

      bp-literary-design-group[sidebar-color="violet"]::after {
        background: var(--color-violet-50);
      }

      bp-literary-design-group[sidebar-color="purple"]::after {
        background: var(--color-purple-50);
      }

      bp-literary-design-group[sidebar-color="tan"]::after {
        background: var(--color-tan-50);
      }

      bp-literary-design-group[indent="1"] {
        margin-inline-start: 1.5rem;
      }

      bp-literary-design-group[indent="2"] {
        margin-inline-start: 3rem;
      }

      bp-literary-design-group[indent="3"] {
        margin-inline-start: 4.5rem;
      }

      bp-literary-design-group[indent="4"] {
        margin-inline-start: 6rem;
      }

      bp-literary-design-group[indent="5"] {
        margin-inline-start: 7.5rem;
      }

      bp-literary-design-group-sidebar-value {
        transition: color var(--spotlight-transition-duration);
        color: var(--color-gray);
        font-size: var(--group-sidebar-font-size);
        display: block;
        inset-inline-start: 0;
        padding-bottom: 2px;
        position: absolute;
        top: 50%;
        transform: translate(
          calc(-100% - var(--group-sidebar-value-offset)),
          -50%
        );
      }

      [dir="rtl"] bp-literary-design-group-sidebar-value {
        transform: translate(
          calc(100% + var(--group-sidebar-value-offset)),
          -50%
        );
      }

      bp-literary-design-group[sidebar-color]
        bp-literary-design-group-sidebar-value {
        transform: translate(
          calc(
            -100% - var(--group-sidebar-color-width) - var(
                --group-sidebar-color-offset
              ) - var(--group-sidebar-value-offset)
          ),
          -50%
        );
      }

      bp-literary-design-char {
        transition: color var(--spotlight-transition-duration);
        color: var(--color-black);
      }

      bp-literary-design-char[data-style="_em_"] {
        color: inherit;
        font-style: italic;
      }

      bp-literary-design-verse {
        font-size: var(--verse-font-size);
        vertical-align: 4px;
      }

      bp-literary-design-optbreak {
        transition: border var(--spotlight-transition-duration);
        border-bottom: 2px solid var(--color-neutral-10);
        display: block;
        margin: var(--size-1-5) 0;
      }

      bp-literary-design-note {
        display: none;
      }

      bp-literary-design-word-transliteration {
        font-style: italic;
      }

      bp-literary-design-word {
        white-space: nowrap;
      }
    `]),s(S,1,B);window.customElements.define(`${O}-group`,class extends HTMLElement{connectedCallback(){if(this.hasAttribute("title")&&this.style.setProperty("--group-title-height",window.getComputedStyle(this,":before").height),this.hasAttribute("sidebar-value")){let t=document.createElement(`${O}-group-sidebar-value`);t.innerText=this.getAttribute("sidebar-value"),this.insertBefore(t,this.firstChild)}}});window.customElements.define(`${O}-verse`,class extends HTMLElement{connectedCallback(){let t=this.getAttribute("number")??"";this.innerText=t}});window.customElements.define(`${O}-char`,class extends HTMLElement{connectedCallback(){let t=this.getAttribute("word-lang"),e=this.getAttribute("word-original"),r=this.getAttribute("word-transliteration");if(e||r){let c=[];if(e&&c.push(`<bp-text-${t}>${e}</bp-text-${t}>`),r&&c.push(`<${O}-word-transliteration>${r}</${O}-word-transliteration>`),c.length){let d=document.createElement(`${O}-word`);d.innerHTML=`&nbsp;(${c.join(" \u2022 ")})`,this.appendChild(d)}}let a=this.getAttribute("highlight-show"),o=this.getAttribute("highlight-color"),i=this.getAttribute("highlight-reveal-time");if(a||i||o){let c=document.createElement("bp-highlight");i&&c.setAttribute("reveal-time",i),o&&c.setAttribute("color",o),c.setAttribute("can-spotlight","true"),c.setAttribute("show",a??"false"),c.setAttribute("data-id",this.getAttribute("data-id")??""),this.setAttribute("data-id","");for(let d of Array.from(this.childNodes))c.appendChild(d);this.appendChild(c)}let n=this.getAttribute("mark-variant"),v=this.getAttribute("mark-color");if(n||v){let c=document.createElement("bp-mark");c.setAttribute("color",v??""),c.setAttribute("variant",n??"");for(let d of Array.from(this.childNodes))c.appendChild(d);this.appendChild(c)}}});function za(t,e){let r=document.createAttribute(t);return r.value=e,r}function _i(t,e){let r=document.createTreeWalker(t,NodeFilter.SHOW_ELEMENT),a=null,o=null,i=[],n=new Map,v=()=>i.map(d=>d.value).join("."),c=()=>"group-"+i.map(d=>d.value).join("-");for(;r.nextNode();){if(r.currentNode.nodeName!==e)continue;let d=r.currentNode.parentNode;!a||d!==a?(d&&n.has(d)?(i=i.slice(0,(n.get(d)??0)+1),i[i.length-1].value+=1):(!o||!o.contains(r.currentNode)?(i.length?(i=i.slice(0,1),i[i.length-1].value+=1):i.push({value:1}),o=d):i.push({value:1}),d&&n.set(d,i.length-1)),a=d):i[i.length-1].value+=1,r.currentNode.setAttribute("data-key-path",v()),r.currentNode.setAttribute("data-id",c())}}function Ia(t,e,r){let a=e(t);if(t.childNodes.forEach(o=>{a.appendChild(Ia(o,e,r))}),t.nodeType===Node.ELEMENT_NODE&&a.nodeType===Node.ELEMENT_NODE){let o=t,i=a;for(let n=0,v=o.attributes.length;n<v;n++){let c=o.attributes.item(n);if(!c)continue;let d=r(t,c);d&&i.setAttributeNode(d)}}return a}var pr=Ge(He(),1);var Ua,Oa,Da,_e;Da=[x("bp-macro-literary-design")];var he=class extends(Oa=g,Ua=[h({type:Object,attribute:"design-data"})],Oa){constructor(){super(...arguments);l(this,"data",s(_e,8,this)),s(_e,11,this)}renderGroup(r,a,o,i=0){let n=(0,pr.default)("group",{leaf:!r.subgroups?.length,"has-detail-list":r.detailList?.length,"has-title":r.title,"fill-background":r.fillBackground}),v=r.reference?m`<div class="reference">
          <bp-mark color="${r.markColor}" variant="${r.markVariant}">
            ${r.reference}
          </bp-mark>
        </div>`:"",c=r.title?m`<div class="title">${K(r.title)}</div>`:"",d=(0,pr.default)("detail-list",r.detailListType),y=r.detailList?.length?m`<div class="${d}">
          <ol>
            ${r.detailList.map(w=>{let T=w,D=r.detailListType=="custom"&&T.ref?m`<span class="li-ref">${T.ref}</span> `:"";return T?m`<li
                data-indent="${T.indent??0}"
                value="${T.tag??""}"
              >
                ${a=="vertical"?D:""}
                <span class="li-detail">
                  ${a=="horizontal"?D:""}
                  ${K(T.detail??w)}</span
                >
              </li>`:null})}
          </ol>
        </div>`:"",p=r.subgroups?.length?m`<div class="subgroups">
          ${r.subgroups.map((w,T)=>this.renderGroup(w,a,`${o}-${T+1}`,i+1))}
        </div>`:"",k=r.tag?m`<div class="tag">${r.tag}</div>`:"";return m`<div
      class="${n}"
      data-mark-color="${r.markColor}"
      data-mark-variant="${r.markVariant}"
      data-id="group-${o}"
      data-indent="${r.indent}"
      data-depth=${i}
    >
      ${v} ${c} ${y} ${p} ${k}
    </div>`}render(){if(!this.data?.groups?.length)return;let r=(0,pr.default)("container",this.data.direction);return m`<div class="${r}">
      ${this.data.groups.map((a,o)=>this.renderGroup(a,this.data?.direction??"",`${o+1}`))}
    </div>`}};_e=b(Oa),u(_e,5,"data",Ua,he),he=u(_e,0,"MacroLiteraryDesign",Da,he),l(he,"styles",[ke,f`
      :host {
        /* Prevent text contents from being resized by slide. */
        --font-size-xs: 13px;
        --font-size-sm: 14px;
        --font-size-md: 16px;
        --font-size-lg: 18px;
        --font-size-xl: 20px;
      }

      .container {
        display: flex;
        flex-direction: row;
        gap: var(--size-1);
        padding: var(--size-1);
      }

      .container.vertical {
        width: var(--vertical-width);
        flex-direction: column;
      }

      .group {
        --border-color: var(--color-black);
        --indent: 0px;
        position: relative;
        padding: var(--size-1);
        border-radius: var(--radius-md);
        border: 2px solid var(--border-color);
        gap: var(--size-0-5);
        display: flex;
        flex-direction: column;
        margin-top: var(--indent);
        transition:
          color var(--spotlight-transition-duration),
          border var(--spotlight-transition-duration),
          background-color var(--spotlight-transition-duration);
      }

      .vertical .group {
        align-content: start;
        margin-top: unset;
        margin-inline-start: var(--indent);
      }

      .leaf {
        width: var(--size-10);
        min-height: calc(var(--size-25) - var(--indent));
      }

      .leaf.has-detail-list {
        min-width: var(--size-20);
        width: var(--size-20);
      }

      .leaf.has-title {
        min-width: var(--size-15);
        width: var(--size-15);
      }

      .leaf.has-detail-list.has-title {
        min-width: var(--size-20);
        width: var(--size-20);
      }

      .vertical .leaf {
        min-height: unset;
        width: unset;
      }

      .vertical .leaf.has-detail-list.has-title {
        min-height: unset;
        width: unset;
      }

      .title {
        font-weight: var(--font-weight-semibold);
        hyphens: auto;
        color: var(--color-black);
        transition: color var(--spotlight-transition-duration);
      }

      .detail-list {
        font-size: var(--font-size-sm);
        line-height: var(--line-height-normal);
        hyphens: auto;
        color: var(--color-black);
        transition: color var(--spotlight-transition-duration);
      }

      .detail-list ol {
        margin: var(--size-1) 0 var(--size-1) -26px;
        list-style: disc;
      }

      .detail-list.custom ol {
        margin-left: -32px;
        list-style: none;
      }

      .detail-list.custom li {
        display: flex;
      }

      .detail-list.custom li::before {
        padding-right: 5px;
        white-space: nowrap;
      }

      .custom li::before {
        content: attr(value) " -";
      }

      .custom li[value=""]::before {
        content: "•";
        font-size: 22px;
        line-height: 23px;
        margin-top: -2px;
        margin-right: 4px;
        margin-left: -1px;
      }

      .detail-list.custom li[data-indent="1"] {
        padding-left: var(--size-2);
      }

      .detail-list.custom li[data-indent="2"] {
        padding-left: var(--size-4);
      }

      .detail-list.custom li[data-indent="3"] {
        padding-left: var(--size-6);
      }

      .li-ref {
        white-space: nowrap;
        margin-right: 4px;
        font-weight: var(--font-weight-semibold);
      }

      .li-detail {
        word-wrap: break-word;
        min-width: var(--size-1);
      }

      .group[data-indent="1"] {
        --indent: var(--size-3);
      }

      .group[data-indent="2"] {
        --indent: var(--size-6);
      }

      .group[data-indent="3"] {
        --indent: var(--size-9);
      }

      .group[data-indent="4"] {
        --indent: var(--size-12);
      }

      .group[data-indent="5"] {
        --indent: var(--size-15);
      }

      .group[data-indent="6"] {
        --indent: calc(var(--size-15) + var(--size-3));
      }

      .group[data-indent="7"] {
        --indent: calc(var(--size-15) + var(--size-6));
      }

      .subgroups {
        padding-top: var(--size-0-5);
        display: flex;
        flex-direction: row;
        gap: var(--size-1);
        flex-grow: 1;
      }

      .vertical .subgroups {
        flex-direction: column;
      }

      .fill-background {
        background-color: color-mix(
          in srgb,
          var(--border-color),
          transparent 85%
        );
      }

      .tag {
        position: absolute;
        bottom: calc(100% + var(--size-1));
        inset-inline-end: 0;
        inset-inline-start: 0;
        display: flex;
        flex-direction: row;
        justify-content: center;
      }

      .vertical .tag {
        inset-inline-end: calc(100% + var(--size-1));
        inset-inline-start: unset;
        top: 0;
        bottom: 0;
        flex-direction: column;
      }

      .group[data-mark-color="red"][data-mark-variant="highlight-light"] {
        --border-color: var(--color-red-10);
      }

      .group[data-mark-color="orange"][data-mark-variant="highlight-light"] {
        --border-color: var(--color-orange-10);
      }

      .group[data-mark-color="green"][data-mark-variant="highlight-light"] {
        --border-color: var(--color-green-10);
      }

      .group[data-mark-color="turquoise"][data-mark-variant="highlight-light"] {
        --border-color: var(--color-turquoise-10);
      }

      .group[data-mark-color="cyan"][data-mark-variant="highlight-light"] {
        --border-color: var(--color-cyan-10);
      }

      .group[data-mark-color="blue"][data-mark-variant="highlight-light"] {
        --border-color: var(--color-blue-10);
      }

      .group[data-mark-color="violet"][data-mark-variant="highlight-light"] {
        --border-color: var(--color-violet-10);
      }

      .group[data-mark-color="purple"][data-mark-variant="highlight-light"] {
        --border-color: var(--color-purple-10);
      }

      .group[data-mark-color="tan"][data-mark-variant="highlight-light"] {
        --border-color: var(--color-tan-10);
      }

      .group[data-mark-color="black"][data-mark-variant="highlight-light"] {
        --border-color: var(--color-neutral-10);
      }

      .group[data-mark-color="red"][data-mark-variant="highlight"] {
        --border-color: var(--color-red-50);
      }

      .group[data-mark-color="orange"][data-mark-variant="highlight"] {
        --border-color: var(--color-orange-50);
      }

      .group[data-mark-color="green"][data-mark-variant="highlight"] {
        --border-color: var(--color-green-50);
      }

      .group[data-mark-color="turquoise"][data-mark-variant="highlight"] {
        --border-color: var(--color-turquoise-50);
      }

      .group[data-mark-color="cyan"][data-mark-variant="highlight"] {
        --border-color: var(--color-cyan-50);
      }

      .group[data-mark-color="blue"][data-mark-variant="highlight"] {
        --border-color: var(--color-blue-50);
      }

      .group[data-mark-color="violet"][data-mark-variant="highlight"] {
        --border-color: var(--color-violet-50);
      }

      .group[data-mark-color="purple"][data-mark-variant="highlight"] {
        --border-color: var(--color-purple-50);
      }

      .group[data-mark-color="tan"][data-mark-variant="highlight"] {
        --border-color: var(--color-tan-50);
      }

      .group[data-mark-color="black"][data-mark-variant="highlight"] {
        --border-color: var(--color-neutral-50);
      }

      .group[data-mark-color="red"][data-mark-variant="highlight-dark"] {
        --border-color: var(--color-red-70);
      }

      .group[data-mark-color="orange"][data-mark-variant="highlight-dark"] {
        --border-color: var(--color-orange-70);
      }

      .group[data-mark-color="green"][data-mark-variant="highlight-dark"] {
        --border-color: var(--color-green-70);
      }

      .group[data-mark-color="turquoise"][data-mark-variant="highlight-dark"] {
        --border-color: var(--color-turquoise-70);
      }

      .group[data-mark-color="cyan"][data-mark-variant="highlight-dark"] {
        --border-color: var(--color-cyan-70);
      }

      .group[data-mark-color="blue"][data-mark-variant="highlight-dark"] {
        --border-color: var(--color-blue-70);
      }

      .group[data-mark-color="violet"][data-mark-variant="highlight-dark"] {
        --border-color: var(--color-violet-70);
      }

      .group[data-mark-color="purple"][data-mark-variant="highlight-dark"] {
        --border-color: var(--color-purple-70);
      }

      .group[data-mark-color="tan"][data-mark-variant="highlight-dark"] {
        --border-color: var(--color-tan-70);
      }

      .group[data-mark-color="black"][data-mark-variant="highlight-dark"] {
        --border-color: var(--color-neutral-70);
      }
    `]),s(_e,1,he);var qa,Ha,Ba,ja,Va,P;Va=[x("bp-logo")];var Y=class extends(ja=g,Ba=[h()],Ha=[h()],qa=[h()],ja){constructor(){super(...arguments);l(this,"title",s(P,8,this,"BibleProject Logo")),s(P,11,this);l(this,"variant",s(P,12,this,"default")),s(P,15,this);l(this,"lang",s(P,16,this,W("LANGUAGE")??"en")),s(P,19,this)}get src(){switch(this.variant){case"logo-mark":return me("/bibleproject-logo-mark.svg");case"word-mark":return this.lang==="es"?me("/proyectobiblia-word-mark.svg"):me("/bibleproject-word-mark.svg");default:return this.lang==="es"?"/proyectobiblia.svg":me("/bibleproject.svg")}}render(){return m`
      <img
        src="${this.src}"
        style="height: var(--height);"
        title="${this.title}"
      />
    `}};P=b(ja),u(P,5,"title",Ba,Y),u(P,5,"variant",Ha,Y),u(P,5,"lang",qa,Y),Y=u(P,0,"Logo",Va,Y),l(Y,"styles",f`
    :host {
      --height: var(--logo-height, var(--size-4));

      display: block;
    }

    img {
      display: block;
    }
  `),s(P,1,Y);var Ga,Ka,Wa,Fa,Ya,Ja,Qa,Xa,Za,E;Za=[x("bp-lookup")];var C=class extends(Xa=g,Qa=[h({attribute:"anchor-position"})],Ja=[h({type:Boolean,attribute:"no-animation",converter:r=>r==="true"})],Ya=[h({type:Boolean,attribute:"show"})],Fa=[h({attribute:"hebrew"})],Wa=[h({attribute:"roman"})],Ka=[h({attribute:"phonetic"})],Ga=[h({attribute:"num-results"})],Xa){constructor(){super(...arguments);l(this,"anchorPosition",s(E,8,this,"bottom-left")),s(E,11,this);l(this,"noAnimation",s(E,12,this,!1)),s(E,15,this);l(this,"show",s(E,16,this,!1)),s(E,19,this);l(this,"hebrew",s(E,20,this)),s(E,23,this);l(this,"roman",s(E,24,this)),s(E,27,this);l(this,"phonetic",s(E,28,this)),s(E,31,this);l(this,"numResults",s(E,32,this)),s(E,35,this)}render(){let r=this.noAnimation?"--lookup-reveal-duration: 0;":"";return m`
      <div
        style=${r}
        class="lookup ${this.show?"shown":"hidden"} anchor-${this.anchorPosition}"
      >
        <div class="background"></div>
        <span class="word"><slot></slot></span>
        <div class="box-arrow"></div>
        <div class="information-container">
          <div class="information">
            <div class="top-info">
              <bp-text-hebrew class="hebrew">${this.hebrew}</bp-text-hebrew>
              <div class="roman">${this.roman}</div>
            </div>
            <div class="bottom-info">
              <div class="phonetic">${this.phonetic}</div>
              <div class="num-results">${this.numResults} Results</div>
            </div>
          </div>
        </div>
      </div>
    `}};E=b(Xa),u(E,5,"anchorPosition",Qa,C),u(E,5,"noAnimation",Ja,C),u(E,5,"show",Ya,C),u(E,5,"hebrew",Fa,C),u(E,5,"roman",Wa,C),u(E,5,"phonetic",Ka,C),u(E,5,"numResults",Ga,C),C=u(E,0,"Lookup",Za,C),l(C,"styles",f`
    .lookup {
      --arrow-size: 12px;
      --min-box-width: 250px;
      --lookup-reveal-duration: var(--duration-long);
      display: inline-block;
      position: relative;
    }

    .word {
      position: relative;
    }

    .background {
      position: absolute;
      top: 0;
      bottom: 0;
      left: -3px;
      right: -3px;
      transition: background-color var(--lookup-reveal-duration);
      z-index: -1;
    }

    .box-arrow {
      position: absolute;
      border-left: var(--arrow-size) solid transparent;
      border-right: var(--arrow-size) solid transparent;
      box-shadow: 0px 4px 34px rgb(0 0 0 / 15%);
      transition:
        border-bottom-color var(--lookup-reveal-duration),
        border-top-color var(--lookup-reveal-duration);
      z-index: var(--z-20);
    }

    .anchor-bottom-left .box-arrow,
    .anchor-bottom-right .box-arrow {
      top: calc(100% - 2px);
      border-bottom: var(--arrow-size) solid transparent;
    }

    .anchor-top-left .box-arrow,
    .anchor-top-right .box-arrow {
      bottom: calc(100% - 2px);
      border-top: var(--arrow-size) solid transparent;
    }

    .anchor-bottom-left .box-arrow,
    .anchor-top-left .box-arrow {
      left: 16px;
    }

    .anchor-bottom-right .box-arrow,
    .anchor-top-right .box-arrow {
      right: 16px;
    }

    .shown .background {
      background-color: #d7ecff;
    }

    .shown .box-arrow {
      border-bottom-color: #298ae2;
    }

    .anchor-top-left.shown .box-arrow,
    .anchor-top-right.shown .box-arrow {
      border-top-color: var(--color-white);
    }

    .information-container {
      position: absolute;
      z-index: var(--z-10);
    }

    .anchor-bottom-left .information-container,
    .anchor-bottom-right .information-container {
      top: calc(100% + 10px);
    }

    .anchor-top-left .information-container,
    .anchor-top-right .information-container {
      bottom: calc(100% + 10px);
    }

    .anchor-top-left .information-container,
    .anchor-bottom-left .information-container {
      left: -4px;
    }

    .anchor-top-right .information-container,
    .anchor-bottom-right .information-container {
      right: -4px;
    }

    .information {
      background: var(--color-white);
      box-shadow: 0px 4px 34px rgb(0 0 0 / 15%);
      border-radius: 12px;
      min-width: var(--min-box-width);
      opacity: 0;
      transition: opacity var(--lookup-reveal-duration);
    }

    .shown .information {
      opacity: 1;
    }

    .top-info {
      border-radius: 12px 12px 0 0;
      background-color: #298ae2;
      padding: var(--size-2) var(--size-2-5);
    }

    .hebrew {
      font-weight: var(--font-weight-normal);
      font-size: var(--font-size-6xl);
      line-height: var(--line-height-tight);
      color: #9fd2ff;
    }

    .roman {
      font-weight: var(--font-weight-semibold);
      font-size: var(--font-size-6xl);
      line-height: var(--line-height-tight);
      color: var(--color-white);
    }

    .bottom-info {
      border-radius: 0 0 12px 12px;
      padding: var(--size-2) var(--size-2-5);
    }

    .phonetic {
      font-family: sans-serif; // Graphik messes phoenetics up
      font-weight: var(--font-weight-normal);
      font-size: var(--font-size-4xl);
      line-height: var(--line-height-tight);
      color: var(--color-black);
    }

    .num-results {
      font-weight: var(--font-weight-normal);
      font-size: var(--font-size-4xl);
      line-height: var(--line-height-tight);
      color: var(--color-neutral-50);
    }
  `),s(E,1,C);var no=Ge(He(),1);var eo=f`
  mark {
    padding: var(--size-px) var(--size-0-5);
    border-radius: var(--radius-sm);
    font-weight: var(--font-weight-semibold);
    -webkit-box-decoration-break: clone;
    box-decoration-break: clone;
    line-height: var(--line-height-normal);
    transition:
      color var(--spotlight-transition-duration),
      background-color var(--spotlight-transition-duration);
  }

  .text {
    background-color: transparent;
    padding: 0px;
    border-radius: 0px;
  }

  .red {
    color: var(--color-red-50);
  }

  .orange {
    color: var(--color-orange-50);
  }

  .green {
    color: var(--color-green-50);
  }

  .turquoise {
    color: var(--color-turquoise-50);
  }

  .cyan {
    color: var(--color-cyan-50);
  }

  .blue {
    color: var(--color-blue-50);
  }

  .violet {
    color: var(--color-violet-50);
  }

  .purple {
    color: var(--color-purple-50);
  }

  .tan {
    color: var(--color-tan-50);
  }

  .black {
    color: var(--color-neutral-90);
  }

  .red.highlight-light {
    color: var(--color-red-60);
    background-color: var(--color-red-10);
  }

  .orange.highlight-light {
    color: var(--color-orange-60);
    background-color: var(--color-orange-10);
  }

  .green.highlight-light {
    color: var(--color-green-60);
    background-color: var(--color-green-10);
  }

  .turquoise.highlight-light {
    color: var(--color-turquoise-60);
    background-color: var(--color-turquoise-10);
  }

  .cyan.highlight-light {
    color: var(--color-cyan-60);
    background-color: var(--color-cyan-10);
  }

  .blue.highlight-light {
    color: var(--color-blue-60);
    background-color: var(--color-blue-10);
  }

  .violet.highlight-light {
    color: var(--color-violet-60);
    background-color: var(--color-violet-10);
  }

  .purple.highlight-light {
    color: var(--color-purple-60);
    background-color: var(--color-purple-10);
  }

  .tan.highlight-light {
    color: var(--color-tan-60);
    background-color: var(--color-tan-10);
  }

  .black.highlight-light {
    color: var(--color-neutral-60);
    background-color: var(--color-neutral-10);
  }

  .red.highlight {
    color: var(--color-white);
    background-color: var(--color-red-50);
  }

  .orange.highlight {
    color: var(--color-white);
    background-color: var(--color-orange-50);
  }

  .green.highlight {
    color: var(--color-white);
    background-color: var(--color-green-50);
  }

  .turquoise.highlight {
    color: var(--color-white);
    background-color: var(--color-turquoise-50);
  }

  .cyan.highlight {
    color: var(--color-white);
    background-color: var(--color-cyan-50);
  }

  .blue.highlight {
    color: var(--color-white);
    background-color: var(--color-blue-50);
  }

  .violet.highlight {
    color: var(--color-white);
    background-color: var(--color-violet-50);
  }

  .purple.highlight {
    color: var(--color-white);
    background-color: var(--color-purple-50);
  }

  .tan.highlight {
    color: var(--color-white);
    background-color: var(--color-tan-50);
  }

  .black.highlight {
    color: var(--color-white);
    background-color: var(--color-neutral-50);
  }

  .red.highlight-dark {
    color: var(--color-white);
    background-color: var(--color-red-70);
  }

  .orange.highlight-dark {
    color: var(--color-white);
    background-color: var(--color-orange-70);
  }

  .green.highlight-dark {
    color: var(--color-white);
    background-color: var(--color-green-70);
  }

  .turquoise.highlight-dark {
    color: var(--color-white);
    background-color: var(--color-turquoise-70);
  }

  .cyan.highlight-dark {
    color: var(--color-white);
    background-color: var(--color-cyan-70);
  }

  .blue.highlight-dark {
    color: var(--color-white);
    background-color: var(--color-blue-70);
  }

  .violet.highlight-dark {
    color: var(--color-white);
    background-color: var(--color-violet-70);
  }

  .purple.highlight-dark {
    color: var(--color-white);
    background-color: var(--color-purple-70);
  }

  .tan.highlight-dark {
    color: var(--color-white);
    background-color: var(--color-tan-70);
  }

  .black.highlight-dark {
    color: var(--color-white);
    background-color: var(--color-neutral-70);
  }
`;var ro,to,ao,oo,io,N;io=[x("bp-mark")];var J=class extends(oo=g,ao=[h()],to=[h()],ro=[h({type:Boolean,attribute:"can-spotlight"})],oo){constructor(){super(...arguments);l(this,"color",s(N,8,this,"orange")),s(N,11,this);l(this,"variant",s(N,12,this,"highlight")),s(N,15,this);l(this,"canSpotlight",s(N,16,this)),s(N,19,this)}render(){let r=(0,no.default)(this.color,this.variant,{"can-spotlight":this.canSpotlight});return m`<mark class="${r}"><slot></slot></mark>`}};N=b(oo),u(N,5,"color",ao,J),u(N,5,"variant",to,J),u(N,5,"canSpotlight",ro,J),J=u(N,0,"Mark",io,J),l(J,"styles",eo),s(N,1,J);var so,lo,co,uo,vo,M;vo=[x("bp-scripture-callout")];var Q=class extends(uo=g,co=[h()],lo=[h()],so=[h()],uo){constructor(){super(...arguments);l(this,"reference",s(M,8,this)),s(M,11,this);l(this,"translation",s(M,12,this)),s(M,15,this);l(this,"footnote",s(M,16,this)),s(M,19,this)}render(){return m`
      <figure>
        <header>
          ${this.reference&&m` <span class="reference">${this.reference}</span> `}
          ${this.translation&&m` <span class="translation">${this.translation}</span> `}
        </header>

        <slot></slot>

        ${this.footnote&&m` <footer>${this.footnote}</footer> `}

        <slot name="caption"></slot>
      </figure>
    `}};M=b(uo),u(M,5,"reference",co,Q),u(M,5,"translation",lo,Q),u(M,5,"footnote",so,Q),Q=u(M,0,"ScriptureCallout",vo,Q),l(Q,"styles",f`
    :host {
      display: block;
      margin: var(--size-2) 0;
    }

    ::slotted(p) {
      margin: 0 !important;
    }

    ::slotted(bp-caption) {
      padding: var(--size-1);
      font-size: inherit;
      background-color: var(--color-neutral-05);
      border-radius: var(--radius-md);
    }

    figure {
      display: flex;
      flex-direction: column;
      gap: var(--size-1);
      box-shadow: inset var(--size-1) 0 0 -5px var(--color-neutral-10);
      padding: 0 0 0 var(--size-2);
      margin: 0;
      line-height: var(--line-height-normal);
    }

    header {
      display: flex;
      gap: var(--size-1);
    }

    footer {
      color: var(--color-gray);
      font-size: var(--font-size-xs);
    }

    .reference {
      font-weight: var(--font-weight-bold);
    }

    .translation {
      color: var(--color-gray);
      font-size: var(--font-size-xs);
      font-weight: var(--font-weight-semibold);
      vertical-align: 4px;
    }
  `),s(M,1,Q);var mo,ho,po,Ae;po=[x("bp-scripture-link")];var pe=class extends(ho=g,mo=[h()],ho){constructor(){super(...arguments);l(this,"reference",s(Ae,8,this)),s(Ae,11,this)}handleClick(r){r.preventDefault(),document.dispatchEvent(new CustomEvent("bp:scripture_link",{detail:{reference:this.reference}}))}render(){return m` <button @click="${this.handleClick}"><slot></slot></button> `}};Ae=b(ho),u(Ae,5,"reference",mo,pe),pe=u(Ae,0,"ScriptureLink",po,pe),l(pe,"styles",f`
    :host {
      display: inline-block;
    }

    button {
      font: var(--font-sans);
      border: unset;
      background: unset;
      padding: unset;
      font-size: inherit;
      color: inherit;
      cursor: pointer;
      text-align: inherit;
      line-height: inherit;
      text-decoration: underline;
    }
  `),s(Ae,1,pe);var go=t=>t??$;var fo,bo,xo,yo,wo,L;wo=[x("bp-slide-anchor")];var X=class extends(yo=g,xo=[h({attribute:"slide-id"})],bo=[h({type:Boolean,attribute:"show"})],fo=[be()],yo){constructor(){super(...arguments);l(this,"slideId",s(L,8,this)),s(L,11,this);l(this,"show",s(L,12,this,!1)),s(L,15,this);l(this,"empty",s(L,16,this,!0)),s(L,19,this)}scrollIntoView(){let r;this.parentElement?.tagName&&this.parentElement?.tagName==="P"?r=this.parentElement.previousElementSibling:r=this.previousElementSibling,r&&(["H1","H2","H3","H4"].includes(r.nodeName)?r:this.shadowRoot?.querySelector("a"))?.scrollIntoView({behavior:"smooth",inline:"nearest"})}handleSlotchange({target:r}){this.empty=!this.show||!r.assignedNodes({flatten:!0}).length}render(){return m`
      <a id="${go(this.slideId)}" data-empty="${this.empty}">
        <slot @slotchange=${this.handleSlotchange}></slot>
      </a>
    `}};L=b(yo),u(L,5,"slideId",xo,X),u(L,5,"show",bo,X),u(L,5,"empty",fo,X),X=u(L,0,"SlideAnchor",wo,X),l(X,"styles",f`
    a[data-empty="false"] {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      line-height: var(--line-height-normal);
      color: inherit;
      border: 1px solid currentColor;
      font-weight: var(--font-weight-semibold);
      border-radius: var(--radius-full);
      padding: var(--size-0-5) var(--size-1-5);
    }

    a[data-empty="true"] {
      display: none;
    }
  `),s(L,1,X);var $o=f`
  :host {
    --spinner-color: #222225;
    --spinner-size: var(--size-3);
    --part-height: 8px;
    --part-width: 4px;
    --part-offset: 10px;

    display: inline-block;
  }

  .spinner {
    position: relative;
    width: var(--spinner-size);
    height: var(--spinner-size);
  }

  [data-invert] {
    --spinner-color: var(--color-white);
  }

  [data-size="xs"] {
    --spinner-size: var(--size-2);
    --part-height: 5px;
    --part-width: 2.5px;
    --part-offset: 6.5px;
  }

  [data-size="sm"] {
    --spinner-size: var(--size-2-5);
    --part-height: 6.5px;
    --part-width: 3.5px;
    --part-offset: 8.5px;
  }

  [data-size="lg"] {
    --spinner-size: var(--size-5);
    --part-height: 13.25px;
    --part-width: 5.25px;
    --part-offset: 17.5px;
  }

  .spinner > div {
    position: absolute;
    top: var(--part-height);
    left: var(--part-offset);
    width: var(--part-width);
    height: var(--part-height);
    background-color: var(--spinner-color);
    border-radius: var(--part-width);
    animation: spinner-part 1s linear infinite;
    will-change: opacity;
  }

  .spinner > div:nth-child(1) {
    transform: rotate(45deg) translateY(calc(-1 * var(--part-height)));
    animation-delay: -1.625s;
  }

  .spinner > div:nth-child(2) {
    transform: rotate(90deg) translateY(calc(-1 * var(--part-height)));
    animation-delay: -1.5s;
  }

  .spinner > div:nth-child(3) {
    transform: rotate(135deg) translateY(calc(-1 * var(--part-height)));
    animation-delay: -1.375s;
  }

  .spinner > div:nth-child(4) {
    transform: rotate(180deg) translateY(calc(-1 * var(--part-height)));
    animation-delay: -1.25s;
  }

  .spinner > div:nth-child(5) {
    transform: rotate(225deg) translateY(calc(-1 * var(--part-height)));
    animation-delay: -1.125s;
  }

  .spinner > div:nth-child(6) {
    transform: rotate(270deg) translateY(calc(-1 * var(--part-height)));
    animation-delay: -1s;
  }

  .spinner > div:nth-child(7) {
    transform: rotate(315deg) translateY(calc(-1 * var(--part-height)));
    animation-delay: -0.875s;
  }

  .spinner > div:nth-child(8) {
    transform: rotate(360deg) translateY(calc(-1 * var(--part-height)));
    animation-delay: -0.75s;
  }

  @keyframes spinner-part {
    0% {
      opacity: 0.85;
    }
    50% {
      opacity: 0.25;
    }
    100% {
      opacity: 0.25;
    }
  }
`;var Eo,ko,_o,Ao,Z;Ao=[x("bp-spinner")];var te=class extends(_o=g,ko=[h()],Eo=[h({type:Boolean})],_o){constructor(){super(...arguments);l(this,"size",s(Z,8,this,"md")),s(Z,11,this);l(this,"invert",s(Z,12,this,!1)),s(Z,15,this)}render(){return m`
      <div
        class="spinner"
        data-size="${this.size}"
        ?data-invert=${!!this.invert}
        role="status"
      >
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
      </div>
    `}};Z=b(_o),u(Z,5,"size",ko,te),u(Z,5,"invert",Eo,te),te=u(Z,0,"Spinner",Ao,te),l(te,"styles",$o),s(Z,1,te);var gr={ServerError:"SERVER_ERROR",ClientError:"CLIENT_ERROR",JsonParseError:"JSON_PARSE_ERROR",MissingUrl:"MISSING_URL"},Ve=class extends re{constructor(e,r,a){super(e,r,a),this.name="BpApiClientError"}};function So(t){return t.reduce((e,r)=>`${e}${r}`,"")}async function Ai(t){try{return await t.json()}catch{throw new Ve(`Invalid JSON response from "${t.url}"`,gr.JsonParseError)}}async function Si(t={}){let e=W("API_URL");if(!e)throw new Ve("API URL missing",gr.MissingUrl);let r=new Headers(t.headers);r.set("Content-Type","application/json"),r.set("X-BibleProject-Language",W("LANGUAGE")??"en");let a=await Wr(e,{...t,mode:"cors",headers:r}),o=await Ai(a);if(!a.ok){let i=a.status>=500?gr.ServerError:gr.ClientError;throw new Ve(`Application error code ${a.status} for "${a.url}"`,i,o)}return o}async function To(t,e){return Si({method:"POST",body:JSON.stringify(t),...e})}async function zo(t){let{data:e}=await To({query:So`
      query GetTeacherNotes($sessionId: ID!) {
        teacherNotes(sessionId: $sessionId) {
          contentHtml
          id
        }
      }
    `,variables:{sessionId:t}});return{data:e.teacherNotes}}var Co=f`
  :host {
    display: block;
    line-height: var(--line-height-normal);
  }

  strong {
    font-weight: var(--font-weight-semibold);
  }

  h1,
  h2,
  h3,
  h4 {
    margin: var(--size-2) 0 var(--size-2) 0;
    line-height: var(--line-height-snug);
  }

  h1 {
    font-size: var(--font-size-2xl);
    font-weight: var(--font-weight-normal);
    margin-top: 0px;
  }

  h2 {
    font-size: var(--font-size-lg);
  }

  h3 {
    font-size: var(--font-size-md);
  }

  h4 {
    font-size: var(--font-size-xs);
    text-transform: uppercase;
  }

  p {
    margin: var(--size-2) 0;
  }

  a {
    color: var(--color-black);
  }

  ul {
    padding: 0 0 0 var(--size-3);
    margin: var(--size-2) 0;
  }

  ol {
    padding: 0 0 0 var(--size-3);
    margin: var(--size-2) 0;
  }

  ol ::marker {
    font-weight: var(--font-weight-semibold);
  }

  li {
    margin: 0;
  }

  ul li span {
    margin-left: 1px;
  }

  ol li span {
    margin-left: 0px;
  }

  ul ul,
  ol ol,
  ol li ul,
  ul li ol {
    margin: 0;
  }

  blockquote {
    box-shadow: inset var(--size-1) 0 0 -5px currentColor;
    padding: 0 0 0 var(--size-2);
    margin: 0 0 0 var(--size-1);
  }

  bp-cite {
    --bp-cite-color: var(--color-black);
  }

  bp-spinner {
    margin-top: var(--size-1);
    margin-bottom: var(--size-1);
    margin-left: 50%;
    transform: translate(-50%);
  }
`;var Ro,Po,No,Mo,ee;Mo=[x("bp-teacher-notes")];var ae=class extends(No=g,Po=[h({attribute:"arc-id"})],Ro=[be()],No){constructor(){super(...arguments);l(this,"arcId",s(ee,8,this)),s(ee,11,this);l(this,"data",s(ee,12,this)),s(ee,15,this)}scrollToSlideAnchor(r){this.shadowRoot?.querySelector(`[slide-id="${r}"]`)?.scrollIntoView()}updated(r){!r.has("arcId")||!this.arcId||zo(this.arcId).then(async({data:a})=>{this.data=a,this.updateDOMNodes()}).catch(()=>{})}handleLinkClick(r){globalThis.window.BibleProjectApp&&r.preventDefault(),document.dispatchEvent(new CustomEvent("bp:external_link",{detail:{href:r.currentTarget.href}}))}async updateDOMNodes(){await this.updateComplete,this.shadowRoot?.querySelectorAll("a").forEach(r=>{r.setAttribute("target","_blank"),r.removeEventListener("click",this.handleLinkClick),r.addEventListener("click",this.handleLinkClick)})}render(){return this.data?K(this.data.contentHtml):m`<bp-spinner size="lg"></bp-spinner>`}};ee=b(No),u(ee,5,"arcId",Po,ae),u(ee,5,"data",Ro,ae),ae=u(ee,0,"TeacherNotes",Mo,ae),l(ae,"styles",Co),s(ee,1,ae);var Lo,Jr,Ti;Lo=[x("bp-text-greek")];var Se=class extends(Ti=g){render(){return m` <slot></slot> `}};Jr=b(Ti),Se=u(Jr,0,"TextGreek",Lo,Se),l(Se,"styles",f`
    :host {
      font-family: var(--font-greek);
      display: inline-block;
      font-weight: normal;
    }
  `),s(Jr,1,Se);var Io,Qr,zi;Io=[x("bp-text-hebrew")];var Te=class extends(zi=g){render(){return m` <slot></slot> `}};Qr=b(zi),Te=u(Qr,0,"TextHebrew",Io,Te),l(Te,"styles",f`
    :host {
      font-family: var(--font-hebrew);
      display: inline-block;
      font-weight: normal;
      direction: rtl;
    }
  `),s(Qr,1,Te);
/*! Bundled license information:

classnames/index.js:
  (*!
  	Copyright (c) 2018 Jed Watson.
  	Licensed under the MIT License (MIT), see
  	http://jedwatson.github.io/classnames
  *)

@lit/reactive-element/css-tag.js:
  (**
   * @license
   * Copyright 2019 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/reactive-element.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/lit-html.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/css-tag.js:
  (**
   * @license
   * Copyright 2019 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/reactive-element.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-element/lit-element.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/is-server.js:
  (**
   * @license
   * Copyright 2022 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/custom-element.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/property.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/state.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/base.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/event-options.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/query.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/query-all.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/query-async.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/query-assigned-elements.js:
  (**
   * @license
   * Copyright 2021 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/query-assigned-nodes.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/directive.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/directives/unsafe-html.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/directive-helpers.js:
  (**
   * @license
   * Copyright 2020 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/async-directive.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/directives/ref.js:
  (**
   * @license
   * Copyright 2020 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/directives/if-defined.js:
  (**
   * @license
   * Copyright 2018 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)
*/
