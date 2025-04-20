#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from typing import Optional, List, Dict, Any

import click

from clify.parser import OpenAPIParser
from clify.generator import CLIGenerator


class DynamicCLI(click.MultiCommand):
    """
    OpenAPI仕様から動的にコマンドをロードするMultiCommandクラス
    """

    def __init__(self, openapi_file: Optional[str] = None, **attrs: Any):
        self.openapi_file = openapi_file or os.getenv("OPENAPI_FILE_PATH")
        self.generated_cli: Optional[click.Group] = None
        self.spec: Optional[Dict[str, Any]] = None  # specを保持するように変更

        if not self.openapi_file:
            # OpenAPIファイルが指定されていない場合は、通常のヘルプを表示するためのダミーとして初期化
            # name引数とhelp引数を削除
            super().__init__(**attrs)
            return

        try:
            click.echo(f"OpenAPIファイル: {self.openapi_file}", err=True)
            parser = OpenAPIParser(self.openapi_file)
            self.spec = parser.parse()  # specをインスタンス変数に格納
            click.echo("OpenAPIファイルの解析が完了しました", err=True)

            generator = CLIGenerator(self.spec)  # specを渡す
            self.generated_cli = generator.generate()
            click.echo("CLIの生成が完了しました", err=True)

            # 親クラスのコンストラクタを呼び出す (ヘルプテキストなどを設定)
            # OpenAPIのinfoから説明を取得
            help_text = self.spec.get("info", {}).get(
                "description", "Generated CLI from OpenAPI spec"
            )
            # name引数とhelp引数を削除
            super().__init__(**attrs)

        except Exception as e:
            click.echo(
                f"エラー: OpenAPIファイルの処理中にエラーが発生しました: {str(e)}",
                err=True,
            )
            # エラーが発生した場合でもMultiCommandとして初期化するが、コマンドは空にする
            self.generated_cli = click.Group(name="clify")  # 空のGroup
            # name引数とhelp引数を削除
            super().__init__(**attrs)
            # ここで sys.exit(1) を呼ぶと MultiCommand の初期化が完了しない可能性があるためコメントアウト
            # sys.exit(1)

    def list_commands(self, ctx: click.Context) -> List[str]:
        """
        利用可能なコマンドのリストを返す
        """
        if self.generated_cli:
            return sorted(self.generated_cli.commands.keys())
        return []

    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        """
        指定されたコマンド名のコマンドオブジェクトを返す
        """
        if self.generated_cli:
            return self.generated_cli.commands.get(cmd_name)
        return None


# --- cli 関数の修正 ---
# @click.group(invoke_without_command=True) # 古いデコレータを削除
@click.command(cls=DynamicCLI)  # 新しいMultiCommandクラスを使用
@click.version_option()
@click.option(
    "--openapi-file",
    "-f",
    envvar="OPENAPI_FILE_PATH",
    help="OpenAPIファイルのパス（環境変数OPENAPI_FILE_PATHでも指定可能）",
    required=False,
)
# --- ↓↓↓ グローバルオプションを追加 ↓↓↓ ---
@click.option(
    "--server",
    "-s",
    help="APIサーバーのURL",
)
# --- ↑↑↑ グローバルオプションを追加 ↑↑↑ ---
# --- ↓↓↓ 不要になった認証オプションを削除 ↓↓↓ ---
# @click.option(
#     "--defaultApiKey", # securityScheme名に合わせる
#     help="APIキー (X-API-Key)", # ヘッダー名も記載
#     envvar="CLIFY_DEFAULTAPIKEY", # 環境変数名も合わせる
# )
# --- ↑↑↑ 不要になった認証オプションを削除 ↑↑↑ ---
@click.pass_context
def cli(
    ctx: click.Context,
    openapi_file: Optional[str] = None,
    server: Optional[str] = None,
    # defaultapikey: Optional[str] = None, # 不要になった引数を削除
) -> None:
    """
    OpenAPI仕様からCLIを自動生成するツール

    環境変数OPENAPI_FILE_PATHまたは--openapi-fileオプションでOpenAPIファイルのパスを指定すると、
    そのAPIのCLIとして利用できます。
    """
    ctx.ensure_object(dict)  # ctx.objを初期化

    # DynamicCLIインスタンスからデフォルトサーバーを取得
    default_server = ""
    if isinstance(ctx.command, DynamicCLI) and ctx.command.spec:
        servers = ctx.command.spec.get("servers", [])
        if servers:
            default_server = servers[0].get("url", "")

    # serverオプションが指定されていなければデフォルト値を使用
    ctx.obj["server"] = server if server is not None else default_server
    # --- ↓↓↓ 不要になった認証パラメータ設定を削除 ↓↓↓ ---
    # ctx.obj["defaultapikey"] = defaultapikey
    # --- ↑↑↑ 不要になった認証パラメータ設定を削除 ↑↑↑ ---

    # --- 既存のハンドリングロジック ---
    if not isinstance(ctx.command, DynamicCLI) or not ctx.command.openapi_file:
        if not ctx.invoked_subcommand:
            click.echo(ctx.get_help())
            sys.exit(0)
        # OpenAPIファイルがないのにサブコマンドが指定された場合（エラーケース）
        # DynamicCLI内でエラーメッセージ表示済みのはず
        # sys.exit(1) # 必要なら

    # ClickがMultiCommandのlist_commands/get_commandを呼び出して処理を進める
    pass


def main() -> None:
    """
    CLIのエントリーポイント
    """
    cli()


if __name__ == "__main__":
    main()
