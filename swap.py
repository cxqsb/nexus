import sys
import time
import threading
from web3 import Web3, HTTPProvider
import requests
import subprocess

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
            max_fee_per_gas = base_fee_per_gas + max_priority_fee_per_gas

            # 构建交易
            transaction = contract.functions.increment().build_transaction({
                'from': address,
                'nonce': web3.eth.get_transaction_count(address),
                'gas': 300000,
                'maxFeePerGas': int(max_fee_per_gas),
                'maxPriorityFeePerGas': int(max_priority_fee_per_gas),
                'chainId': web3.eth.chain_id
            })

            # 签名交易
            signed_txn = web3.eth.account.sign_transaction(transaction, private_key)

            # 发送交易
            txn_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)

            tx_hash_str = web3.to_hex(txn_hash)
            print(f"账号 {address}: 交易已发送，哈希值：{tx_hash_str}")

            # 等待交易确认
            txn_receipt = web3.eth.wait_for_transaction_receipt(txn_hash)
            print(f"账号 {address}: 交易已确认，区块号：{txn_receipt.blockNumber}")

            # 等待30秒后再次执行
            time.sleep(30)

        except Exception as e:
            print(f"账号 {address}: 交易失败：{str(e)}")
            # 如果发生错误，等待一段时间再重试
            time.sleep(60)

def main():
    accounts_and_proxies = get_user_input()

    threads = []
    for account_proxy in accounts_and_proxies:
        private_key = account_proxy["private_key"]
        proxy_url = account_proxy["proxy"]
        thread = threading.Thread(target=perform_transaction, args=(private_key, proxy_url))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
