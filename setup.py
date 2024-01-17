from setuptools import setup, find_packages

# Assurez-vous d'avoir importé les fonctions nécessaires de votre projet
def parse_requirements():
    with open("requirements.txt", 'r') as file:
        requirements = file.readlines()
        requirements = [r.strip() for r in requirements]
        requirements = [r for r in requirements if r and not r.startswith('#')]
    return requirements
setup(
    name='sense',
    version='0.1.4',
    description='Daemon for Model Inference and Auto-Scaling for ρ Subnet',
    long_description='This repository includes a daemon service designed to automate the inference process for Large Language Models (LLMs) / GenAI models and manage the auto-scaling of resources. The daemon intelligently adjusts computational resources in response to real-time demand and system performance, ensuring high efficiency and robust model performance.',
    author='Cortex Foundation',
    author_email='flavia@cortex.foundation',
    packages=find_packages(),
    install_requires=[
        parse_requirements()
    ],
    entry_points={
        'console_scripts': [
            'sense = cli:run',
        ],
    },
)