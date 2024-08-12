from setuptools import find_packages, setup

setup(
    name="moxie_dune",
    packages=find_packages(exclude=["moxie_dune_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud",
        "requests",
        "gql",
        "dune_client"
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
