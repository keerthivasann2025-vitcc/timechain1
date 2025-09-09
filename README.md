<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>TimeChain</title>
<style>
  :root{--bg:#f6f8fb;--card:#ffffff;--accent:#2b6cb0;--muted:#666;}
  *{box-sizing:border-box;font-family:Inter,system-ui,Arial,sans-serif}
  body{margin:0;background:var(--bg);color:#111}
  header{background:var(--accent);color:#fff;padding:18px 20px}
  header h1{margin:0;font-size:1.4rem}
  .container{max-width:1100px;margin:20px auto;padding:12px}
  .grid{display:grid;grid-template-columns:1fr 380px;gap:20px}
  .card{background:var(--card);border-radius:10px;padding:14px;box-shadow:0 6px 18px rgba(20,20,60,0.06)}
  label{display:block;font-weight:600;margin-bottom:6px}
  input[type="text"],textarea,select{width:100%;padding:10px;border:1px solid #ddd;border-radius:8px;margin-bottom:10px}
  button{background:var(--accent);color:#fff;border:0;padding:10px 12px;border-radius:8px;cursor:pointer}
  button.ghost{background:transparent;color:var(--accent);border:1px solid var(--accent)}
  .small{font-size:0.9rem;padding:6px 8px;border-radius:6px}
  .report-list{display:flex;flex-direction:column;gap:10px}
  .report-item{border:1px dashed #e6eefb;padding:10px;border-radius:8px;background:#fbfdff}
  .meta{font-size:0.85rem;color:var(--muted);display:flex;gap:8px;flex-wrap:wrap}
  .file-preview{max-width:100%;border-radius:6px;margin-top:8px}
  .status-pill{padding:6px 8px;border-radius:999px;font-weight:600;font-size:0.8rem}
  .status-pending{background:#fff3cd;color:#7a5b00;border:1px solid #ffe8a8}
  .status-progress{background:#e6f7ff;color:#055160;border:1px solid #bfeaf9}
  .status-solved{background:#e6ffed;color:#0b5b2e;border:1px solid #bdf6c9}
  footer{max-width:1100px;margin:14px auto;padding:10px 12px;color:var(--muted);font-size:0.9rem}
  .row{display:flex;gap:8px;align-items:center}
  .leaderboard{list-style:none;padding:0;margin:0}
  .leaderboard li{padding:6px 0;border-bottom:1px solid #eee;display:flex;justify-content:space-between}
  @media(max-width:900px){.grid{grid-template-columns:1fr}}
</style>
</head>
<body>

<header>
  <h1>⏳ TimeChain</h1>
</header>

<div class="container">
  <div class="grid">
    <!-- Left: Reporting + My Issues -->
    <div>
      <div class="card">
        <h2 style="margin-top:0">Report an Issue</h2>

        <label>Your Name</label>
        <input id="reporterName" type="text" placeholder="Enter your name">

        <label>Description</label>
        <textarea id="desc" rows="3" placeholder="Describe the problem"></textarea>

        <label>Category</label>
        <select id="category">
          <option value="general">General</option>
          <option value="health">Health (serious)</option>
          <option value="education">Education</option>
          <option value="sanitation">Sanitation</option>
          <option value="infrastructure">Infrastructure</option>
        </select>

        <label>Attach photo/video (optional)</label>
        <input id="file" type="file" accept="image/*,video/*">

        <div style="display:flex;gap:8px;margin:8px 0">
          <button id="getLocationBtn" class="small ghost">📍 Use current location</button>
          <input id="locationText" type="text" placeholder="Or type location">
        </div>

        <button id="submitBtn">Submit Issue</button>
      </div>

      <div class="card" style="margin-top:16px">
        <h2>My Issues</h2>
        <div id="myReports" class="report-list"></div>
      </div>
    </div>

    <!-- Right: NGO Panel + Leaderboard -->
    <div>
      <div class="card">
        <h2>NGO Panel</h2>
        <label>NGO Name</label>
        <input id="ngoName" type="text" placeholder="Enter NGO name">

        <div style="display:flex;gap:8px;margin-bottom:10px">
          <button id="ngoModeBtn" class="small ghost">Switch to NGO mode</button>
          <button id="refreshBtn" class="small">Refresh</button>
        </div>

        <div id="allReports" class="report-list" style="max-height:50vh;overflow:auto"></div>
      </div>

      <div class="card" style="margin-top:16px">
        <h2>🏆 Leaderboard</h2>
        <h3 style="margin:4px 0">Reporters</h3>
        <ul id="reporterBoard" class="leaderboard"></ul>
        <h3 style="margin:8px 0 4px">NGOs</h3>
        <ul id="ngoBoard" class="leaderboard"></ul>
      </div>
    </div>
  </div>
</div>

<footer>
  ⏳ TimeChain demo — local only (data stored in your browser).  
  Reporters earn 10–30 pts per issue. NGOs earn +5 pts for accepting, +20 pts for solving.
</footer>

<script>
const STORAGE_KEY = 'timechain_reports';
const POINTS_KEY = 'timechain_points';
let ngoMode = false;

function readReports(){ return JSON.parse(localStorage.getItem(STORAGE_KEY)||'[]'); }
function writeReports(arr){ localStorage.setItem(STORAGE_KEY,JSON.stringify(arr)); }
function readPoints(){ return JSON.parse(localStorage.getItem(POINTS_KEY)||'{"reporters":{},"ngos":{}}'); }
function writePoints(obj){ localStorage.setItem(POINTS_KEY,JSON.stringify(obj)); }
function uid(){return 'r_'+Math.random().toString(36).slice(2,9);}

function awardPoints(type,name,amount){
  const pts=readPoints();
  if(type==='reporter'){ if(!pts.reporters[name]) pts.reporters[name]=0; pts.reporters[name]+=amount; }
  else { if(!pts.ngos[name]) pts.ngos[name]=0; pts.ngos[name]+=amount; }
  writePoints(pts); renderBoards();
}
function renderBoards(){
  const pts=readPoints();
  const rb=document.getElementById('reporterBoard'); rb.innerHTML='';
  Object.entries(pts.reporters).sort((a,b)=>b[1]-a[1]).forEach(([n,p])=>{
    rb.innerHTML+=`<li><span>${n}</span><span>${p} pts</span></li>`;
  });
  const nb=document.getElementById('ngoBoard'); nb.innerHTML='';
  Object.entries(pts.ngos).sort((a,b)=>b[1]-a[1]).forEach(([n,p])=>{
    nb.innerHTML+=`<li><span>${n}</span><span>${p} pts</span></li>`;
  });
}

function submitReport(){
  const name=document.getElementById('reporterName').value.trim();
  const desc=document.getElementById('desc').value.trim();
  const cat=document.getElementById('category').value;
  const loc=document.getElementById('locationText').value.trim();
  if(!name||!desc) return alert("Fill your name & description");

  const report={id:uid(),reporter:name,desc,cat,location:loc,createdAt:Date.now(),status:'pending',acceptedBy:null};
  const arr=readReports(); arr.push(report); writeReports(arr);

  let pts=10; if(cat==='health') pts=30; else if(cat==='sanitation') pts=20;
  awardPoints('reporter',name,pts);

  document.getElementById('desc').value=''; document.getElementById('locationText').value='';
  renderMyReports(name); renderAllReports(); alert("Report submitted +"+pts+" pts!");
}

function renderMyReports(name){
  const cont=document.getElementById('myReports'); cont.innerHTML='';
  readReports().filter(r=>r.reporter===name).forEach(r=>{
    cont.innerHTML+=`<div class="report-item"><strong>${r.cat}</strong> - ${r.desc}<br>
    <span class="meta">${r.status} | ${r.location||'no location'}</span></div>`;
  });
}

function renderAllReports(){
  const cont=document.getElementById('allReports'); cont.innerHTML='';
  readReports().forEach(r=>{
    let html=`<div class="report-item"><strong>${r.cat}</strong> - ${r.desc}<br>
    <div class="meta">Reporter: ${r.reporter} | Status: ${r.status}</div>`;
    if(ngoMode && r.status!=='solved'){
      html+=`<div class="row" style="margin-top:6px">
        <button class="small" onclick="acceptReport('${r.id}')">Accept</button>
        <button class="small ghost" onclick="solveReport('${r.id}')">Solve</button>
      </div>`;
    }
    html+='</div>'; cont.innerHTML+=html;
  });
}

function acceptReport(id){
  const ngo=document.getElementById('ngoName').value.trim(); if(!ngo) return alert("Enter NGO name");
  const arr=readReports(); const r=arr.find(x=>x.id===id); if(!r) return;
  r.status='in_progress'; r.acceptedBy=ngo; writeReports(arr);
  awardPoints('ngo',ngo,5); renderAllReports(); alert("NGO accepted +5 pts");
}
function solveReport(id){
  const ngo=document.getElementById('ngoName').value.trim(); if(!ngo) return alert("Enter NGO name");
  const arr=readReports(); const r=arr.find(x=>x.id===id); if(!r) return;
  r.status='solved'; writeReports(arr);
  awardPoints('ngo',ngo,20); renderAllReports(); alert("Issue solved +20 pts");
}

function toggleNgoMode(){
  ngoMode=!ngoMode;
  document.getElementById('ngoModeBtn').textContent=ngoMode?"NGO mode ON":"Switch to NGO mode";
  renderAllReports();
}

document.getElementById('submitBtn').onclick=submitReport;
document.getElementById('ngoModeBtn').onclick=toggleNgoMode;
document.getElementById('refreshBtn').onclick=()=>{renderBoards();renderAllReports();};

renderBoards(); renderAllReports();
</script>
</body>
</html>
