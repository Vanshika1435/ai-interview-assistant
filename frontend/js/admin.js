const API = 'https://ai-interview-assistant-backend-v5hv.onrender.com';
let adminCreds = null;

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('adminLoginBtn').addEventListener('click', doLogin);
  document.getElementById('adminLogoutBtn').addEventListener('click', doLogout);

  document.getElementById('adminPassword').addEventListener('keydown', e => {
    if (e.key === 'Enter') doLogin();
  });
});

async function doLogin() {
  const email    = document.getElementById('adminEmail').value.trim();
  const password = document.getElementById('adminPassword').value.trim();
  const errEl    = document.getElementById('adminLoginError');

  if (!email || !password) {
    showError('Please enter email and password.'); return;
  }

  const btn = document.getElementById('adminLoginBtn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Signing in...';

  try {
    const res = await fetch(`${API}/admin/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Login failed');

    adminCreds = { email, password };
    errEl.classList.remove('show');
    showDashboard();
    loadStats();
  } catch (e) {
    showError(e.message || 'Invalid credentials');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Sign In';
  }
}

function showError(msg) {
  const el = document.getElementById('adminLoginError');
  el.textContent = msg;
  el.classList.add('show');
}

function doLogout() {
  adminCreds = null;
  document.getElementById('adminDashWrap').classList.add('hidden');
  document.getElementById('adminLoginWrap').classList.remove('hidden');
  document.getElementById('adminPassword').value = '';
}

function showDashboard() {
  document.getElementById('adminLoginWrap').classList.add('hidden');
  document.getElementById('adminDashWrap').classList.remove('hidden');
}

async function loadStats() {
  if (!adminCreds) return;
  const { email, password } = adminCreds;

  try {
    const res = await fetch(
      `${API}/admin/stats?email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`
    );
    if (!res.ok) { doLogout(); return; }
    const data = await res.json();

    document.getElementById('adminTotalUsers').textContent    = data.total_users;
    document.getElementById('adminTotalSessions').textContent = data.total_sessions;
    document.getElementById('adminAvgScore').textContent      = data.avg_score.toFixed(1);

    renderUsersTable(data.users);
    renderSessionsTable(data.sessions);
  } catch (e) {
    showToast('Failed to load stats', 'error');
  }
}

function renderUsersTable(users) {
  const tbody = document.getElementById('usersTableBody');
  if (!users.length) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--text-faint);padding:24px;">No users yet.</td></tr>';
    return;
  }
  tbody.innerHTML = users.map((u, i) => `
    <tr>
      <td style="color:var(--text-faint)">${i + 1}</td>
      <td style="font-weight:600">${u.name || '—'}</td>
      <td style="color:var(--text-muted)">${u.email}</td>
      <td style="color:var(--text-muted)">${u.joined}</td>
      <td><span class="badge badge-muted">${u.sessions}</span></td>
      <td>${scoreBadge(u.avg_score)}</td>
    </tr>`).join('');
}

function renderSessionsTable(sessions) {
  const tbody = document.getElementById('sessionsTableBody');
  if (!sessions.length) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:var(--text-faint);padding:24px;">No sessions yet.</td></tr>';
    return;
  }
  tbody.innerHTML = sessions.map((s, i) => `
    <tr>
      <td style="color:var(--text-faint)">${i + 1}</td>
      <td style="color:var(--text-muted);font-size:0.83rem">${s.user}</td>
      <td><span class="badge ${s.type === 'HR' ? 'badge-warning' : 'badge-primary'}">${s.type}</span></td>
      <td style="color:var(--text-muted)">${s.topic}</td>
      <td style="text-align:center">${s.questions}</td>
      <td>${scoreBadge(s.score)}</td>
      <td style="color:var(--text-muted)">${s.date}</td>
    </tr>`).join('');
}

function scoreBadge(score) {
  const s = parseFloat(score) || 0;
  const cls = s >= 7 ? 'badge-success' : s >= 4 ? 'badge-warning' : 'badge-danger';
  return `<span class="badge ${cls}">${s.toFixed(1)}</span>`;
}

function showToast(msg, type = 'info') {
  const icons = {
    success: '<polyline points="20 6 9 17 4 12"/>',
    error:   '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>',
    info:    '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
  };
  const wrap = document.getElementById('toastContainer');
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">${icons[type]}</svg>${msg}`;
  wrap.appendChild(el);
  setTimeout(() => el.remove(), 3500);
}