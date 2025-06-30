from setuptools import setup, find_packages

setup(
    name="package",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langchain",
        "langgraph",
        "langchain_community",
        "langchain_groq",
    ],
    include_package_data=True
)
