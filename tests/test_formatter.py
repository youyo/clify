#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import pytest
from unittest.mock import MagicMock

from clify.formatter import ResponseFormatter


class TestResponseFormatter:
    """ResponseFormatterのテスト"""

    def test_format_json_response(self):
        """JSONレスポンスが正しくフォーマットされることを確認"""
        # モックレスポンスを作成
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"id": 1, "name": "test"}
        mock_response.text = '{"id": 1, "name": "test"}'

        # フォーマッターを作成
        formatter = ResponseFormatter()

        # レスポンスをフォーマット
        result = formatter.format(mock_response)

        # 結果を確認
        assert "Status: 200 OK" in result
        assert '"id": 1' in result
        assert '"name": "test"' in result

    def test_format_text_response(self):
        """テキストレスポンスが正しくフォーマットされることを確認"""
        # モックレスポンスを作成
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.text = "Hello, world!"

        # フォーマッターを作成
        formatter = ResponseFormatter()

        # レスポンスをフォーマット
        result = formatter.format(mock_response)

        # 結果を確認
        assert "Status: 200 OK" in result
        assert "Hello, world!" in result

    def test_format_json_data(self):
        """JSONデータが正しくフォーマットされることを確認"""
        # テストデータ
        data = {"id": 1, "name": "test", "items": [1, 2, 3]}

        # フォーマッターを作成
        formatter = ResponseFormatter()

        # データをフォーマット
        result = formatter.format_json(data)

        # 結果を確認
        expected = json.dumps(data, indent=2, ensure_ascii=False)
        assert result == expected

    def test_format_yaml_data(self):
        """YAMLデータが正しくフォーマットされることを確認（pyyamlがインストールされている場合）"""
        # テストデータ
        data = {"id": 1, "name": "test", "items": [1, 2, 3]}

        # フォーマッターを作成
        formatter = ResponseFormatter(format_type="yaml")

        try:
            import yaml

            # データをフォーマット
            result = formatter.format_json(data)

            # 結果を確認
            assert "id: 1" in result
            assert "name: test" in result
            assert "items:" in result
        except ImportError:
            # pyyamlがインストールされていない場合はJSONとしてフォーマットされる
            result = formatter.format_json(data)
            expected = json.dumps(data, indent=2, ensure_ascii=False)
            assert result == expected

    def test_format_table_data_list(self):
        """テーブルデータ（リスト）が正しくフォーマットされることを確認（tabulateがインストールされている場合）"""
        # テストデータ（リスト）
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Charlie"},
        ]

        # フォーマッターを作成
        formatter = ResponseFormatter(format_type="table")

        try:
            from tabulate import tabulate

            # データをフォーマット
            result = formatter.format_json(data)

            # 結果を確認
            assert "id" in result
            assert "name" in result
            assert "Alice" in result
            assert "Bob" in result
            assert "Charlie" in result
        except ImportError:
            # tabulateがインストールされていない場合はJSONとしてフォーマットされる
            result = formatter.format_json(data)
            expected = json.dumps(data, indent=2, ensure_ascii=False)
            assert result == expected

    def test_format_table_data_dict(self):
        """テーブルデータ（辞書）が正しくフォーマットされることを確認（tabulateがインストールされている場合）"""
        # テストデータ（辞書）
        data = {"id": 1, "name": "Alice", "email": "alice@example.com"}

        # フォーマッターを作成
        formatter = ResponseFormatter(format_type="table")

        try:
            from tabulate import tabulate

            # データをフォーマット
            result = formatter.format_json(data)

            # 結果を確認
            assert "Key" in result
            assert "Value" in result
            assert "id" in result
            assert "name" in result
            assert "Alice" in result
        except ImportError:
            # tabulateがインストールされていない場合はJSONとしてフォーマットされる
            result = formatter.format_json(data)
            expected = json.dumps(data, indent=2, ensure_ascii=False)
            assert result == expected

    def test_format_error(self):
        """エラーメッセージが正しくフォーマットされることを確認"""
        # フォーマッターを作成
        formatter = ResponseFormatter()

        # エラーメッセージをフォーマット
        result = formatter.format_error("Something went wrong")

        # 結果を確認
        assert result == "Error: Something went wrong"
