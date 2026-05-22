"""Pomodoro timer demo app for workshop phases."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


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
        font-family: system-ui, -apple-system, sans-serif;
        background: #f6f7fb;
      }
      .timer {
        position: relative;
        width: 240px;
        height: 240px;
      }
      .ring {
        width: 100%;
        height: 100%;
        transform: rotate(-90deg);
      }
      .track {
        fill: none;
        stroke: #e4e7f2;
        stroke-width: 12;
      }
      .progress {
        fill: none;
        stroke: #4f46e5;
        stroke-width: 12;
        stroke-linecap: round;
        transition: stroke-dashoffset 0.2s linear;
      }
      #time-display {
        position: absolute;
        inset: 0;
        display: grid;
        place-items: center;
        font-size: 3rem;
        font-weight: 700;
        color: #1f2937;
      }
    </style>
  </head>
  <body>
    <main class="timer" aria-label="Pomodoro timer">
      <svg class="ring" viewBox="0 0 120 120" aria-hidden="true">
        <circle class="track" cx="60" cy="60" r="54"></circle>
        <circle id="progress-ring" class="progress" cx="60" cy="60" r="54"></circle>
      </svg>
      <div id="time-display" aria-live="polite"></div>
    </main>

    <script>
      const MODES = {
        work: { label: "work", seconds: 25 * 60 },
        shortBreak: { label: "shortBreak", seconds: 5 * 60 },
        longBreak: { label: "longBreak", seconds: 15 * 60 },
      };

      const state = {
        mode: "work",
        remainingSeconds: MODES.work.seconds,
        totalSeconds: MODES.work.seconds,
      };

      const progressRing = document.getElementById("progress-ring");
      const timeDisplay = document.getElementById("time-display");
      const radius = Number(progressRing.getAttribute("r"));
      const circumference = 2 * Math.PI * radius;

      function formatTime(totalSeconds) {
        const minutes = Math.floor(totalSeconds / 60)
          .toString()
          .padStart(2, "0");
        const seconds = (totalSeconds % 60).toString().padStart(2, "0");
        return `${minutes}:${seconds}`;
      }

      function renderProgress(remainingSeconds, totalSeconds) {
        const ratio =
          totalSeconds > 0
            ? Math.max(0, Math.min(1, remainingSeconds / totalSeconds))
            : 0;
        progressRing.style.strokeDasharray = `${circumference}`;
        progressRing.style.strokeDashoffset = `${circumference * (1 - ratio)}`;
      }

      function render() {
        timeDisplay.textContent = formatTime(state.remainingSeconds);
        renderProgress(state.remainingSeconds, state.totalSeconds);
      }

      render();
    </script>
  </body>
</html>
"""


class TimerPageHandler(BaseHTTPRequestHandler):
    """Serve a tiny single-page app for the Pomodoro timer UI."""

    def do_GET(self) -> None:  # noqa: N802
        if self.path not in ("/", "/index.html"):
            self.send_error(404, "Not Found")
            return

        body = HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 8000), TimerPageHandler)
    print("Pomodoro app: http://127.0.0.1:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()
