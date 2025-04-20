#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest
from pathlib import Path

from clify.parser import OpenAPIParser


class TestOpenAPIParser:
    """OpenAPIParserのテスト"""

    def test_parse_yaml(self, sample_openapi_yaml):
        """YAMLファイルを解析できることを確認"""
        parser = OpenAPIParser(sample_openapi_yaml)
        spec = parser.parse()

        # 基本情報の確認
        assert spec["openapi"] == "3.1.0"
        assert spec["info"]["title"] == "Example API"
        assert spec["servers"][0]["url"] == "https://api.example.com/v1"

        # パスの確認
        assert "/users" in spec["paths"]
        assert "/users/{userId}" in spec["paths"]

        # メソッドの確認
        assert "get" in spec["paths"]["/users"]
        assert "post" in spec["paths"]["/users"]
        assert "get" in spec["paths"]["/users/{userId}"]

    def test_parse_json(self, sample_openapi_json):
        """JSONファイルを解析できることを確認"""
        parser = OpenAPIParser(sample_openapi_json)
        spec = parser.parse()

        # 基本情報の確認
        assert spec["openapi"] == "3.1.0"
        assert spec["info"]["title"] == "Example API"
        assert spec["servers"][0]["url"] == "https://api.example.com/v1"

    def test_get_endpoints(self, sample_openapi_yaml):
        """エンドポイント情報を取得できることを確認"""
        parser = OpenAPIParser(sample_openapi_yaml)
        parser.parse()
        endpoints = parser.get_endpoints()

        # エンドポイント数の確認
        assert len(endpoints) == 3

        # エンドポイント情報の確認
        endpoint_paths = [endpoint["path"] for endpoint in endpoints]
        endpoint_methods = [endpoint["method"] for endpoint in endpoints]

        assert "/users" in endpoint_paths
        assert "/users/{userId}" in endpoint_paths
        assert "GET" in endpoint_methods
        assert "POST" in endpoint_methods

    def test_get_servers(self, sample_openapi_yaml):
        """サーバー情報を取得できることを確認"""
        parser = OpenAPIParser(sample_openapi_yaml)
        parser.parse()
        servers = parser.get_servers()

        assert len(servers) == 1
        assert servers[0]["url"] == "https://api.example.com/v1"

    def test_file_not_found(self):
        """存在しないファイルを指定した場合にエラーになることを確認"""
        parser = OpenAPIParser("non_existent_file.yaml")
        with pytest.raises(FileNotFoundError):
            parser.parse()

    def test_invalid_openapi_spec(self, tmp_path):
        """無効なOpenAPI仕様の場合にエラーになることを確認"""
        # 無効なOpenAPI仕様ファイルを作成
        invalid_file = tmp_path / "invalid.yaml"
        with open(invalid_file, "w") as f:
            f.write("invalid: yaml")

        parser = OpenAPIParser(str(invalid_file))
        with pytest.raises(ValueError):
            parser.parse()
