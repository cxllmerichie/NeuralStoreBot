from __future__ import annotations

from typing import Optional
import aiohttp
import os

import search


class Product:
    def __init__(self, product: dict):
        self.title: str = product['title']
        self.total: int = int(float(product['balance']))
        self.price: str = f"{product['price']} {product['currency']}"
        self.details: dict[str, str] = {tag['title']: tag['items'][0]['title'] for tag in product['tags']}  # FIXME: filter
        self.image_url: Optional[str] = product['image_path']

    @classmethod
    def init(cls, data: dict) -> Optional[Product]:
        if (
                not data['sku']  # skip non-product elements
                or
                not data['balance']  # skip non-product elements
                or
                not float(data['balance'])  # skip products with balance 0
        ):
            return
        return Product(data)

    def __str__(self) -> str:
        """
        :return: string representation of the product, supposed to be displayed in the Telegram message.
        """
        info = f"""<b>{self.title}</b>\n\nЦена: {self.price}\nВ наличии: {self.total}"""
        if details := '\n'.join(f'{key}: <i>{value}</i>' for key, value in self.details.items()):
            info += f"\n\n<u>Информация</u>:\n{details}"
        return info


class Data:  # FIXME: data actualization
    _url: str = 'https://api.dntrade.com.ua'
    _key: str = os.getenv('DNTRADE_KEY')

    products: list[Product] = []

    @property
    def titles(self) -> str:
        """
        :return: titles of all products, one per line.
        """
        return '\n'.join(product.title for product in self.products)

    async def collect(self) -> None:
        """
        Collect data about all products from all shops.
        :return: None.
        """
        async with aiohttp.ClientSession(base_url=self._url) as s_shops:
            async with s_shops.get(
                    url='/products/stores',
                    headers={'ApiKey': self._key}
            ) as r_shops:
                for store in list(filter(lambda s: s['is_sell'], (await r_shops.json())['stores'])):
                    async with aiohttp.ClientSession(base_url=self._url) as s_products:
                        async with s_products.post(
                                url='/products/list',
                                headers={'ApiKey': self._key},
                                params={'store_id': store['id']}
                        ) as r_products:
                            for product in (await r_products.json())['products']:
                                if product := Product.init(product):
                                    self.products.append(product)

    async def like(self, what: str) -> list[Product]:
        """
        Find list of products which match the criteria.
        :param what: element defining criteria.
        :return: list of products.
        """
        return [product for product in self.products if await search.is_match(what, product.title)]
