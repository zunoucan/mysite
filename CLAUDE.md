# 東京23区 区立住宅アプリ

東京23区の区立住宅情報を取得・表示し、申請書自動記入と自動申請ができるAndroidアプリ。

## プロジェクト構成

```
mysite/
├── backend/          # Python FastAPI バックエンド
│   ├── app/
│   │   ├── main.py          # FastAPI エントリーポイント
│   │   ├── config.py        # 設定（DATABASE_URL 等）
│   │   ├── db.py            # SQLModel/SQLite
│   │   ├── seed.py          # 23区マスターデータ
│   │   ├── models/          # DBモデル（Ward, HousingListing）
│   │   ├── api/             # REST エンドポイント
│   │   │   ├── listings.py  # GET /api/v1/listings/
│   │   │   └── apply.py     # POST /api/v1/apply/
│   │   ├── scraper/         # 各区スクレイパー
│   │   │   └── wards/       # 区ごとのスクレイパー実装
│   │   ├── services/
│   │   │   ├── form_filler.py   # PDF申請書自動記入
│   │   │   └── auto_submit.py   # Playwright自動申請（プレミアム）
│   │   └── scheduler/
│   │       └── scrape_job.py    # 6時間ごとのスクレイピング
│   ├── requirements.txt
│   └── Dockerfile
├── android/          # Kotlin/Compose Androidアプリ
│   ├── app/src/main/java/com/tokyohousing/
│   │   ├── MainActivity.kt       # ナビゲーション
│   │   ├── TokyoHousingApp.kt    # Hilt Application
│   │   ├── data/
│   │   │   ├── api/HousingApi.kt        # Retrofit インターフェース
│   │   │   ├── model/HousingModels.kt   # データクラス
│   │   │   └── repository/              # リポジトリ層
│   │   ├── viewmodel/                   # ViewModel
│   │   ├── ui/screens/                  # Compose 画面
│   │   ├── billing/BillingManager.kt    # Google Play Billing
│   │   └── di/AppModule.kt             # Hilt DI
│   └── gradle/libs.versions.toml        # 依存関係バージョン管理
└── docker-compose.yml
```

## バックエンド起動

```bash
cd backend
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload
```

または Docker:

```bash
docker-compose up -d
```

## API エンドポイント

| Method | Path | 説明 |
|--------|------|------|
| GET | /api/v1/listings/ | 住宅一覧（区・家賃・間取りでフィルタ可） |
| GET | /api/v1/listings/{id} | 住宅詳細 |
| GET | /api/v1/listings/wards/ | 23区一覧 |
| POST | /api/v1/apply/fill-pdf | PDF申請書自動記入（無料） |
| POST | /api/v1/apply/submit | 自動申請（プレミアムはWebフォーム送信） |

## Androidアプリ

Android Studio で `android/` を開いてビルド。

**依存技術**: Jetpack Compose, Hilt, Room, Retrofit, DataStore, Google Play Billing

**画面構成**:
- `ListingsScreen` - 住宅一覧 + 区・家賃フィルター
- `DetailScreen` - 住宅詳細 + 申請書PDF記入ボタン + 自動申請ボタン
- `ProfileScreen` - ユーザー情報登録（DataStoreに保存）

## 課金設計

| 機能 | 無料 | プレミアム |
|------|------|----------|
| 住宅情報閲覧 | ✅ | ✅ |
| PDF申請書自動記入 | ✅ | ✅ |
| PDF自動記入後ダウンロード | ✅ | ✅ |
| Webフォーム自動送信 | ❌ | ✅ |

- 課金: Google Play In-App Billing (INAPP, product ID: `auto_submit_monthly`)
- 初期リリース: 全機能無料（premiumToken 検証を緩くしておく）
- 有料化時: Google Play Console でプロダクト有効化 + バックエンドの `_verify_premium_token()` を本実装に差し替え

## スクレイピング注意事項

- 各区Webサイトの利用規約を確認すること
- User-Agentにアプリ名と連絡先を含める（実装済み）
- スクレイピング間隔は6時間以上に設定（サーバー負荷配慮）
- ページ構造変更時はスクレイパーの更新が必要

## TODO（次のステップ）

- [ ] 各区スクレイパーの実URLでの動作確認・調整
- [ ] 申請書PDF座標マッピング（区ごとに異なるレイアウト対応）
- [ ] Google Play Console でアプリ登録 & Billing テスト
- [ ] Push通知: 新着住宅情報を FCM で通知
- [ ] お気に入り機能
- [ ] バックエンドのクラウドデプロイ（Cloud Run 推奨）
