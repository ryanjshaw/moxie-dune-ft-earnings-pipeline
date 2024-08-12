from dagster import EnvVar
from gql import Client
from gql.transport.requests import RequestsHTTPTransport

from moxie_dune.constants import AIRSTACK_GQL_ENDPOINT

airstack_client = Client(
    transport=RequestsHTTPTransport(
        url=AIRSTACK_GQL_ENDPOINT,
        headers={
            'Authorization': EnvVar("GRAPHQL_AUTH_TOKEN").get_value()
        }
    ),
    fetch_schema_from_transport=False
)
