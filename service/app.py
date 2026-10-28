from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime
import subprocess
import json
import html

LOG_FILE = Path("/home/iot/service-recovery-project/logs/recovery.log")
SERVICE = "test-web.service"


class Dashboard(BaseHTTPRequestHandler):

    def status(self):
        result = subprocess.run(
            ["systemctl", "is-active", SERVICE],
            capture_output=True, text=True
        )
        return result.stdout.strip() or "unknown"

    def entries(self):
        if not LOG_FILE.exists():
            return []
        lines = LOG_FILE.read_text(errors="replace").splitlines()
        result = []
        for line in lines:
            if line.startswith("Time:"):
                result.append({
                    "time": line[6:].strip(),
                    "status": "",
                    "recovery": "Monitoring check"
                })
            elif line.startswith("Status:") and result:
                result[-1]["status"] = line[7:].strip()
            elif line.startswith("Recovery:") and result:
                result[-1]["recovery"] = line[9:].strip()
        return result

    def do_GET(self):
        if self.path == "/api":
            entries = self.entries()
            successes = sum(
                e["recovery"].startswith("SUCCESS") for e in entries
            )
            data = {
                "status": self.status(),
                "attempts": successes,
                "entries": entries[-50:],
                "time": datetime.now().strftime("%d %b %Y %H:%M:%S")
            }
            body = json.dumps(data).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return

        page = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Linux Service Recovery</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#f1f5fb;color:#1b2b46;font:15px Arial,sans-serif}
header{background:linear-gradient(115deg,#122440,#234b7c);color:white;padding:25px 30px;display:flex;justify-content:space-between;align-items:center;gap:15px;flex-wrap:wrap}
h1{font-size:25px;margin:0}.sub{color:#c5d5ee;margin-top:8px;font-size:13px}
.layout{display:grid;grid-template-columns:205px 1fr;min-height:calc(100vh - 100px)}
aside{background:#172b49;padding:22px 12px;color:#d9e5f8}
nav button{width:100%;border:0;background:transparent;color:inherit;text-align:left;padding:14px;border-radius:8px;margin-bottom:7px;cursor:pointer;font-size:14px}
nav button:hover,nav button.active{background:#2b4c82;color:white}
main{padding:25px;min-width:0}
.cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:15px}
.card,.panel{background:white;border:1px solid #e1e9f4;border-radius:13px;padding:20px;box-shadow:0 4px 15px #1b37600a;min-width:0}
.card h3{font-size:14px;margin:0 0 18px;color:#50627f}
.big{font-size:24px;font-weight:bold;margin-bottom:9px;overflow-wrap:anywhere}
.muted{color:#74839a;font-size:12px}
.green{color:#07864b}.red{color:#c33131}.blue{color:#2868e8}.purple{color:#7550d4}
.content{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(250px,1fr);gap:17px;margin-top:20px}
.panel{margin-bottom:17px}
h2{font-size:17px;margin:0 0 18px}
.line{display:flex;justify-content:space-between;gap:12px;padding:13px 0;border-bottom:1px solid #edf1f6;font-size:13px}
.line:last-child{border-bottom:0}
.pill{border-radius:20px;padding:6px 9px;font-size:11px;font-weight:bold;background:#dcfce7;color:#087443}
table{border-collapse:collapse;width:100%;font-size:12px}
th,td{text-align:left;padding:11px 8px;border-bottom:1px solid #edf1f6;overflow-wrap:anywhere}
th{background:#f4f7fc;color:#586b87}
.tablewrap{overflow:auto}
.actions{display:grid;gap:10px}
.actions button,.download{border:0;border-radius:8px;padding:13px;background:#2868e8;color:white;font-weight:bold;cursor:pointer}
.actions button:nth-child(2){background:#6848c7}.actions button:nth-child(3){background:#167d85}
.notice{margin-top:14px;padding:12px;background:#edf4ff;border-radius:8px;color:#50678b;font-size:12px;line-height:1.5}
.view{display:none}.view.active{display:block}
footer{text-align:center;color:#8290a5;font-size:12px;padding:12px}
@media(max-width:1000px){.cards{grid-template-columns:repeat(2,minmax(0,1fr))}.content{grid-template-columns:1fr}}
@media(max-width:620px){.layout{grid-template-columns:1fr}aside nav{display:flex;flex-wrap:wrap}nav button{width:auto}main{padding:12px}.cards{gap:8px}.card,.panel{padding:13px}.big{font-size:19px}header{padding:20px}}
</style>
</head>
<body>
<header>
 <div><h1>🐧 Linux Service Recovery</h1><div class="sub">MONITOR · DETECT · RECOVER · STAY ONLINE</div></div>
 <div>🟢 Local System Monitor<br><small id="clock">Connecting...</small></div>
</header>
<div class="layout">
<aside><nav>
 <button class="active" data-view="dashboard">▦ &nbsp; Dashboard</button>
 <button data-view="logs">▤ &nbsp; Recovery Logs</button>
 <button data-view="settings">⚙ &nbsp; Settings</button>
 <button data-view="about">ⓘ &nbsp; About Project</button>
</nav></aside>
<main>
<section id="dashboard" class="view active">
<div class="cards">
 <div class="card"><h3>🟢 Service Status</h3><div class="big green" id="status">Loading</div><div class="muted">test-web.service</div></div>
 <div class="card"><h3>🔄 Successful Recoveries</h3><div class="big blue" id="attempts">—</div><div class="muted">Recorded recovery events</div></div>
 <div class="card"><h3>⏱ Monitoring Interval</h3><div class="big purple">1 minute</div><div class="muted">Configured monitor schedule</div></div>
 <div class="card"><h3>📄 Recovery Report</h3><div class="big green" id="report">Checking</div><div class="muted">Actual local log file</div></div>
</div>
<div class="content"><div>
 <div class="panel"><h2>📈 Service Overview</h2>
 <div class="line"><span>Systemd service</span><b>test-web.service</b></div>
 <div class="line"><span>Current status</span><b id="detailStatus">Checking</b></div>
 <div class="line"><span>Dashboard endpoint</span><b>127.0.0.1:8080</b></div>
 <div class="line"><span>Last updated</span><b id="updated">—</b></div>
 <div class="notice">This dashboard reads the real Linux service status and recovery log. The scheduled monitor performs automatic recovery.</div>
 </div>
 <div class="panel"><h2>🧾 Recent Recovery History</h2><div class="tablewrap"><table><thead><tr><th>Time</th><th>Status</th><th>Result</th></tr></thead><tbody id="recent"><tr><td colspan="3">Loading...</td></tr></tbody></table></div><p class="muted" id="message">Connecting to backend...</p></div>
</div><div>
 <div class="panel"><h2>🖥 Service Details</h2>
 <div class="line"><span>Service type</span><b>Python HTTP</b></div>
 <div class="line"><span>Port</span><b>8080</b></div>
 <div class="line"><span>Recovery engine</span><b>Bash + cron</b></div>
 <div class="line"><span>Refresh interval</span><b>10 seconds</b></div>
 </div>
 <div class="panel"><h2>⚡ Quick Actions</h2><div class="actions">
 <button onclick="refreshData()">⟳ &nbsp; Refresh Status</button>
 <button onclick="showView('logs')">▤ &nbsp; View All Logs</button>
 <button onclick="downloadLogs()">⇩ &nbsp; Download Report</button>
 </div><div class="notice">For safety, service stop/start commands remain in the terminal. This page does not run arbitrary commands as root.</div></div>
</div></div>
</section>
<section id="logs" class="view"><div class="panel"><h2>📋 Recovery Logs</h2><p class="muted">Latest records from the actual recovery log.</p><div class="tablewrap"><table><thead><tr><th>Time</th><th>Status</th><th>Result</th></tr></thead><tbody id="all"><tr><td colspan="3">Loading...</td></tr></tbody></table></div><p><button class="download" onclick="downloadLogs()">Download report</button></p></div></section>
<section id="settings" class="view"><div class="panel"><h2>⚙️ Monitoring Configuration</h2><div class="line"><span>Monitored service</span><b>test-web.service</b></div><div class="line"><span>Monitor schedule</span><b>Every minute (cron)</b></div><div class="line"><span>Dashboard refresh</span><b>10 seconds</b></div><div class="line"><span>Log file</span><b>logs/recovery.log</b></div><div class="notice">These are the current project settings, displayed for reference.</div></div></section>
<section id="about" class="view"><div class="panel"><h2>About This Project</h2><p>An automated Linux service monitoring and recovery system using Bash, systemd, cron, Ansible and a Python dashboard.</p><div class="line"><span>Monitoring</span><b>systemctl</b></div><div class="line"><span>Automation</span><b>Bash and cron</b></div><div class="line"><span>Configuration management</span><b>Ansible</b></div><div class="line"><span>Interface</span><b>Python, HTML, CSS, JavaScript</b></div></div></section>
<footer>Linux Service Recovery Dashboard · Local monitoring interface</footer>
</main></div>
<script>
let entries=[];
function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function render(id,list){document.getElementById(id).innerHTML=list.map(e=>{let k=e.status.includes('HEALTHY')?'healthy':e.status.includes('FAILURE')?'failure':'recovery';return `<tr><td>${esc(e.time)}</td><td><span class="pill ${k}">${esc(e.status||'RECORDED')}</span></td><td>${esc(e.recovery)}</td></tr>`}).join('')||'<tr><td colspan="3">No entries yet</td></tr>';}
async function refreshData(){try{let r=await fetch('/api',{cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status);let d=await r.json();let active=d.status==='active';let s=document.getElementById('status');s.textContent=d.status.toUpperCase();s.className='big '+(active?'green':'red');document.getElementById('detailStatus').textContent=d.status.toUpperCase();document.getElementById('attempts').textContent=d.attempts;document.getElementById('clock').textContent=d.time;document.getElementById('updated').textContent=d.time;document.getElementById('report').textContent='Available';entries=d.entries.slice().reverse();render('recent',entries.slice(0,8));render('all',entries);document.getElementById('message').textContent='Live data updated at '+d.time;}catch(e){document.getElementById('message').textContent='Backend error: '+e.message;}}
function showView(id){document.querySelectorAll('.view').forEach(x=>x.classList.remove('active'));document.getElementById(id).classList.add('active');document.querySelectorAll('nav button').forEach(x=>x.classList.toggle('active',x.dataset.view===id));if(id==='logs')refreshData();}
document.querySelectorAll('nav button').forEach(b=>b.addEventListener('click',()=>showView(b.dataset.view)));
function downloadLogs(){let blob=new Blob([entries.map(e=>`${e.time}\n${e.status}\n${e.recovery}`).join('\n\n')],{type:'text/plain'});let u=URL.createObjectURL(blob);let a=document.createElement('a');a.href=u;a.download='recovery-report.txt';a.click();URL.revokeObjectURL(u);}
refreshData();setInterval(refreshData,10000);
</script>
</body>
</html>'''
        body = page.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


HTTPServer(("0.0.0.0", 8080), Dashboard).serve_forever()
