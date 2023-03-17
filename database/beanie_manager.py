from dataclasses import dataclass
from typing import List, Type

from beanie import init_beanie, Document

__all__ = ['BeanieManager', 'BeanieConnectData']

from motor.motor_asyncio import AsyncIOMotorClient

from untils.role_manager import RoleManager, RoleCarrier


@dataclass
class BeanieConnectData:
    username: str
    password: str
    host: str
    port: int
    database: int


class BeanieManager:
    def __init__(self,models: List[Type[Document]], connect_data: BeanieConnectData, role_manager: RoleManager):
        self._connect_data = connect_data
        self._role_manager = role_manager
        self._models = models

    async def init(self):
        for model in [model for model in self._models if issubclass(model, RoleCarrier)]:
            model.init_role_manager(self._role_manager)
        client = AsyncIOMotorClient(f'mongodb://{self._connect_data.username}:{self._connect_data.password}@{self._connect_data.host}:{self._connect_data.port}/{self._connect_data.database}?authSource=admin&directConnection=true')
        await init_beanie(document_models=self._models, database=client[self._connect_data.database])
