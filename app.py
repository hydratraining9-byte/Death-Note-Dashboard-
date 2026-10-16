import asyncio
import glob
import os
import random
from flask import Flask, jsonify, render_template_string, request
from telethon import TelegramClient, events, functions, types
from telethon.errors import SessionPasswordNeededError

app = Flask(__name__)

API_ID = 39898677
API_HASH = "ecc862416723402ae18ef3d45e1d2dc9"
BOT_TOKEN = "8811774917:AAFxVg7_Je7_TqiUXXzg4Z5vqPMiFxooYb0"
ADMIN_ID = 7677244398  # <--- သင့်ရဲ့ Telegram User ID ကို ဒီမှာ ထည့်ပါ

temp_clients = {}
bot_page_counter = 1

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Death Note - Premium Dynamic Dashboard</title>
    <style>
        @keyframes bloodFlow {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        body { 
            background: linear-gradient(135deg, #200000, #0a0000, #150000, #050000);
            background-size: 400% 400%;
            animation: bloodFlow 12s ease infinite;
            color: #fff; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            padding: 20px; 
            margin: 0; 
        }
        #intro-splash {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: #000; display: flex; flex-direction: column;
            justify-content: center; align-items: center; z-index: 9999;
            animation: fadeIn 1s ease-in-out;
        }
        #intro-splash h1 { color: #ef4444; font-size: 32px; text-shadow: 0 0 20px rgba(239,68,68,0.8); margin-bottom: 10px; }
        #intro-splash p { color: #f87171; font-size: 14px; letter-spacing: 2px; }

        .container { max-width: 1100px; margin: auto; display: none; }
        .top-header { display: flex; justify-content: space-between; align-items: center; background: rgba(30, 5, 5, 0.9); padding: 15px 25px; border-radius: 12px; margin-bottom: 20px; border: 1px solid rgba(239, 68, 68, 0.4); box-shadow: 0 8px 32px rgba(220, 38, 38, 0.3); }
        .logo-area h1 { margin: 0; color: #ef4444; font-size: 22px; text-shadow: 0 0 10px rgba(239, 68, 68, 0.6); }
        .creator-tag { color: #f87171; font-size: 13px; font-weight: bold; }
        .badge-connected { background: rgba(20, 40, 30, 0.9); color: #2ecc71; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: bold; border: 1px solid rgba(46, 204, 113, 0.5); }
        .card { background: rgba(25, 8, 10, 0.9); padding: 22px; border-radius: 12px; margin-bottom: 20px; border: 1px solid rgba(239, 68, 68, 0.3); box-shadow: 0 4px 20px rgba(100,0,0,0.5); }
        .card h3 { margin-top: 0; color: #fca5a5; font-size: 16px; border-bottom: 1px solid rgba(239, 68, 68, 0.3); padding-bottom: 8px; }
        .form-row { display: grid; grid-template-columns: 2fr 2fr 1fr; gap: 15px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 6px; color: #fca5a5; font-size: 13px; }
        input, select, textarea { width: 100%; padding: 11px; background: rgba(10, 2, 3, 0.95); border: 1px solid rgba(239, 68, 68, 0.4); color: #fff; border-radius: 8px; box-sizing: border-box; }
        button { background: linear-gradient(135deg, #dc2626, #991b1b); color: white; border: none; padding: 11px 18px; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%; box-shadow: 0 4px 12px rgba(220, 38, 38, 0.4); }
        button:hover { background: linear-gradient(135deg, #ef4444, #dc2626); }
        .btn-danger { background: linear-gradient(135deg, #7f1d1d, #450a0a); }
        .btn-secondary { background: linear-gradient(135deg, #059669, #047857); width: auto; padding: 8px 16px; font-size: 13px; }
        .btn-delete { background: #991b1b; color: white; border: none; padding: 5px 10px; border-radius: 4px; font-size: 11px; cursor: pointer; }
        .accounts-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .accounts-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
        .account-box { background: rgba(40, 10, 12, 0.8); border: 1px solid rgba(239, 68, 68, 0.4); padding: 12px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; font-size: 13px; }
        .status-valid { background: rgba(14, 42, 34, 0.9); color: #2ecc71; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; text-align: center; }
        .stat-card { background: rgba(25, 8, 10, 0.9); border: 1px solid rgba(239, 68, 68, 0.3); padding: 15px; border-radius: 8px; }
        .stat-card .number { font-size: 24px; font-weight: bold; color: #f87171; margin-top: 5px; }
        .logs { background: rgba(5, 1, 2, 0.95); padding: 15px; border-radius: 8px; border: 1px solid rgba(239, 68, 68, 0.4); font-family: monospace; font-size: 12px; height: 150px; overflow-y: auto; color: #f87171; }
    </style>
</head>
<body>

    <div id="intro-splash">
        <h1>💀 DEATH NOTE</h1>
        <p>INITIALIZING DYNAMIC SYSTEM...</p>
    </div>

    <div class="container" id="main-container">
        <div class="top-header">
            <div class="logo-area">
                <h1>💀 DEATH NOTE DASHBOARD</h1>
                <div class="creator-tag">Dashboard Creator: Xypar | Link: www.xyper.com</div>
            </div>
            <div class="badge-connected">🟢 Secure & Connected</div>
        </div>

        {% if is_admin %}
        <div class="card">
            <div class="accounts-header">
                <h3 style="margin:0; border:none; padding:0;">Authorized Accounts ({{ accounts|length }})</h3>
                <button class="btn-secondary" onclick="toggleAddBox()">+ Add Account</button>
            </div>
            
            <div id="addAccountBox" style="display:none; background:rgba(10,2,3,0.95); padding:20px; border-radius:8px; margin-bottom:20px; border:1px solid rgba(239,68,68,0.4);">
                <div id="step1">
                    <div class="form-group"><label>Phone Number (+959...)</label><input type="text" id="phoneInput" placeholder="+959xxxxxxxx"></div>
                    <button type="button" class="btn-secondary" onclick="sendCode()">Request OTP</button>
                </div>
                <div id="step2" style="display:none;">
                    <div class="form-group"><label>Enter OTP Code</label><input type="text" id="codeInput" placeholder="12345"></div>
                    <button type="button" class="btn-secondary" onclick="verifyCode()">Verify OTP</button>
                </div>
                <div id="step3" style="display:none;">
                    <div class="form-group"><label>Two-Step Verification Password</label><input type="password" id="passwordInput" placeholder="Enter Cloud Password"></div>
                    <button type="button" class="btn-secondary" onclick="verifyPassword()">Confirm Password</button>
                </div>
            </div>

            <div class="accounts-grid">
                {% for acc in accounts %}
                <div class="account-box">
                    <div style="display: flex; align-items: center;">
                        <span>📱 {{ acc.phone }}</span>
                        {% if acc.is_premium %}
                        <span style="background: #eab308; color: #000; font-size: 10px; padding: 2px 6px; border-radius: 4px; margin-left: 6px; font-weight: bold;">⭐ Premium</span>
                        {% endif %}
                    </div>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <span class="status-valid">Active</span>
                        <button class="btn-delete" onclick="deleteAccount('{{ acc.phone }}')">Delete</button>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        <!-- USER MASS REPORTER -->
        <div class="card">
            <h3>👤 User Mass Reporter</h3>
            <form id="userReportForm">
                <div class="form-row">
                    <div class="form-group">
                        <label>Target Username / Link</label>
                        <input type="text" id="target" name="target" placeholder="@username" onblur="fetchUserInfo(this.value)" required>
                    </div>
                    <div class="form-group">
                        <label>Message Link (Required)</label>
                        <input type="text" id="msgLink" name="msgLink" placeholder="https://t.me/c/.../..." required>
                    </div>
                    <div class="form-group">
                        <label>Delay (sec)</label>
                        <input type="number" id="delay" name="delay" value="10" min="1">
                    </div>
                </div>
                <div id="userInfoBox" style="margin-bottom: 15px; font-size: 13px; color: #fca5a5; display:none;"></div>
                <div class="form-group">
                    <label>Report Reason</label>
                    <select id="reason" name="reason">
                        <option value="Auto">🔀 Auto-Random (All Official Reasons)</option>
                        <option value="Spam">Spam</option>
                        <option value="ChildAbuse">Child Abuse</option>
                        <option value="Violence">Violence</option>
                        <option value="Pornography">Pornography</option>
                        <option value="Copyright">Copyright</option>
                    </select>
                </div>
                {% if is_admin %}
                <button type="submit">Start User Mass Execution</button>
                {% else %}
                <button type="button" disabled style="opacity: 0.5;">Access Restricted (Guest Mode)</button>
                {% endif %}
            </form>
        </div>

        <!-- GROUP MASS REPORTER -->
        <div class="card">
            <h3>👥 Group Mass Reporter</h3>
            <form id="groupReportForm">
                <div class="form-row">
                    <div class="form-group"><label>Group Link / Username</label><input type="text" id="groupTarget" name="target" placeholder="https://t.me/..." required></div>
                    <div class="form-group"><label>Message Link (Required)</label><input type="text" id="groupMsgLink" name="msgLink" placeholder="https://t.me/c/..." required></div>
                    <div class="form-group"><label>Delay (sec)</label><input type="number" id="groupDelay" name="delay" value="10" min="1"></div>
                </div>
                <div class="form-group"><label>Group Report Reason</label>
                    <select id="groupReason" name="reason">
                        <option value="Auto">🔀 Auto-Random (Group Reasons)</option>
                        <option value="Spam">Spam</option>
                        <option value="Violence">Violence</option>
                        <option value="Pornography">Pornography</option>
                    </select>
                </div>
                {% if is_admin %}
                <button type="submit">Start Group Mass Execution</button>
                {% else %}
                <button type="button" disabled style="opacity: 0.5;">Access Restricted (Guest Mode)</button>
                {% endif %}
            </form>
        </div>

        <!-- CHANNEL MASS REPORTER -->
        <div class="card">
            <h3>📢 Channel Mass Reporter</h3>
            <form id="channelReportForm">
                <div class="form-row">
                    <div class="form-group"><label>Channel Link / Username</label><input type="text" id="channelTarget" name="target" placeholder="https://t.me/..." required></div>
                    <div class="form-group"><label>Message Link (Required)</label><input type="text" id="channelMsgLink" name="msgLink" placeholder="https://t.me/c/..." required></div>
                    <div class="form-group"><label>Delay (sec)</label><input type="number" id="channelDelay" name="delay" value="10" min="1"></div>
                </div>
                <div class="form-group"><label>Channel Report Reason</label>
                    <select id="channelReason" name="reason">
                        <option value="Auto">🔀 Auto-Random (Channel Reasons)</option>
                        <option value="Copyright">Copyright</option>
                        <option value="Pornography">Pornography</option>
                    </select>
                </div>
                {% if is_admin %}
                <button type="submit">Start Channel Mass Execution</button>
                {% else %}
                <button type="button" disabled style="opacity: 0.5;">Access Restricted (Guest Mode)</button>
                {% endif %}
            </form>
        </div>

        <div class="stats-grid" style="margin-bottom: 20px;">
            <div class="stat-card"><div style="color:#fca5a5; font-size:13px;">Processed</div><div class="number" id="statProcessed">0</div></div>
            <div class="stat-card"><div style="color:#fca5a5; font-size:13px;">Success</div><div class="number" id="statSuccess" style="color:#2ecc71;">0</div></div>
            <div class="stat-card"><div style="color:#fca5a5; font-size:13px;">Failed</div><div class="number" id="statFailed" style="color:#ef4444;">0</div></div>
            <div class="stat-card"><div style="color:#fca5a5; font-size:13px;">Runtime</div><div class="number">00:00</div></div>
        </div>

        <div class="logs" id="logs">[System] Death Note Premium Dynamic Dashboard initialized securely...</div>
    </div>

    <script>
        setTimeout(() => {
            document.getElementById('intro-splash').style.display = 'none';
            document.getElementById('main-container').style.display = 'block';
        }, 3000);

        let currentPhone = ""; let phoneCodeHash = "";
        function toggleAddBox() {
            let box = document.getElementById('addAccountBox');
            box.style.display = box.style.display === 'none' ? 'block' : 'none';
        }
        async function sendCode() {
            const phone = document.getElementById('phoneInput').value.trim();
            const logsBox = document.getElementById('logs');
            if(!phone) { alert("Please enter phone number"); return; }
            const response = await fetch('/send_code', { method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded'}, body: `phone=${phone}` });
            const res = await response.json();
            if(res.status === 'success') {
                currentPhone = phone; phoneCodeHash = res.phone_code_hash;
                document.getElementById('step1').style.display = 'none';
                document.getElementById('step2').style.display = 'block';
                logsBox.innerHTML += `<br>[SUCCESS] OTP dispatched!`;
            } else { logsBox.innerHTML += `<br>[ERROR] ${res.message}`; }
        }
        async function verifyCode() {
            const code = document.getElementById('codeInput').value.trim();
            const response = await fetch('/verify_code', { method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded'}, body: `phone=${currentPhone}&code=${code}&hash=${phoneCodeHash}` });
            const res = await response.json();
            if(res.status === 'success') {
                setTimeout(() => location.reload(), 1500);
            } else if(res.status === 'needs_password') {
                document.getElementById('step2').style.display = 'none';
                document.getElementById('step3').style.display = 'block';
            } else { alert(res.message); }
        }
        async function verifyPassword() {
            const password = document.getElementById('passwordInput').value.trim();
            const response = await fetch('/verify_password', { method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded'}, body: `phone=${currentPhone}&password=${password}` });
            const res = await response.json();
            if(res.status === 'success') {
                setTimeout(() => location.reload(), 1500);
            } else { alert(res.message); }
        }
        async function deleteAccount(phone) {
            if(!confirm(`Delete session for ${phone}?`)) return;
            await fetch('/delete_account', { method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded'}, body: `phone=${phone}` });
            location.reload();
        }
        async function fetchUserInfo(username) {
            if(!username) return;
            const res = await fetch(`/get_user_info?username=${encodeURIComponent(username)}`);
            const data = await res.json();
            const box = document.getElementById('userInfoBox');
            if(data.status === 'success') {
                box.style.display = 'block';
                box.innerHTML = `👤 Target Info: <b>${data.name}</b> (@${data.username}) | ID: ${data.id}`;
            } else {
                box.style.display = 'block';
                box.innerHTML = `⚠️ Target info could not be fetched.`;
            }
        }

        async function handleReportSubmit(formId, endpoint) {
            document.getElementById(formId).onsubmit = async function(e) {
                e.preventDefault();
                const logsBox = document.getElementById('logs');
                logsBox.innerHTML += `<br>[INFO] Executing Report Module...`;
                const formData = new URLSearchParams(new FormData(this));
                const response = await fetch(endpoint, { method: 'POST', body: formData });
                const result = await response.json();
                document.getElementById('statProcessed').innerText = result.processed;
                document.getElementById('statSuccess').innerText = result.success;
                document.getElementById('statFailed').innerText = result.failed;
                if(result.details) {
                    result.details.forEach(d => { logsBox.innerHTML += `<br>👉 ${d.status}`; });
                }
            };
        }
        handleReportSubmit('userReportForm', '/run_module');
        handleReportSubmit('groupReportForm', '/run_group_module');
        handleReportSubmit('channelReportForm', '/run_channel_module');
    </script>
</body>
</html>
"""


def get_user_sessions():
  return [
      f for f in glob.glob("*.session") if not f.startswith("death_note_bot")
  ]


@app.route("/")
def index():
  is_admin = (
      request.remote_addr == "127.0.0.1" or request.remote_addr == "::1"
  )
  session_files = get_user_sessions()
  accounts = []
  for idx, file in enumerate(session_files, start=1):
    phone = file.replace(".session", "")
    is_prem = phone.endswith("7")
    accounts.append(
        {"id": idx, "phone": phone, "is_premium": is_prem, "is_active": True}
    )

  if not is_admin:
    accounts = [
        {"id": i, "phone": "Anonymous***", "is_premium": False, "is_active": False}
        for i in range(len(accounts))
    ]

  return render_template_string(
      HTML_TEMPLATE, accounts=accounts, is_admin=is_admin
  )


@app.route("/send_code", methods=["POST"])
def send_code():
  phone = request.form.get("phone").strip()
  session_name = phone.replace("+", "")

  async def do_send():
    client = TelegramClient(session_name, API_ID, API_HASH)
    await client.connect()
    sent = await client.send_code_request(phone)
    temp_clients[phone] = client
    return sent.phone_code_hash

  try:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    hash_code = loop.run_until_complete(do_send())
    return jsonify({"status": "success", "phone_code_hash": hash_code})
  except Exception as e:
    return jsonify({"status":"error", "message": str(e)})


@app.route("/verify_code", methods=["POST"])
def verify_code():
  phone = request.form.get("phone").strip()
  code = request.form.get("code").strip()
  hash_val = request.form.get("hash").strip()
  client = temp_clients.get(phone)
  if not client:
    return jsonify({"status": "error", "message": "Session expired."})

  async def do_verify():
    try:
      await client.sign_in(phone=phone, code=code, phone_code_hash=hash_val)
      if not await client.is_user_authorized():
        await client.disconnect()
        return "not_auth"
      await client.disconnect()
      return "success"
    except SessionPasswordNeededError:
      return "needs_password"
    except Exception as e:
      await client.disconnect()
      raise e

  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
  status = loop.run_until_complete(do_verify())
  if status == "success":
    return jsonify({"status": "success"})
  elif status == "needs_password":
    return jsonify({"status": "needs_password"})
  else:
    return jsonify({"status": "error", "message": "Authorization failed."})


@app.route("/verify_password", methods=["POST"])
def verify_password():
  phone = request.form.get("phone").strip()
  password = request.form.get("password").strip()
  client = temp_clients.get(phone)
  if not client:
    return jsonify({"status": "error", "message": "Session expired."})

  async def do_password():
    try:
      await client.sign_in(password=password)
      if not await client.is_user_authorized():
        await client.disconnect()
        return False
      await client.disconnect()
      return True
    except Exception as e:
      await client.disconnect()
      raise e

  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
  success = loop.run_until_complete(do_password())
  if success:
    return jsonify({"status": "success"})
  return jsonify({"status": "error", "message": "Password incorrect."})


@app.route("/delete_account", methods=["POST"])
def delete_account():
  phone = request.form.get("phone").strip()
  sf = f"{phone.replace('+', '')}.session"
  if os.path.exists(sf):
    os.remove(sf)
    return jsonify({"status": "success"})
  return jsonify({"status": "error"})


@app.route("/get_user_info", methods=["GET"])
def get_user_info():
  username = request.args.get("username").strip()
  session_files = get_user_sessions()
  if not session_files:
    return jsonify({"status": "error"})

  async def fetch_info():
    client = TelegramClient(
        session_files[0].replace(".session", ""), API_ID, API_HASH
    )
    await client.connect()
    try:
      entity = await client.get_entity(username)
      await client.disconnect()
      return {
          "status": "success",
          "name": getattr(entity, "first_name", "Unknown"),
          "username": getattr(entity, "username", username),
          "id": entity.id,
      }
    except Exception:
      await client.disconnect()
      return {"status": "error"}

  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
  res = loop.run_until_complete(fetch_info())
  return jsonify(res)


def execute_mass_report(target, msg_link, delay):
  session_files = get_user_sessions()
  success_count, fail_count = 0, 0
  details = []

  async def send_reports():
    nonlocal success_count, fail_count
    for file in session_files:
      acc_name = file.replace(".session", "")
      client = TelegramClient(acc_name, API_ID, API_HASH)
      try:
        await client.connect()
        if await client.is_user_authorized():
          entity = await client.get_input_entity(target)
          await client(
              functions.account.ReportPeerRequest(
                  peer=entity,
                  reason=types.InputReportReasonSpam(),
                  message=f"Death Note Report - Msg: {msg_link}",
              )
          )
          success_count += 1
          details.append({"account": acc_name, "status": f"{acc_name} - done"})
        else:
          fail_count += 1
          details.append(
              {
                  "account": acc_name,
                  "status": f"{acc_name} - fail (တရားမဝင်သေးပါ/Unauthorized)",
              }
          )
        await client.disconnect()
        await asyncio.sleep(delay)
      except Exception as e:
        fail_count += 1
        details.append(
            {"account": acc_name, "status": f"{acc_name} - fail ({str(e)})"}
        )

  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
  loop.run_until_complete(send_reports())
  return success_count, fail_count, details


@app.route("/run_module", methods=["POST"])
def run_module():
  target = request.form.get("target")
  msg_link = request.form.get("msgLink")
  delay = int(request.form.get("delay", 10))
  s, f, details = execute_mass_report(target, msg_link, delay)
  return jsonify(
      {"processed": s + f, "success": s, "failed": f, "details": details}
  )


@app.route("/run_group_module", methods=["POST"])
def run_group_module():
  target = request.form.get("target")
  msg_link = request.form.get("msgLink")
  delay = int(request.form.get("delay", 10))
  s, f, details = execute_mass_report(target, msg_link, delay)
  return jsonify(
      {"processed": s + f, "success": s, "failed": f, "details": details}
  )


@app.route("/run_channel_module", methods=["POST"])
def run_channel_module():
  target = request.form.get("target")
  msg_link = request.form.get("msgLink")
  delay = int(request.form.get("delay", 10))
  s, f, details = execute_mass_report(target, msg_link, delay)
  return jsonify(
      {"processed": s + f, "success": s, "failed": f, "details": details}
  )


# --- TELEGRAM BOT HANDLER (PROTECTED CONTENT / NO FORWARD) ---
async def start_telegram_bot():
  bot = TelegramClient("death_note_bot", API_ID, API_HASH)
  await bot.start(bot_token=BOT_TOKEN)
  user_forms = {}

  @bot.on(events.NewMessage(pattern="/start"))
  async def start_handler(event):
    sender_id = event.sender_id
    global bot_page_counter
    current_page = bot_page_counter
    bot_page_counter += 1
    if bot_page_counter > 1000:
      bot_page_counter = 1

    if sender_id != ADMIN_ID:
      await event.respond(
          f"📓 **Death Note စာမျက်နှာ {current_page} မှ ကြိုဆိုပါတယ်။**\n\n📌"
          " Menu Commands:\n/form - တိုင်ကြားရန် Form ဖြည့်မည်\n/help -"
          " အချက်အလက်နှင့် အကူအညီ\n/owner - ပိုင်ရှင်ကို ဆက်သွယ်ရန်",
          noforward=True,
      )
    else:
      await event.respond(
          "💀 **Welcome Admin (Xyper)**. System is active.", noforward=True
      )

  @bot.on(events.NewMessage(pattern="/owner"))
  async def owner_handler(event):
    await event.respond(
        "👑 **Owner / Creator:** Xypar\n\n⚠️ But Owner နဲ့ တိုက်ရိုက်ဆက်သွယ်ချင်ပါက"
        " Premium user တစ်ဦးဖြစ်ရမည်။",
        noforward=True,
    )

  @bot.on(events.NewMessage(pattern="/help"))
  async def help_handler(event):
    await event.respond(
        "ℹ️ **Death Note System Help:**\nဒီ Bot ကနေတစ်ဆင့် တိုင်ကြားလိုသည်များကို"
        " Form ဖြင့် တင်သွင်းနိုင်ပြီး Admin မှ စိစစ် အရေးယူပေးမည် ဖြစ်ပါသည်။",
        noforward=True,
    )

  @bot.on(events.NewMessage(pattern="/location"))
  async def location_handler(event):
    await event.respond(
        "⚠️ သတိပေးချက်။ သင်၏ IP Address နှင့် Device အချက်အလက်များကို"
        " လုံခြုံရေးအရ မှတ်တမ်းတင်ပြီးပါပြီ။",
        noforward=True,
    )

  @bot.on(events.NewMessage(pattern="/form"))
  async def form_handler(event):
    user_forms[event.sender_id] = {"step": "target"}
    await event.respond(
        "📝 **Death Note Report Form**\nTarget Username / Link ကို ပေးပို့ပါ။",
        noforward=True,
    )

  @bot.on(events.NewMessage(func=lambda e: e.sender_id in user_forms))
  async def form_steps(event):
    sender_id = event.sender_id
    data = user_forms[sender_id]
    text = event.raw_text.strip()

    if data["step"] == "target":
      data["target"] = text
      data["step"] = "msg_link"
      await event.respond(
          "🔗 ကျေးဇူးပြု၍ Message Link ကို ပေးပို့ပါ။", noforward=True
      )
    elif data["step"] == "msg_link":
      data["msg_link"] = text
      data["step"] = "reason"
      await event.respond(
          "⚖️ တိုင်ကြားလိုသည့် အကြောင်းအရင်း (ဥပမာ - Spam, Pornography, Violence"
          " စသည်ဖြင့်) ကို ပေးပို့ပါ။",
          noforward=True,
      )
    elif data["step"] == "reason":
      data["reason"] = text
      data["step"] = "screenshot"
      await event.respond(
          "📷 ကျေးဇူးပြု၍ သက်သေ Screenshot ပုံကို ပေးပို့ပါ။", noforward=True
      )
    elif data["step"] == "screenshot":
      target_info = data.get("target")
      msg_l = data.get("msg_link")
      reas = data.get("reason")

      admin_msg = (
          f"🚨 **New Report Form Received!**\n\n👤 From User ID: `{sender_id}`\n🎯"
          f" Target: `{target_info}`\n🔗 Message Link: `{msg_l}`\n⚖️ Reason:"
          f" `{reas}`"
      )
      # Admin ဆီသို့ Forward လို့မရအောင် ပို့ခြင်း
      await bot.send_message(ADMIN_ID, admin_msg, noforward=True)

      if event.photo:
        photo_path = await event.download_media()
        await bot.send_file(
            ADMIN_ID,
            photo_path,
            caption="📸 Protected Screenshot (Forward/Save Restricted)",
            noforward=True,
        )
        if os.path.exists(photo_path):
          os.remove(photo_path)

      await event.respond(
          "✅ သင်၏ Form တိုင်ကြားချက်ကို Admin ဆီသို့ အောင်မြင်စွာ ပေးပို့ပြီးပါပြီ!",
          noforward=True,
      )
      del user_forms[sender_id]

  await bot.run_until_disconnected()


def run_bot_thread():
  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
  loop.run_until_complete(start_telegram_bot())


if __name__ == "__main__":
  import threading

  threading.Thread(target=run_bot_thread, daemon=True).start()
  app.run(host="0.0.0.0", port=5001)
