#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from typing import Any, Dict, Optional, Union

import click
import requests

from clify.formatter import ResponseFormatter
from clify.handler import CommandHandler


class APIRequestExecutor:
    """
    APIリクエストを実行するクラス
    """

    def __init__(self, handler: CommandHandler):
        """
        初期化

        Args:
            handler: コマンドハンドラー
        """
        self.handler = handler
        self.formatter = ResponseFormatter()

    def execute(self) -> str:
        """
        APIリクエストを実行する

        Returns:
            str: フォーマットされたレスポンス
        """
        try:
            # リクエストを実行
            response = self._send_request()

            # レスポンスをフォーマット
            formatted_response = self.formatter.format(response)
            return formatted_response

        except requests.RequestException as e:
            # リクエストエラーの場合
            error_message = f"リクエストエラー: {str(e)}"
            click.echo(error_message, err=True)
            formatted_error = self.formatter.format_error(error_message)
            return formatted_error

        except Exception as e:
            # その他のエラーの場合
            error_message = f"エラー: {str(e)}"
            click.echo(error_message, err=True)
            formatted_error = self.formatter.format_error(error_message)
            return formatted_error

    def _send_request(self) -> requests.Response:
        """
        HTTPリクエストを送信する

        Returns:
            requests.Response: レスポンス

        Raises:
            requests.RequestException: リクエストに失敗した場合
        """
        # リクエストパラメータを準備
        url = self.handler.url
        method = self.handler.method
        headers = self.handler.headers
        params = self.handler.query_params
        json_data = self.handler.body

        # デバッグ情報を表示（--verboseオプションが指定されている場合）
        if self.handler.params.get("verbose"):
            click.echo(f"URL: {url}", err=True)
            click.echo(f"Method: {method}", err=True)
            click.echo(f"Headers: {json.dumps(headers, indent=2)}", err=True)
            click.echo(f"Query Parameters: {json.dumps(params, indent=2)}", err=True)
            if json_data:
                click.echo(f"Request Body: {json.dumps(json_data, indent=2)}", err=True)

        # リクエストを送信
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_data,
            timeout=30,  # タイムアウト30秒
        )

        # レスポンスステータスコードをチェック
        response.raise_for_status()

        return response
