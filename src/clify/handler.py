#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import re
from typing import Any, Dict, List, Optional, Union

import click


class CommandHandler:
    """
    コマンドハンドラークラス
    APIリクエストの構築と実行を担当
    """

    def __init__(
        self,
        server: str,
        path: str,
        method: str,
        operation: Dict[str, Any],
        params: Dict[str, Any],
    ):
        """
        初期化

        Args:
            server: APIサーバーのURL
            path: APIパス
            method: HTTPメソッド
            operation: オペレーション情報
            params: コマンドラインパラメータ
        """
        self.server = server
        self.path = path
        self.method = method.upper()
        self.operation = operation
        self.params = params
        self.url = self._build_url()
        self.headers = self._build_headers()
        self.query_params = self._build_query_params()
        self.body = self._build_body()

    def _build_url(self) -> str:
        """
        URLを構築する

        Returns:
            str: 構築されたURL
        """
        # サーバーURLの末尾のスラッシュを削除
        server = self.server.rstrip("/")

        # パスの先頭のスラッシュを削除
        path = self.path.lstrip("/")

        # パスパラメータを置換
        path_with_params = self._replace_path_params(path)

        # URLを構築
        return f"{server}/{path_with_params}"

    def _replace_path_params(self, path: str) -> str:
        """
        パスパラメータを置換する

        Args:
            path: APIパス

        Returns:
            str: パラメータが置換されたパス
        """
        # パスパラメータを検出
        path_params = re.findall(r"{([^}]+)}", path)

        # パスパラメータを置換
        for param in path_params:
            # パラメータ名をコマンドライン引数名に変換
            option_name = self._convert_to_option_name(param)

            # パラメータ値を取得
            value = self.params.get(option_name)

            if value is None:
                raise click.UsageError(f"パスパラメータ '{param}' が指定されていません")

            # パラメータを置換
            path = path.replace(f"{{{param}}}", str(value))

        return path

    def _build_headers(self) -> Dict[str, str]:
        """
        HTTPヘッダーを構築する

        Returns:
            Dict[str, str]: HTTPヘッダー
        """
        headers = {
            "User-Agent": "clify/1.0.0",
        }

        # Content-Typeを設定
        if self.method in ["POST", "PUT", "PATCH"] and self.params.get("data"):
            headers["Content-Type"] = "application/json"

        # ヘッダーパラメータを追加
        parameters = self.operation.get("parameters", [])
        for param in parameters:
            if param.get("in") == "header":
                param_name = param.get("name", "")
                option_name = self._convert_to_option_name(param_name)
                value = self.params.get(option_name)

                if value is not None:
                    headers[param_name] = str(value)

        # 認証ヘッダーを追加
        self._add_auth_headers(headers)

        return headers

    def _add_auth_headers(self, headers: Dict[str, str]) -> None:
        """
        認証ヘッダーを追加する

        Args:
            headers: HTTPヘッダー
        """
        # Basic認証
        username = self.params.get("username")
        password = self.params.get("password")
        if username and password:
            import base64

            auth = base64.b64encode(f"{username}:{password}".encode()).decode()
            headers["Authorization"] = f"Basic {auth}"

        # Bearerトークン
        token = self.params.get("token")
        if token and "Authorization" not in headers:
            headers["Authorization"] = f"Bearer {token}"

        # APIキー
        for param_name, param_value in self.params.items():
            if param_name not in ["username", "password", "token"] and param_value:
                # APIキーの場所を確認（ヘッダーかクエリパラメータか）
                components = self.operation.get("components", {})
                security_schemes = components.get("securitySchemes", {})

                for scheme_name, scheme in security_schemes.items():
                    if scheme_name == param_name and scheme.get("type") == "apiKey":
                        in_value = scheme.get("in", "")
                        name = scheme.get("name", "")

                        if in_value == "header" and name:
                            headers[name] = param_value

    def _build_query_params(self) -> Dict[str, str]:
        """
        クエリパラメータを構築する

        Returns:
            Dict[str, str]: クエリパラメータ
        """
        query_params = {}

        # クエリパラメータを追加
        parameters = self.operation.get("parameters", [])
        for param in parameters:
            if param.get("in") == "query":
                param_name = param.get("name", "")
                option_name = self._convert_to_option_name(param_name)
                value = self.params.get(option_name)

                if value is not None:
                    query_params[param_name] = str(value)

        # APIキーがクエリパラメータの場合
        components = self.operation.get("components", {})
        security_schemes = components.get("securitySchemes", {})

        for scheme_name, scheme in security_schemes.items():
            if scheme.get("type") == "apiKey" and scheme.get("in") == "query":
                name = scheme.get("name", "")
                value = self.params.get(scheme_name)

                if name and value:
                    query_params[name] = value

        return query_params

    def _build_body(self) -> Optional[Dict[str, Any]]:
        """
        リクエストボディを構築する

        Returns:
            Optional[Dict[str, Any]]: リクエストボディ
        """
        if self.method not in ["POST", "PUT", "PATCH"]:
            return None

        data = self.params.get("data")
        if not data:
            return None

        # ファイルからJSONを読み込む
        if data.startswith("@"):
            file_path = data[1:]
            if not os.path.exists(file_path):
                raise click.UsageError(f"ファイルが見つかりません: {file_path}")

            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    raise click.UsageError(f"JSONの解析に失敗しました: {file_path}")

        # 文字列からJSONを解析
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            raise click.UsageError("JSONの解析に失敗しました")

    def _convert_to_option_name(self, name: str) -> str:
        """
        パラメータ名をオプション名に変換する

        Args:
            name: パラメータ名

        Returns:
            str: オプション名
        """
        # camelCaseをケバブケースに変換
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1-\2", name)
        kebab = re.sub("([a-z0-9])([A-Z])", r"\1-\2", s1).lower()

        # 特殊文字をハイフンに変換
        kebab = re.sub(r"[^a-z0-9-]", "-", kebab)

        # 連続するハイフンを1つに
        kebab = re.sub(r"-+", "-", kebab)

        # 先頭と末尾のハイフンを削除
        return kebab.strip("-")
