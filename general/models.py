from __future__ import annotations
from httpx import Client, AsyncClient, Response as httpxResponse
from typing import Any, TypedDict
from functools import cached_property
from math import floor

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

# Typed Dicts


class Resources(TypedDict, total=False):
    money: float
    food: float
    water: float
    lumber: float
    iron: float


# Queries

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
    id: int  # Alias of kingdom_id
    kingdom_name: str
    name: str  # Alias of kingdom_name
    kingdom_leader: str
    leader: str  # Alias of kingdom_leader
    kingdom_score: float
    score: float  # Alias of kingdom_score
    kingdom_population: int
    population: int  # Alias of kingdom_population
    warriors: int
    calvary: int
    cavalry: int  # Alias of calvary
    ships: int
    housing: int
    farms: int
    water_wells: int
    lumber_mill: int
    iron_mines: int
    barracks: int
    docks: int
    watch_towers: int
    hospitals: int
    schools: int
    defensive_slots: int

    @property
    def max_population(self) -> int:
        return (self.housing * 100) + 100

    @property
    def population_growth(self) -> int:
        return floor((self.housing * 10) * (1 - self.disease))

    @property
    def educated_population(self) -> int:
        return self.schools * 100

    @cached_property
    def total_buildings(self) -> int:
        return (
            self.housing +
            + self.farms
            + self.water_wells
            + self.lumber_mill
            + self.iron_mines
            + self.barracks
            + self.docks
            + self.watch_towers
            + self.hospitals
            + self.schools
        )

    @cached_property
    def crime(self) -> float:
        return round(
            min(max((
                ((self.kingdom_population / (self.total_buildings - self.watch_towers - self.hospitals + 1)) - (self.watch_towers * 10)) / 100
            ), 0), 1),
            4
        )

    @cached_property
    def disease(self) -> float:
        return round(
            min(max((
                ((self.kingdom_population / (self.total_buildings - self.watch_towers - self.hospitals + 1) * 2) - (self.hospitals * 5)) / 100
            ), 0), 1),
            4
        )

    @cached_property
    def income(self) -> Resources:
        return {
            "money": round(
                (((
                    (self.kingdom_population + (self.educated_population * 6)) -
                    (self.warriors + (self.calvary * 5) + (self.ships * 25))
                ) * 15) * (1 - self.crime)) - (
                    (self.warriors * 10) +
                    (self.calvary * 100) +
                    (self.ships * 1000)
                ), 2
            ),
            "water": round(
                (self.water_wells * 75) - ((
                    (self.kingdom_population * 1) +
                    (self.warriors * 2) +
                    (self.calvary * 4)
                ) / 4) - (self.farms * 2.5), 2
            ),
            "lumber": round(self.lumber_mill * 2.15, 2),
            "iron": round(self.iron_mines * 2.15, 2),
            "food": round(
                (self.farms * 75) - ((
                    self.kingdom_population +
                    (self.warriors * 2) +
                    (self.calvary * 4)
                ) / 4), 2
            )
        }


class AllianceResponse(Response, Alliance):
    ...


class KingdomResponse(Response, Kingdom):
    _ALIASES = {
        "kingdom_population": "population",
        "calvary": "cavalry",
        "kingdom_id": "id",
        "kingdom_name": "name",
        "kingdom_leader": "leader",
        "kingdom_score": "score",
    }


class KingdomsResponse(Response):
    _RESOLVERS = {
        "kingdoms": KingdomResponse
    }
    kingdoms: list[Kingdom]
