import asyncio
import aiohttp
from aiohttp import BasicAuth
from web3 import AsyncWeb3
from consts import *
from models import *
from logger import logger


class Client:
    def __init__(self):
        self.w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(POLYGON_RPC))
        self.token_contract = self.w3.eth.contract(self.w3.to_checksum_address(TOKEN_ADDRESS), abi=ERC20_ABI)

    @staticmethod
    async def fetch_goldrush(method: str, url: str, params: dict = None):
        async with aiohttp.ClientSession(
                headers={'Content-Type': 'application/json'}, auth=BasicAuth(GOLDRUSH_API_TOKEN, ),
                timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            logger.info(f'{method} {url} params={params}')
            while True:
                try:
                    response = await session.request(method, url, params=params)
                    data = await response.json()
                    return response, data
                except TimeoutError:
                    logger.info(f'Got timeout after 10 sec')
                    ...

    async def get_balance(self, owner_address: str) -> TokenAmount:
        token = await self.get_token_info(self.token_contract.address)
        balance = await self.token_contract.functions.balanceOf(self.w3.to_checksum_address(owner_address)).call()
        token_amount = TokenAmount(owner_address, balance, token, True)
        logger.info(token_amount)
        return token_amount

    async def get_balance_batch(self, addresses: list[str]) -> list[TokenAmount]:
        batch_balance = await asyncio.gather(*[self.get_balance(address) for address in addresses])
        logger.info(batch_balance)
        return batch_balance

    async def get_top_holders(self, n: int) -> list[TokenAmount]:
        response, data = await self.fetch_goldrush(
            'GET',
            f'https://api.covalenthq.com/v1/matic-mainnet/tokens/{self.token_contract.address}/token_holders_v2/'
        )
        data = data['data']['items']
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
        logger.info(top_holders)
        return top_holders

    async def _get_top_holder_with_transaction_date(self, holder: TokenAmount) -> str:
        response, data = await self.fetch_goldrush(
            'GET',
            f'https://api.covalenthq.com/v1/matic-mainnet/address/{holder.owner_address}/transactions_summary/'
        )
        return data['data']['items'][0]['latest_transaction']['block_signed_at']

    async def get_top_holders_with_transaction_date(self, n: int) -> list:
        holders = await self.get_top_holders(n)
        tx_dates = await asyncio.gather(*[self._get_top_holder_with_transaction_date(holder) for holder in holders])
        result = [(holder.owner_address, holder.format_ether(), date) for holder, date in zip(holders, tx_dates)]
        logger.info(result)
        return result

    async def get_token_info(self, address: str = TOKEN_ADDRESS) -> Token:
        contract = self.w3.eth.contract(self.w3.to_checksum_address(address), abi=ERC20_ABI)
        token = Token.get_instance(address) or Token(
            address,
            *(await asyncio.gather(
                contract.functions.name().call(),
                contract.functions.decimals().call(),
                contract.functions.symbol().call(),
                contract.functions.totalSupply().call()
            ))
        )
        logger.info(token)
        return token


async def main():
    client = Client()
    await client.get_top_holders_with_transaction_date(3)


if __name__ == '__main__':
    asyncio.run(main())
