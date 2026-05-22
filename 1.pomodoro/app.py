from http.server import BaseHTTPRequestHandler, HTTPServer


HTML = """<!doctype html>
<html lang="ja">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Pomodoro Timer</title>
    <style>
      body {
        margin: 0;
        min-height: 100vh;
        display: grid;
        place-items: center;
        background: #f6f7fb;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }
      .timer-card {
        width: min(360px, 92vw);
        background: #fff;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.12);
        padding: 28px;
        text-align: center;
      }
      .ring-wrapper {
        width: 220px;
        height: 220px;
        margin: 0 auto 16px;
        position: relative;
      }
      .ring-wrapper svg {
        transform: rotate(-90deg);
      }
      .time {
        position: absolute;
        inset: 0;
        display: grid;
        place-items: center;
        font-size: 2.6rem;
        font-weight: 700;
        color: #0f172a;
      }
      .actions {
        display: flex;
        justify-content: center;
        gap: 12px;
      }
      button {
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 1rem;
        cursor: pointer;
      }
      #toggle-btn {
        background: #2563eb;
        color: #fff;
      }
      #reset-btn {
        background: #e2e8f0;
        color: #0f172a;
      }
    </style>
  </head>
  <body>
    <main class="timer-card">
      <div class="ring-wrapper">
        <svg width="220" height="220" viewBox="0 0 220 220" aria-hidden="true">
          <circle cx="110" cy="110" r="95" stroke="#e2e8f0" stroke-width="14" fill="none"></circle>
          <circle
            id="progress-ring"
            cx="110"
            cy="110"
            r="95"
            stroke="#2563eb"
            stroke-width="14"
            fill="none"
            stroke-linecap="round"
          ></circle>
        </svg>
        <div id="time-display" class="time">25:00</div>
      </div>
      <div class="actions">
        <button id="toggle-btn" type="button">開始</button>
        <button id="reset-btn" type="button">リセット</button>
      </div>
    </main>

    <script>
      const TOTAL_SECONDS = 25 * 60;
      const timeDisplay = document.getElementById("time-display");
      const toggleBtn = document.getElementById("toggle-btn");
      const resetBtn = document.getElementById("reset-btn");
      const progressRing = document.getElementById("progress-ring");

      const radius = Number(progressRing.getAttribute("r"));
      const circumference = 2 * Math.PI * radius;
      progressRing.style.strokeDasharray = String(circumference);

      let remainingSeconds = TOTAL_SECONDS;
      let intervalId = null;
      let timerState = "stopped"; // stopped | running | paused

      function formatTime(total) {
        const minutes = Math.floor(total / 60);
        const seconds = total % 60;
        return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
      }

      function updateRing() {
        const progress = remainingSeconds / TOTAL_SECONDS;
        progressRing.style.strokeDashoffset = String(circumference * (1 - progress));
      }

      function updateTimerUI() {
        timeDisplay.textContent = formatTime(remainingSeconds);
        updateRing();
      }

      function updateToggleButton() {
        if (timerState === "running") {
          toggleBtn.textContent = "一時停止";
          return;
        }
        if (timerState === "paused") {
          toggleBtn.textContent = "再開";
          return;
        }
        toggleBtn.textContent = "開始";
      }

      function stopInterval() {
        if (intervalId !== null) {
          clearInterval(intervalId);
          intervalId = null;
        }
      }

      function startCountdown() {
        if (intervalId !== null || remainingSeconds <= 0) {
          return;
        }
        timerState = "running";
        updateToggleButton();
        intervalId = setInterval(() => {
          if (remainingSeconds <= 0) {
            stopInterval();
            timerState = "stopped";
            updateToggleButton();
            return;
          }
          remainingSeconds -= 1;
          updateTimerUI();
          if (remainingSeconds <= 0) {
            stopInterval();
            timerState = "stopped";
            updateToggleButton();
          }
        }, 1000);
      }

      function pauseCountdown() {
        stopInterval();
        timerState = "paused";
        updateToggleButton();
      }

      function resetCountdown() {
        stopInterval();
        remainingSeconds = TOTAL_SECONDS;
        timerState = "stopped";
        updateTimerUI();
        updateToggleButton();
      }

      toggleBtn.addEventListener("click", () => {
        if (timerState === "running") {
          pauseCountdown();
          return;
        }
        startCountdown();
      });

      resetBtn.addEventListener("click", resetCountdown);

      updateTimerUI();
      updateToggleButton();
    </script>
  </body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML.encode("utf-8"))


def main() -> None:
    server = HTTPServer(("127.0.0.1", 8000), Handler)
    print("http://127.0.0.1:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()
