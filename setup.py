from setuptools import setup, find_packages

setup(
    name="Flashcards",
    version="1.0",
    description="Simple flashcard app",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
