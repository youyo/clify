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

    def __init__(self, **attrs: Any):
        # コンストラクタでは属性の初期化のみ
        self._spec: Optional[Dict[str, Any]] = None
        self._generated_cli: Optional[click.Group] = None
        self._openapi_file_path: Optional[str] = None
        self._initialized = False
        # self.ctx_obj: Dict[str, Any] = {} # ctx_obj 属性を削除
        super().__init__(**attrs)

    def _get_openapi_file_path(self) -> Optional[str]:
        """環境変数からOpenAPIファイルパスを取得"""
        # 環境変数のみを参照
        return os.getenv("OPENAPI_FILE_PATH")

    def _ensure_cli_generated(self, ctx: click.Context) -> None:
        """CLIが生成されていなければ解析・生成を行う"""
        if self._initialized:
            return

        # 環境変数から取得 (ctx 不要)
        self._openapi_file_path = self._get_openapi_file_path()

        if not self._openapi_file_path:
            # OpenAPIファイルがない場合、コマンドは生成しない
            # click.echo("デバッグ: OpenAPIファイルパスが見つかりません。", err=True) # デバッグ用
            self._generated_cli = click.Group(name="clify")  # 空のGroup
            self._initialized = True
            return

        try:
            # click.echo(f"OpenAPIファイル (ensure): {self._openapi_file_path}", err=True) # デバッグ用
            parser = OpenAPIParser(self._openapi_file_path)
            self._spec = parser.parse()
            base_url = parser.get_base_url()  # parser から base_url を取得
            # click.echo("OpenAPIファイルの解析が完了しました (ensure)", err=True) # デバッグ用

            # CLIGenerator に base_url を渡す
            generator = CLIGenerator(self._spec, base_url=base_url)
            self._generated_cli = generator.generate()
            # click.echo("CLIの生成が完了しました (ensure)", err=True) # デバッグ用

            # ヘルプテキストを更新 (任意)
            # help_text = self._spec.get("info", {}).get("description", "Generated CLI")
            # self.help = help_text

        except Exception as e:
            # エラー発生時はログ出力し、空のGroupを設定して続行（ヘルプ表示のため）
            click.echo(
                f"エラー: OpenAPIファイルの処理中にエラーが発生しました: {str(e)}",
                err=True,
            )
            self._generated_cli = click.Group(name="clify")  # エラー時も空のGroup

        self._initialized = True

    def list_commands(self, ctx: click.Context) -> List[str]:
        """利用可能なコマンドのリストを返す"""
        self._ensure_cli_generated(ctx)  # CLI生成を確認/実行
        if self._generated_cli:
            return sorted(self._generated_cli.commands.keys())
        return []

    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        """指定されたコマンド名のコマンドオブジェクトを返す"""
        self._ensure_cli_generated(ctx)
        if self._generated_cli:
            command = self._generated_cli.commands.get(cmd_name)
            # Click のデフォルト動作では obj は引き継がれるはずだが、
            # 明示的に設定してみる (これが根本原因かは不明)
            # if command:
            #     # サブコマンド用の新しいコンテキストを作成し、obj をコピーする
            #     # 注意: この方法は Click の内部実装に依存する可能性があり、推奨されない場合がある
            #     sub_ctx = command.make_context(cmd_name, [], parent=ctx)
            #     sub_ctx.obj = ctx.obj # 親の obj をコピー
            #     # make_context が適切でない場合、別の方法を検討する必要がある
            return command
        return None


# --- cli 関数の修正 ---
@click.command(cls=DynamicCLI)
@click.version_option()
# --- ↓↓↓ --openapi-file オプションを追加 ↓↓↓ ---
@click.option(
    "--openapi-file",
    "-f",
    help="OpenAPIファイルのパス（環境変数OPENAPI_FILE_PATHでも指定可能）",  # ヘルプメッセージを修正
    required=False,  # 環境変数で指定できるため必須ではない
    type=click.Path(exists=True, dir_okay=False),  # ファイルの存在チェックを追加
)
# --- ↑↑↑ --openapi-file オプションを追加 ↑↑↑ ---
@click.option(
    "--server",
    "-s",
    help="APIサーバーのURL",
)
@click.pass_context
def cli(
    ctx: click.Context,
    openapi_file: Optional[str] = None,  # 引数を追加
    server: Optional[str] = None,
) -> None:
    """
    OpenAPI仕様からCLIを自動生成するツール

    環境変数OPENAPI_FILE_PATHでOpenAPIファイルのパスを指定すると、
    そのAPIのCLIとして利用できます。
    """
    # この関数は MultiCommand のサブコマンドが呼び出される *前* に実行される
    # ここでは ctx.obj の設定など、サブコマンドで共通に必要な処理を行う

    dynamic_cli_instance = ctx.command
    if not isinstance(dynamic_cli_instance, DynamicCLI):
        click.echo("エラー: DynamicCLIのインスタンスを取得できませんでした。", err=True)
        sys.exit(1)

    # --- ctx.obj の設定ロジックを generator.py に移動したので削除 ---

    # --- OpenAPIファイルパスの処理 ---
    # コマンドライン引数と環境変数の両方を考慮する
    # DynamicCLI インスタンスにファイルパスを渡す
    if openapi_file:
        dynamic_cli_instance._openapi_file_path = openapi_file
    else:
        # 環境変数から取得する処理は _ensure_cli_generated 内で行われる
        pass

    # --- OpenAPIファイル指定がない場合やエラー時のハンドリング ---
    # _ensure_cli_generated が呼ばれる前にファイルパスの有無を確認
    if (
        not dynamic_cli_instance._openapi_file_path
        and not dynamic_cli_instance._get_openapi_file_path()
    ):
        if not ctx.invoked_subcommand:
            # サブコマンドなし、ファイル指定なし -> ヘルプ表示
            click.echo(ctx.get_help())
            sys.exit(0)
        else:
            # サブコマンドあり、ファイル指定なし -> エラー
            click.echo("エラー: OpenAPIファイルが指定されていません。", err=True)
            click.echo(
                "`--openapi-file` オプションまたは環境変数 `OPENAPI_FILE_PATH` で指定してください。",
                err=True,
            )
            sys.exit(1)

    # _ensure_cli_generated 内でエラーが発生した場合、空の Group が設定される。
    # list_commands/get_command は空リスト/Noneを返し、Clickが "Missing command" 等のエラーを出す。
    # ここで追加のエラーハンドリングは不要かもしれない。

    pass


def main() -> None:
    """
    CLIのエントリーポイント
    """
    cli()


if __name__ == "__main__":
    main()
