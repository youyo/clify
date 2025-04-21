#!/usr/bin/env python
# -*- coding: utf-8 -*-

from click.testing import CliRunner
from clify.parser import OpenAPIParser
from clify.generator import CLIGenerator


class TestCLIGenerator:
    """CLIGeneratorのテスト"""

    def test_generate(self, sample_openapi_yaml):
        """CLIコマンドが生成されることを確認"""
        # OpenAPI仕様を解析
        parser = OpenAPIParser(sample_openapi_yaml)
        spec = parser.parse()

        # CLIを生成
        generator = CLIGenerator(spec)
        dynamic_cli = generator.generate()

        # 生成されたCLIが呼び出し可能であることを確認
        assert callable(dynamic_cli)

        # ヘルプが表示されることを確認
        runner = CliRunner()
        result = runner.invoke(dynamic_cli, ["--help"])

        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_command_generation(self, sample_openapi_yaml):
        """各エンドポイントに対応するコマンドが生成されることを確認"""
        # OpenAPI仕様を解析
        parser = OpenAPIParser(sample_openapi_yaml)
        spec = parser.parse()

        # CLIを生成
        generator = CLIGenerator(spec)
        dynamic_cli = generator.generate()

        # コマンド一覧を取得
        runner = CliRunner()
        result = runner.invoke(dynamic_cli, ["--help"])

        # 各エンドポイントに対応するコマンドが存在することを確認
        assert "get-users" in result.output
        assert "create-user" in result.output
        assert "get-user-by-id" in result.output

    def test_command_options(self, sample_openapi_yaml):
        """コマンドのオプションが正しく生成されることを確認"""
        # OpenAPI仕様を解析
        parser = OpenAPIParser(sample_openapi_yaml)
        spec = parser.parse()

        # CLIを生成
        generator = CLIGenerator(spec)
        dynamic_cli = generator.generate()

        # get-usersコマンドのヘルプを取得
        runner = CliRunner()
        result = runner.invoke(dynamic_cli, ["get-users", "--help"])

        # クエリパラメータがオプションとして存在することを確認
        assert "--limit" in result.output

        # get-user-by-idコマンドのヘルプを取得
        result = runner.invoke(dynamic_cli, ["get-user-by-id", "--help"])

        # パスパラメータが引数として存在することを確認
        assert "USER_ID" in result.output

    def test_server_option(self, sample_openapi_yaml):
        """サーバーURLを指定するオプションが存在することを確認"""
        # OpenAPI仕様を解析
        parser = OpenAPIParser(sample_openapi_yaml)
        spec = parser.parse()

        # CLIを生成
        generator = CLIGenerator(spec)
        dynamic_cli = generator.generate()

        # ヘルプを取得
        runner = CliRunner()
        result = runner.invoke(dynamic_cli, ["--help"])

        # サーバーURLを指定するオプションが存在することを確認
        assert "--server" in result.output

    def test_convert_to_command_name(self, sample_openapi_yaml):
        """operationIdがコマンド名に正しく変換されることを確認"""
        # OpenAPI仕様を解析
        parser = OpenAPIParser(sample_openapi_yaml)
        spec = parser.parse()

        # CLIジェネレーターを作成
        generator = CLIGenerator(spec)

        # 変換をテスト
        assert generator._convert_to_command_name("getUsers") == "get-users"
        assert generator._convert_to_command_name("createUser") == "create-user"
        assert generator._convert_to_command_name("getUserById") == "get-user-by-id"
        assert generator._convert_to_command_name("user_details") == "user-details"
        assert generator._convert_to_command_name("user.details") == "user-details"

    def test_convert_to_option_name(self, sample_openapi_yaml):
        """パラメータ名がオプション名に正しく変換されることを確認"""
        # OpenAPI仕様を解析
        parser = OpenAPIParser(sample_openapi_yaml)
        spec = parser.parse()

        # CLIジェネレーターを作成
        generator = CLIGenerator(spec)

        # 変換をテスト
        assert generator._convert_to_option_name("userId") == "user-id"
        assert generator._convert_to_option_name("limit") == "limit"
        assert generator._convert_to_option_name("page_size") == "page-size"
        assert generator._convert_to_option_name("filter.name") == "filter-name"
