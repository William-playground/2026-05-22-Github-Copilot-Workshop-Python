# Pomodoro Timer App
#
# 視覚的フィードバックを強化したポモドーロタイマー。
#
# 機能:
#   - 円形プログレスバーの滑らかなアニメーション
#   - 残り時間に応じた色のグラデーション変化 (青 → 黄 → 赤)
#   - 集中時間中のパーティクル背景エフェクト
#
# 標準ライブラリ (tkinter) のみで動作するため、追加の依存関係は不要です。

import math
import random
import tkinter as tk

# --- 設定値 -------------------------------------------------------------

WORK_SECONDS = 25 * 60        # 集中時間 (デフォルト 25 分)
SHORT_BREAK_SECONDS = 5 * 60  # 短い休憩
LONG_BREAK_SECONDS = 15 * 60  # 長い休憩

# アニメーション用フレームレート (ミリ秒)
FRAME_INTERVAL_MS = 33  # ~30 FPS

# 円形プログレスバーの描画パラメータ
CANVAS_SIZE = 480
RING_MARGIN = 60
RING_WIDTH = 18

# 色のグラデーション (残り時間の進捗 0.0=開始, 1.0=終了)
# 青 (#3498db) → 黄 (#f1c40f) → 赤 (#e74c3c)
GRADIENT_STOPS = [
    (0.0, (52, 152, 219)),   # 青
    (0.5, (241, 196, 15)),   # 黄
    (1.0, (231, 76, 60)),    # 赤
]

# 背景色 (集中時間の暗めの背景)
BG_COLOR = "#1c1f2b"
TEXT_COLOR = "#ecf0f1"
MUTED_TEXT_COLOR = "#7f8c9b"


# --- ユーティリティ -----------------------------------------------------

def _lerp(a, b, t):
    """線形補間"""
    return a + (b - a) * t


def _lerp_color(c1, c2, t):
    """2 色間を線形補間する"""
    return tuple(int(round(_lerp(c1[i], c2[i], t))) for i in range(3))


def gradient_color(progress):
    """進捗 (0.0–1.0) に対応するグラデーション色を #RRGGBB で返す。

    GRADIENT_STOPS に基づき、青 → 黄 → 赤 の段階的な変化を表現する。
    """
    p = max(0.0, min(1.0, progress))
    for i in range(len(GRADIENT_STOPS) - 1):
        p0, c0 = GRADIENT_STOPS[i]
        p1, c1 = GRADIENT_STOPS[i + 1]
        if p <= p1:
            local = 0.0 if p1 == p0 else (p - p0) / (p1 - p0)
            r, g, b = _lerp_color(c0, c1, local)
            return f"#{r:02x}{g:02x}{b:02x}"
    r, g, b = GRADIENT_STOPS[-1][1]
    return f"#{r:02x}{g:02x}{b:02x}"


def format_time(seconds):
    """秒数を MM:SS に整形する"""
    seconds = max(0, int(math.ceil(seconds)))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


# --- パーティクル -------------------------------------------------------

class Particle:
    """集中時間中の背景演出に用いる浮遊パーティクル。"""

    __slots__ = ("x", "y", "vx", "vy", "radius", "life", "max_life", "item_id")

    def __init__(self, x, y, vx, vy, radius, life):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.life = life
        self.max_life = life
        self.item_id = None

    @classmethod
    def spawn(cls, width, height):
        """画面下部からゆっくり上昇するパーティクルを生成する。"""
        return cls(
            x=random.uniform(0, width),
            y=random.uniform(height * 0.85, height),
            vx=random.uniform(-0.3, 0.3),
            vy=random.uniform(-1.2, -0.4),
            radius=random.uniform(2.0, 5.0),
            life=random.uniform(2.5, 5.0),
        )

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.life -= dt

    @property
    def alive(self):
        return self.life > 0


# --- アプリケーション ---------------------------------------------------

class PomodoroApp:
    """円形プログレス + グラデーション + パーティクル背景のポモドーロタイマー。"""

    MODES = {
        "work": ("集中時間", WORK_SECONDS),
        "short_break": ("短い休憩", SHORT_BREAK_SECONDS),
        "long_break": ("長い休憩", LONG_BREAK_SECONDS),
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        self.mode = "work"
        self.total_seconds = self.MODES[self.mode][1]
        self.remaining_seconds = float(self.total_seconds)
        self.running = False
        self._last_tick_ms = None

        # 波紋エフェクト用 (集中開始/再開時に発生)
        self._ripples = []  # list of dicts {radius, max_radius, item_id}
        self._particles = []

        self._build_ui()
        self._draw_static()
        self._tick()  # アニメーションループ開始

    # -- UI 構築 --------------------------------------------------------

    def _build_ui(self):
        self.canvas = tk.Canvas(
            self.root,
            width=CANVAS_SIZE,
            height=CANVAS_SIZE,
            bg=BG_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack(padx=20, pady=(20, 10))

        mode_frame = tk.Frame(self.root, bg=BG_COLOR)
        mode_frame.pack(pady=(0, 8))
        self.mode_buttons = {}
        for key, (label, _) in self.MODES.items():
            btn = tk.Button(
                mode_frame,
                text=label,
                width=10,
                relief="flat",
                bg="#2c3142",
                fg=TEXT_COLOR,
                activebackground="#3a4159",
                activeforeground=TEXT_COLOR,
                command=lambda k=key: self.set_mode(k),
                cursor="hand2",
            )
            btn.pack(side=tk.LEFT, padx=4)
            self.mode_buttons[key] = btn

        ctrl_frame = tk.Frame(self.root, bg=BG_COLOR)
        ctrl_frame.pack(pady=(4, 20))
        self.start_button = tk.Button(
            ctrl_frame,
            text="開始",
            width=10,
            relief="flat",
            bg="#27ae60",
            fg="white",
            activebackground="#2ecc71",
            activeforeground="white",
            command=self.toggle,
            cursor="hand2",
        )
        self.start_button.pack(side=tk.LEFT, padx=6)
        self.reset_button = tk.Button(
            ctrl_frame,
            text="リセット",
            width=10,
            relief="flat",
            bg="#34495e",
            fg="white",
            activebackground="#46627f",
            activeforeground="white",
            command=self.reset,
            cursor="hand2",
        )
        self.reset_button.pack(side=tk.LEFT, padx=6)

        self._update_mode_buttons()

    def _draw_static(self):
        cx = cy = CANVAS_SIZE / 2
        r = CANVAS_SIZE / 2 - RING_MARGIN

        # 背景トラック (薄いグレーのリング)
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            outline="#2c3142",
            width=RING_WIDTH,
            tags=("track",),
        )

        # 進捗アーク (描画は _redraw_progress で随時更新)
        self.arc_id = self.canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=90,
            extent=-359.999,  # 360 だと描画されないので僅かに小さく
            style=tk.ARC,
            outline=gradient_color(0.0),
            width=RING_WIDTH,
            tags=("progress",),
        )

        # 残り時間テキスト
        self.time_text_id = self.canvas.create_text(
            cx, cy - 10,
            text=format_time(self.remaining_seconds),
            fill=TEXT_COLOR,
            font=("Helvetica", 48, "bold"),
        )
        # モードラベル
        self.mode_text_id = self.canvas.create_text(
            cx, cy + 40,
            text=self.MODES[self.mode][0],
            fill=MUTED_TEXT_COLOR,
            font=("Helvetica", 14),
        )

    # -- 状態操作 -------------------------------------------------------

    def set_mode(self, mode):
        if mode not in self.MODES:
            return
        self.mode = mode
        self.total_seconds = self.MODES[mode][1]
        self.remaining_seconds = float(self.total_seconds)
        self.running = False
        self._last_tick_ms = None
        self._particles.clear()
        self._clear_ripples()
        self.start_button.config(text="開始")
        self.canvas.itemconfigure(
            self.mode_text_id, text=self.MODES[mode][0]
        )
        self._update_mode_buttons()
        self._redraw_progress()

    def toggle(self):
        if self.remaining_seconds <= 0:
            self.remaining_seconds = float(self.total_seconds)
        self.running = not self.running
        self._last_tick_ms = None
        self.start_button.config(text="一時停止" if self.running else "再開")
        if self.running and self.mode == "work":
            self._spawn_ripple()

    def reset(self):
        self.running = False
        self.remaining_seconds = float(self.total_seconds)
        self._last_tick_ms = None
        self._particles.clear()
        self._clear_ripples()
        self.start_button.config(text="開始")
        self._redraw_progress()

    def _update_mode_buttons(self):
        for key, btn in self.mode_buttons.items():
            if key == self.mode:
                btn.config(bg="#3a4159")
            else:
                btn.config(bg="#2c3142")

    # -- 描画ヘルパ ------------------------------------------------------

    def _redraw_progress(self):
        progress = 0.0
        if self.total_seconds > 0:
            elapsed = self.total_seconds - self.remaining_seconds
            progress = max(0.0, min(1.0, elapsed / self.total_seconds))

        # 残り割合 (1.0 -> 円が満タン, 0.0 -> 消える)
        remaining_ratio = 1.0 - progress
        extent = -359.999 * remaining_ratio
        if abs(extent) < 0.01:
            extent = -0.01  # tk が描画を省略しないよう僅かに残す

        color = gradient_color(progress)
        self.canvas.itemconfigure(
            self.arc_id, extent=extent, outline=color,
        )
        self.canvas.itemconfigure(
            self.time_text_id, text=format_time(self.remaining_seconds)
        )

    # -- 背景エフェクト --------------------------------------------------

    def _spawn_ripple(self):
        cx = cy = CANVAS_SIZE / 2
        item = self.canvas.create_oval(
            cx, cy, cx, cy,
            outline=gradient_color(
                1.0 - self.remaining_seconds / max(1, self.total_seconds)
            ),
            width=2,
        )
        self.canvas.tag_lower(item, "track")
        self._ripples.append(
            {"radius": 0.0, "max_radius": CANVAS_SIZE * 0.7, "item_id": item}
        )

    def _clear_ripples(self):
        for r in self._ripples:
            self.canvas.delete(r["item_id"])
        self._ripples.clear()

    def _update_ripples(self, dt):
        for r in list(self._ripples):
            r["radius"] += 80 * dt  # px/sec
            if r["radius"] >= r["max_radius"]:
                self.canvas.delete(r["item_id"])
                self._ripples.remove(r)
                continue
            cx = cy = CANVAS_SIZE / 2
            rad = r["radius"]
            self.canvas.coords(
                r["item_id"], cx - rad, cy - rad, cx + rad, cy + rad
            )

    def _update_particles(self, dt):
        # 集中時間で実行中のみ新規生成
        if self.running and self.mode == "work":
            # フレームあたりおよそ 0–2 個生成
            if random.random() < 0.6:
                p = Particle.spawn(CANVAS_SIZE, CANVAS_SIZE)
                p.item_id = self.canvas.create_oval(
                    p.x - p.radius, p.y - p.radius,
                    p.x + p.radius, p.y + p.radius,
                    fill="#5dade2", outline="",
                )
                self.canvas.tag_lower(p.item_id, "track")
                self._particles.append(p)

        for p in list(self._particles):
            p.update(dt)
            if not p.alive or p.y < -10:
                self.canvas.delete(p.item_id)
                self._particles.remove(p)
                continue
            self.canvas.coords(
                p.item_id,
                p.x - p.radius, p.y - p.radius,
                p.x + p.radius, p.y + p.radius,
            )

    # -- メインループ ----------------------------------------------------

    def _tick(self):
        now_ms = self.root.tk.call("clock", "milliseconds")
        if self._last_tick_ms is None:
            dt = FRAME_INTERVAL_MS / 1000.0
        else:
            dt = max(0.0, (now_ms - self._last_tick_ms) / 1000.0)
        self._last_tick_ms = now_ms

        if self.running and self.remaining_seconds > 0:
            self.remaining_seconds = max(0.0, self.remaining_seconds - dt)
            if self.remaining_seconds <= 0:
                self.running = False
                self.start_button.config(text="開始")
                self._spawn_ripple()

        self._redraw_progress()
        self._update_ripples(dt)
        self._update_particles(dt)

        self.root.after(FRAME_INTERVAL_MS, self._tick)


def main():
    root = tk.Tk()
    PomodoroApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
