from httpx import AsyncClient
from math import ceil
from asyncio import gather
from bs4 import BeautifulSoup
from ..models import AlliancesQuery

__all__ = ("fetch_members",)


async def fetch_members(alliance_id: int, member_count: int = None) -> list[int]:
    if not member_count:
        member_count = AlliancesQuery(alliance_id).sync_fetch().member_count

    total_pages = ceil(member_count / 15)
    async with AsyncClient() as client:
        coros = [client.get(url=f"https://riseofkingsonline.com/world/alliances/{alliance_id}?page={page}") for page in range(1, total_pages + 1)]
        fetched_pages = await gather(*coros)

    members = []

    for page in fetched_pages:
        bs_page = BeautifulSoup(page, "html.parser")
        first = True
        for row in bs_page.find("table").find_all("tr"):
            if first:
                first = False
                continue
            members.append(int(row.find_all("td")[1].find("a")["href"].replace("https://riseofkingsonline.com/kingdom/", "")))
    return members
