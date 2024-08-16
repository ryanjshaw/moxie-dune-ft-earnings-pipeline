# Moxie Fan Token Earnings Offchain -> Dune Data Pipeline

This is a Dagster project for retrieving Moxie lifetime earnings data for
all Fan Tokens, and uploading that dataset to Dune.

![Global Asset Lineage](docs/Global_Asset_Lineage.svg)

Demonstrates:
- how to query multiple pages* of Fan Token Auction data from the Airstack GraphQL API
  - I limited the number of results to 100 to ensure that the paging function works, 
    but Airstack supports going up to 200 items per page
- how to lookup associated Moxie Lifetime Earnings data in batches for efficiency
- produce a CSV file suitable for upload into Dune from the above data
- using the DuneClient to upload the CSV data as a table

See [Moxie Fan Token Rate of Return](https://dune.com/queries/3979826) for an example of how to use the uploaded data.

## Useful Links

- [Airstack API Studio](https://app.airstack.xyz/api-studio)
- [Get a free plan for your API usage](https://warpcast.com/betashop.eth/0x2ec2bd6e)
- [Moxie Protocol Subgraph API](https://developer.moxie.xyz/api/protocol/overview)
- [Fan Token Auction Subgraph API](https://developer.moxie.xyz/api/auction/overview)
- [Fan Token Auction Clearing Price API](https://developer.moxie.xyz/api/clearing-price-api/overview)
- [Vesting API](https://developer.moxie.xyz/api/vesting/overview)

## Getting started

1. Copy `.env-example` to `.env` and populate your Airstack and Dune API keys

2. Install your Dagster code location as a Python package. By using the --editable flag, pip will install your Python package in ["editable mode"](https://pip.pypa.io/en/latest/topics/local-project-installs/#editable-installs) so that as you develop, local code changes will automatically apply.

```bash
pip install -e ".[dev]"
```

3. Then, start the Dagster UI web server:

```bash
dagster dev
```

4. Open http://localhost:3000 with your browser to see the project.

5. Click "Materialize All" to run the pipeline

## Development

### Adding new Python dependencies

You can specify new Python dependencies in `setup.py`.

### Unit testing

Tests are in the `moxie_dune_tests` directory and you can run tests using `pytest`:

```bash
pytest moxie_dune_tests
```

### Schedules and sensors

If you want to enable Dagster [Schedules](https://docs.dagster.io/concepts/partitions-schedules-sensors/schedules) or [Sensors](https://docs.dagster.io/concepts/partitions-schedules-sensors/sensors) for your jobs, the [Dagster Daemon](https://docs.dagster.io/deployment/dagster-daemon) process must be running. This is done automatically when you run `dagster dev`.

Once your Dagster Daemon is running, you can start turning on schedules and sensors for your jobs.

## Deploy on Dagster Cloud

The easiest way to deploy your Dagster project is to use Dagster Cloud.

Check out the [Dagster Cloud Documentation](https://docs.dagster.cloud) to learn more.
