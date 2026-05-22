# データモデル仕様

## 概要

現在の実装では、サーバーサイドのデータモデル（データベースやスキーマ定義）は存在しません。

タイマーの状態はすべてクライアントサイド（ブラウザのメモリ上）で管理されます。

## フロントエンド上の状態（概念モデル）

`static/js/timer.js` で管理される状態は現時点では未実装（スタブ）ですが、将来的に以下の情報を保持することが想定されます。

| フィールド | 型 | 説明 |
|---|---|---|
| remainingSeconds | number | 残り秒数 |
| isRunning | boolean | タイマーが動作中かどうか |
| currentPhase | string | 現在のフェーズ（`work` / `shortBreak` / `longBreak`） |
| completedPomodoros | number | 完了したポモドーロ数 |

> **備考**: 現在 `timer.js` はスタブ（`console.log` のみ）であり、上記の状態管理は実装されていません。
