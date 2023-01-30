"""create codes table

Revision ID: bc2e6c418b6f
Revises:
Create Date: 2022-12-25 22:50:38.972153

"""
import asyncio
from collections import defaultdict
from typing import List, Mapping, Sequence, Set

import nest_asyncio
from alembic import op
from rates.database.engine import get_engine
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

# revision identifiers, used by Alembic.
revision = "bc2e6c418b6f"
down_revision = None
branch_labels = None
depends_on = None


async def get_region_ports(connection: AsyncConnection, region: str) -> Sequence[str]:
    """
    Returns ports for the given region

    :param connection: sqlalchemy connection
    :type connection: AsyncConnection
    :param region: region slug
    :type region: str
    :return: list of region ports
    :rtype: Sequence[str]
    """
    region_ports_query = await connection.execute(
        text("SELECT code FROM ports WHERE parent_slug = :parent_slug "),
        {"parent_slug": region},
    )
    region_ports: Sequence[str] = region_ports_query.scalars().all()
    return region_ports


async def build_region_to_port_connection(
    connection: AsyncConnection, regions: List[Mapping[str, str]]
) -> Mapping[str, Set[str]]:
    """
    Returns connections between region and ports
    Supports cases when region has parent and children regions
    Algorithm is similar to Breadth First search

    :param connection: sqlalchemy connection
    :type connection: AsyncConnection
    :param regions: list of regions with slug and parent slug
    :type regions: List[Mapping[str, str]]
    :return: connections between region and ports
    :rtype: Mapping[str, Set[str]]
    """
    region_to_port: Mapping[str, Set[str]] = defaultdict(set)
    for region in regions:
        # get and store region ports
        region_ports = await get_region_ports(connection, region["slug"])
        region_to_port[region["slug"]].update(region_ports)
        # check if region has subregions
        if subregions := [
            subregion
            for subregion in regions
            if subregion["parent_slug"] == region["slug"]
        ]:
            while subregions:
                subregion = subregions.pop()
                # get and store subregion ports
                subregion_ports = await get_region_ports(connection, subregion["slug"])
                region_to_port[subregion["slug"]].update(subregion_ports)
                # append subregion ports into current region
                region_to_port[region["slug"]].update(subregion_ports)
                # check if subregion has subregions
                if region_subregions := [
                    subregion_subregion
                    for subregion_subregion in regions
                    if subregion_subregion["parent_slug"] == subregion["slug"]
                ]:
                    subregions.extend(region_subregions)
    return region_to_port


async def get_codes_table_values(
    connection: AsyncConnection,
) -> List[Mapping[str, str]]:
    """
    Creates values for `codes` table

    :param connection: sqlalchemy connection
    :type connection: AsyncConnection
    :return: list of values as mapping with `key` and `code` fields
    :rtype: List[Mapping[str, str]]
    """
    regions_query = await connection.execute(
        text("SELECT slug, parent_slug FROM regions")
    )
    regions: List[Mapping[str, str]] = [row for row in regions_query.mappings()]

    region_to_port = await build_region_to_port_connection(connection, regions)

    insert_values: List[Mapping[str, str]] = []
    unique_ports = set()
    # add region - port connection
    for region, ports in region_to_port.items():
        unique_ports.update(ports)
        for port in ports:
            insert_values.append({"key": region, "code": port})
    # add port - port connection
    for port in unique_ports:
        insert_values.append({"key": port, "code": port})
    return insert_values


def upgrade() -> None:
    # TODO(maybe): fix once alembic has better support for async I/O
    # Problem description:
    # as alembic creates event loop in env.py, the event loop will be already running
    # here - it's impossible to run tasks and wait for the result (trying to do so
    # will give the error "RuntimeError: This event loop is already running")
    # fresh event loop is required to run queries with async engine
    # Solution description:
    # nest_asyncio allows to create event loop inside another event loop
    # to solve this problem
    # Additional notes:
    # I don't like this solution, but in my opinion it's better than
    # having two database drivers
    nest_asyncio.apply()
    asyncio.run(create_and_fill_codes_table())


async def create_and_fill_codes_table():
    # table stores region slug/port code - port code connection to simplify
    # data querying (allows to handle ports and regions in one way)
    engine = get_engine()
    async with engine.connect() as connection:
        # create table first
        create_table_query = text(
            "CREATE TABLE codes ("
            "   key text NOT NULL, "
            "   code text NOT NULL, "
            "   PRIMARY KEY (key, code) "
            ")"
        )
        await connection.execute(create_table_query)

        # fill it up with data
        insert_values = await get_codes_table_values(connection)
        insert_query = text("INSERT INTO codes (key, code) VALUES (:key, :code)")
        await connection.execute(insert_query, insert_values)
        await connection.commit()


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS codes")
