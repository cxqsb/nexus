import sys
from web3 import Web3
import time

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

# 创建连接到节点的 Web3 实例
web3 = Web3(Web3.HTTPProvider(RPC_URL))

# 检查连接
if not web3.is_connected():
    print("无法连接到 Nexus 节点。请检查网络连接和 RPC URL。")
    sys.exit()

def perform_transaction(private_key):
    try:
        # 从私钥获取账户地址
        account = web3.eth.account.from_key(private_key)

        # 获取合约实例
        contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

        # 构建交易
        transaction = contract.functions.increment().build_transaction({
            'from': account.address,
            'nonce': web3.eth.get_transaction_count(account.address),
            'gas': 300000,
            'gasPrice': web3.toWei('10', 'gwei')
        })

        # 签名交易
        signed_txn = web3.eth.account.sign_transaction(transaction, private_key)

        # 发送交易
        txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

        tx_hash_str = web3.toHex(txn_hash)
        print(f"交易已发送，哈希值：{tx_hash_str}")

        # 等待交易确认
        txn_receipt = web3.eth.wait_for_transaction_receipt(txn_hash)

        print(f"交易已确认，区块号：{txn_receipt.blockNumber}")
    except Exception as e:
        print(f"交易失败：{str(e)}")

def main():
    # 提示用户输入私钥
    private_key = input("请输入您的私钥：").strip()
    if not private_key:
        print("私钥不能为空！")
        sys.exit()

    # 持续执行交易
    while True:
        perform_transaction(private_key)
        # 等待30秒后再次执行
        time.sleep(30)

if __name__ == "__main__":
    main()
