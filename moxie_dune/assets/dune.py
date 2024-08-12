import csv
import json
import os

from dagster import asset, EnvVar
from dune_client.client import DuneClient

from moxie_dune.constants import FT_SUBJECT_EARNINGS_JSON_PATH, FT_SUBJECT_EARNINGS_CSV_PATH


@asset(
    group_name="dune",
    deps=["ft_subject_earnings_json"]
)
def ft_subject_earnings_csv(context) -> None:
    """Lifetime Moxie earnings of Fan Token Subjects"""

    with open(FT_SUBJECT_EARNINGS_JSON_PATH, "r") as f:
        ft_subject_earnings_data = json.load(f)

    with open(FT_SUBJECT_EARNINGS_CSV_PATH, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=ft_subject_earnings_data[0].keys())
        writer.writeheader()
        writer.writerows(ft_subject_earnings_data)


@asset(
    group_name="dune",
    deps=["ft_subject_earnings_csv"]
)
def ft_subject_earnings_on_dune(context) -> None:
    """fta_moxie_earnings Dune table"""

    os.environ["DUNE_API_KEY"] = EnvVar("DUNE_API_KEY").get_value()
    dune = DuneClient.from_env()

    with open(FT_SUBJECT_EARNINGS_CSV_PATH) as open_file:
        data = open_file.read()

        table = dune.upload_csv(
            data=str(data),
            description="Moxie Fan Token subject lifetime earnings",
            table_name="moxie_ft_subject_lifetime_earnings",  # define your table name here
            is_private=False
        )

        context.log.info(f"Uploaded {table}")
