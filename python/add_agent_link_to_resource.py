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
def load_agent_link_rows(csv_path: str, number: int = None) -> List[Dict[str, str]]:
    rows = []
    count = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            resource_id = row.get("resource_URI")
            corp_id = row.get("agent_corporate_entity_id")
            if resource_id and corp_id:
                rows.append(row)
                count += 1
                if number is not None and count >= number:
                    break
    return rows

# ------------------------------------------------------------
# Business Logic
# ------------------------------------------------------------
def add_agent_link(resource: dict, corp_id: str) -> bool:
    agent_ref = f"/agents/corporate_entities/{corp_id}"
    for agent in resource.get("linked_agents", []):
        if agent.get("ref") == agent_ref:
            return False  # Already present, skip
    new_agent = {
        "is_primary": False,
        "role": TARGET_ROLE,
        "relator": TARGET_RELATOR,
        "terms": [],
        "ref": agent_ref,
    }
    resource.setdefault("linked_agents", []).append(new_agent)
    return True

def process_add_links(
    client: ArchivesSpaceClient,
    rows: List[Dict[str, str]],
    dry_run: bool,
    print_linked_agents: bool = False,
):
    summary = {
        "added": [],
        "skipped": [],
        "errors": [],
    }
    for row in rows:
        resource_id = row["resource_URI"]
        corp_id = row["agent_corporate_entity_id"]
        endpoint = f"/repositories/{REPOSITORY_ID}/resources/{resource_id}"
        try:
            resource = client.get(endpoint)
            added = add_agent_link(resource, corp_id)
            if not added:
                logger.info(f"Agent {corp_id} already present in resource {resource_id}, skipping.")
                summary["skipped"].append((corp_id, resource_id))
                if dry_run and print_linked_agents:
                    logger.info(f"linked_agents for resource {resource_id}:\n{json.dumps(resource.get('linked_agents', []), indent=2)}")
                continue
            if dry_run:
                logger.info(f"Would add agent {corp_id} to resource {resource_id} with role={TARGET_ROLE}, relator={TARGET_RELATOR}")
                if print_linked_agents:
                    logger.info(f"linked_agents for resource {resource_id}:\n{json.dumps(resource.get('linked_agents', []), indent=2)}")
                summary["added"].append((corp_id, resource_id))
                continue
            client.post(endpoint, resource)
            logger.info(f"Added agent {corp_id} to resource {resource_id}")
            summary["added"].append((corp_id, resource_id))
        except Exception as e:
            logger.error(f"Failed processing {resource_id}: {e}")
            summary["errors"].append((corp_id, resource_id, str(e)))
    return summary

# ------------------------------------------------------------
# Reporting
# ------------------------------------------------------------
def print_summary(summary):
    logger.info("---- Summary ----")
    logger.info(f"Added: {len(summary['added'])}")
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
        help="When in dry-run, print the linked_agents section of each resource processed."
    )
    parser.add_argument(
        "--log-to-file",
        action="store_true",
        help="If set, write logs to add_agent_link_to_resource.log as well as console."
    )
    args = parser.parse_args()

    if args.log_to_file:
        file_handler = logging.FileHandler("add_agent_link_to_resource.log", mode="a", encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        logger.addHandler(file_handler)

    config_file = "asnake_local_settings.cfg"
    csv_file = "add-agent-link-source-rps_2026-02-13.csv"
    config = ConfigLoader(config_file)
    client = ArchivesSpaceClient(config)
    rows = load_agent_link_rows(csv_file, number=args.number)
    logger.info(f"Processing {len(rows)} records")
    summary = process_add_links(client, rows, args.dry_run, print_linked_agents=args.print_linked_agents)
    print_summary(summary)

if __name__ == "__main__":
    main()
    sys.exit(0)
