#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from clify.handler import CommandHandler


class TestCommandHandler:
    """CommandHandlerのテスト"""

    def test_build_url(self):
        """URLが正しく構築されることを確認"""
        # 基本的なケース
        handler = CommandHandler(
            server="https://api.example.com",
            path="/users",
            method="GET",
            operation={},
            params={},
        )
        assert handler.url == "https://api.example.com/users"

        # サーバーURLの末尾にスラッシュがある場合
        handler = CommandHandler(
            server="https://api.example.com/",
            path="/users",
            method="GET",
            operation={},
            params={},
        )
        assert handler.url == "https://api.example.com/users"

        # パスの先頭にスラッシュがない場合
        handler = CommandHandler(
            server="https://api.example.com",
            path="users",
            method="GET",
            operation={},
            params={},
        )
        assert handler.url == "https://api.example.com/users"

    def test_replace_path_params(self):
        """パスパラメータが正しく置換されることを確認"""
        # パスパラメータがある場合
        handler = CommandHandler(
            server="https://api.example.com",
            path="/users/{userId}",
            method="GET",
            operation={},
            params={"user-id": 123},
        )
        assert handler.url == "https://api.example.com/users/123"

        # 複数のパスパラメータがある場合
        handler = CommandHandler(
            server="https://api.example.com",
            path="/users/{userId}/posts/{postId}",
            method="GET",
            operation={},
            params={"user-id": 123, "post-id": 456},
        )
        assert handler.url == "https://api.example.com/users/123/posts/456"

        # パスパラメータが指定されていない場合
        with pytest.raises(Exception):
            handler = CommandHandler(
                server="https://api.example.com",
                path="/users/{userId}",
                method="GET",
                operation={},
                params={},
            )
            handler.url  # URLにアクセスするとエラーになる

    def test_build_headers(self):
        """HTTPヘッダーが正しく構築されることを確認"""
        # 基本的なケース
        handler = CommandHandler(
            server="https://api.example.com",
            path="/users",
            method="GET",
            operation={},
            params={},
        )
        headers = handler.headers
        assert "User-Agent" in headers

        # POSTリクエストでデータがある場合
        handler = CommandHandler(
            server="https://api.example.com",
            path="/users",
            method="POST",
            operation={},
            params={"data": '{"name": "test"}'},
        )
        headers = handler.headers
        assert headers.get("Content-Type") == "application/json"

        # ヘッダーパラメータがある場合
        handler = CommandHandler(
            server="https://api.example.com",
            path="/users",
            method="GET",
            operation={
                "parameters": [
                    {
                        "name": "X-API-Key",
                        "in": "header",
                        "required": True,
                    }
                ]
            },
            params={"x-api-key": "test-key"},
        )
        headers = handler.headers
        assert headers.get("X-API-Key") == "test-key"

    def test_build_query_params(self):
        """クエリパラメータが正しく構築されることを確認"""
        # クエリパラメータがある場合
        handler = CommandHandler(
            server="https://api.example.com",
            path="/users",
            method="GET",
            operation={
                "parameters": [
                    {
                        "name": "limit",
                        "in": "query",
                        "required": False,
                    },
                    {
                        "name": "offset",
                        "in": "query",
                        "required": False,
                    },
                ]
            },
            params={"limit": 10, "offset": 20},
        )
        query_params = handler.query_params
        assert query_params.get("limit") == "10"
        assert query_params.get("offset") == "20"

        # クエリパラメータが指定されていない場合
        handler = CommandHandler(
            server="https://api.example.com",
            path="/users",
            method="GET",
            operation={
                "parameters": [
                    {
                        "name": "limit",
                        "in": "query",
                        "required": False,
                    }
                ]
            },
            params={},
        )
        query_params = handler.query_params
        assert "limit" not in query_params

    def test_build_body(self):
        """リクエストボディが正しく構築されることを確認"""
        # JSONデータがある場合
        handler = CommandHandler(
            server="https://api.example.com",
            path="/users",
            method="POST",
            operation={},
            params={"data": '{"name": "test", "email": "test@example.com"}'},
        )
        body = handler.body
        assert body.get("name") == "test"
        assert body.get("email") == "test@example.com"

        # GETリクエストの場合はボディがない
        handler = CommandHandler(
            server="https://api.example.com",
            path="/users",
            method="GET",
            operation={},
            params={"data": '{"name": "test"}'},
        )
        assert handler.body is None

        # データが指定されていない場合
        handler = CommandHandler(
            server="https://api.example.com",
            path="/users",
            method="POST",
            operation={},
            params={},
        )
        assert handler.body is None

    def test_convert_to_option_name(self):
        """パラメータ名がオプション名に正しく変換されることを確認"""
        handler = CommandHandler(
            server="https://api.example.com",
            path="/users",
            method="GET",
            operation={},
            params={},
        )

        # 変換をテスト
        assert handler._convert_to_option_name("userId") == "user-id"
        assert handler._convert_to_option_name("limit") == "limit"
        assert handler._convert_to_option_name("page_size") == "page-size"
        assert handler._convert_to_option_name("filter.name") == "filter-name"
