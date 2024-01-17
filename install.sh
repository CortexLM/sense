#!/bin/bash

# Color variables
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Initial Confirmation
echo -e "${BLUE}************************************************\n\
* This script will perform the following actions:\n\
* 1. Install Miniconda.\n\
* 2. Clone the GitHub repository CortexLM/sense.\n\
* 3. Create and activate a conda environment named 'sense'.\n\
* 4. Install CUDA Toolkit.\n\
* 5. Detect CUDA version and install PyTorch.\n\
* 6. Install project dependencies.\n\
************************************************${NC}\n${RED}* Please do not install Sense on the same server as your validator/miner. \n${BLUE}* Please confirm to proceed (y/n):${NC}"
read -r choice
if [ "$choice" != "y" ]; then
    echo -e "${RED}Installation aborted.${NC}"
    exit 1
fi

# Step 1: Installation of Miniconda
echo -e "${BLUE}Step 1: Installing Miniconda${NC}"
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh
~/miniconda3/bin/conda init bash
source ~/miniconda3/etc/profile.d/conda.sh

# Step 2: Cloning GitHub Repository
echo -e "${BLUE}Step 2: Cloning GitHub Repository${NC}"
git clone --branch 0.1.4 https://github.com/CortexLM/sense /srv/sense
cd /srv/sense
# Step 3: Creating and Activating Conda Environment
echo -e "${BLUE}Step 3: Creating and Activating Conda Environment 'sense'${NC}"
conda create -n sense python=3.10 -y
conda activate sense

# Step 4: Installation of CUDA Toolkit
echo -e "${BLUE}Step 4: Installing CUDA Toolkit${NC}"
conda install cudatoolkit -y

# Step 5: Detect CUDA Version and Install PyTorch
echo -e "${BLUE}Step 5: Detecting CUDA Version and Installing PyTorch${NC}"
cuda_version=$(nvcc --version | grep "release" | sed 's/.*release \(.*\),.*/\1/')
echo "CUDA Version Detected: $cuda_version"
if [[ $cuda_version == 11.* ]]; then
    pip3 install xformers torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 -U
elif [[ $cuda_version == 12.* ]]; then
    pip3 install xformers torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 -U
else
    pip3 install xformers torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 -U
fi

# Step 6: Installation of Project Dependencies
echo -e "${BLUE}Step 6: Installing Project Dependencies${NC}"
pip3 install ninja
if [[ $cuda_version == 11.* ]]; then
    pip3 install https://github.com/chengzeyi/stable-fast/releases/download/v1.0.1/stable_fast-1.0.1+torch212cu118-cp310-cp310-manylinux2014_x86_64.whl
elif [[ $cuda_version == 12.* ]]; then
    pip3 install https://github.com/chengzeyi/stable-fast/releases/download/v1.0.1/stable_fast-1.0.1+torch212cu121-cp310-cp310-manylinux2014_x86_64.whl
fi

pip3 install -r requirements.txt
pip3 install -e .

echo -e "${BLUE}To access the conda environment, type bash and conda activate sense.${NC}"
echo -e "${BLUE}Installation completed successfully.${NC}"
