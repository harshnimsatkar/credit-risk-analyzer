from setuptools import setup, find_packages


def get_requirements(file_path: str):
    requirements = []
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and line != "-e .":
                requirements.append(line)
    return requirements


setup(
    name="credit-risk-analyzer",
    version="1.0.0",
    author="Harsh Nimsatkar",
    author_email="nimsatkarharsh@gmail.com",
    description="End-to-end credit card fraud detection using SQL rules + LightGBM",
    packages=find_packages(),
    install_requires=get_requirements("requirements.txt"),
)