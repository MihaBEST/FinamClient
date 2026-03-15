from setuptools import setup, find_packages
import os

# Чтение требований из requirements.txt
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

# Чтение README для описания
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Finam Trading Bot"

setup(
    name="finbot",                  # Имя пакета
    version="0.1.0",                # Версия
    author="MihaBEST",              # Ваше имя
    description="Trading bot for Finam API",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/MihaBEST/FinamBot.git",
    packages=find_packages(),       # Автоматически находит пакеты (папки с __init__.py)
    python_requires=">=3.8",
    install_requires=read_requirements(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
