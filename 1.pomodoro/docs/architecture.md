# アーキテクチャ概要

## 構成

ポモドーロタイマーは、Flask をベースとした最小構成の Web アプリケーションです。

```
1.pomodoro/
├── app.py              # Flask アプリケーションエントリーポイント
├── requirements.txt    # Python 依存パッケージ
├── templates/
│   └── index.html      # メインページ HTML テンプレート
└── static/
    ├── css/
    │   └── style.css   # スタイルシート
    └── js/
        └── timer.js    # タイマーロジック（JavaScript）
```

## 技術スタック

| 区分 | 技術 |
|------|------|
| バックエンド | Python / Flask (>=3.0, <4.0) |
| フロントエンド | HTML / CSS / JavaScript（バニラJS） |
| テンプレートエンジン | Jinja2（Flask 組み込み） |

## アプリケーション構造

### バックエンド（`app.py`）

- `Flask(__name__)` でアプリケーションインスタンスを生成
- ルート `/` に対して `index.html` テンプレートをレンダリングして返す
- デバッグモード有効 (`debug=True`) で起動

### フロントエンド

- タイマーの状態管理・UI 操作はすべてクライアントサイド（JavaScript）で行う
- サーバーとの通信は現時点では不要

## 起動方法

```bash
cd 1.pomodoro
python3 app.py
```

デフォルトで `http://127.0.0.1:5000` で起動します。
