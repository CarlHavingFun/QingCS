# ComfyUI auth client inspection

- JavaScript URL: `https://my-agent.com.cn/auth/static/js/index.CXslS62G.js`
- JavaScript bytes: `579026`

## Auth-related string literals
```text
./portal.AuthenticatedView.BkKpWsEw.js
./components.LogoutButton.B7v3EhX5.js
./portal.Authenticated.D-xUXtuP.js
./layouts.Login.DIbxNq8s.js
./services.WebAuthn.CMS9jsil.js
./services.Password.CtBaoSU7.js
./reset-password.ResetPasswordStep1.B3B3pEPv.js
./reset-password.ResetPassword.Dmvf3ueE.js
./reset-password.ResetPasswordStep2.D1WksXmr.js
./services.PasswordPolicyConfiguration.D-o1iFSu.js
./portal.PasswordForm.Bka5b58Z.js
./views.RevokeResetPasswordTokenView.D2hkchMF.js
```

## Auth-related path candidates
```text
/api/change-password
/api/configuration/password-policy
/api/firstfactor/reauthenticate
/api/logout
/api/oidc/device-authorization
/api/reset-password
/api/reset-password/identity/finish
/api/reset-password/identity/start
/api/secondfactor/password
/api/secondfactor/webauthn
/api/secondfactor/webauthn/credential
/api/secondfactor/webauthn/credential/register
/api/secondfactor/webauthn/credentials
/authenticated
/components.LogoutButton.B7v3EhX5.js
/device-authorization
/layouts.Login.DIbxNq8s.js
/logout
/one-time-password
/password
/portal.Authenticated.D-xUXtuP.js
/portal.AuthenticatedView.BkKpWsEw.js
/portal.PasswordForm.Bka5b58Z.js
/reset-password.ResetPassword.Dmvf3ueE.js
/reset-password.ResetPasswordStep1.B3B3pEPv.js
/reset-password.ResetPasswordStep2.D1WksXmr.js
/reset-password/step1
/reset-password/step2
/revoke/reset-password
/services.Password.CtBaoSU7.js
/services.PasswordPolicyConfiguration.D-o1iFSu.js
/services.WebAuthn.CMS9jsil.js
/two-factor-authentication
/views.RevokeResetPasswordTokenView.D2hkchMF.js
/webauthn
```

## Sanitized code snippets
```text
const __vite__mapDeps=(i,m=__vite__mapDeps,d=(m.f||(m.f=["./portal.AuthenticatedView.BkKpWsEw.js","./components.LogoutButton.B7v3EhX5.js","./components.TypographyWithTooltip.BWaznSOU.js","./constants.constants.C_X5TlRH.js","./layouts.Minimal.CDmQc
hTooltip.BWaznSOU.js","./constants.constants.C_X5TlRH.js","./layouts.Minimal.CDmQcwHr.js","./portal.Authenticated.D-xUXtuP.js","./components.SuccessIcon.CFUWO4h8.js","./portal.FirstFactorForm.5Gd6DmSP.js","./mui.VisibilityOff.Dutj1hF9.js","./mui.TextField.BfBIdloI.js","./broadcas
s.Login.DIbxNq8s.js","./hooks.Abort.Cs78VfZ6.js","./hooks.OpenIDConnect.9zf8EOg6.js","./services.WebAuthn.CMS9jsil.js","./esm.CAMkWa7m.js","./services.Password.CtBaoSU7.js","./portal.SecondFactorForm.BMjcW2ga.js","./components.FingerTouchIcon.ldUA8LKI.js","../css/FingerTouchIcon.
pathname,r)||n.nextLocation.pathname;return h_(i.pathname,o)!=null||h_(i.pathname,a)!=null}var Wy=`/authenticated`,Gy=`/2fa`,Ky=`/password`,qy=`/webauthn`,Jy=`/one-time-password`,Yy=`/push-notification`,Xy=`/reset-password/step1`,Zy=`/reset-password/step2`,Qy=`/logout`,$y=`/setti
.pathname,o)!=null||h_(i.pathname,a)!=null}var Wy=`/authenticated`,Gy=`/2fa`,Ky=`/password`,qy=`/webauthn`,Jy=`/one-time-password`,Yy=`/push-notification`,Xy=`/reset-password/step1`,Zy=`/reset-password/step2`,Qy=`/logout`,$y=`/settings`,eb=`/two-factor-authentication`,tb=`/revoke
`,Xy=`/reset-password/step1`,Zy=`/reset-password/step2`,Qy=`/logout`,$y=`/settings`,eb=`/two-factor-authentication`,tb=`/revoke/one-time-code`,nb=`/revoke/reset-password`,rb=`/security`,ib=`/consent`,ab=`/completion`,ob=`/openid`,sb=`/decision`,cb=`/device-authorization`,lb=`seco
set-password`,rb=`/security`,ib=`/consent`,ab=`/completion`,ob=`/openid`,sb=`/decision`,cb=`/device-authorization`,lb=`second-factor.method`,ub=`privacy-policy.accepted`,db=`lang.preference`,fb=`lang.current`,pb=`theme.name`,mb=null,hb=`authelia.test`,gb=`foo`;function _b(){if(mb
od`,ub=`privacy-policy.accepted`,db=`lang.preference`,fb=`lang.current`,pb=`theme.name`,mb=null,hb=`authelia.test`,gb=`foo`;function _b(){if(mb!==null)return mb;if(mb=!1,typeof globalThis<`u`&&globalThis.localStorage!==null){mb=!0;try{globalThis.localStorage.setItem(hb,gb),global
ield.BfBIdloI.js","./broadcast-channel.BDKUom3L.js","./mui.FormControlLabel.DqJ5eCdG.js","./layouts.Login.DIbxNq8s.js","./hooks.Abort.Cs78VfZ6.js","./hooks.OpenIDConnect.9zf8EOg6.js","./services.WebAuthn.CMS9jsil.js","./esm.CAMkWa7m.js","./services.Password.CtBaoSU7.js","./portal
mberme`)===`true`}function Ob(){return wb(`resetpassword`)===`true`}function kb(){return wb(`passkeylogin`)===`true`}function Ab(){return wb(`resetpasswordcustomurl`)}function jb(){return wb(`privacypolicyurl`)!==``}function Mb(){return wb(`privacypolicyurl`)}function Nb(){return
uthentication_level===cE.Unauthenticated&&t.pathname===`/`,children:(0,B.jsx)(hE,{disabled:i,passkeyLogin:e.passkeyLogin,rememberMe:e.rememberMe,resetPassword:e.resetPassword,resetPasswordCustomURL:e.resetPasswordCustomURL,onAuthenticationStart:()=>a(!0),onAuthenticationStop:()=>
evel===cE.Unauthenticated&&t.pathname===`/`,children:(0,B.jsx)(hE,{disabled:i,passkeyLogin:e.passkeyLogin,rememberMe:e.rememberMe,resetPassword:e.resetPassword,resetPasswordCustomURL:e.resetPasswordCustomURL,onAuthenticationStart:()=>a(!0),onAuthenticationStop:()=>a(!1),onAuthent
ment:(0,B.jsx)(bE,{})}),(0,B.jsx)(jv,{path:`/*`,element:(0,B.jsx)(vE,{duoSelfEnrollment:Tb(),passkeyLogin:kb(),rememberMe:Db(),resetPassword:Ob(),resetPasswordCustomURL:Ab()})})]})})})})]})})})}var{slice:OE,forEach:kE}=[];function AE(e){return kE.call(OE.call(arguments,1),t=>{if(
/hooks.OpenIDConnect.9zf8EOg6.js","./services.WebAuthn.CMS9jsil.js","./esm.CAMkWa7m.js","./services.Password.CtBaoSU7.js","./portal.SecondFactorForm.BMjcW2ga.js","./components.FingerTouchIcon.ldUA8LKI.js","../css/FingerTouchIcon.fwu5v7xH.css","./components.PushNotificationIcon.CZ
n.CktcjJFP.css","./components.SwitchUserButton.tLT1oYm3.js","./portal.SignOut.DY6S-5kA.js","./reset-password.ResetPasswordStep1.B3B3pEPv.js","./reset-password.ResetPassword.Dmvf3ueE.js","./reset-password.ResetPasswordStep2.D1WksXmr.js","./services.PasswordPolicyConfiguration.D-o1
","./components.SwitchUserButton.tLT1oYm3.js","./portal.SignOut.DY6S-5kA.js","./reset-password.ResetPasswordStep1.B3B3pEPv.js","./reset-password.ResetPassword.Dmvf3ueE.js","./reset-password.ResetPasswordStep2.D1WksXmr.js","./services.PasswordPolicyConfiguration.D-o1iFSu.js","./se
1oYm3.js","./portal.SignOut.DY6S-5kA.js","./reset-password.ResetPasswordStep1.B3B3pEPv.js","./reset-password.ResetPassword.Dmvf3ueE.js","./reset-password.ResetPasswordStep2.D1WksXmr.js","./services.PasswordPolicyConfiguration.D-o1iFSu.js","./settings.router.OrkHyl5v.js","./compon
ortal.SignOut.DY6S-5kA.js","./reset-password.ResetPasswordStep1.B3B3pEPv.js","./reset-password.ResetPassword.Dmvf3ueE.js","./reset-password.ResetPasswordStep2.D1WksXmr.js","./services.PasswordPolicyConfiguration.D-o1iFSu.js","./settings.router.OrkHyl5v.js","./components.Informati
eset-password.ResetPasswordStep1.B3B3pEPv.js","./reset-password.ResetPassword.Dmvf3ueE.js","./reset-password.ResetPasswordStep2.D1WksXmr.js","./services.PasswordPolicyConfiguration.D-o1iFSu.js","./settings.router.OrkHyl5v.js","./components.InformationIcon.CuxJHPCu.js","./hooks.Ti
ResetPasswordStep1.B3B3pEPv.js","./reset-password.ResetPassword.Dmvf3ueE.js","./reset-password.ResetPasswordStep2.D1WksXmr.js","./services.PasswordPolicyConfiguration.D-o1iFSu.js","./settings.router.OrkHyl5v.js","./components.InformationIcon.CuxJHPCu.js","./hooks.Timer.Clw-qxIs.j
t-password.ResetPassword.Dmvf3ueE.js","./reset-password.ResetPasswordStep2.D1WksXmr.js","./services.PasswordPolicyConfiguration.D-o1iFSu.js","./settings.router.OrkHyl5v.js","./components.InformationIcon.CuxJHPCu.js","./hooks.Timer.Clw-qxIs.js","./mui.ListItem.L-CYdChg.js","./mui.
./views.RevokeOneTimeCodeView.CTyG1zyD.js","./hooks.Revoke.BXY5ardT.js","./views.<redacted>.D2hkchMF.js"])))=>i.map(i=>d[i]); var e=Object.create,t=Object.defineProperty,n=Object.getOwnPropertyDescriptor,r=Object.getOwnPropertyNames,i=Object.getPrototypeOf,a=Obj
 as a string (in rgb format, for example "12 12 12") or undefined if you want to remove the channel token.`))}function qd(e){return typeof e==`number`?`${e}px`:typeof e==`string`||typeof e==`function`||Array.isArray(e)?e:`8px`}var Jd=e=>{try{return e()}catch{}},Yd=(e=`mui`)=>Eu(e
!Q.isObject(e))throw TypeError(`target must be an object`);t||=new FormData,n=Q.toFlatObject(n,{metaTokens:!0,dots:!1,indexes:!1},!1,function(e,t){return!Q.isUndefined(t[e])});let r=n.metaTokens,i=n.visitor||d,a=n.dots,o=n.indexes,s=n.Blob||typeof Blob<`u`&&Blob,c=n.maxDepth===vo
ject(n,{metaTokens:!0,dots:!1,indexes:!1},!1,function(e,t){return!Q.isUndefined(t[e])});let r=n.metaTokens,i=n.visitor||d,a=n.dots,o=n.indexes,s=n.Blob||typeof Blob<`u`&&Blob,c=n.maxDepth===void 0?100:n.maxDepth,l=s&&Q.isSpecCompliantForm(t);if(!Q.isFunction(i))throw TypeError(`v
om(e,$.ERR_BAD_RESPONSE,this,null,wC(this,`response`)):e}}return e}],timeout:0,xsrfCookieName:`XSRF-TOKEN`,xsrfHeaderName:`X-XSRF-TOKEN`,maxContentLength:-1,maxBodyLength:-1,env:{FormData:yC.classes.FormData,Blob:yC.classes.Blob},validateStatus:function(e){return e>=200&&e<300},h
ull,wC(this,`response`)):e}}return e}],timeout:0,xsrfCookieName:`XSRF-TOKEN`,xsrfHeaderName:`X-XSRF-TOKEN`,maxContentLength:-1,maxBodyLength:-1,env:{FormData:yC.classes.FormData,Blob:yC.classes.Blob},validateStatus:function(e){return e>=200&&e<300},headers:{common:{Accept:`applic
quest:o,transformResponse:o,paramsSerializer:o,timeout:o,timeoutMessage:o,withCredentials:o,withXSRFToken:o,adapter:o,responseType:o,xsrfCookieName:o,xsrfHeaderName:o,onUploadProgress:o,onDownloadProgress:o,decompress:o,maxContentLength:o,maxBodyLength:o,beforeRedirect:o,transpor
ss:o,maxContentLength:o,maxBodyLength:o,beforeRedirect:o,transport:o,httpAgent:o,httpsAgent:o,cancelToken:o,socketPath:o,allowedSocketPaths:o,responseEncoding:o,validateStatus:s,headers:(e,t,n)=>i(HC(e),HC(t),n,!0)};return Q.forEach(Object.keys({...e,...t}),function(r){if(r===`__
:`),n=e.substring(0,i).trim().toLowerCase(),r=e.substring(i+1).trim(),!(!n||t[n]&&MS[n])&&(n===`set-cookie`?t[n]?t[n].push(r):t[n]=[r]:t[n]=t[n]?t[n]+`, `+r:r)}),t};function PS(e){let t=0,n=e.length;for(;t<n;){let n=e.charCodeAt(t);if(n!==9&&n!==32)break;t+=1}for(;n>t;){let t=e.c
.iterator]()}toString(){return Object.entries(this.toJSON()).map(([e,t])=>e+`: `+t).join(` `)}getSetCookie(){return this.get(`set-cookie`)||[]}get[Symbol.toStringTag](){return`AxiosHeaders`}static from(e){return e instanceof this?e:new this(e)}static concat(e,...t){let n=new this
 Object.entries(this.toJSON()).map(([e,t])=>e+`: `+t).join(` `)}getSetCookie(){return this.get(`set-cookie`)||[]}get[Symbol.toStringTag](){return`AxiosHeaders`}static from(e){return e instanceof this?e:new this(e)}static concat(e,...t){let n=new this(e);return t.forEach(e=>n.set(
SyntaxError`?$.from(e,$.ERR_BAD_RESPONSE,this,null,wC(this,`response`)):e}}return e}],timeout:0,xsrfCookieName:`XSRF-TOKEN`,xsrfHeaderName:`X-XSRF-TOKEN`,maxContentLength:-1,maxBodyLength:-1,env:{FormData:yC.classes.FormData,Blob:yC.classes.Blob},validateStatus:function(e){return
(i)&&s.push(`domain=${i}`),a===!0&&s.push(`secure`),Q.isString(o)&&s.push(`SameSite=${o}`),document.cookie=s.join(`; `)},read(e){if(typeof document>`u`)return null;let t=document.cookie.split(`;`);for(let n=0;n<t.length;n++){let r=t[n].replace(/^\s+/,``),i=r.indexOf(`=`);if(i!==-
Site=${o}`),document.cookie=s.join(`; `)},read(e){if(typeof document>`u`)return null;let t=document.cookie.split(`;`);for(let n=0;n<t.length;n++){let r=t[n].replace(/^\s+/,``),i=r.indexOf(`=`);if(i!==-1&&r.slice(0,i)===e)return decodeURIComponent(r.slice(i+1))}return null},remove
ializer:o,timeout:o,timeoutMessage:o,withCredentials:o,withXSRFToken:o,adapter:o,responseType:o,xsrfCookieName:o,xsrfHeaderName:o,onUploadProgress:o,onDownloadProgress:o,decompress:o,maxContentLength:o,maxBodyLength:o,beforeRedirect:o,transport:o,httpAgent:o,httpsAgent:o,cancelTo
,n=e=>Q.hasOwnProp(t,e)?t[e]:void 0,r=n(`data`),i=n(`withXSRFToken`),a=n(`xsrfHeaderName`),o=n(`xsrfCookieName`),s=n(`headers`),c=n(`auth`),l=n(`baseURL`),u=n(`allowAbsoluteUrls`),d=n(`url`);if(t.headers=s=YS.from(s),t.url=lC(VC(l,d,u),e.params,e.paramsSerializer),c&&s.set(`Autho
me`)}function Fb(){return wb(`basepath`)}var Z=Fb(),Ib=Z+`/api/oidc/consent`,Lb=Z+`/api/oidc/device-authorization`,Rb=Z+`/api/firstfactor`,zb=Z+`/api/firstfactor/passkey`,Bb=Z+`/api/firstfactor/reauthenticate`,Vb=Z+`/api/secondfactor/totp/register`,Hb=Z+`/api/secondfactor/totp`,U
typeof process<`u`&&process.nextTick||jS,isIterable:e=>e!=null&&Fx(e[wx])},MS=Q.toObjectSet([`age`,`authorization`,`content-length`,`content-type`,`etag`,`expires`,`from`,`host`,`if-modified-since`,`if-unmodified-since`,`last-modified`,`location`,`max-forwards`,`proxy-authorizati
`,`host`,`if-modified-since`,`if-unmodified-since`,`last-modified`,`location`,`max-forwards`,`proxy-authorization`,`referer`,`retry-after`,`user-agent`]),NS=e=>{let t={},n,r,i;return e&&e.split(` `).forEach(function(e){i=e.indexOf(`:`),n=e.substring(0,i).trim().toLowerCase(),r=e.
):r(e),this}};YS.accessor([`Content-Type`,`Content-Length`,`Accept`,`Accept-Encoding`,`User-Agent`,`Authorization`]),Q.reduceDescriptors(YS.prototype,({value:e},t)=>{let n=t[0].toUpperCase()+t.slice(1);return{get:()=>e,set(e){this[n]=e}}}),Q.freezeMethods(YS);var XS=`[REDACTED **
ls`),d=n(`url`);if(t.headers=s=YS.from(s),t.url=lC(VC(l,d,u),e.params,e.paramsSerializer),c&&s.set(`Authorization`,`Basic `+btoa((c.username||``)+`:`+(c.password?KC(c.password):``))),Q.isFormData(r)&&(yC.hasStandardBrowserEnv||yC.<redacted>?s.setContentType(vo
=`error_description`,XT=`error_hint`,ZT=`error_debug`,QT=`error_uri`,$T=`openid_connect`,eE=`device_authorization`;function tE(e){let[t,n]=(0,f.useState)(void 0),[r,i]=(0,f.useState)(!1),[a,o]=(0,f.useState)(void 0),s=(0,f.useCallback)(()=>e(),[e]);return[t,(0,f.useCallback)(()=>
u`?c:``,dangerouslySetInnerHTML:{__html:`(function() { try { let colorScheme = ''; const mode = localStorage.getItem('${i}') || '${t}'; const dark = localStorage.getItem('${a}-dark') || '${r}'; const light = localStorage.getItem('${a}-light') || '${n}'; if (mode === 'sy
try { let colorScheme = ''; const mode = localStorage.getItem('${i}') || '${t}'; const dark = localStorage.getItem('${a}-dark') || '${r}'; const light = localStorage.getItem('${a}-light') || '${n}'; if (mode === 'system') { // handle system mode const mql = wind
Item('${i}') || '${t}'; const dark = localStorage.getItem('${a}-dark') || '${r}'; const light = localStorage.getItem('${a}-light') || '${n}'; if (mode === 'system') { // handle system mode const mql = window.matchMedia('(prefers-color-scheme: dark)'); if (mql.ma
(!t&&typeof window<`u`&&(t=window),{get(n){if(typeof window>`u`)return;if(!t)return n;let r;try{r=t.localStorage.getItem(e)}catch{}return r||n},set:n=>{if(t)try{t.localStorage.setItem(e,n)}catch{}},subscribe:n=>{if(!t)return _u;let r=t=>{let r=t.newValue;t.key===e&&n(r)};return t
)return;if(!t)return n;let r;try{r=t.localStorage.getItem(e)}catch{}return r||n},set:n=>{if(t)try{t.localStorage.setItem(e,n)}catch{}},subscribe:n=>{if(!t)return _u;let r=t=>{let r=t.newValue;t.key===e&&n(r)};return t.addEventListener(`storage`,r),()=>{t.removeEventListener(`stor
elia.test`,gb=`foo`;function _b(){if(mb!==null)return mb;if(mb=!1,typeof globalThis<`u`&&globalThis.localStorage!==null){mb=!0;try{globalThis.localStorage.setItem(hb,gb),globalThis.localStorage.removeItem(hb)}catch{mb=!1}}return mb}function vb(e){return _b()?globalThis.localStora
null)return mb;if(mb=!1,typeof globalThis<`u`&&globalThis.localStorage!==null){mb=!0;try{globalThis.localStorage.setItem(hb,gb),globalThis.localStorage.removeItem(hb)}catch{mb=!1}}return mb}function vb(e){return _b()?globalThis.localStorage.getItem(e):null}function yb(e,t){return
is<`u`&&globalThis.localStorage!==null){mb=!0;try{globalThis.localStorage.setItem(hb,gb),globalThis.localStorage.removeItem(hb)}catch{mb=!1}}return mb}function vb(e){return _b()?globalThis.localStorage.getItem(e):null}function yb(e,t){return _b()?(globalThis.localStorage.setItem(
 e=Math.random().toString(32).slice(2);window.history.replaceState({key:e},``)}try{let n=JSON.parse(sessionStorage.getItem(e)||`{}`)[t||window.history.state.key];typeof n==`number`&&window.scrollTo(0,n)}catch(t){console.error(t),sessionStorage.removeItem(e)}}).toString();return f
}`)[t||window.history.state.key];typeof n==`number`&&window.scrollTo(0,n)}catch(t){console.error(t),sessionStorage.removeItem(e)}}).toString();return f.createElement(`script`,{...n,suppressHydrationWarning:!0,dangerouslySetInnerHTML:{__html:`(${c})(${Qv(JSON.stringify(t||Ry))}, $
=`auto`}),[]),Hy(f.useCallback(()=>{if(c.state===`idle`){let t=By(o,s,a,e);zy[t]=window.scrollY}try{sessionStorage.setItem(t||Ry,JSON.stringify(zy))}catch(e){Wg(!1,`Failed to save scroll positions in sessionStorage, <ScrollRestoration /> will not work properly (${e}).`)}window.hi
sessionStorage.setItem(t||Ry,JSON.stringify(zy))}catch(e){Wg(!1,`Failed to save scroll positions in sessionStorage, <ScrollRestoration /> will not work properly (${e}).`)}window.history.scrollRestoration=`auto`},[c.state,e,a,o,s,t])),typeof document<`u`&&(f.useLayoutEffect(()=>{t
ollRestoration=`auto`},[c.state,e,a,o,s,t])),typeof document<`u`&&(f.useLayoutEffect(()=>{try{let e=sessionStorage.getItem(t||Ry);e&&(zy=JSON.parse(e))}catch{}},[t]),f.useLayoutEffect(()=>{let t=n?.enableScrollRestoration(zy,()=>window.scrollY,e?(t,n)=>By(t,n,a,e):void 0);return(
alStorage.setItem(n,e)}},VE=null,HE=()=>{if(VE!==null)return VE;try{if(VE=typeof window<`u`&&window.sessionStorage!==null,!VE)return!1;let e=`i18next.translate.boo`;window.sessionStorage.setItem(e,`foo`),window.sessionStorage.removeItem(e)}catch{VE=!1}return VE},UE={name:`session
E=typeof window<`u`&&window.sessionStorage!==null,!VE)return!1;let e=`i18next.translate.boo`;window.sessionStorage.setItem(e,`foo`),window.sessionStorage.removeItem(e)}catch{VE=!1}return VE},UE={name:`sessionStorage`,lookup(e){let{lookupSessionStorage:t}=e;if(t&&HE())return windo
age!==null,!VE)return!1;let e=`i18next.translate.boo`;window.sessionStorage.setItem(e,`foo`),window.sessionStorage.removeItem(e)}catch{VE=!1}return VE},UE={name:`sessionStorage`,lookup(e){let{lookupSessionStorage:t}=e;if(t&&HE())return window.sessionStorage.getItem(t)||void 0},ca
S.from(s),t.url=lC(VC(l,d,u),e.params,e.paramsSerializer),c&&s.set(`Authorization`,`Basic `+btoa((c.username||``)+`:`+(c.password?KC(c.password):``))),Q.isFormData(r)&&(yC.hasStandardBrowserEnv||yC.<redacted>?s.setContentType(void 0):Q.isFunction(r.getHeaders)
/g,` `):e}function aD(e){if(typeof e!=`string`||e.length===0)return e;try{let t=new URL(e);return t.username||t.password?(t.username=``,t.password=``,t.toString()):e}catch{return e.replace(/(\/\/)[^/@\s]+@/g,`$1`)}}function oD(){return typeof XMLHttpRequest==`function`||typeof XM
{if(typeof e!=`string`||e.length===0)return e;try{let t=new URL(e);return t.username||t.password?(t.username=``,t.password=``,t.toString()):e}catch{return e.replace(/(\/\/)[^/@\s]+@/g,`$1`)}}function oD(){return typeof XMLHttpRequest==`function`||typeof XMLHttpRequest==`object`}f
nerHTML|<redacted>|suppressHydrationWarning|valueLink|abbr|accept|acceptCharset|accessKey|action|allow|allowUserMedia|allowPaymentRequest|allowFullScreen|allowTransparency|alt|async|autoComplete|autoPlay|capture|cellPadding|cellSpacing|challenge|charSet|checke
Name:i,color:a=`inherit`,component:o=`svg`,fontSize:s=`medium`,htmlColor:c,inheritViewBox:l=!1,titleAccess:u,viewBox:d=`0 0 24 24`,...p}=n,m=f.isValidElement(r)&&r.type===`svg`,h={...n,color:a,component:o,fontSize:s,instanceFontSize:e.fontSize,inheritViewBox:l,viewBox:d,hasSvgAsC
i.returnObjects&&!this.options.returnObjects){this.options.returnedObjectHandler||this.logger.warn(`accessing an object - but returnObjects options is not enabled!`);let e=this.options.returnedObjectHandler?this.options.returnedObjectHandler(h,E,{...i,ns:c}):`key '${s} (${this.la
 resolved as namespace "${o}" was not yet loaded`,`This means something IS WRONG in your setup. You access the t function before i18next.init / i18next.loadNamespace / i18next.changeLanguage was done. Wait for the callback or Promise to resolve before accessing it!!!`)),p.forEach
loadNamespace / i18next.changeLanguage was done. Wait for the callback or Promise to resolve before accessing it!!!`)),p.forEach(r=>{if(this.isValidLookup(n))return;a=r;let o=[c];if(this.i18nFormat?.addLookupKeys)this.i18nFormat.addLookupKeys(o,c,r,e,t);else{let e;u&&(e=this.plur
${n}" as the namespace "${t}" was not yet loaded`,`This means something IS WRONG in your setup. You access the t function before i18next.init / i18next.loadNamespace / i18next.changeLanguage was done. Wait for the callback or Promise to resolve before accessing it!!!`);return}if(
loadNamespace / i18next.changeLanguage was done. Wait for the callback or Promise to resolve before accessing it!!!`);return}if(!(n==null||n===``)){if(this.backend?.create){let s={...a,isUpdate:i},c=this.backend.create.bind(this.backend);if(c.length<6)try{let i;i=c.length===5?c(e
f this?e:new this(e)}static concat(e,...t){let n=new this(e);return t.forEach(e=>n.set(e)),n}static accessor(e){let t=(this[VS]=this[VS]={accessors:{}}).accessors,n=this.prototype;function r(e){let r=HS(e);t[r]||(JS(n,e),t[r]=!0)}return Q.isArray(e)?e.forEach(r):r(e),this}};YS.ac
__mapDeps=(i,m=__vite__mapDeps,d=(m.f||(m.f=["./portal.AuthenticatedView.BkKpWsEw.js","./components.LogoutButton.B7v3EhX5.js","./components.TypographyWithTooltip.BWaznSOU.js","./constants.constants.C_X5TlRH.js","./layouts.Minimal.CDmQcwHr.js","./portal.Authenticated.D-xUXtuP.js",
e-time-password`,Yy=`/push-notification`,Xy=`/reset-password/step1`,Zy=`/reset-password/step2`,Qy=`/logout`,$y=`/settings`,eb=`/two-factor-authentication`,tb=`/revoke/one-time-code`,nb=`/revoke/reset-password`,rb=`/security`,ib=`/consent`,ab=`/completion`,ob=`/openid`,sb=`/decisi
=Z+`/api/change-password`,tx=Z+`/api/reset-password`,nx=Z+`/api/checks/safe-redirection`,rx=Z+`/api/logout`,ix=Z+`/api/state`,ax=Z+`/api/user/info`,ox=Z+`/api/user/info/2fa_method`,sx=Z+`/api/user/session/elevation`,cx=Z+`/api/configuration`,lx=Z+`/api/configuration/password-poli
```
