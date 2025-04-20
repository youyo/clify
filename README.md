# clify

OpenAPI 仕様から CLI を自動生成するツール

## 概要

clify は、OpenAPI ファイルのパスを環境変数で指定して与えるだけで、その API の CLI として利用できるツールです。API の操作をコマンドラインから簡単に行うことができます。

## 特徴

- OpenAPI 3.0/3.1 仕様をサポート
- 環境変数で OpenAPI ファイルのパスを指定可能
- 各 API エンドポイントに対応するサブコマンドを自動生成
- パラメータに対応するオプションを自動生成
- JSON レスポンスの整形表示
- 認証情報の管理

## インストール

```bash
pip install clify
```

## 使い方

### 環境変数で OpenAPI ファイルを指定

```bash
export OPENAPI_FILE_PATH=/path/to/openapi.yaml
clify
```

### コマンドラインオプションで OpenAPI ファイルを指定

```bash
clify --openapi-file /path/to/openapi.yaml
```

### URL で OpenAPI ファイルを指定

```bash
clify --openapi-file https://example.com/api/openapi.yaml
```

### コマンド一覧の表示

```bash
clify --help
```

### 特定のコマンドのヘルプを表示

```bash
clify <command> --help
```

### API リクエストの実行

```bash
clify <command> [options]
```

### サーバー URL の指定

```bash
clify --server https://api.example.com <command> [options]
```

### 認証情報の指定

```bash
# Basic認証
clify --username user --password pass <command> [options]

# Bearerトークン
clify --token your-token <command> [options]

# APIキー
clify --api-key your-api-key <command> [options]
```

### JSON データの送信

```bash
clify <command> --data '{"key": "value"}'
# または
clify <command> --data @file.json
```

## 例

### OpenAPI ファイルの例

```yaml
openapi: 3.1.0
info:
  version: 1.0.0
  title: Example API
servers:
  - url: https://api.example.com/v1
paths:
  /users:
    get:
      summary: Get all users
      operationId: getUsers
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
      responses:
        200:
          description: Successful response
    post:
      summary: Create a new user
      operationId: createUser
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                email:
                  type: string
      responses:
        201:
          description: User created
```

### 生成される CLI

```bash
# ユーザー一覧を取得
clify get-users --limit 10

# 新しいユーザーを作成
clify create-user --data '{"name": "John", "email": "john@example.com"}'
```

## 開発

### 依存関係のインストール

```bash
pip install -e ".[dev]"
```

### テストの実行

```bash
pytest
```

### ビルド

```bash
python -m build
```

## ライセンス

MIT
