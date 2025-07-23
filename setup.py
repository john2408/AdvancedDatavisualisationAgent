"""Setup file for the Visual Agent application."""

from setuptools import setup, find_packages

setup(
    name="visual-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.32.0",
        "plotly>=5.18.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "python-dotenv>=1.0.0",
        "psycopg2-binary>=2.9.9",
        "elasticsearch>=8.12.0",
        "requests>=2.31.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "cachetools>=5.3.0"
    ],
    python_requires=">=3.8",
) 