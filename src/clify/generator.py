#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from typing import Any, Callable, Dict, List, Optional, Union

import click

from clify.handler import CommandHandler
from clify.request import APIRequestExecutor


class CLIGenerator:
    """
    OpenAPI仕様からCLIコマンドを生成するクラス
    """

    def __init__(self, spec: Dict[str, Any]):
        """
        初期化

        Args:
            spec: OpenAPI仕様
        """
        self.spec = spec
        self.title = spec.get("info", {}).get("title", "API")
        self.description = spec.get("info", {}).get("description", "")
        self.servers = spec.get("servers", [])
        self.default_server = self.servers[0]["url"] if self.servers else ""
        self.security_schemes = self._get_security_schemes()

    def generate(self) -> Callable:
        """
        CLIコマンドを生成する

        Returns:
            Callable: 生成されたCLIコマンド
        """

        # ルートコマンドグループを作成
        @click.group(help=self.description)
        @click.option(
            "--server",
            "-s",
            default=self.default_server,
            help="APIサーバーのURL",
        )
        @click.pass_context
        def dynamic_cli(ctx: click.Context, server: str) -> None:
            ctx.ensure_object(dict)
            ctx.obj["server"] = server

        # 認証オプションを追加
        self._add_auth_options(dynamic_cli)

        # パスごとにサブコマンドを生成
        paths = self.spec.get("paths", {})
        click.echo(f"利用可能なパス: {list(paths.keys())}", err=True)

        for path, path_item in paths.items():
            click.echo(f"パス '{path}' のメソッド: {list(path_item.keys())}", err=True)
            for method, operation in path_item.items():
                if method in ["get", "post", "put", "delete", "patch", "head"]:
                    operation_id = operation.get("operationId", "")
                    command_name = (
                        self._convert_to_command_name(operation_id)
                        if operation_id
                        else f"{method}{path.replace('/', '_')}"
                    )
                    click.echo(
                        f"コマンド '{command_name}' を生成します（{method} {path}）",
                        err=True,
                    )
                    self._create_command(dynamic_cli, path, method, operation)

        # 生成されたコマンドの一覧を表示
        click.echo("生成されたコマンド:", err=True)
        for command in dynamic_cli.commands:
            click.echo(f"- {command}", err=True)

        return dynamic_cli

    def _get_security_schemes(self) -> Dict[str, Dict[str, Any]]:
        """
        セキュリティスキームを取得する

        Returns:
            Dict[str, Dict[str, Any]]: セキュリティスキーム情報
        """
        components = self.spec.get("components", {})
        return components.get("securitySchemes", {})

    def _add_auth_options(self, command: click.Group) -> None:
        """
        認証オプションを追加する

        Args:
            command: コマンドグループ
        """
        for scheme_name, scheme in self.security_schemes.items():
            scheme_type = scheme.get("type", "")

            if scheme_type == "apiKey":
                command = click.option(
                    f"--{scheme_name}",
                    help=f"APIキー ({scheme.get('name', '')})",
                    envvar=f"CLIFY_{scheme_name.upper()}",
                )(command)

            elif scheme_type == "http":
                scheme_scheme = scheme.get("scheme", "")
                if scheme_scheme == "basic":
                    command = click.option(
                        "--username",
                        help="Basic認証のユーザー名",
                        envvar="CLIFY_USERNAME",
                    )(command)
                    command = click.option(
                        "--password",
                        help="Basic認証のパスワード",
                        envvar="CLIFY_PASSWORD",
                    )(command)
                elif scheme_scheme == "bearer":
                    command = click.option(
                        "--token",
                        help="Bearerトークン",
                        envvar="CLIFY_TOKEN",
                    )(command)

            elif scheme_type == "oauth2":
                command = click.option(
                    "--token",
                    help="OAuth2トークン",
                    envvar="CLIFY_TOKEN",
                )(command)

    def _create_command(
        self, parent: click.Group, path: str, method: str, operation: Dict[str, Any]
    ) -> None:
        """
        コマンドを作成する

        Args:
            parent: 親コマンドグループ
            path: APIパス
            method: HTTPメソッド
            operation: オペレーション情報
        """
        # コマンド名を生成
        operation_id = operation.get("operationId")
        if operation_id:
            command_name = self._convert_to_command_name(operation_id)
        else:
            # operationIdがない場合はパスとメソッドから生成
            path_part = re.sub(r"[{}]", "", path.replace("/", "_"))
            command_name = f"{method}{path_part}"
            command_name = self._convert_to_command_name(command_name)

        # コマンドの説明を取得
        summary = operation.get("summary", "")
        description = operation.get("description", "")
        help_text = f"{summary}\n\n{description}" if description else summary

        # パラメータを取得
        parameters = operation.get("parameters", [])

        # リクエストボディを取得
        request_body = operation.get("requestBody", {})

        # コマンド関数を定義
        @click.command(name=command_name, help=help_text)
        @click.pass_context
        def command_func(ctx: click.Context, **kwargs: Any) -> None:
            # コマンドハンドラーを作成
            handler = CommandHandler(
                server=ctx.obj["server"],
                path=path,
                method=method,
                operation=operation,
                params=kwargs,
            )

            # APIリクエストを実行
            executor = APIRequestExecutor(handler)
            result = executor.execute()

            # 結果を表示
            click.echo(result)

        # パラメータごとにオプションを追加
        for param in parameters:
            param_name = param.get("name", "")
            param_in = param.get("in", "")
            param_required = param.get("required", False)
            param_schema = param.get("schema", {})
            param_description = param.get("description", "")

            # パラメータ名をコマンドライン引数名に変換
            option_name = self._convert_to_option_name(param_name)

            # オプションを追加
            option_decl = f"--{option_name}"
            if param_in == "path":
                # パスパラメータは必須
                command_func = click.argument(option_name)(command_func)
            else:
                # クエリパラメータやヘッダーはオプション
                command_func = click.option(
                    option_decl,
                    required=param_required,
                    help=param_description,
                )(command_func)

        # リクエストボディがある場合
        if request_body:
            content = request_body.get("content", {})
            for content_type, content_schema in content.items():
                if "application/json" in content_type:
                    command_func = click.option(
                        "--data",
                        "-d",
                        help="JSONデータ（文字列またはファイルパス@file.json）",
                    )(command_func)
                    break

        # 親コマンドグループに追加
        parent.add_command(command_func)

    def _convert_to_command_name(self, name: str) -> str:
        """
        operationIdをコマンド名に変換する

        Args:
            name: 変換元の名前

        Returns:
            str: コマンド名
        """
        # camelCaseをケバブケースに変換
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1-\2", name)
        kebab = re.sub("([a-z0-9])([A-Z])", r"\1-\2", s1).lower()

        # アンダースコアとドットをハイフンに変換
        kebab = kebab.replace("_", "-").replace(".", "-")

        # 特殊文字を削除（アンダースコアとドットは既に変換済み）
        kebab = re.sub(r"[^a-z0-9-]", "", kebab)

        # 連続するハイフンを1つに
        kebab = re.sub(r"-+", "-", kebab)

        # 先頭と末尾のハイフンを削除
        return kebab.strip("-")

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
