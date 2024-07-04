from decimal import Decimal

__all__ = ['Token', 'TokenAmount']


class Token:
    _instances = {}

    def __new__(
            cls,
            address: str,
            name: str,
            decimals: int,
            symbol: str,
            total_supply: int,
    ):
        if address not in cls._instances:
            cls._instances[address] = super().__new__(cls)
        return cls._instances[address]

    def __init__(
            self,
            address: str,
            name: str,
            decimals: int,
            symbol: str,
            total_supply: int,
    ):
        self.address = address
        self.name = name
        self.decimals = decimals
        self.symbol = symbol
        self.total_supply = total_supply

    def __str__(self):
        return '{' + (f'address: "{self.address}", symbol: "{self.symbol}", name: "{self.name}", totalSupply: '
                      f'{self.total_supply}, decimals: {self.decimals}') + '}'

    @classmethod
    def get_instance(cls, address: str):
        return cls._instances.get(address, None)


class TokenAmount:
    def __init__(
            self,
            owner_address: str,
            amount: int | float | str | Decimal,
            token: Token,
            wei: bool = False,
    ):
        self.owner_address = owner_address
        self.token = token
        if wei:
            self._wei: int = int(amount)
            self._ether: Decimal = self._convert_wei_to_ether(amount)
        else:
            self._wei: int = self._convert_ether_to_wei(amount)
            self._ether: Decimal = Decimal(str(amount))

    @property
    def wei(self):
        return self._wei

    @wei.setter
    def wei(self, value):
        self._wei = value
        self._ether = self._convert_wei_to_ether(value)

    @property
    def ether(self):
        return self._ether

    @ether.setter
    def ether(self, value):
        self._ether = value
        self._wei = self._convert_ether_to_wei(value)

    def format_ether(self) -> str:
        sign, digits, exponent = self.ether.as_tuple()
        num_decimal_places = abs(exponent)
        return f"{self.ether:.{num_decimal_places}f}"

    def _convert_wei_to_ether(self, amount: int | float | str | Decimal) -> Decimal:
        return Decimal(str(amount)) / 10 ** self.token.decimals

    def _convert_ether_to_wei(self, amount: int | float | str | Decimal) -> int:
        return int(Decimal(str(amount)) * 10 ** self.token.decimals)

    def __str__(self):
        return f"({self.owner_address}, {self.format_ether()} {self.token.symbol})"

    def __repr__(self):
        return self.__str__()
