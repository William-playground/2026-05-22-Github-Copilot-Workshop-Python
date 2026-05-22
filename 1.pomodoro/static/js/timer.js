const STORAGE_KEY = "pomodoroDailyProgress";
const SESSION_SECONDS = 25 * 60;

function getTodayDateString() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function createDefaultProgress() {
  return {
    date: getTodayDateString(),
    completedCount: 0,
    focusSeconds: 0,
  };
}

function loadProgress() {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (!saved) {
    return createDefaultProgress();
  }

  try {
    const parsed = JSON.parse(saved);
    const today = getTodayDateString();
    if (parsed.date !== today) {
      return createDefaultProgress();
    }

    return {
      date: today,
      completedCount: Number(parsed.completedCount) || 0,
      focusSeconds: Number(parsed.focusSeconds) || 0,
    };
  } catch (error) {
    return createDefaultProgress();
  }
}

function saveProgress(progress) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
}

function formatFocusTime(seconds) {
  const totalMinutes = Math.floor(seconds / 60);
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;

  if (hours === 0) {
    return `${minutes}分`;
  }
  if (minutes === 0) {
    return `${hours}時間`;
  }
  return `${hours}時間${minutes}分`;
}

function renderProgress(progress) {
  const completedCountElement = document.getElementById("completed-count");
  const focusTimeElement = document.getElementById("focus-time");
  completedCountElement.textContent = progress.completedCount;
  focusTimeElement.textContent = formatFocusTime(progress.focusSeconds);
}

document.addEventListener("DOMContentLoaded", () => {
  const completeButton = document.getElementById("complete-session");
  const progress = loadProgress();
  saveProgress(progress);
  renderProgress(progress);

  completeButton.addEventListener("click", () => {
    progress.completedCount += 1;
    progress.focusSeconds += SESSION_SECONDS;
    saveProgress(progress);
    renderProgress(progress);
  });
});
