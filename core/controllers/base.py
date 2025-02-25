from .generic import Controller
from typing import ClassVar, Generic, TypeVar
from core.service import BaseService

SERVICE = TypeVar('SERVICE', bound=BaseService)

class BaseController(Controller, Generic[SERVICE]):

    service: ClassVar[SERVICE]


    async def get(self, pk: SERVICE.repository.pk_field):
        return await self.service.get_by_id(pk)

