
from setuptools import setup, find_packages
import os

# Read manual major/minor version from VERSION file
with open('VERSION', 'r') as f:
    manual_version = f.read().strip()

# Use BUILDID env var (e.g. from Azure DevOps) or fallback to 'local'
def get_combined_version():
    build_id = os.getenv('BUILDID')
    if build_id:
        return f"{manual_version}.{build_id}"
    # fallback: use date and time as build id if not set
    from datetime import datetime
    date_build = datetime.now().strftime('%y%m%d%H%M%S')
    return f"{manual_version}.{date_build}"

setup(
    name="custom_ai_gateway_policies",
    version=get_combined_version(),
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