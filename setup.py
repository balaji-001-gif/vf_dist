from setuptools import setup, find_packages

setup(
    name="freshroute",
    version="1.0.0",
    description="Farm to Customer Distribution Platform",
    author="Your Company",
    author_email="admin@freshroute.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        "requests>=2.28.0",
        "twilio>=8.0.0",
        "paho-mqtt>=1.6.0",
        "reportlab>=4.0.0",
        "weasyprint>=59.0",
        "pandas>=2.0.0",
        "openpyxl>=3.1.0",
    ],
)
