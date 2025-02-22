import sys
import time
import threading
from web3 import Web3, HTTPProvider
import requests
import subprocess

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
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

# 提示用户输入私钥和IP
def get_user_input():
    accounts_and_proxies = []

    while True:
        private_key = input("请输入你的私钥：").strip()
        if not private_key:
            print("私钥不能为空，请重新输入。")
            continue

        use_proxy = input("是否使用代理IP？ (y/n): ").strip().lower()
        if use_proxy == 'y':
            proxy = input("请输入代理IP（格式：http://username:password@proxy_address:port）：").strip()
            accounts_and_proxies.append({"private_key": private_key, "proxy": proxy})
        else:
            accounts_and_proxies.append({"private_key": private_key, "proxy": None})

        another = input("是否继续输入另一个账号？ (y/n): ").strip().lower()
        if another != 'y':
            break

    return accounts_and_proxies

# 执行交易
def perform_transaction(private_key, proxy_url):
    while True:
        try:
            # 设置代理
            session = requests.Session()
            if proxy_url:
                session.proxies = {
                    'http': proxy_url,
                    'https': proxy_url,
                }
            provider = HTTPProvider(RPC_URL, session=session)
            web3 = Web3(provider)

            if not web3.is_connected():
                print(f"无法通过代理 {proxy_url} 连接到节点")
                return

            # 从私钥获取账户地址
            account = web3.eth.account.from_key(private_key)
            address = account.address

            # 输出当前账号和使用的代理 IP
            print(f"账号 {address} 使用代理 {proxy_url}")

            # 获取合约实例
            contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

            # 获取当前区块的 baseFeePerGas
            latest_block = web3.eth.get_block('latest')
            base_fee_per_gas = latest_block['baseFeePerGas']

            # 设置 maxPriorityFeePerGas，例如 2 Gwei
            max_priority_fee_per_gas = web3.to_wei('2', 'gwei')

            # 计算 maxFeePerGas
            max_fee_per_gas = base_fee_per_gas + max_priority
