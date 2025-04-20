#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import pytest
import yaml
from pathlib import Path


@pytest.fixture
def sample_openapi_yaml():
    """サンプルのOpenAPI YAMLファイルのパスを返す"""
    # テスト用のOpenAPIファイルを作成
    yaml_path = Path(__file__).parent / "fixtures" / "sample_openapi.yaml"

    # fixtures ディレクトリが存在しない場合は作成
    yaml_path.parent.mkdir(exist_ok=True)

    # サンプルのOpenAPI仕様
    openapi_spec = {
        "openapi": "3.1.0",
        "info": {
            "version": "1.0.0",
            "title": "Example API",
            "description": "This is an example API for testing",
        },
        "servers": [{"url": "https://api.example.com/v1"}],
        "paths": {
            "/users": {
                "get": {
                    "summary": "Get all users",
                    "operationId": "getUsers",
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "description": "Maximum number of users to return",
                            "schema": {"type": "integer", "default": 10},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "integer"},
                                                "name": {"type": "string"},
                                                "email": {"type": "string"},
                                            },
                                        },
                                    }
                                }
                            },
                        }
                    },
                },
                "post": {
                    "summary": "Create a new user",
                    "operationId": "createUser",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "email": {"type": "string"},
                                    },
                                    "required": ["name", "email"],
                                }
                            }
                        },
                    },
                    "responses": {
                        "201": {
                            "description": "User created successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "name": {"type": "string"},
                                            "email": {"type": "string"},
                                        },
                                    }
                                }
                            },
                        }
                    },
                },
            },
            "/users/{userId}": {
                "get": {
                    "summary": "Get user by ID",
                    "operationId": "getUserById",
                    "parameters": [
                        {
                            "name": "userId",
                            "in": "path",
                            "required": True,
                            "description": "ID of the user",
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "name": {"type": "string"},
                                            "email": {"type": "string"},
                                        },
                                    }
                                }
                            },
                        },
                        "404": {"description": "User not found"},
                    },
                }
            },
        },
    }

    # YAMLファイルに書き込み
    with open(yaml_path, "w") as f:
        yaml.dump(openapi_spec, f)

    return str(yaml_path)


@pytest.fixture
def sample_openapi_json():
    """サンプルのOpenAPI JSONファイルのパスを返す"""
    # テスト用のOpenAPIファイルを作成
    json_path = Path(__file__).parent / "fixtures" / "sample_openapi.json"

    # fixtures ディレクトリが存在しない場合は作成
    json_path.parent.mkdir(exist_ok=True)

    # サンプルのOpenAPI仕様（YAMLと同じ内容）
    openapi_spec = {
        "openapi": "3.1.0",
        "info": {
            "version": "1.0.0",
            "title": "Example API",
            "description": "This is an example API for testing",
        },
        "servers": [{"url": "https://api.example.com/v1"}],
        "paths": {
            "/users": {
                "get": {
                    "summary": "Get all users",
                    "operationId": "getUsers",
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "description": "Maximum number of users to return",
                            "schema": {"type": "integer", "default": 10},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "integer"},
                                                "name": {"type": "string"},
                                                "email": {"type": "string"},
                                            },
                                        },
                                    }
                                }
                            },
                        }
                    },
                },
                "post": {
                    "summary": "Create a new user",
                    "operationId": "createUser",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "email": {"type": "string"},
                                    },
                                    "required": ["name", "email"],
                                }
                            }
                        },
                    },
                    "responses": {
                        "201": {
                            "description": "User created successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "name": {"type": "string"},
                                            "email": {"type": "string"},
                                        },
                                    }
                                }
                            },
                        }
                    },
                },
            },
            "/users/{userId}": {
                "get": {
                    "summary": "Get user by ID",
                    "operationId": "getUserById",
                    "parameters": [
                        {
                            "name": "userId",
                            "in": "path",
                            "required": True,
                            "description": "ID of the user",
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "name": {"type": "string"},
                                            "email": {"type": "string"},
                                        },
                                    }
                                }
                            },
                        },
                        "404": {"description": "User not found"},
                    },
                }
            },
        },
    }

    # JSONファイルに書き込み
    with open(json_path, "w") as f:
        json.dump(openapi_spec, f, indent=2)

    return str(json_path)


@pytest.fixture
def mock_env_openapi_path(sample_openapi_yaml):
    """環境変数OPENAPI_FILE_PATHを設定する"""
    old_value = os.environ.get("OPENAPI_FILE_PATH")
    os.environ["OPENAPI_FILE_PATH"] = sample_openapi_yaml
    yield
    if old_value is not None:
        os.environ["OPENAPI_FILE_PATH"] = old_value
    else:
        del os.environ["OPENAPI_FILE_PATH"]
