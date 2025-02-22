import tkinter as tk
from tkinter import messagebox
from web3 import Web3
import threading

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
    exit()

# 创建 GUI 界面
root = tk.Tk()
root.title("交易发送器")

# 创建标签和输入框，让用户输入私钥
tk.Label(root, text="请输入您的私钥：").pack(pady=5)
private_key_entry = tk.Entry(root, show="*", width=50)
private_key_entry.pack(pady=5)

# 创建显示交易哈希值的标签
tx_label = tk.Label(root, text="")
tx_label.pack(pady=10)

# 定义按钮点击事件的处理函数
def send_transaction():
    private_key = private_key_entry.get()
    if not private_key:
        messagebox.showwarning("警告", "请先输入您的私钥！")
        return

    # 使用多线程避免阻塞 GUI
    threading.Thread(target=perform_transaction, args=(private_key,)).start()

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

        # 更新 UI 显示交易哈希
        tx_hash_str = web3.toHex(txn_hash)
        tx_label.config(text=f"交易已发送，哈希值：{tx_hash_str}")

        # 等待交易确认
        txn_receipt = web3.eth.wait_for_transaction_receipt(txn_hash)

        # 更新 UI 显示交易确认信息
        tx_label.config(text=f"交易已确认，哈希值：{tx_hash_str}")

    except Exception as e:
        # 捕获异常并在 UI 中显示
        tx_label.config(text=f"交易失败：{str(e)}")
        messagebox.showerror("错误", f"交易失败：{str(e)}")

# 创建发送交易的按钮
send_button = tk.Button(root, text="发送交易", command=send_transaction)
send_button.pack(pady=20)

# 运行 GUI 主循环
root.mainloop()
