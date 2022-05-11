from setuptools import setup

# Requirements
requirements = [
    "requests",
    "appdirs"
]


setup(
    name="gazelle_api",
    version="1.0.0",
    description="Python API for Gazelle",
    url="https://github.com/hibikidesu/gazelle_api_py",
    author="Hibiki",
    license_files=("LICENSE",),
    py_modules=["gazelle_api"],
    python_requires=">=3.7",
    install_requires=requirements,
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities"
    ]
)
