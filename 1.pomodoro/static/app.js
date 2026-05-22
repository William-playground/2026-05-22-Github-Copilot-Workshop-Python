// Pomodoro Quest – front-end logic
(() => {
  const timerEl = document.getElementById('timer');
  const startBtn = document.getElementById('start-btn');
  const cancelBtn = document.getElementById('cancel-btn');
  const statusEl = document.getElementById('status');
  const modeBtns = document.querySelectorAll('.mode-btn');
  const tabBtns = document.querySelectorAll('.tab-btn');
  const toastEl = document.getElementById('toast');

  let selectedMinutes = 25;
  let remaining = selectedMinutes * 60;
  let interval = null;
  let currentSessionId = null;
  let statsCache = null;
  let activeTab = 'weekly';

  function fmt(seconds) {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  }

  function render() {
    timerEl.textContent = fmt(remaining);
  }

  function setRunning(running) {
    startBtn.disabled = running;
    cancelBtn.disabled = !running;
    modeBtns.forEach((b) => (b.disabled = running));
  }

  function showToast(msg) {
    toastEl.textContent = msg;
    toastEl.classList.remove('hidden');
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => toastEl.classList.add('hidden'), 3500);
  }

  modeBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      if (interval) return;
      modeBtns.forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      selectedMinutes = parseInt(btn.dataset.minutes, 10);
      remaining = selectedMinutes * 60;
      render();
    });
  });

  startBtn.addEventListener('click', async () => {
    try {
      const res = await fetch('/api/sessions/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ duration_minutes: selectedMinutes }),
      });
      if (!res.ok) throw new Error('start failed');
      const data = await res.json();
      currentSessionId = data.session_id;
      remaining = selectedMinutes * 60;
      render();
      setRunning(true);
      statusEl.textContent = '集中タイム中... 頑張って！';
      interval = setInterval(tick, 1000);
    } catch (err) {
      statusEl.textContent = 'セッションを開始できませんでした。';
    }
  });

  cancelBtn.addEventListener('click', async () => {
    if (!currentSessionId) return;
    clearInterval(interval);
    interval = null;
    try {
      await fetch(`/api/sessions/${currentSessionId}/cancel`, { method: 'POST' });
    } catch (_) {}
    currentSessionId = null;
    remaining = selectedMinutes * 60;
    render();
    setRunning(false);
    statusEl.textContent = 'セッションを中止しました。';
  });

  async function tick() {
    remaining -= 1;
    render();
    if (remaining <= 0) {
      clearInterval(interval);
      interval = null;
      await completeSession();
    }
  }

  async function completeSession() {
    if (!currentSessionId) return;
    const id = currentSessionId;
    currentSessionId = null;
    try {
      const res = await fetch(`/api/sessions/${id}/complete`, { method: 'POST' });
      const data = await res.json();
      let msg = `🎉 ポモドーロ完了！+${data.xp_gained} XP`;
      if (data.leveled_up) {
        msg += ` / レベルアップ → Lv.${data.profile.level} 🆙`;
      }
      if (data.new_badges && data.new_badges.length) {
        msg += ` / 新バッジ: ${data.new_badges.map((b) => b.name).join(', ')}`;
      }
      showToast(msg);
      statusEl.textContent = '休憩を取りましょう☕';
      applyProfile(data.profile);
      await refreshStats();
    } catch (err) {
      statusEl.textContent = 'セッションの保存に失敗しました。';
    }
    setRunning(false);
    remaining = selectedMinutes * 60;
    render();
  }

  function applyProfile(p) {
    document.getElementById('level').textContent = p.level;
    document.getElementById('streak').textContent = p.streak;
    document.getElementById('best-streak').textContent = p.best_streak;
    document.getElementById('total-completed').textContent = p.total_completed;
    const fill = document.getElementById('xp-fill');
    fill.style.width = `${p.level_progress.percent}%`;
    document.getElementById('xp-text').textContent =
      `${p.level_progress.level_xp} / ${p.level_progress.next_level_xp} XP (合計 ${p.xp})`;
    const list = document.getElementById('badges');
    list.innerHTML = '';
    if (!p.badges.length) {
      list.innerHTML = '<li class="empty">まだバッジはありません。ポモドーロを完了して獲得しましょう！</li>';
    } else {
      for (const b of p.badges) {
        const li = document.createElement('li');
        li.innerHTML = `<span class="badge-name">🏅 ${b.name}</span><span class="badge-desc">${b.description}</span>`;
        list.appendChild(li);
      }
    }
  }

  function renderStats() {
    if (!statsCache) return;
    const data = statsCache[activeTab];
    const summary = data.summary;
    const summaryEl = document.getElementById('stats-summary');
    summaryEl.innerHTML = `
      <div><span class="num">${summary.completed}</span><span class="lab">完了数</span></div>
      <div><span class="num">${summary.completion_rate}%</span><span class="lab">完了率</span></div>
      <div><span class="num">${summary.average_focus_minutes}</span><span class="lab">平均集中(分)</span></div>
      <div><span class="num">${summary.total_focus_minutes}</span><span class="lab">合計集中(分)</span></div>
    `;
    const chart = document.getElementById('chart');
    chart.innerHTML = '';
    const max = Math.max(1, ...data.daily.map((d) => d.completed));
    for (const d of data.daily) {
      const bar = document.createElement('div');
      bar.className = 'bar' + (d.completed === 0 ? ' zero' : '');
      bar.style.height = `${(d.completed / max) * 100}%`;
      bar.dataset.label = `${d.date}: ${d.completed}回`;
      chart.appendChild(bar);
    }
  }

  tabBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      tabBtns.forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      activeTab = btn.dataset.range;
      renderStats();
    });
  });

  async function refreshProfile() {
    const res = await fetch('/api/profile');
    if (res.ok) applyProfile(await res.json());
  }
  async function refreshStats() {
    const res = await fetch('/api/stats');
    if (res.ok) {
      statsCache = await res.json();
      renderStats();
    }
  }

  render();
  refreshProfile();
  refreshStats();
})();
