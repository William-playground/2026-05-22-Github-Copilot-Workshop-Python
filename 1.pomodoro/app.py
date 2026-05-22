import streamlit as st


st.set_page_config(page_title="ポモドーロタイマー", page_icon="🍅", layout="centered")

st.markdown(
    """
    <style>
      .app-wrap {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
      }
      .timer-card {
        width: 100%;
        max-width: 420px;
        background: #ffffff;
        border-radius: 20px;
        padding: 28px 24px;
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.12);
        text-align: center;
      }
      .title {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 12px;
      }
      .status {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.9rem;
        font-weight: 600;
        color: #b45309;
        background: #fef3c7;
        margin-bottom: 20px;
      }
      .ring {
        width: 220px;
        height: 220px;
        margin: 0 auto 20px;
        border-radius: 50%;
        background: conic-gradient(#f97316 0deg 216deg, #fde7da 216deg 360deg);
        display: grid;
        place-items: center;
      }
      .ring-inner {
        width: 176px;
        height: 176px;
        border-radius: 50%;
        background: #ffffff;
        display: grid;
        place-items: center;
        color: #111827;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: 0.02em;
      }
      .actions {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
        margin-bottom: 20px;
      }
      .btn {
        border-radius: 10px;
        padding: 10px 0;
        font-weight: 700;
        border: 0;
      }
      .btn-start {
        color: #ffffff;
        background: #f97316;
      }
      .btn-reset {
        color: #374151;
        background: #f3f4f6;
      }
      .progress-panel {
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 14px 12px;
        text-align: left;
      }
      .progress-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #374151;
        margin-bottom: 10px;
      }
      .progress-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
      }
      .metric-label {
        font-size: 0.82rem;
        color: #6b7280;
        margin-bottom: 2px;
      }
      .metric-value {
        font-size: 1.1rem;
        font-weight: 700;
        color: #111827;
      }
      @media (max-width: 480px) {
        .timer-card {
          padding: 22px 16px;
        }
        .title {
          font-size: 1.5rem;
        }
        .ring {
          width: 180px;
          height: 180px;
        }
        .ring-inner {
          width: 142px;
          height: 142px;
          font-size: 2rem;
        }
      }
    </style>
    <div class="app-wrap">
      <div class="timer-card">
        <div class="title">ポモドーロタイマー</div>
        <div class="status">作業中</div>
        <div class="ring">
          <div class="ring-inner">25:00</div>
        </div>
        <div class="actions">
          <button class="btn btn-start">開始</button>
          <button class="btn btn-reset">リセット</button>
        </div>
        <div class="progress-panel">
          <div class="progress-title">今日の進捗</div>
          <div class="progress-grid">
            <div>
              <div class="metric-label">完了数</div>
              <div class="metric-value">0 回</div>
            </div>
            <div>
              <div class="metric-label">集中時間</div>
              <div class="metric-value">0 分</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
