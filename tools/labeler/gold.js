const $ = (id) => document.getElementById(id);
const EMOTIONS = [["joy","vui"],["sadness","buồn"],["anger","tức giận"],["fear_anxiety","sợ / lo âu"],["surprise","ngạc nhiên"],["disgust","ghê tởm"],["neutral","trung tính"]];
const options = {
  valence: [["1","1 · rất tiêu cực"],["2","2 · tiêu cực"],["3","3 · trung tính"],["4","4 · tích cực"],["5","5 · rất tích cực"]],
  arousal: [["1","1 · rất bình thản"],["2","2 · bình thản"],["3","3 · trung bình"],["4","4 · kích động"],["5","5 · rất kích động"]],
  gender: [["","—"],["female","nữ"],["male","nam"]],
  age_group: [["","—"],["child","trẻ em"],["teen","thiếu niên"],["young_adult","thanh niên"],["middle_aged","trung niên"],["senior","cao tuổi"]],
  dialect: [["","—"],["north","Bắc"],["central","Trung"],["south","Nam"]],
};
const AUTH_KEY = "goldReviewAuth";
let auth = sessionStorage.getItem(AUTH_KEY) || "", item = null, picked = "", committed = false, sending = false;
for (const [id, vals] of Object.entries(options)) $(id).innerHTML = vals.map(([v,l]) => `<option value="${v}">${l}</option>`).join("");
$("emotion").innerHTML = EMOTIONS.map(([v,l]) => `<button type="button" class="emo-${v}" data-v="${v}">${l}</button>`).join("");
const emoButtons = () => [...$("emotion").querySelectorAll("button")];
const headers = (json=false) => ({Authorization: auth, ...(json ? {"Content-Type":"application/json"} : {})});
async function api(url, init={}) { const r=await fetch(url,{...init,headers:{...headers(!!init.body),...(init.headers||{})}}); if(!r.ok){let d={};try{d=await r.json()}catch{} throw new Error(d.detail||`HTTP ${r.status}`)} return r.json(); }
function values(){return {emotion:picked,valence:+$("valence").value,arousal:+$("arousal").value,gender:$("gender").value,age_group:$("age_group").value,dialect:$("dialect").value}}
function pick(v){picked=v;for(const b of emoButtons())b.classList.toggle("sel",b.dataset.v===v);$("commit").disabled=!v}
// Stage 1: emotion only. The owner's V/A stays on the server until commit (change 014).
function stage1(){picked="";committed=false;for(const b of emoButtons()){b.disabled=false;b.classList.remove("sel")}
  for(const id of ["gender","age_group","dialect"]){$(id).value=item[id]??"";$(id).disabled=true}
  $("va").classList.add("hidden");$("commit").classList.remove("hidden");$("commit").disabled=true;
  $("save").classList.add("hidden");$("edit").classList.add("hidden");$("reject-box").classList.add("hidden");
  $("save-reject").classList.add("hidden");$("cancel-reject").classList.add("hidden");$("reject").classList.remove("hidden");$("reject-reason").value=""}
function stage2(va){committed=true;$("valence").value=va.valence??"";$("arousal").value=va.arousal??"";
  for(const b of emoButtons())b.disabled=true;$("va").classList.remove("hidden");
  $("commit").classList.add("hidden");$("save").classList.remove("hidden");$("edit").classList.remove("hidden")}
function editMeta(){for(const id of ["valence","arousal","gender","age_group","dialect"])$(id).disabled=false;$("edit").classList.add("hidden")}
function rejectMode(on){$("commit").classList.toggle("hidden",on||committed);$("save").classList.toggle("hidden",on||!committed);$("edit").classList.toggle("hidden",on||!committed||!$("valence").disabled);
  $("reject").classList.toggle("hidden",on);$("save-reject").classList.toggle("hidden",!on);$("cancel-reject").classList.toggle("hidden",!on);$("reject-box").classList.toggle("hidden",!on);if(on)$("reject-reason").focus()}
function heard(on){$("commit").disabled=on?!picked:true;$("reject").disabled=!on;for(const b of emoButtons())b.disabled=committed||!on;$("status").textContent=on?"":"Hãy nghe hết audio trước khi trả lời."}
function show(d){$("who").textContent=`User: ${d.user}`;$("progress").textContent=`${d.completed}/${d.total}`;item=d.item;$("card").classList.toggle("hidden",!item);$("done").classList.toggle("hidden",!!item);if(!item)return;$("subtitle").textContent=item.subtitle||"(không có subtitle)";stage1();heard(false);const a=$("audio");a.pause();a.removeAttribute("src");a.onended=()=>heard(true);fetch(item.wav,{headers:headers()}).then(r=>{if(!r.ok)throw new Error(`HTTP ${r.status}`);return r.blob()}).then(b=>{a.src=URL.createObjectURL(b)}).catch(e=>$("status").textContent=`Không tải được audio: ${e.message}`)}
async function next(){show(await api("/gold-review/next"))}
async function commit(){if(sending||!item||!picked)return;sending=true;$("status").textContent="";try{stage2(await api(`/gold-review/commit/${item.key}`,{method:"POST",body:JSON.stringify({emotion:picked})}))}catch(e){$("status").textContent=e.message}finally{sending=false}}
async function save(rejected=false){if(sending||!item)return;const reject_reason=$("reject-reason").value.trim();if(rejected&&!reject_reason){$("status").textContent="Vui lòng nhập lý do loại.";$("reject-reason").focus();return}sending=true;$("status").textContent="Đang lưu…";try{await api(`/gold-review/item/${item.key}`,{method:"POST",body:JSON.stringify({rejected,reject_reason,...values()})});await next()}catch(e){$("status").textContent=e.message}finally{sending=false}}
async function enter(){await api("/gold-review/login",{method:"POST"});sessionStorage.setItem(AUTH_KEY,auth);$("password").value="";$("login").classList.add("hidden");$("review").classList.remove("hidden");await next()}
$("login-form").addEventListener("submit",async e=>{e.preventDefault();auth=`Basic ${btoa(unescape(encodeURIComponent(`${$("username").value}:${$("password").value}`)))}`;try{await enter()}catch(e){auth="";sessionStorage.removeItem(AUTH_KEY);$("login-status").textContent=e.message}});
$("emotion").addEventListener("click",e=>{const b=e.target.closest("button");if(b&&!b.disabled)pick(b.dataset.v)});
function logout(){auth="";item=null;picked="";committed=false;sessionStorage.removeItem(AUTH_KEY);const a=$("audio");a.pause();a.removeAttribute("src");$("review").classList.add("hidden");$("login").classList.remove("hidden");$("login-status").textContent="";$("password").value="";$("password").focus()}
$("logout").onclick=logout;
$("commit").onclick=commit;$("save").onclick=()=>save();$("edit").onclick=editMeta;
$("reject").onclick=()=>rejectMode(true);$("save-reject").onclick=()=>save(true);$("cancel-reject").onclick=()=>{rejectMode(false);$("status").textContent=""};
if(auth)enter().catch(()=>{auth="";sessionStorage.removeItem(AUTH_KEY);$("login").classList.remove("hidden");$("review").classList.add("hidden");$("login-status").textContent="Phiên đăng nhập đã hết. Vui lòng đăng nhập lại."});
