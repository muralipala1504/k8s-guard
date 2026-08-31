from setuptools import setup, find_packages

setup(
    name="k8s-guard",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "kubernetes>=28.1.0",
        "gradio>=4.26.0",
        "sqlalchemy>=2.0.25",
        "slack-sdk>=3.27.0",
        "pyyaml>=6.0.1",
        "click>=8.1.7",
        "rich>=13.7.0",
        "python-dotenv>=1.0.1",
    ],
    entry_points={
        "console_scripts": [
            "k8s-guard=k8s_guard.main:cli",
        ],
    },
)
