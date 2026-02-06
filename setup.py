
import os
from setuptools import setup, find_packages
from datetime import datetime


# Read manual major/minor version from VERSION file
with open('VERSION', 'r') as f:
    manual_version = f.read().strip()

# Use BUILDID env var (e.g. from Azure DevOps) or fallback to 'local'

def get_dynamic_version():
    build_id = os.getenv('BUILDID')
    if build_id:
        parts = manual_version.split('.')
        if len(parts) == 1:
            # e.g. '1' -> '1.0.{build_id}'
            return f"{parts[0]}.0.{build_id}"
        elif len(parts) == 2:
            # e.g. '1.1' -> '1.1.{build_id}'
            return f"{parts[0]}.{parts[1]}.{build_id}"
        else:
            # e.g. '1.1.0' or more -> '1.1.{build_id}'
            return f"{parts[0]}.{parts[1]}.{build_id}"
    else:
        return manual_version
    
 
setup(
    name="custom_ai_gateway_policies",
    version=get_dynamic_version(),
    description="Emulate Databricks cluster policies for model serving endpoints.",
    author="Tomas Romero",
    author_email="tomas.romero@gmail.com",
    url="https://github.com/trr78/CustomAIGatewayPolicies",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "databricks-sdk>=0.80.0"
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "flake8",
            "pep8-naming"
        ]
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
        # use_scm_version=False,