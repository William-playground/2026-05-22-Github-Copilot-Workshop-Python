document.addEventListener("DOMContentLoaded", () => {
  const initialSeconds = 25 * 60;
  const timerDisplay = document.getElementById("timer-display");
  const statusDisplay = document.getElementById("timer-status");
  const elapsedDisplay = document.getElementById("elapsed-display");
  const remainingDisplay = document.getElementById("remaining-display");
  const startButton = document.getElementById("start-btn");
  const pauseButton = document.getElementById("pause-btn");
  const resetButton = document.getElementById("reset-btn");

  let remainingSeconds = initialSeconds;
  let elapsedSeconds = 0;
  let timerId = null;

  const formatSeconds = (seconds) => {
    const safeSeconds = Math.max(0, seconds);
    const minutes = String(Math.floor(safeSeconds / 60)).padStart(2, "0");
    const sec = String(safeSeconds % 60).padStart(2, "0");
    return `${minutes}:${sec}`;
  };

  const render = () => {
    const remainingText = formatSeconds(remainingSeconds);
    timerDisplay.textContent = remainingText;
    elapsedDisplay.textContent = formatSeconds(elapsedSeconds);
    remainingDisplay.textContent = remainingText;
  };

  const setStatus = (isRunning) => {
    statusDisplay.textContent = isRunning ? "実行中" : "停止中";
    statusDisplay.classList.toggle("running", isRunning);
    statusDisplay.classList.toggle("stopped", !isRunning);
    startButton.disabled = isRunning;
    pauseButton.disabled = !isRunning;
  };

  const stopTimer = () => {
    if (timerId !== null) {
      clearInterval(timerId);
      timerId = null;
    }
    setStatus(false);
  };

  const tick = () => {
    remainingSeconds -= 1;
    elapsedSeconds += 1;
    render();

    if (remainingSeconds <= 0) {
      stopTimer();
    }
  };

  startButton.addEventListener("click", () => {
    if (timerId !== null) {
      return;
    }
    timerId = window.setInterval(tick, 1000);
    setStatus(true);
  });

  pauseButton.addEventListener("click", () => {
    stopTimer();
  });

  resetButton.addEventListener("click", () => {
    stopTimer();
    remainingSeconds = initialSeconds;
    elapsedSeconds = 0;
    render();
  });

  render();
  setStatus(false);
});
