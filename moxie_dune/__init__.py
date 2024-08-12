from dagster import Definitions, load_assets_from_modules, EnvVar

from .assets import airstack, dune
from .resources import airstack_client

all_assets = load_assets_from_modules([airstack, dune])

defs = Definitions(
    assets=all_assets,
    resources={
        "airstack_client": airstack_client
    }
)
