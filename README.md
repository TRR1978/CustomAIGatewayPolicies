# CustomAIGatewayPolicies

Emulate Databricks cluster policies for model serving endpoints. This project provides a framework to define, enforce, and manage policies for Databricks model serving endpoints using the Databricks SDK.

## Features
- Policy definition and enforcement for model serving endpoints
- Integration with Databricks SDK
- Extensible and configurable

## Getting Started

### Usage


#### 1. Instala pipenv
Si no tienes pipenv instalado:
```sh
pip install pipenv
```

#### 2. Instala las dependencias y crea el entorno virtual
Desde la raíz del proyecto:
```sh
pipenv install --dev
```

#### 3. Activa el entorno virtual
```sh
pipenv shell
```

#### 4. Añade dependencias
Para dependencias normales:
```sh
pipenv install <paquete>
```
Para dependencias de desarrollo:
```sh
pipenv install --dev <paquete>
```

#### 5. Ejecuta los tests
```sh
pipenv run pytest
```

---
See the `example/` folder for usage examples.

## Contributing
See `CONTRIBUTING.md` for guidelines.

## License
MIT License. See `LICENSE` for details.
