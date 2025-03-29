from web3 import Web3
from datetime import datetime
from loguru import logger

logger.add('log.log', format='{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}', level='DEBUG')

RPC = "https://rpc.soneium.org"
w3 = Web3(Web3.HTTPProvider(RPC))

WALLETS = open("wallets.txt")
WALLETS_TO_GET_BALANCE = []

now = datetime.now()
formatted_date = now.strftime("%d-%m-%Y %H:%M:%S")

nft_contract_address = "0x2A21B17E366836e5FFB19bd47edB03b4b551C89d"
token_id = 0

erc1155_abi = [
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "account",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "id",
                "type": "uint256"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

nft_contract = w3.eth.contract(address=w3.to_checksum_address(nft_contract_address), abi=erc1155_abi)

source_data = {}
for line in WALLETS.readlines():
    if line.strip():
        line = line.strip()

        if line[:2] != '0x':
            line = '0x' + line

        if len(line) > 50:
            recipient_address = w3.eth.account.from_key(line).address
            WALLETS_TO_GET_BALANCE.append(recipient_address)
            source_data[recipient_address] = line
        else:
            WALLETS_TO_GET_BALANCE.append(line)
            source_data[line] = line

def write_failed_wallet(address: str):
    with open('failed.txt', 'a', encoding="utf-8") as f:
        f.write(f'{address}\n')

def write_wallet_with_badge(address: str):
    with open('with_badge.txt', 'a', encoding="utf-8") as f:
        f.write(f'{address}\n')

def write_wallet_without_badge(address: str):
    with open('without_badge.txt', 'a', encoding="utf-8") as f:
        f.write(f'{address}\n')

def get_balance():
    success_wallets = 0

    for wallet in WALLETS_TO_GET_BALANCE:
        try:
            wallet_address = Web3.to_checksum_address(wallet)
            amount = nft_contract.functions.balanceOf(wallet_address, token_id).call()
            if amount > 0:
                logger.success(f"{wallet} | Soneium OG Badge was found on the wallet")
                write_wallet_with_badge(f"{wallet}")
                success_wallets += 1
            else:
                logger.info(f"{wallet} | Current address doesn't hold this nft")
                write_wallet_without_badge(source_data[wallet])
        except Exception as e:
            print(e)
            logger.error(f"{wallet} | Error while receiving the balance")
            write_failed_wallet(source_data[wallet])


    logger.success(f"Total hold: {success_wallets}/{len(WALLETS_TO_GET_BALANCE)}")

write_wallet_with_badge(f'-----------{formatted_date}------------')
write_wallet_without_badge(f'-----------{formatted_date}------------')
write_failed_wallet(f'-----------{formatted_date}------------')

if __name__ == '__main__':
    get_balance()
