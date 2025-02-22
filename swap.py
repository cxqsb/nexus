from web3 import Web3

# 输入你的私钥
private_key = input("请输入你的私钥: ")

# 连接到Nexus节点
rpc_url = 'https://rpc.nexus.xyz/http'
web3 = Web3(Web3.HTTPProvider(rpc_url))

# 检查是否成功连接到节点
if not web3.is_connected():
    print("无法连接到Nexus节点")
    exit()

# 设置钱包地址和私钥
account = web3.eth.account.from_key(private_key)

# 智能合约地址和 ABI
contract_address = '0x6DDc7dd77CbeeA3445b70CB04E0244BBa245e011'
abi = [
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

# 创建智能合约实例
contract = web3.eth.contract(address=contract_address, abi=abi)

# 创建一个函数来执行交易
def perform_transaction():
    try:
        # 构建交易
        transaction = contract.functions.increment().buildTransaction({
            'from': account.address,
            'nonce': web3.eth.getTransactionCount(account.address),
            'gas': 30000,
            'gasPrice': web3.toWei('10', 'gwei')  # 使用 10 gwei 的 gas price
        })

        # 签名交易
        signed_txn = web3.eth.account.signTransaction(transaction, private_key)

        # 发送交易
        txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print('Transaction sent:', web3.toHex(txn_hash))

        # 等待交易被确认
        txn_receipt = web3.eth.waitForTransactionReceipt(txn_hash)
        print('Transaction confirmed:', web3.toHex(txn_hash))

    except Exception as e:
        print('Error executing transaction:', str(e))

# 设置一个间隔来持续执行交易
import time

while True:
    perform_transaction()
    time.sleep(30)  # 每30秒执行一次交易
