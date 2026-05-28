const API = 'https://ai-interview-assistant-backend-v5hv.onrender.com';
const token = localStorage.getItem('token');
if (!token) window.location.href = 'index.html';

let selectedType = 'HR';
let selectedTopic = 'Python';

/* ─── INIT ─── */
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  loadUserInfo();
  loadStats();
  loadHistory();
  bindEvents();
});

/* ─── THEME ─── */
function initTheme() {
  const saved = localStorage.getItem('theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
  updateThemeIcon(saved);
}
function updateThemeIcon(theme) {
  const icon = document.getElementById('themeIcon');
  icon.innerHTML = theme === 'dark'
    ? '<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>'
    : '<path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>';
}
document.getElementById('themeToggle').addEventListener('click', () => {
  const curr = document.documentElement.getAttribute('data-theme');
  const next = curr === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  updateThemeIcon(next);
});

/* ─── EVENTS ─── */
function bindEvents() {
  document.getElementById('logoutBtn').addEventListener('click', () => {
    localStorage.clear(); window.location.href = 'index.html';
  });

  // Interview type selection
  document.querySelectorAll('.interview-type-card').forEach(card => {
    card.addEventListener('click', () => {
      document.querySelectorAll('.interview-type-card').forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
      selectedType = card.dataset.type;
      document.getElementById('topicSection').classList.toggle('hidden', selectedType !== 'Technical');
    });
  });

  // Topic chip selection
  document.querySelectorAll('.topic-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('.topic-chip').forEach(c => c.classList.remove('selected'));
      chip.classList.add('selected');
      selectedTopic = chip.dataset.topic;
    });
  });

  // Start interview
  document.getElementById('startInterviewBtn').addEventListener('click', startInterview);
  document.getElementById('quickStartBtn').addEventListener('click', startInterview);

  // History toggle
  document.getElementById('historyToggleBtn').addEventListener('click', toggleHistory);

  // Resume
  document.getElementById('resumeBrowse').addEventListener('click', () => document.getElementById('resumeInput').click());
  document.getElementById('resumeDropZone').addEventListener('click', () => document.getElementById('resumeInput').click());
  document.getElementById('resumeInput').addEventListener('change', handleResumeSelect);
  document.getElementById('analyzeResumeBtn').addEventListener('click', analyzeResume);

  // Drag and drop
  const dz = document.getElementById('resumeDropZone');
  dz.addEventListener('dragover', e => { e.preventDefault(); dz.classList.add('drag-over'); });
  dz.addEventListener('dragleave', () => dz.classList.remove('drag-over'));
  dz.addEventListener('drop', e => {
    e.preventDefault(); dz.classList.remove('drag-over');
    const f = e.dataTransfer.files[0];
    if (f && f.type === 'application/pdf') setResumeFile(f);
  });
}

/* ─── USER INFO ─── */
async function loadUserInfo() {
  try {
    const res = await fetch(`${API}/auth/me`, { headers: authHeaders() });
    if (!res.ok) return logout();
    const user = await res.json();
    document.getElementById('userEmail').textContent = user.email;
    document.getElementById('welcomeName').textContent = user.full_name?.split(' ')[0] || user.email.split('@')[0];
  } catch { /* silent */ }
}

/* ─── STATS ─── */
async function loadStats() {
  try {
    const res = await fetch(`${API}/interview/stats`, { headers: authHeaders() });
    if (!res.ok) return;
    const d = await res.json();
    document.getElementById('totalInterviews').textContent = d.total_interviews ?? 0;
    document.getElementById('avgScore').textContent = d.average_score ? d.average_score.toFixed(1) : '0.0';
    document.getElementById('totalQuestions').textContent = d.questions_answered ?? 0;
  } catch { /* silent */ }
}

/* ─── HISTORY ─── */
async function loadHistory() {
  try {
    const res = await fetch(`${API}/interview/sessions`, { headers: authHeaders() });
    if (!res.ok) return;
    const sessions = await res.json();
    renderHistory(sessions);
  } catch { /* silent */ }
}

function renderHistory(sessions) {
  const list = document.getElementById('historyList');
  const empty = document.getElementById('historyEmpty');
  const count = document.getElementById('historyCount');

  count.textContent = sessions.length;

  if (!sessions.length) {
    empty.style.display = 'block';
    list.innerHTML = '';
    return;
  }
  empty.style.display = 'none';

  list.innerHTML = sessions.map(s => {
    const type = s.interview_type || 'HR';
    const score = s.average_score ? s.average_score.toFixed(1) : '—';
    const date = s.created_at ? new Date(s.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '';
    const label = type === 'HR' ? 'HR' : (s.topic || 'Technical');
    return `
      <div class="history-item" onclick="window.location.href='interview.html?session=${s.id}'">
        <div class="history-dot ${type.toLowerCase()}"></div>
        <div class="history-info">
          <div class="history-title">${label} Interview</div>
          <div class="history-meta">${date} · ${s.questions_count || 0} questions</div>
        </div>
        <div class="history-score">${score}</div>
      </div>`;
  }).join('');
}

function toggleHistory() {
  const btn = document.getElementById('historyToggleBtn');
  const panel = document.getElementById('historyPanel');
  btn.classList.toggle('open');
  panel.classList.toggle('open');
}

/* ─── START INTERVIEW ─── */
async function startInterview() {
  showLoading('Setting up your interview...');
  try {
    const body = { interview_type: selectedType };
    if (selectedType === 'Technical') body.topic = selectedTopic;

    const res = await fetch(`${API}/interview/start`, {
      method: 'POST',
      headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error('Failed to start');
    const data = await res.json();
    localStorage.setItem("interview_type", selectedType);
    localStorage.setItem("interview_topic", selectedType === "Technical" ? selectedTopic : "");
    localStorage.setItem("session_id", data.session_id);
    localStorage.setItem("first_question", data.first_question || "");
    window.location.href = "interview.html";
  } catch (e) {
    hideLoading();
    showToast('Could not start interview. Is the backend running?', 'error');
  }
}

/* ─── RESUME ─── */
let resumeFile = null;

function handleResumeSelect(e) {
  const f = e.target.files[0];
  if (f) setResumeFile(f);
}

function setResumeFile(f) {
  resumeFile = f;
  document.getElementById('resumeFileName').style.display = 'flex';
  document.getElementById('resumeFileNameText').textContent = f.name;
  document.getElementById('resumeAnalysisResult').style.display = 'none';
}

async function analyzeResume() {
  if (!resumeFile) return;
  showLoading('Analyzing your resume...');

  const formData = new FormData();
  formData.append('file', resumeFile);

  try {
    const res = await fetch(`${API}/resume/upload`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });
    if (!res.ok) throw new Error('Upload failed');
    const data = await res.json();
    hideLoading();
    renderResumeAnalysis(data.analysis || data);
  } catch (e) {
    hideLoading();
    showToast('Resume analysis failed. Try again.', 'error');
  }
}

function renderResumeAnalysis(analysis) {
  const result = document.getElementById('resumeAnalysisResult');
  result.style.display = 'block';

  // Skills
  const skillsEl = document.getElementById('analysisSkills');
  const skills = Array.isArray(analysis.skills) ? analysis.skills : (analysis.skills || '').split(',');
  skillsEl.innerHTML = skills.filter(Boolean).map(s =>
    `<span class="skill-tag">${s.trim()}</span>`
  ).join('');

  // Level
  document.getElementById('analysisLevel').textContent = analysis.experience_level || 'Unknown';

  // Topics
  const topicsEl = document.getElementById('analysisTopics');
  const topics = Array.isArray(analysis.suggested_topics) ? analysis.suggested_topics : (analysis.suggested_topics || '').split(',');
  topicsEl.innerHTML = topics.filter(Boolean).map(t =>
    `<span class="topic-tag">${t.trim()}</span>`
  ).join('');

  // Strengths & improvement
  document.getElementById('analysisStrengths').textContent = analysis.strengths || '—';
  document.getElementById('analysisImprovement').textContent = analysis.improvement_areas || '—';

  result.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/* ─── HELPERS ─── */
function authHeaders() {
  return { Authorization: `Bearer ${token}` };
}

function logout() {
  localStorage.clear(); window.location.href = 'index.html';
}

function showLoading(text = 'Loading...') {
  document.getElementById('loadingText').textContent = text;
  document.getElementById('loadingOverlay').classList.remove('hidden');
}

function hideLoading() {
  document.getElementById('loadingOverlay').classList.add('hidden');
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