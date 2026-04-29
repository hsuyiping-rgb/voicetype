// Radio card active state
document.querySelectorAll('.radio-card input[type="radio"]').forEach(radio => {
  radio.addEventListener('change', () => {
    const group = radio.closest('.radio-group');
    group.querySelectorAll('.radio-card').forEach(c => c.classList.remove('active'));
    radio.closest('.radio-card').classList.add('active');
  });
});

// Password visibility toggle
document.querySelectorAll('.toggle-vis').forEach(btn => {
  btn.addEventListener('click', () => {
    const input = document.getElementById(btn.dataset.target);
    input.type = input.type === 'password' ? 'text' : 'password';
    btn.textContent = input.type === 'password' ? '👁' : '🙈';
  });
});

// Form submit → PATCH API
document.getElementById('settings-form').addEventListener('submit', async e => {
  e.preventDefault();
  const form = e.target;
  const data = {};
  new FormData(form).forEach((v, k) => { data[k] = v; });

  const btn = document.getElementById('save-btn');
  const msg = document.getElementById('save-msg');
  btn.disabled = true;
  btn.textContent = '儲存中…';

  try {
    const res = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('儲存失敗');
    msg.textContent = '✓ 已儲存';
    msg.classList.add('show');
    setTimeout(() => msg.classList.remove('show'), 2500);
  } catch (err) {
    msg.textContent = '❌ ' + err.message;
    msg.style.color = '#E74C3C';
    msg.classList.add('show');
  } finally {
    btn.disabled = false;
    btn.textContent = '儲存設定';
  }
});

// 狀態輪詢（每 2 秒）
async function pollStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    const badge = document.getElementById('status-badge');
    // 簡單對應（主程式狀態未整合時顯示待機）
    badge.className = 'badge badge--idle';
    badge.textContent = '待機中';
  } catch (_) {}
}
setInterval(pollStatus, 2000);
