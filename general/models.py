from __future__ import annotations
from httpx import Client, AsyncClient, Response as httpxResponse
from typing import Any


class ApiCall:
    URL: str
    CLIENT_TIMEOUT: int

    def __init__(self, route: str, timeout: int = 15):
        self.URL = "https://riseofkingsonline.com/api/" + route.strip('/')
        self.CLIENT_TIMEOUT = timeout

    async def _fetch(self) -> httpxResponse:
        async with AsyncClient(timeout=self.CLIENT_TIMEOUT) as client:
            response = await client.get(self.URL)
            return response

    def _sync_fetch(self) -> httpxResponse:
        with Client(timeout=self.CLIENT_TIMEOUT) as client:
            response = client.get(self.URL)
            return response


def from_class_array(data: list, model: Any):
    if not data:
        return []
    try:
        return [model.parse(i)[0] for i in data]
    except Exception as e:
        raise Exception(f"Model is not valid. - {e}")


class Response:
    _RESOLVERS = {}
    _ALIASES: dict[str: str] = {}
    MODEL_NAME: str = ""
    success: bool

    @classmethod
    def parse(cls, data: dict[str:Any]):
        responses = []
        if not data.get("success", True):
            raise Exception("API Error.")

        new = cls()
        for key, value in data.items():
            if key in cls._RESOLVERS:
                if isinstance(value, list):
                    value = from_class_array(value, cls._RESOLVERS[key])
                elif type(cls._RESOLVERS[key]) is list:
                    for conversion in cls._RESOLVERS[key]:
                        value = conversion(value)
                else:
                    value = cls._RESOLVERS[key](value)
            setattr(new, key, value)
            if key in cls._ALIASES:
                setattr(new, cls._ALIASES[key], value)
        responses.append(new)

        return responses


class AlliancesQuery(ApiCall):
    def __init__(self, alliance_id: int):
        super().__init__(route=f"/alliance/{alliance_id}")

    async def fetch(self) -> AllianceResponse:
        return AllianceResponse.parse(await self._fetch())[0]  # noqa

    def sync_fetch(self) -> AllianceResponse:
        return AllianceResponse.parse(self._sync_fetch().json())[0]  # noqa


class KingdomQuery(ApiCall):
    def __init__(self, kingdom_id: int):
        super().__init__(route=f"/kingdom/{kingdom_id}")

    async def fetch(self) -> KingdomResponse:
        return KingdomResponse.parse(await self._fetch())[0]  # noqa

    def sync_fetch(self) -> KingdomResponse:
        return KingdomResponse.parse(self._sync_fetch().json())[0]  # noqa


class KingdomsQuery(ApiCall):
    def __init__(self):
        super().__init__(route=f"/kingdoms/")

    async def fetch(self) -> KingdomsResponse:
        return KingdomsResponse.parse(await self._fetch())[0]  # noqa

    def sync_fetch(self) -> KingdomsResponse:
        return KingdomsResponse.parse(self._sync_fetch().json())[0]  # noqa


class Alliance:
    alliance_id: int
    alliance_name: str
    alliance_score: float
    alliance_member_count: int
    government_ids: int


class Kingdom:
    kingdom_id: int
    kingdom_name: str
    kingdom_leader: str
    kingdom_score: float
    kingdom_population: int
    kingdom_id: int
    calvary: int
    ships: int
    housing: int
    housing: int
    water_wells: int
    lumber_mill: int
    iron_mines: int
    barracks: int
    docks: int
    watch_towers: int
    hospitals: int
    schools: int
    defensive_slots: int


class AllianceResponse(Response, Alliance):
    ...


class KingdomResponse(Response, Kingdom):
    ...


class KingdomsResponse(Response):
    _RESOLVERS = {
        "kingdoms": KingdomResponse
    }
    kingdoms: list[Kingdom]
