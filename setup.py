from setuptools import setup, find_packages

setup(
    name="gestionetudiant",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pymongo>=4.6.0",
        "redis>=5.0.0",
        "bcrypt>=4.0.0",
        "pandas>=2.0.0",
        "fpdf>=1.7.0",
        "openpyxl>=3.0.0",
        "python-dotenv>=1.0.0",
        "colorama>=0.4.0",
        "tabulate>=0.9.0",
        "email-validator>=2.0.0"
    ],
) 