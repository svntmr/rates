"""create codes table

Revision ID: bc2e6c418b6f
Revises:
Create Date: 2022-12-25 22:50:38.972153

"""
from collections import defaultdict
from typing import List, Mapping, Set

from alembic import op
from rates.database.engine import get_engine
from sqlalchemy import text
from sqlalchemy.engine import Connection

# revision identifiers, used by Alembic.
revision = "bc2e6c418b6f"
down_revision = None
branch_labels = None
depends_on = None


def get_region_ports(connection: Connection, region: str) -> List[str]:
    """
    Returns ports for the given region

    :param connection: sqlalchemy connection
    :type connection: Connection
    :param region: region slug
    :type region: str
    :return: list of region ports
    :rtype: List[str]
    """
    region_ports = (
        connection.execute(
            text("SELECT code FROM ports WHERE parent_slug = :parent_slug "),
            {"parent_slug": region},
        )
        .scalars()
        .all()
    )
    return region_ports


def build_region_to_port_connection(
    connection: Connection, regions: List[Mapping[str, str]]
) -> Mapping[str, Set[str]]:
    """
    Returns connections between region and ports
    Supports cases when region has parent and children regions
    Algorithm is similar to Breadth First search

    :param connection: sqlalchemy connection
    :type connection: Connection
    :param regions: list of regions with slug and parent slug
    :type regions: List[Mapping[str, str]]
    :return: connections between region and ports
    :rtype: Mapping[str, Set[str]]
    """
    region_to_port: Mapping[str, Set[str]] = defaultdict(set)
    for region in regions:
        # get and store region ports
        region_ports = get_region_ports(connection, region["slug"])
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
                subregion_ports = get_region_ports(connection, subregion["slug"])
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


def get_codes_table_values(connection: Connection) -> List[Mapping[str, str]]:
    """
    Creates values for `codes` table

    :param connection: sqlalchemy connection
    :type connection: Connection
    :return: list of values as mapping with `key` and `code` fields
    :rtype: List[Mapping[str, str]]
    """
    regions: List[Mapping[str, str]] = [
        row
        for row in connection.execute(
            text("SELECT slug, parent_slug FROM regions")
        ).mappings()
    ]

    region_to_port = build_region_to_port_connection(connection, regions)

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
    # table stores region slug/port code - port code connection to simplify
    # data querying (allows to handle ports and regions in one way)
    engine = get_engine()
    with engine.connect() as connection:
        # create table first
        create_table_query = text(
            "CREATE TABLE codes (key text NOT NULL, code text NOT NULL )"
        )
        connection.execute(create_table_query)

        # fill it up with data
        insert_values = get_codes_table_values(connection)
        insert_query = text("INSERT INTO codes (key, code) VALUES (:key, :code)")
        connection.execute(insert_query, insert_values)
        # connection actually has this method!
        connection.commit()  # type: ignore[attr-defined]


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS codes")
