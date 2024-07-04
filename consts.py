import json
import os
from dotenv import load_dotenv
load_dotenv()

POLYGON_RPC = 'https://polygon-rpc.com/'
TOKEN_ADDRESS = '0x1a9b54a3075119f1546c52ca0940551a6ce5d2d0'
SOME_ADDRESS = '0x51f1774249Fc2B0C2603542Ac6184Ae1d048351d'
SOME_ADDRESSES = [SOME_ADDRESS, '0x4830AF4aB9cd9E381602aE50f71AE481a7727f7C']
with open('erc20.json', encoding='utf-8') as f:
    ERC20_ABI = json.load(f)
GOLDRUSH_API_TOKEN = os.getenv('GOLDRUSH_API_TOKEN')
