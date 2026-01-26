from setuptools import setup, find_packages

setup(
    name="custom_ai_gateway_policies",
    version="0.1.0",
    description="Emulate Databricks cluster policies for model serving endpoints.",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/CustomAIGatewayPolicies",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "databricks-sdk>=0.80.0"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)