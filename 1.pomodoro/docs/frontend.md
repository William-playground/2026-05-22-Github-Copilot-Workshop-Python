# フロントエンド モジュールドキュメント

## 概要

フロントエンドは HTML / CSS / JavaScript（バニラJS）で構成されています。

---

## HTML テンプレート

### `templates/index.html`

アプリケーションのメインページです。

**構造**

```html
<main class="app-shell">
  <section class="timer-card" aria-labelledby="app-title">
    <header class="app-header">
      <h1 id="app-title">ポモドーロタイマー</h1>
    </header>
    <p class="loading-message">タイマー画面を準備中です。</p>
  </section>
</main>
```

**読み込まれるリソース**

- `static/css/style.css` — スタイルシート
- `static/js/timer.js` — タイマーロジック

---

## CSS

### `static/css/style.css`

アプリケーション全体のスタイルを定義します。

**主なクラス**

| クラス名 | 説明 |
|---|---|
| `.app-shell` | 画面全体のラッパー。グリッドレイアウトで中央配置 |
| `.timer-card` | タイマーを表示するカード（最大幅 400px、角丸） |
| `.app-header` | アプリタイトル領域 |
| `.loading-message` | 読み込み中メッセージ（グレー、中央揃え） |

**カラーパレット**

| 変数/値 | 用途 |
|---|---|
| `#6f62c3` | 背景色（紫系） |
| `#f8f7fc` | カード背景色（オフホワイト） |
| `#30303a` | テキストカラー（ほぼ黒） |
| `#6b6876` | サブテキストカラー（グレー） |

**フォント**

`"Noto Sans JP"`, `"Yu Gothic"`, sans-serif（日本語対応フォントスタック）

---

## JavaScript

### `static/js/timer.js`

タイマーのロジックを担当するスクリプトです。

**現在の実装状況**

```javascript
console.log("Pomodoro timer assets loaded.");
```

現時点ではスタブ実装です。アセット読み込みの確認メッセージのみ出力します。タイマー機能は未実装です。
