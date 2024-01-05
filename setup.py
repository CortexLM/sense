from setuptools import setup, find_packages

# Assurez-vous d'avoir importé les fonctions nécessaires de votre projet

setup(
    name='sense',
    version='0.0.1',
    description='Daemon for Model Inference and Auto-Scaling for ρ Subnet',
    long_description='This repository includes a daemon service designed to automate the inference process for Large Language Models (LLMs) / GenAI models and manage the auto-scaling of resources. The daemon intelligently adjusts computational resources in response to real-time demand and system performance, ensuring high efficiency and robust model performance.',
    author='Cortex Foundation',
    author_email='flavia@cortex.foundation',
    packages=find_packages(),
    install_requires=[

    ],
    entry_points={
        'console_scripts': [
            'sense = cli:run',
        ],
    },
)