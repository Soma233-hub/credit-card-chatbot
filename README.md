# クレジットカードユーザー分析チャットボット

クレジットカード会社のマーケティング部門向けに開発されたチャットボットです。データベースに登録されたクレジットカードユーザーの情報を自然言語で検索・分析することができます。

## 機能

- ユーザーの購入履歴や行動パターンの分析
- 高額・中額・少額利用者の分類と集計
- 特定カテゴリでの購入履歴分析
- ユーザーの活動状況（アクティブ・休眠）の分析
- 時系列データの可視化

## 技術スタック

- [Langchain](https://github.com/hwchase17/langchain): 自然言語処理とSQLクエリ生成
- [SQLite](https://www.sqlite.org/): データベース（MCPで他のDBにも対応可能）
- [OpenAI API](https://openai.com/): GPT-3.5 Turboを使用した自然言語理解
- [Chainlit](https://github.com/Chainlit/chainlit): チャットインターフェース
- [SQLAlchemy](https://www.sqlalchemy.org/): データベース接続
- [Matplotlib](https://matplotlib.org/): データ可視化

## セットアップ方法

### 前提条件

- Python 3.9以上
- OpenAI APIキー

### インストール手順

1. リポジトリをクローン

```bash
git clone https://github.com/yourusername/credit-card-chatbot.git
cd credit-card-chatbot
```

2. 仮想環境を作成して有効化

```bash
python -m venv .venv
source .venv/bin/activate  # Linuxの場合
# または
venv\Scripts\activate  # Windowsの場合
```

3. 依存パッケージをインストール

```bash
pip install -r requirements.txt
```

4. 環境変数の設定

`.env`ファイルを作成し、以下の内容を設定します：

```
OPENAI_API_KEY=your_openai_api_key_here
DB_TYPE=sqlite  # または mysql, postgresql など
DB_PATH=db/data/credit_card_users.db  # SQLiteの場合
# 他のDBを使用する場合は以下も設定
# DB_HOST=localhost
# DB_PORT=3306
# DB_NAME=credit_card_db
# DB_USER=username
# DB_PASSWORD=password
```

### データベースのセットアップ

1. データベーススキーマの作成

```bash
python db/create_schema.py
```

2. デモデータの生成（約10,000ユーザー、1年分のデータ）

```bash
python db/generate_demo_data.py
```

## 使用方法

1. Chainlitアプリケーションを起動

```bash
chainlit run app.py --port 8001
```

2. ブラウザで http://localhost:8001 にアクセス

3. チャットインターフェースで質問を入力

### 質問例

以下のような質問を試してみてください：

- ここ半年間の購入額の合計を参考にしてユーザを高額利用者、中額利用者、少額利用者の３カテゴリにわけてそれぞれのカテゴリの人数を出してほしい。退会済みユーザは除外すること。
- ここ3ヶ月間で美容カテゴリで1000円以上の購入履歴が一度でもある人数を出してほしい。退会済みユーザは除外すること。
- ペット好きかつ旅行好きと思われるユーザを、アクティブと休眠とでそれぞれ人数出して欲しい。退会済みユーザは当然除外すること。
- ここ半年間の解約者数の推移を数値で教えて
- ここ半年間のアクティブ者数の推移を数値で教えて
- ここ半年間のアクティブ者の月別平均購入額の推移を数値で教えて

## プロジェクト構造

```
.
├── app.py                  # Chainlitアプリケーションのメインファイル
├── chainlit.md             # Chainlitの説明ファイル
├── requirements.txt        # 依存パッケージリスト
├── .env                    # 環境変数設定ファイル
├── db/                     # データベース関連ファイル
│   ├── create_schema.py    # データベーススキーマ作成スクリプト
│   ├── generate_demo_data.py # デモデータ生成スクリプト
│   └── data/               # データベースファイル保存ディレクトリ
└── src/                    # ソースコード
    ├── chatbot.py          # チャットボットのメインロジック
    ├── db_connection.py    # データベース接続モジュール（MCP実装）
    ├── models.py           # SQLAlchemyモデル
    └── query_generator.py  # SQLクエリ生成モジュール
```

## データベース構造

### usersテーブル
- user_id: ユーザーID（主キー）
- name: ユーザー名
- email: メールアドレス
- registration_date: 登録日
- is_active: アクティブフラグ（1=アクティブ、0=非アクティブ）
- is_dormant: 休眠フラグ（1=休眠、0=非休眠）
- is_cancelled: 退会フラグ（1=退会済み、0=未退会）
- last_activity_date: 最終アクティビティ日

### categoriesテーブル
- category_id: カテゴリID（主キー）
- category_name: カテゴリ名

### purchasesテーブル
- purchase_id: 購入ID（主キー）
- user_id: ユーザーID（外部キー）
- amount: 購入金額
- purchase_date: 購入日
- category_id: カテゴリID（外部キー）

## カスタマイズ方法

### 別のデータベースへの接続

`.env`ファイルの`DB_TYPE`と関連設定を変更することで、MySQL、PostgreSQLなど他のデータベースに接続できます。

### OpenAIモデルの変更

`src/chatbot.py`と`src/query_generator.py`の`model_name`パラメータを変更することで、別のOpenAIモデルを使用できます。

## ライセンス

MIT

## 注意事項

- このアプリケーションはデモ用です。実際の運用では、セキュリティ対策やエラーハンドリングを強化してください。
- OpenAI APIの使用には料金が発生します。使用量に注意してください。
