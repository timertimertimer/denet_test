import asyncio
import aiohttp
from decimal import Decimal
from pprint import pprint
from aiohttp import BasicAuth
from web3 import AsyncWeb3
from consts import *
from models import *


class Client:
    def __init__(self):
        self.w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(POLYGON_RPC))
        self.token_contract = self.w3.eth.contract(self.w3.to_checksum_address(TOKEN_ADDRESS), abi=ERC20_ABI)

    @staticmethod
    async def fetch_goldrush(method: str, url: str, params: dict = None):
        async with aiohttp.ClientSession(
                headers={'Content-Type': 'application/json'}, auth=BasicAuth(GOLDRUSH_API_TOKEN, )
        ) as session:
            print(method, url, params)
            return await session.request(method, url, params=params)

    async def get_balance(self, owner_address: str) -> TokenAmount:
        token = await self.get_token_info(self.token_contract.address)
        balance = await self.token_contract.functions.balanceOf(self.w3.to_checksum_address(owner_address)).call()
        token_amount = TokenAmount(owner_address, balance, token, True)
        pprint(token_amount)
        return token_amount

    async def get_balance_batch(self, addresses: list[str]) -> list[TokenAmount]:
        batch_balance = await asyncio.gather(*[self.get_balance(address) for address in addresses])
        pprint(batch_balance)
        return batch_balance

    async def get_top_holders(self, n: int) -> list[TokenAmount]:
        response = await self.fetch_goldrush(
            'GET',
            f'https://api.covalenthq.com/v1/matic-mainnet/tokens/{self.token_contract.address}/token_holders_v2/'
        )
        data = (await response.json())['data']['items']
        top_holders = [
            TokenAmount(
                holder['address'],
                holder['balance'],
                Token(
                    self.token_contract.address,
                    holder['contract_name'],
                    holder['contract_decimals'],
                    holder['contract_ticker_symbol'],
                    holder['total_supply'],
                ),
                True
            )
            for holder in data[:n]
        ]
        pprint(top_holders)
        return top_holders

    async def _get_top_holder_with_transaction_date(self, holder: TokenAmount) -> str:
        response = await self.fetch_goldrush(
            'GET',
            f'https://api.covalenthq.com/v1/matic-mainnet/address/{holder.owner_address}/transactions_summary/'
        )
        return (await response.json())['data']['items'][0]['latest_transaction']['block_signed_at']

    async def get_top_holders_with_transaction_date(self, n: int) -> list:
        holders = await self.get_top_holders(n)
        return list(zip(holders, await asyncio.gather(
            *[self._get_top_holder_with_transaction_date(holder) for holder in holders])))

    async def get_token_info(self, address) -> Token:
        token = Token(
            address,
            *(await asyncio.gather(
                self.token_contract.functions.name().call(),
                self.token_contract.functions.decimals().call(),
                self.token_contract.functions.symbol().call(),
                self.token_contract.functions.totalSupply().call()
            ))
        )
        print(token)
        return token


async def main():
    client = Client()
    await client.get_top_holders_with_transaction_date(1)


if __name__ == '__main__':
    asyncio.run(main())
