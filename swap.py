import sys
import time
import threading
from web3 import Web3, HTTPProvider
import requests
import subprocess

# 安装依赖
def install_dependencies():
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'web3', 'requests'])
        print("依赖安装成功")
    except subprocess.CalledProcessError as e:
        print(f"安装依赖时出错: {str(e)}")
        sys.exit(1)

install_dependencies()

# 设置连接到区块链节点的 RPC URL
RPC_URL = 'https://rpc.nexus.xyz/http'

# 智能合约地址和 ABI
CONTRACT_ADDRESS = '0x6DDc7dd77CbeeA3445b70CB04E0244BBa245e011'
ABI = [
    {
        "constant": False,
        "inputs": [],
        "name": "increment",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "getCount",
        "outputs
