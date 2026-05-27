const API = 'http://localhost:8000';

// Redirect if already logged in
if (localStorage.getItem('token')) {
  window.location.href = 'dashboard.html';
}

function showError(msg) {
  const el = document.getElementById('authError');
  el.textContent = msg;
  el.classList.add('show');
}

function hideError() {
  document.getElementById('authError').classList.remove('show');
}

function setLoading(btnId, loading) {
  const btn = document.getElementById(btnId);
  if (loading) {
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Please wait...';
  } else {
    btn.disabled = false;
  }
}

async function doLogin() {
  hideError();
  const email    = document.getElementById('loginEmail').value.trim();
  const password = document.getElementById('loginPassword').value.trim();

  if (!email || !password) { showError('Please fill in all fields.'); return; }

  setLoading('loginBtn', true);
  try {
    const res = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Login failed');
    localStorage.setItem('token', data.access_token);
    window.location.href = 'dashboard.html';
  } catch (e) {
    showError(e.message);
    document.getElementById('loginBtn').disabled = false;
    document.getElementById('loginBtn').textContent = 'Login';
  }
}

async function doRegister() {
  hideError();
  const full_name = document.getElementById('regName').value.trim();
  const email     = document.getElementById('regEmail').value.trim();
  const password  = document.getElementById('regPassword').value.trim();

  if (!full_name || !email || !password) { showError('Please fill in all fields.'); return; }
  if (password.length < 6) { showError('Password must be at least 6 characters.'); return; }

  setLoading('registerBtn', true);
  try {
    const res = await fetch(`${API}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ full_name, email, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Registration failed');
    localStorage.setItem('token', data.access_token);
    window.location.href = 'dashboard.html';
  } catch (e) {
    showError(e.message);
    document.getElementById('registerBtn').disabled = false;
    document.getElementById('registerBtn').textContent = 'Create Account';
  }
}

// Enter key support
document.addEventListener('keydown', e => {
  if (e.key !== 'Enter') return;
  const loginVisible = !document.getElementById('loginForm').classList.contains('hidden');
  if (loginVisible) doLogin(); else doRegister();
});