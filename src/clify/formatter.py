#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from typing import Any
import click
import requests


class ResponseFormatter:
    """
    APIレスポンスをフォーマットするクラス
    """

    def __init__(self, format_type: str = "json"):
        """
        初期化

        Args:
            format_type: フォーマットタイプ（json, yaml, tableなど）
        """
        self.format_type = format_type

    def format(self, response: requests.Response) -> str:
        """
        レスポンスをフォーマットする

        Args:
            response: APIレスポンス

        Returns:
            str: フォーマットされたレスポンス
        """
        # ステータスコードを表示
        status_line = f"Status: {response.status_code} {response.reason}"

        try:
            # JSONレスポンスの場合
            if "application/json" in response.headers.get("Content-Type", ""):
                data = response.json()
                return f"{status_line}\n\n{self.format_json(data)}"

            # テキストレスポンスの場合
            return f"{status_line}\n\n{response.text}"

        except ValueError:
            # JSONでない場合はテキストとして表示
            return f"{status_line}\n\n{response.text}"

    def format_json(self, data: Any) -> str:
        """
        JSONデータをフォーマットする

        Args:
            data: JSONデータ

        Returns:
            str: フォーマットされたJSON
        """
        if self.format_type == "json":
            return json.dumps(data, indent=2, ensure_ascii=False)

        elif self.format_type == "yaml":
            try:
                import yaml

                return yaml.dump(data, default_flow_style=False, allow_unicode=True)
            except ImportError:
                click.echo("YAMLフォーマットには'pyyaml'パッケージが必要です", err=True)
                return json.dumps(data, indent=2, ensure_ascii=False)

        elif self.format_type == "table":
            try:
                from tabulate import tabulate

                # データがリストの場合
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    headers = data[0].keys()
                    rows = [[item.get(key, "") for key in headers] for item in data]
                    return tabulate(rows, headers=headers, tablefmt="grid")

                # データが辞書の場合
                elif isinstance(data, dict):
                    rows = [[key, value] for key, value in data.items()]
                    return tabulate(rows, headers=["Key", "Value"], tablefmt="grid")

                # その他の場合はJSONとして表示
                return json.dumps(data, indent=2, ensure_ascii=False)

            except ImportError:
                click.echo(
                    "テーブルフォーマットには'tabulate'パッケージが必要です", err=True
                )
                return json.dumps(data, indent=2, ensure_ascii=False)

        # デフォルトはJSON
        return json.dumps(data, indent=2, ensure_ascii=False)

    def format_error(self, error_message: str) -> str:
        """
        エラーメッセージをフォーマットする

        Args:
            error_message: エラーメッセージ

        Returns:
            str: フォーマットされたエラーメッセージ
        """
        return f"Error: {error_message}"
