<div align="center">

# **⚡️ Sense - Daemon for Flavia Project**
Daemon for Model Inference and Auto-Scaling for ρ Subnet

[![Discord Chat](https://img.shields.io/discord/308323056592486420.svg)](https://discord.gg/bittensor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 


[Discord](https://discord.gg/bittensor) • [Cortex Foundation](https://cortex.foundation/) • [Bittensor](https://bittensor.com/whitepaper)
</div>

#
### 🔴 This is an alpha version. Please report any bugs or suggest any improvements.
### 📋 Introduction
This repository includes a daemon service designed to automate the inference process for Large Language Models (LLMs) / GenAI models and manage the auto-scaling of resources. The daemon intelligently adjusts computational resources in response to real-time demand and system performance, ensuring high efficiency and robust model performance.

### ✨ Features
- **🤖 Automated Model Inference:** Streamlines the process of deploying LLMs for inference tasks.
- **⚖️ Dynamic Auto-Scaling:** Adjusts resource allocation based on current workload and performance metrics, optimizing for cost and efficiency.
- **👀 Continuous Monitoring:** Regularly checks system health and performance, ensuring reliable operation.
- **🛠️ Error Handling and Failover:** Implements robust error handling and failover mechanisms to maintain continuous service.

## 🔧 Installation

**Runpod Template** :  https://www.runpod.io/console/explore/1gty0lb4lw

**To install the script, follow these steps:**

**Download the script:**

```wget -q https://raw.githubusercontent.com/CortexLM/sense/0.2.4/install.sh```

**Make the script executable:**

```chmod  +x install.sh```

**Run the auto-installer:**

```./install.sh```

**Initialize conda environment:**

```bash```

```conda activate sense```

**Init Sense Directory:**

```cd /srv/sense && sense init```

**Generate config:**

```sense config init```


**Install Node.js and PM2:**

```curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash```

```export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"```

```[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"```

```nvm install --lts```

```npm i pm2 -g```



Then generate an API key, which will ask you to allocate the GPUs. You can only allocate one GPU for the Diffusion model, and (1,2 or 4 GPUs). To allocate them, simply enter the GPU ID.

For 8 GPUs :
Diffusions: ```4,5,6,7```
Turbomind ```0,1,2,3```

**Run:**

Miners ⛏️

```pm2 start run.py --name sense -- --process_name sense_daemon --host 0.0.0.0 --port 8080```
If an OOM error occurs, please modify --instance_num and decrease it.

Validators 🥇

```pm2 start run.py --name sense -- --process_name sense_daemon --host 0.0.0.0 --port 8080 --prevent_oom --instance_num 1```


## 📋 Requirements

### **Validators :**

1x80GB GPU or 3x48GB GPU

Storage: 300GB

RAM: 32GB


### **Miners :**

5x24GB GPU or 2x80GB GPU

Storage: 500GB

RAM: 64GB


## ⚖️ Support our Subnet: Assigning weights
As a validator in the Bittensor network, your support is crucial for the success and efficiency of subnets like Flavia. We invite you to consider assigning weights to our subnet, which will significantly contribute to its performance and the overall robustness of the network.

To allocate weights to the Flavia subnet, you can use the ```btcli root weights``` (**SN17**) command.

By assigning weights to our subnet, you play a vital role in enhancing its inference capabilities and overall contribution to the BitTensor network. Your support helps us maintain a high-performance, reliable, and efficient subnet for decentralized model inference.

We appreciate your contribution and thank you for your support in advancing decentralized AI with Flavia.




## 📜 License
This repository is licensed under the MIT License.
```text
# The MIT License (MIT)
# Copyright © 2023 Yuma Rao

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
```
