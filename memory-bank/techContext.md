# 技術コンテキスト: clify

## 使用技術

### 言語とバージョン

- Python 3.10 以上（3.12 から変更）

### 主要ライブラリ

- **Click**: CLI インターフェース構築
- **PyYAML**: YAML 形式の OpenAPI ファイル解析
- **jsonschema**: JSON スキーマバリデーション
- **requests**: HTTP リクエスト実行
- **pytest**: テスト実装

### 開発ツール

- **setuptools_scm**: バージョン管理
- **uv**: パッケージ管理（新規追加）
- **black**: コードフォーマット
- **isort**: インポート順序整理
- **flake8**: コード品質チェック
- **mypy**: 型チェック

## 開発環境設定

### プロジェクト構造

- src-layout を採用

```
clify/
├── pyproject.toml
├── setup.py
├── LICENSE
├── README.md
├── .gitignore
├── .github/
│   └── workflows/
│       └── publish.yaml
├── tests/
│   ├── conftest.py
│   ├── test_cli.py
│   ├── test_parser.py
│   ├── test_generator.py
│   ├── test_handler.py
│   ├── test_request.py
│   └── test_formatter.py
└── src/
    └── clify/
        ├── __init__.py
        ├── cli.py
        ├── parser.py
        ├── generator.py
        ├── handler.py
        ├── request.py
        └── formatter.py
```

### 開発環境

- Python 3.10 以上
- 仮想環境（.venv）
- uv パッケージマネージャー

## 技術的制約

### OpenAPI 対応

- OpenAPI 3.0/3.1 仕様をサポート
- JSON/YAML 形式の OpenAPI ファイルに対応

### 認証方法

- 基本認証
- API キー認証
- OAuth2.0（クライアントクレデンシャルフロー）

### HTTP メソッド

- GET, POST, PUT, DELETE, PATCH, HEAD をサポート

## 依存関係

### 必須依存関係

```
click>=8.0.0
pyyaml>=6.0
jsonschema>=4.0.0
requests>=2.25.0
```

### 開発依存関係

```
pytest>=7.0.0
black>=23.0.0
isort>=5.0.0
flake8>=6.0.0
mypy>=1.0.0
```

### オプション依存関係

```
tabulate>=0.9.0  # テーブル形式出力
pygments>=2.10.0  # シンタックスハイライト
```

## パッケージング

### PyPI 公開

- setuptools_scm を使用したバージョン管理
- GitHub Actions による自動パブリッシュ

### インストール方法

```bash
pip install clify
```

または

```bash
uv pip install clify
```

### 開発用インストール

```bash
uv pip install -e .
```

### エントリーポイント

```
clify = clify.cli:main
```

## 実装の詳細

### コマンド生成の流れ

1. OpenAPI ファイルを解析（parser.py）
2. API エンドポイント情報を抽出
3. Click を使用して CLI コマンドを生成（generator.py）
4. コマンドライン引数を解析（cli.py）
5. API リクエストを実行（request.py）
6. レスポンスを整形して表示（formatter.py）

### デバッグ機能

- cli.py と generator.py にデバッグ情報を表示する機能を追加
- 生成されたコマンドの一覧表示
- コマンドライン引数の表示
