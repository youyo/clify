#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
import copy
import requests
import yaml


class OpenAPIParser:
    """
    OpenAPI仕様ファイルを解析するクラス
    """

    def __init__(self, file_path: str):
        """
        初期化

        Args:
            file_path: OpenAPIファイルのパス（ローカルファイルパスまたはURL）
        """
        self.file_path = file_path
        self.spec: Dict[str, Any] = {}
        self.base_url: Optional[str] = None  # ベースURLを保持する属性を追加

    def parse(self) -> Dict[str, Any]:
        """
        OpenAPI仕様を解析する

        Returns:
            Dict[str, Any]: 解析されたOpenAPI仕様
        """
        # ファイルを読み込む
        content = self._load_file()

        # JSONまたはYAMLとして解析
        raw_spec: Dict[str, Any]
        if self.file_path.endswith(".json") or content.strip().startswith("{"):
            raw_spec = json.loads(content)
        else:
            raw_spec = yaml.safe_load(content)

        # OpenAPI 2.0 (Swagger) かどうかを判定して変換
        if raw_spec.get("swagger") == "2.0":
            self.spec = self._convert_v2_to_v3(raw_spec)
        else:
            self.spec = raw_spec

        # OpenAPI 3.x 仕様として検証
        self._validate_openapi_spec()

        return self.spec

    def _load_file(self) -> str:
        """
        ファイルを読み込む

        Returns:
            str: ファイルの内容

        Raises:
            FileNotFoundError: ファイルが見つからない場合
            ValueError: URLが無効な場合
            requests.RequestException: リクエストに失敗した場合
        """
        # URLかどうかを判定
        parsed_url = urlparse(self.file_path)
        if parsed_url.scheme in ["http", "https"]:
            # ベースURLを保持 (スキーム + ホスト名)
            self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            # URLの場合はリクエストを送信
            response = requests.get(self.file_path)
            response.raise_for_status()
            return response.text
        else:
            # ローカルファイルの場合
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(f"ファイルが見つかりません: {self.file_path}")

            with open(self.file_path, "r", encoding="utf-8") as f:
                return f.read()

    def _validate_openapi_spec(self) -> None:
        """
        OpenAPI 3.x 仕様かどうかを検証する
        """
        # 基本的な検証
        if "openapi" not in self.spec:
            raise ValueError(
                "OpenAPI仕様ではありません: 'openapi'フィールドがありません"
            )

        if not isinstance(self.spec.get("paths"), dict):  # pathsが辞書であるかも確認
            raise ValueError("OpenAPI仕様ではありません: 'paths'フィールドが不正です")

        # バージョンの確認
        openapi_version = self.spec["openapi"]
        if not isinstance(openapi_version, str) or not openapi_version.startswith("3."):
            raise ValueError(
                f"サポートされていないOpenAPIバージョンです: {openapi_version}"
            )

    def _convert_v2_to_v3(self, spec_v2: Dict[str, Any]) -> Dict[str, Any]:
        """
        OpenAPI 2.0 仕様を 3.x 形式に変換する（基本的な変換のみ）
        """
        # print(
        #     "OpenAPI 2.0 仕様を検出しました。3.x 形式に変換します。", file=sys.stderr
        # )  # デバッグ用出力削除
        spec_v3 = copy.deepcopy(spec_v2)  # 元の辞書を変更しないようにコピー

        # 1. openapi バージョン設定
        spec_v3["openapi"] = "3.0.0"
        spec_v3.pop("swagger", None)  # swagger フィールド削除

        # 2. servers の生成
        host = spec_v2.get("host")
        basePath = spec_v2.get("basePath", "")
        schemes = spec_v2.get("schemes", ["https"])  # デフォルトは https
        if host:
            spec_v3["servers"] = [
                {"url": f"{scheme}://{host}{basePath}"} for scheme in schemes
            ]
        spec_v3.pop("host", None)
        spec_v3.pop("basePath", None)
        spec_v3.pop("schemes", None)

        # 3. securityDefinitions -> components.securitySchemes
        security_definitions = spec_v2.get("securityDefinitions")
        if security_definitions:
            if "components" not in spec_v3:
                spec_v3["components"] = {}
            spec_v3["components"]["securitySchemes"] = {}
            for name, definition in security_definitions.items():
                sec_type = definition.get("type")
                if sec_type == "basic":
                    spec_v3["components"]["securitySchemes"][name] = {
                        "type": "http",
                        "scheme": "basic",
                    }
                elif sec_type == "apiKey":
                    spec_v3["components"]["securitySchemes"][name] = {
                        "type": "apiKey",
                        "name": definition.get("name"),
                        "in": definition.get("in"),
                    }
                elif sec_type == "oauth2":
                    flow = definition.get("flow")
                    flows = {}
                    if flow == "implicit":
                        flows["implicit"] = {
                            "authorizationUrl": definition.get("authorizationUrl"),
                            "scopes": definition.get("scopes", {}),
                        }
                    elif flow == "password":
                        flows["password"] = {
                            "tokenUrl": definition.get("tokenUrl"),
                            "scopes": definition.get("scopes", {}),
                        }
                    elif flow == "application":
                        flows["clientCredentials"] = {
                            "tokenUrl": definition.get("tokenUrl"),
                            "scopes": definition.get("scopes", {}),
                        }
                    elif flow == "accessCode":  # OpenAPI 3.0 では authorizationCode
                        flows["authorizationCode"] = {
                            "authorizationUrl": definition.get("authorizationUrl"),
                            "tokenUrl": definition.get("tokenUrl"),
                            "scopes": definition.get("scopes", {}),
                        }
                    if flows:
                        spec_v3["components"]["securitySchemes"][name] = {
                            "type": "oauth2",
                            "flows": flows,
                        }
            spec_v3.pop("securityDefinitions", None)

        # 4. definitions -> components.schemas
        definitions = spec_v2.get("definitions")
        if definitions:
            if "components" not in spec_v3:
                spec_v3["components"] = {}
            spec_v3["components"]["schemas"] = definitions
            spec_v3.pop("definitions", None)

        # 5. consumes/produces と body パラメータの変換
        global_consumes = spec_v2.get("consumes", ["application/json"])  # デフォルト
        global_produces = spec_v2.get("produces", ["application/json"])  # デフォルト
        spec_v3.pop("consumes", None)
        spec_v3.pop("produces", None)

        if "paths" in spec_v3:
            for path, path_item in spec_v3["paths"].items():
                if not isinstance(path_item, dict):
                    continue  # 不正な形式はスキップ

                # パスレベルのパラメータを操作レベルにコピー（参照を解決する必要があるが、ここでは単純化）
                path_level_params = path_item.get("parameters", [])

                for method, operation in path_item.items():
                    if method.lower() in [
                        "get",
                        "post",
                        "put",
                        "delete",
                        "patch",
                        "head",
                        "options",
                        "trace",
                    ] and isinstance(operation, dict):
                        # 操作レベルのパラメータと結合
                        operation_params = operation.get("parameters", [])
                        combined_params = copy.deepcopy(
                            path_level_params
                        ) + copy.deepcopy(operation_params)
                        operation["parameters"] = []  # いったんクリア

                        # consumes/produces
                        op_consumes = operation.get("consumes", global_consumes)
                        op_produces = operation.get("produces", global_produces)
                        operation.pop("consumes", None)
                        operation.pop("produces", None)

                        request_body_schema = None
                        request_body_required = False
                        body_param_name = None

                        # パラメータ処理 (bodyパラメータを分離)
                        for param in combined_params:
                            if isinstance(param, dict) and param.get("in") == "body":
                                body_param_name = param.get("name")
                                request_body_schema = param.get("schema")
                                request_body_required = param.get("required", False)
                            else:
                                # パラメータの型変換 (nullableなど)
                                if isinstance(param, dict) and "type" in param:
                                    if param["type"] == "file":
                                        param["type"] = "string"
                                        param["format"] = "binary"
                                operation["parameters"].append(param)

                        # requestBody の生成
                        if request_body_schema:
                            operation["requestBody"] = {
                                "required": request_body_required,
                                "content": {},
                            }
                            for content_type in op_consumes:
                                operation["requestBody"]["content"][content_type] = {
                                    "schema": request_body_schema
                                }

                        # responses の変換
                        if "responses" in operation and isinstance(
                            operation["responses"], dict
                        ):
                            for status_code, response in operation["responses"].items():
                                if isinstance(response, dict) and "schema" in response:
                                    schema = response.pop("schema")
                                    response["content"] = {}
                                    for content_type in op_produces:
                                        response["content"][content_type] = {
                                            "schema": schema
                                        }
                                # headers の変換 (必要なら)

                # パスレベルの parameters は削除
                path_item.pop("parameters", None)

        # $ref の参照先を更新 (#/definitions/ -> #/components/schemas/)
        def update_refs(node):
            if isinstance(node, dict):
                for key, value in node.items():
                    if (
                        key == "$ref"
                        and isinstance(value, str)
                        and value.startswith("#/definitions/")
                    ):
                        node[key] = value.replace(
                            "#/definitions/", "#/components/schemas/", 1
                        )
                    else:
                        update_refs(value)
            elif isinstance(node, list):
                for item in node:
                    update_refs(item)

        update_refs(spec_v3)

        # print(
        #     "OpenAPI 2.0 から 3.x への変換が完了しました。", file=sys.stderr
        # )  # デバッグ用出力削除
        return spec_v3

    def get_base_url(self) -> Optional[str]:  # ベースURL取得メソッドを追加
        """ロード元がURLの場合、そのベースURLを返す"""
        return self.base_url

    def get_endpoints(self) -> List[Dict[str, Any]]:
        """
        APIエンドポイント情報を取得する

        Returns:
            List[Dict[str, Any]]: エンドポイント情報のリスト
        """
        endpoints = []

        for path, path_item in self.spec.get("paths", {}).items():
            for method, operation in path_item.items():
                if method in ["get", "post", "put", "delete", "patch", "head"]:
                    endpoint = {
                        "path": path,
                        "method": method.upper(),
                        "operation_id": operation.get(
                            "operationId", f"{method}_{path}"
                        ),
                        "summary": operation.get("summary", ""),
                        "description": operation.get("description", ""),
                        "parameters": operation.get("parameters", []),
                        "request_body": operation.get("requestBody", {}),
                        "responses": operation.get("responses", {}),
                    }
                    endpoints.append(endpoint)

        return endpoints

    def get_servers(self) -> List[Dict[str, str]]:
        """
        サーバー情報を取得する

        Returns:
            List[Dict[str, str]]: サーバー情報のリスト
        """
        return self.spec.get("servers", [])

    def get_security_schemes(self) -> Dict[str, Any]:
        """
        セキュリティスキーム情報を取得する

        Returns:
            Dict[str, Any]: セキュリティスキーム情報
        """
        components = self.spec.get("components", {})
        return components.get("securitySchemes", {})
