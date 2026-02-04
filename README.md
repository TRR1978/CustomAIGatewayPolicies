```
 ██████╗██╗   ██╗███████╗████████╗ ██████╗ ███╗   ███╗                          
██╔════╝██║   ██║██╔════╝╚══██╔══╝██╔═══██╗████╗ ████║                          
██║     ██║   ██║███████╗   ██║   ██║   ██║██╔████╔██║                          
██║     ██║   ██║╚════██║   ██║   ██║   ██║██║╚██╔╝██║                          
╚██████╗╚██████╔╝███████║   ██║   ╚██████╔╝██║ ╚═╝ ██║                          
 ╚═════╝ ╚═════╝ ╚══════╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝                          
                                                                                
 █████╗ ██╗     ██████╗  █████╗ ████████╗███████╗██╗    ██╗ █████╗ ██╗   ██╗    
██╔══██╗██║    ██╔════╝ ██╔══██╗╚══██╔══╝██╔════╝██║    ██║██╔══██╗╚██╗ ██╔╝    
███████║██║    ██║  ███╗███████║   ██║   █████╗  ██║ █╗ ██║███████║ ╚████╔╝     
██╔══██║██║    ██║   ██║██╔══██║   ██║   ██╔══╝  ██║███╗██║██╔══██║  ╚██╔╝      
██║  ██║██║    ╚██████╔╝██║  ██║   ██║   ███████╗╚███╔███╔╝██║  ██║   ██║       
╚═╝  ╚═╝╚═╝     ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝   ╚═╝       
                                                                                
██████╗  ██████╗ ██╗     ██╗ ██████╗██╗███████╗███████╗                         
██╔══██╗██╔═══██╗██║     ██║██╔════╝██║██╔════╝██╔════╝                         
██████╔╝██║   ██║██║     ██║██║     ██║█████╗  ███████╗                         
██╔═══╝ ██║   ██║██║     ██║██║     ██║██╔══╝  ╚════██║                         
██║     ╚██████╔╝███████╗██║╚██████╗██║███████╗███████║                         
╚═╝      ╚═════╝ ╚══════╝╚═╝ ╚═════╝╚═╝╚══════╝╚══════╝                         
```

A framework that emulates Databricks cluster policies for model serving endpoints. This project enables defining, enforcing, and managing policies for Databricks model serving endpoints using the Databricks SDK.

---

## Table of Contents
- [Development Environment Setup](#development-environment-setup)
- [What's New](#whats-new)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Usage](#usage)
- [Contributing](#contributing)
- [Contributors](#contributors)
- [License](#license)

---

## Development Environment Setup

To ensure all developers work with a consistent environment and imports resolve correctly, follow these steps:

### 1. Environment Variables
- The `.env.example` file contains the recommended configuration (e.g., `PYTHONPATH=src`).
- **Do not edit or commit `.env` to the repository.** Each developer should create their own local `.env` if needed.
- To use the base configuration, copy the example file:

**Linux/Mac**
```sh
cp .env.example .env
```

**Windows**
```powershell
copy .env.example .env
```

### 2. VS Code Setup (Optional but Recommended)
You may create a `.vscode/settings.json` file with:

```json
{
  "terminal.integrated.env.windows": {
    "PYTHONPATH": "${workspaceFolder}/src"
  },
  "python.envFile": "${workspaceFolder}/.env"
}
```

This ensures consistent import behavior in the editor without manually creating a `.env` file.

### 3. pytest Configuration
The `pytest.ini` file already includes:

```
pythonpath = src
```

This allows tests to run correctly without additional configuration.

### Summary
- Use `.env.example` as a template for your local `.env`.
- Never commit `.env` to the repository.
- VS Code users can automate environment configuration via `.vscode/settings.json`.

---

## What's New
- Added `dry_mode` parameter for safe policy evaluation and testing.
- New `get_rules_by_prefix` method for flexible rule filtering.
- Enhanced `details` attribute in `Endpoint` for richer metadata.
- Improved JSON schema validation for policies and rules.

---

## Features
- Define and enforce policies for model serving endpoints.
- Integrate seamlessly with the Databricks SDK.
- Extensible and configurable architecture.
- Dry‑run mode for safe policy evaluation.
- Rule filtering by prefix (e.g., `ai_gateway.*`).
- Rich endpoint metadata for advanced policy checks.

---

## Getting Started

### Usage

#### 1. Install pipenv
If you don’t have pipenv installed:
```sh
pip install pipenv
```

#### 2. Install dependencies and create the virtual environment
From the project root:
```sh
pipenv install --dev
```

#### 3. Activate the virtual environment
```sh
pipenv shell
```

#### 4. Add dependencies
Regular dependencies:
```sh
pipenv install <package>
```

Development dependencies:
```sh
pipenv install --dev <package>
```

#### 5. Run tests
```sh
pipenv run pytest
```

For usage examples, see the `example/` directory.

---

## Contributing
Refer to `CONTRIBUTING.md` for contribution guidelines.

---

## Contributors
- GitHub Copilot (AI Assistant)  
- Databricks Assistant (AI)

---

## License
MIT License. See `LICENSE` for details.

---

If you'd like, I can also generate a version with badges, a more formal tone, or a more concise style.