import sys
import csv
import json
import argparse
import logging
import configparser
from pathlib import Path
from typing import Dict, List, Tuple, Set

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


REPOSITORY_ID = 2
DEFAULT_TIMEOUT = 10


# ------------------------------------------------------------
# Logging
# ------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ------------------------------------------------------------
# Config Loader
# ------------------------------------------------------------


class ConfigLoader:
    """
    Loads configuration required to connect to ArchivesSpace.
    """

    def __init__(self, path: str):
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        parser = configparser.ConfigParser()
        parser.read(path)

        self.base_url = parser.get("ArchivesSpace", "baseURL")
        self.user = parser.get("ArchivesSpace", "user")
        self.password = parser.get("ArchivesSpace", "password")


# ------------------------------------------------------------
# ArchivesSpace Client
# ------------------------------------------------------------


class ArchivesSpaceClient:
    """
    Production-grade ArchivesSpace API client.

    Features:
    - persistent HTTP session
    - retry logic
    - centralized API calls
    """

    def __init__(self, config: ConfigLoader):

        self.base_url = config.base_url
        self.user = config.user
        self.password = config.password

        self.session = self._build_session()
        self.session.headers.update(self._authenticate())

    def _build_session(self) -> requests.Session:

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)

        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    def _authenticate(self) -> Dict[str, str]:

        login_url = f"{self.base_url}/users/{self.user}/login"

        logger.info("Authenticating with ArchivesSpace")

        resp = self.session.post(
            login_url,
            data={"password": self.password},
            timeout=DEFAULT_TIMEOUT,
        )

        resp.raise_for_status()

        token = resp.json()["session"]

        return {
            "X-ArchivesSpace-Session": token,
            "Content-Type": "application/json",
        }

    def get(self, endpoint: str):

        url = f"{self.base_url}{endpoint}"

        resp = self.session.get(url, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()

        return resp.json()

    def post(self, endpoint: str, payload: dict):

        url = f"{self.base_url}{endpoint}"

        resp = self.session.post(
            url,
            json=payload,
            timeout=DEFAULT_TIMEOUT,
        )

        resp.raise_for_status()

        return resp.json()


# ------------------------------------------------------------
# Constants for target values
# ------------------------------------------------------------

TARGET_ROLE = "source"  # Change to desired role value
TARGET_RELATOR = "rps"  # Change to desired relator value


# ------------------------------------------------------------
# CSV Processing
# ------------------------------------------------------------


def load_corp_resource_pairs(csv_path: str, number: int = None) -> Set[Tuple[str, str]]:
    pairs = set()
    count = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            corp_id = row.get("corporate_entity_id")
            resource_id = row.get("resource_id")
            if corp_id and resource_id:
                pairs.add((corp_id, resource_id))
                count += 1
                if number is not None and count >= number:
                    break
    return pairs


def load_resource_ids(csv_path: str) -> Set[str]:

    resource_ids = set()

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            resource_id = row.get("resource_id")

            if resource_id:
                resource_ids.add(resource_id)

    return resource_ids


# ------------------------------------------------------------
# Business Logic
# ------------------------------------------------------------


def update_agent_link(resource: dict, corp_id: str) -> bool:
    """
    Ensures agent link has role='source' and relator='rps'.

    Returns True if modification occurred.
    """

    agent_ref = f"/agents/corporate_entities/{corp_id}"
    updated = False

    for agent in resource.get("linked_agents", []):
        if agent.get("ref") != agent_ref:
            continue
        role = agent.get("role")
        relator = agent.get("relator") if "relator" in agent else None
        # If relator is missing or not TARGET_RELATOR, or role is not TARGET_ROLE, update/add as needed
        if role != TARGET_ROLE or relator != TARGET_RELATOR:
            agent["_old_role"] = role
            agent["_old_relator"] = relator
            agent["role"] = TARGET_ROLE
            agent["relator"] = TARGET_RELATOR
            updated = True

    return updated


def process_updates(
    client: ArchivesSpaceClient,
    pairs: Set[Tuple[str, str]],
    dry_run: bool,
    print_linked_agents: bool = False,
):

    summary = {
        "updated": [],
        "skipped": [],
        "errors": [],
    }

    for corp_id, resource_id in pairs:
        endpoint = f"/repositories/{REPOSITORY_ID}/resources/{resource_id}"

        try:
            resource = client.get(endpoint)
            changed = update_agent_link(resource, corp_id)
            if not changed:
                logger.info(f"No update needed for resource {resource_id}, agent {corp_id}: role and relator already correct.")
                summary["skipped"].append((corp_id, resource_id))
                if dry_run and print_linked_agents:
                    logger.info(f"linked_agents for resource {resource_id}:\n{json.dumps(resource.get('linked_agents', []), indent=2)}")
                continue
            # Find the updated agent for reporting
            agent_ref = f"/agents/corporate_entities/{corp_id}"
            updated_agent = None
            for agent in resource.get("linked_agents", []):
                if agent.get("ref") == agent_ref and ("_old_role" in agent or "_old_relator" in agent):
                    updated_agent = agent
                    break
            if dry_run:
                if updated_agent:
                    old_role = updated_agent.get("_old_role")
                    old_relator = updated_agent.get("_old_relator")
                    logger.info(f"Would update resource {resource_id}, role {old_role}->{TARGET_ROLE}, relator {old_relator}->{TARGET_RELATOR}")
                else:
                    logger.info(f"Would update resource {resource_id} (details unavailable)")
                if print_linked_agents:
                    logger.info(f"linked_agents for resource {resource_id}:\n{json.dumps(resource.get('linked_agents', []), indent=2)}")
                summary["updated"].append((corp_id, resource_id))
                continue
            client.post(endpoint, resource)
            logger.info(f"Updated resource {resource_id}")
            summary["updated"].append((corp_id, resource_id))
        except Exception as e:
            logger.error(f"Failed processing {resource_id}: {e}")
            summary["errors"].append((corp_id, resource_id, str(e)))

    return summary


# ------------------------------------------------------------
# Resource Caching
# ------------------------------------------------------------


def fetch_resource_records(
    client: ArchivesSpaceClient,
    resource_ids: List[str],
    output_file: str,
):

    resources = []

    for rid in resource_ids:
        endpoint = f"/repositories/{REPOSITORY_ID}/resources/{rid}"

        try:
            resource = client.get(endpoint)

            resources.append(resource)

        except Exception as e:
            logger.warning(f"Failed fetching resource {rid}: {e}")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(resources, f, indent=2)

    logger.info(f"Saved {len(resources)} resources to {output_file}")

    return resources


# ------------------------------------------------------------
# Reporting
# ------------------------------------------------------------


def print_summary(summary):

    logger.info("---- Summary ----")

    logger.info(f"Updated: {len(summary['updated'])}")
    logger.info(f"Skipped: {len(summary['skipped'])}")
    logger.info(f"Errors: {len(summary['errors'])}")

    if summary["errors"]:
        for corp_id, resource_id, err in summary["errors"]:
            logger.error(f"{corp_id} / {resource_id} -> {err}")


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Preview changes without updating records",
    )
    parser.add_argument(
        "--no-dry-run",
        dest="dry_run",
        action="store_false",
    )
    parser.add_argument(
        "--number",
        type=int,
        default=None,
        help="Only process the first N rows from the CSV",
    )
    parser.add_argument(
        "--print-linked-agents",
        action="store_true",
        help="When in dry-run, print the linked_agents section of each resource processed.",
    )
    parser.add_argument(
        "--log-to-file",
        action="store_true",
        help="If set, write logs to as_query_corp_entities_all_ids.log as well as console.",
    )
    args = parser.parse_args()

    if args.log_to_file:
        file_handler = logging.FileHandler("as_query_corp_entities_all_ids.log", mode="a", encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        logger.addHandler(file_handler)

    config_file = "asnake_local_settings.cfg"
    csv_file = "agents-corporate-entities_resources_links-to-update_2026-01-13.csv"
    config = ConfigLoader(config_file)
    client = ArchivesSpaceClient(config)
    pairs = load_corp_resource_pairs(csv_file, number=args.number)
    logger.info(f"Processing {len(pairs)} records")
    summary = process_updates(client, pairs, args.dry_run, print_linked_agents=args.print_linked_agents)
    print_summary(summary)
    resource_cache = "resource_records.json"
    if Path(resource_cache).exists():
        logger.info(f"Loading cached resources from {resource_cache}")
        with open(resource_cache) as f:
            json.load(f)
    else:
        resource_ids = list(load_resource_ids(csv_file))
        fetch_resource_records(
            client,
            resource_ids,
            resource_cache,
        )


if __name__ == "__main__":
    main()
    sys.exit(0)