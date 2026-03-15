from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="finambot",                # Имя пакета (будет использоваться при import finbot)
    version="0.1.0",              # Версия
    author="Miha",           # Ваше имя
    description="Trading bot for Finam API with ML signals",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MihaBEST/FinamBot", # Ссылка на ваш репо
    packages=find_packages(),     # Автоматически находит все пакеты (папки с __init__.py)
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        # Если хотите запускать бота командой в терминале (опционально)
        "console_scripts": [
            "finbot-run=finbot.bot:run_async", 
        ],
    },
)
