# clify

A tool that automatically generates CLI from OpenAPI specifications

## Overview

clify is a tool that allows you to use an API as a CLI by simply specifying the path to an OpenAPI file through an environment variable. It enables you to easily perform API operations from the command line.

## Features

- Supports OpenAPI 3.0/3.1 specifications
- Ability to specify OpenAPI file path via environment variables
- Automatically generates subcommands corresponding to each API endpoint
- Automatically generates options corresponding to parameters
- Formatted display of JSON responses
- Authentication information management

## Installation

```bash
pip install clify
```

## Usage

### Specify OpenAPI file with environment variable

```bash
export OPENAPI_FILE_PATH=/path/to/openapi.yaml
clify
```

### Specify OpenAPI file with command line option

```bash
clify --openapi-file /path/to/openapi.yaml
```

### Specify OpenAPI file with URL

```bash
clify --openapi-file https://example.com/api/openapi.yaml
```

### Display list of commands

```bash
clify --help
```

### Display help for a specific command

```bash
clify <command> --help
```

### Execute API request

```bash
clify <command> [options]
```

### Specify server URL

```bash
clify --server https://api.example.com <command> [options]
```

### Specify authentication information

```bash
# Basic authentication
clify --username user --password pass <command> [options]

# Bearer token
clify --token your-token <command> [options]

# API key
clify --api-key your-api-key <command> [options]
```

### Send JSON data

```bash
clify <command> --data '{"key": "value"}'
# or
clify <command> --data @file.json
```

## Examples

### Example OpenAPI file

```yaml
openapi: 3.1.0
info:
  version: 1.0.0
  title: Example API
servers:
  - url: https://api.example.com/v1
paths:
  /users:
    get:
      summary: Get all users
      operationId: getUsers
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
      responses:
        200:
          description: Successful response
    post:
      summary: Create a new user
      operationId: createUser
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                email:
                  type: string
      responses:
        201:
          description: User created
```

### Generated CLI

```bash
# Get list of users
clify get-users --limit 10

# Create a new user
clify create-user --data '{"name": "John", "email": "john@example.com"}'
```

## Development

### Install dependencies

```bash
pip install -e ".[dev]"
```

### Run tests

```bash
pytest
```

### Build

```bash
python -m build
```

## License

MIT
