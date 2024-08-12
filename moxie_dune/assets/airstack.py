import json
import time

from dagster import asset
from gql import gql
from requests.exceptions import RequestException

from moxie_dune.constants import FT_SUBJECT_EARNINGS_JSON_PATH, FT_AUCTIONS_JSON_PATH, FT_SUBJECT_EARNINGS_BATCH_SIZE

all_entity_types = ["NETWORK", "CHANNEL", "USER"]


@asset(
    group_name="airstack",
    required_resource_keys={"airstack_client"}
)
def ft_auctions_json(context):
    """All Fan Token Auctions (FTAs)."""
    airstack_client = context.resources.airstack_client
    query = gql("""
    query GetFanTokenAuctions($cursor: String, $entityType: FarcasterFanTokenAuctionEntityType!) {
      FarcasterFanTokenAuctions(
        input: {
            blockchain: ALL,
            filter: {
                entityType: {_eq: $entityType},
                status: {_eq: COMPLETED}
            },
            order: {estimatedStartTimestamp: ASC},
            limit: 100,
            cursor: $cursor
        }
      ) {
        FarcasterFanTokenAuction {
          entityId
          entityType
          entitySymbol
          entityName
          status
        }
        pageInfo {
            hasNextPage
            nextCursor
        }
      }
    }
    """)

    result = {}
    for entityType in all_entity_types:
        variables = {
            "entityType": entityType,
        }

        entities = gql_execute_with_cursor(context, airstack_client, query, variables)

        # Group entities by type to simplify fetching batches of details later
        result[entityType] = entities

    with open(FT_AUCTIONS_JSON_PATH, "w") as f:
        json.dump(result, f)


@asset(
    group_name="airstack",
    deps=["ft_auctions_json"],
    required_resource_keys={"airstack_client"}
)
def ft_subject_earnings_json(context):
    """Lifetime Moxie earnings of Fan Token Subjects"""
    airstack_client = context.resources.airstack_client
    query = gql("""
    query GetMoxieEarnings($entityType: FarcasterMoxieEarningStatsEntityType!, $entityIds: [String!]) {
        FarcasterMoxieEarningStats(
            input: {
                blockchain: ALL,
                timeframe: LIFETIME,
                filter: {
                    entityType: {_eq: $entityType},
                    entityId: {_in: $entityIds}
                }
            }
        ) {
            FarcasterMoxieEarningStat {
                allEarningsAmountInWei
                endTimestamp
                startTimestamp                
                entityId
                entityType
            }
        }
    }
    """)

    with open(FT_AUCTIONS_JSON_PATH, "r") as f:
        fan_token_auctions_data = json.load(f)

    result = []
    for entity_type in all_entity_types:
        entity_data = fan_token_auctions_data[entity_type]

        # Build a map of (entityType, entityId) -> entitySymbol
        # This is the primary key used in subject token lookups
        symbol = {}
        for item in entity_data:
            key = item["entityId"]
            symbol[key] = item["entitySymbol"]

        # Process entities in batches
        for batch in to_batches(entity_data, FT_SUBJECT_EARNINGS_BATCH_SIZE):
            entity_ids = [
                # In FTA, it's "network:farcaster" but in earnings it's "FARCASTER"
                "FARCASTER" if item["entityType"] == "NETWORK" else item["entityId"]
                for item in batch
            ]

            variables = {
                "entityType": entity_type,
                "entityIds": entity_ids
            }

            context.log.debug(f"Fetching {variables}...")

            response = gql_execute(context, airstack_client, query, variables)

            entities = descend(response)
            for entity in entities:
                key = "network:farcaster" if entity["entityType"] == "NETWORK" else entity["entityId"]
                entity["entitySymbol"] = symbol[key]

            result.extend(entities)

    with open(FT_SUBJECT_EARNINGS_JSON_PATH, "w") as f:
        json.dump(result, f)


# NOTE Make sure you have an Airstack free plan so that rate limits aren't an issue
MAX_RETRIES = 10  # Number of retries
RETRY_DELAY = 2  # Delay between retries in seconds


def to_batches(lst, batch_size):
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]


def descend(dict):
    return dict[list(dict.keys())[0]]


def gql_execute(context, airstack_client, query, variables):
    # Retry logic for a single entity fetch
    for attempt in range(MAX_RETRIES):
        try:
            response = airstack_client.execute(query, variables)
            return descend(response)
        except RequestException as e:
            if attempt < MAX_RETRIES - 1:
                context.log.info(f"Request failed: {e}. Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                raise  # Re-raise the exception if max retries reached


def gql_execute_with_cursor(context, airstack_client, query, variables):
    all_data = []
    next_cursor = None
    page_no = 1

    while True:
        context.log.info(f"Fetching {variables} page {page_no}...")

        params = {"cursor": next_cursor, **variables}
        page = gql_execute(context, airstack_client, query, params)

        data_key = next(key for key in page if key != "pageInfo")
        data = page[data_key]
        page_info = page["pageInfo"]

        all_data.extend(data)

        if not page_info["hasNextPage"]:
            break

        next_cursor = page_info["nextCursor"]
        page_no += 1

    return all_data
