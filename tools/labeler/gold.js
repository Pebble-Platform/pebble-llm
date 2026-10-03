const $ = (id) => document.getElementById(id);
const options = {
  emotion: [["joy","vui"],["sadness","buồn"],["anger","tức giận"],["fear_anxiety","sợ / lo âu"],["surprise","ngạc nhiên"],["disgust","ghê tởm"],["neutral","trung tính"]],
  valence: [["1","1 · rất tiêu cực"],["2","2 · tiêu cực"],["3","3 · trung tính"],["4","4 · tích cực"],["5","5 · rất tích cực"]],
  arousal: [["1","1 · rất bình thản"],["2","2 · bình thản"],["3","3 · trung bình"],["4","4 · kích động"],["5","5 · rất kích động"]],
  gender: [["","—"],["female","nữ"],["male","nam"]],
  age_group: [["","—"],["child","trẻ em"],["teen","thiếu niên"],["young_adult","thanh niên"],["middle_aged","trung niên"],["senior","cao tuổi"]],
  dialect: [["","—"],["north","Bắc"],["central","Trung"],["south","Nam"]],
};
const AUTH_KEY = "goldReviewAuth";
let auth = sessionStorage.getItem(AUTH_KEY) || "", item = null, sending = false;
for (const [id, vals] of Object.entries(options)) $(id).innerHTML = vals.map((x) => { const [v,l] = Array.isArray(x) ? x : [x,x]; return `<option value="${v}">${l}</option>`; }).join("");
const headers = (json=false) => ({Authorization: auth, ...(json ? {"Content-Type":"application/json"} : {})});
async function api(url, init={}) { const r=await fetch(url,{...init,headers:{...headers(!!init.body),...(init.headers||{})}}); if(!r.ok){let d={};try{d=await r.json()}catch{} throw new Error(d.detail||`HTTP ${r.status}`)} return r.json(); }
function values(){return {emotion:$("emotion").value,valence:+$("valence").value,arousal:+$("arousal").value,gender:$("gender").value,age_group:$("age_group").value,dialect:$("dialect").value}}
function emotionColor(){const el=$("emotion");el.className=`emo-${el.value}`}
function restore(){for(const id of Object.keys(options)) $(id).value=item[id]??"";emotionColor();$("reject-reason").value=""}
function editable(on){for(const id of Object.keys(options)) $(id).disabled=!on; $("agree").classList.toggle("hidden",on); $("disagree").classList.toggle("hidden",on); $("reject").classList.toggle("hidden",on); $("save-fix").classList.toggle("hidden",!on); $("save-reject").classList.add("hidden"); $("reject-box").classList.add("hidden"); $("cancel-fix").classList.toggle("hidden",!on)}
function rejectMode(){$("agree").classList.add("hidden");$("disagree").classList.add("hidden");$("reject").classList.add("hidden");$("save-reject").classList.remove("hidden");$("cancel-fix").classList.remove("hidden");$("reject-box").classList.remove("hidden");$("reject-reason").focus()}
function decisionEnabled(on){$("agree").disabled=!on;$("disagree").disabled=!on;$("reject").disabled=!on;$("status").textContent=on?"":"Hãy nghe hết audio trước khi trả lời."}
function show(d){$("who").textContent=`User: ${d.user}`;$("progress").textContent=`${d.completed}/${d.total}`;item=d.item;$("card").classList.toggle("hidden",!item);$("done").classList.toggle("hidden",!!item);if(!item)return;$("subtitle").textContent=item.subtitle||"(không có subtitle)";restore();editable(false);decisionEnabled(false);const a=$("audio");a.pause();a.removeAttribute("src");a.onended=()=>decisionEnabled(true);fetch(item.wav,{headers:headers()}).then(r=>{if(!r.ok)throw new Error(`HTTP ${r.status}`);return r.blob()}).then(b=>{a.src=URL.createObjectURL(b)}).catch(e=>$("status").textContent=`Không tải được audio: ${e.message}`)}
async function next(){show(await api("/gold-review/next"))}
async function save(agreed,rejected=false){if(sending||!item)return;const reject_reason=$("reject-reason").value.trim();if(rejected&&!reject_reason){$("status").textContent="Vui lòng nhập lý do loại.";$("reject-reason").focus();return}sending=true;$("status").textContent="Đang lưu…";try{await api(`/gold-review/item/${item.key}`,{method:"POST",body:JSON.stringify({agreed,rejected,reject_reason,...values()})});await next()}catch(e){$("status").textContent=e.message}finally{sending=false}}
async function enter(){await api("/gold-review/login",{method:"POST"});sessionStorage.setItem(AUTH_KEY,auth);$("password").value="";$("login").classList.add("hidden");$("review").classList.remove("hidden");await next()}
$("login-form").addEventListener("submit",async e=>{e.preventDefault();auth=`Basic ${btoa(unescape(encodeURIComponent(`${$("username").value}:${$("password").value}`)))}`;try{await enter()}catch(e){auth="";sessionStorage.removeItem(AUTH_KEY);$("login-status").textContent=e.message}});
$("emotion").onchange=emotionColor;
$("agree").onclick=()=>save(true);$("disagree").onclick=()=>editable(true);$("reject").onclick=rejectMode;$("save-fix").onclick=()=>save(false);$("save-reject").onclick=()=>save(false,true);
$("cancel-fix").onclick=()=>{restore();editable(false);decisionEnabled(true);$("status").textContent=""};
if(auth)enter().catch(()=>{auth="";sessionStorage.removeItem(AUTH_KEY);$("login").classList.remove("hidden");$("review").classList.add("hidden");$("login-status").textContent="Phiên đăng nhập đã hết. Vui lòng đăng nhập lại."});
