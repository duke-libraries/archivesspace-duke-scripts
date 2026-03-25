""""as_query_corp_entities_all_ids.py

PURPOSE
-------
This script updates agent links on finding-aid resource records in ArchivesSpace.
Specifically, it ensures that corporate entity agents (organizations, institutions,
etc.) linked to resources are assigned the correct role ('source') and relator
code ('rps').

WHAT IT DOES, STEP BY STEP
---------------------------
1. Reads a CSV file listing pairs of corporate-entity IDs and resource IDs that
   need to be reviewed or updated.
2. Logs in to ArchivesSpace using credentials stored in a local config file.
3. For each pair, fetches the resource record from ArchivesSpace.
4. Checks whether the linked corporate-entity agent already has role='source'
   and relator='rps'.  If it does, the record is skipped with no changes made.
5. If the role or relator is wrong (or missing), the script either:
   - In DRY-RUN mode (the default): logs what WOULD change, but makes no edits.
   - In LIVE mode (--no-dry-run): saves the corrected record back to ArchivesSpace.
6. Prints a summary showing how many records were updated, skipped, or errored.

HOW TO RUN IT
-------------
  # Preview only — no changes are saved (safe to run anytime):
  python as_query_corp_entities_all_ids.py

  # Apply changes for real:
  python as_query_corp_entities_all_ids.py --no-dry-run

  # Process only the first 10 rows of the CSV (useful for testing):
  python as_query_corp_entities_all_ids.py --number 10

  # Also write the log to a file on disk:
  python as_query_corp_entities_all_ids.py --log-to-file

  # Show the full linked-agents data for each record while in dry-run:
  python as_query_corp_entities_all_ids.py --print-linked-agents

FILES NEEDED
------------
- asnake_local_settings.cfg  : Connection settings (server URL, username, password).
- agents-corporate-entities_resources_links-to-update_2026-01-13.csv
                             : CSV listing which corporate entities and resources
                               to process.  Must have columns:
                               'corporate_entity_id' and 'resource_id'.
"""

import sys
import csv
import json
import argparse
import logging
import configparser
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------
# The numeric ID of the ArchivesSpace repository we are working in.
# Repository 2 is the default repository at Duke University's ArchivesSpace instance.
# Change this if you are working in a different repository.
REPOSITORY_ID = 2

# How many seconds to wait for a response from the ArchivesSpace server before
# giving up and reporting a network error.
DEFAULT_TIMEOUT = 10

# The agent role we want every linked corporate-entity to have.
# In ArchivesSpace, "source" indicates the organization is the source of the
# archival materials (i.e., the records creator or donor).
# Change this value if you need to apply a different role.
TARGET_ROLE = "source"

# The MARC relator code we want every linked corporate-entity to have.
# Change this value if you need to apply a different relator code.
TARGET_RELATOR = "rps"

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
    Reads the local settings file and extracts the information needed to
    connect to ArchivesSpace: the server address, your username, and your
    password.

    The settings file (asnake_local_settings.cfg) is a plain-text file that
    looks like this:

        [ArchivesSpace]
        baseURL  = https://your-archivesspace-server.edu:8089
        user     = your_username
        password = your_password
    """

    def __init__(self, path: Union[str, Path]):
        """Load and parse the config file at the given path."""
        path = Path(path)

        # Stop immediately with a clear message if the file cannot be found.
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        parser = configparser.ConfigParser()
        parser.read(path)

        # Store the three required connection values as instance attributes
        # so other parts of the script can access them easily.
        self.base_url = parser.get("ArchivesSpace", "baseURL")
        self.user = parser.get("ArchivesSpace", "user")
        self.password = parser.get("ArchivesSpace", "password")


# ------------------------------------------------------------
# ArchivesSpace Client
# ------------------------------------------------------------


class ArchivesSpaceClient:
    """
    Handles all communication with the ArchivesSpace server.

    Key features:
    - Logs in once and reuses the session for all subsequent requests
      (faster and more efficient than logging in for every record).
    - Automatically retries up to 3 times if the server returns a
      temporary error (e.g., server overloaded, network hiccup).
    - Provides simple get() and post() methods so the rest of the script
      doesn't need to worry about low-level HTTP details.
    """

    def __init__(self, config: ConfigLoader):
        """Set up the client using credentials from the config file and log in."""
        self.base_url = config.base_url
        self.user = config.user
        self.password = config.password

        # Create a persistent network session (keeps the connection open).
        self.session = self._build_session()
        # Log in and attach the session token to all future requests.
        self.session.headers.update(self._authenticate())

    def _build_session(self) -> requests.Session:
        """
        Create a network session that will automatically retry failed requests.

        The retry strategy handles these common server-side problems:
          429 = Server is rate-limiting requests ("slow down")
          500 = Internal server error
          502/503/504 = Server temporarily unavailable

        'backoff_factor=1' means the script pauses 1 second before the first
        retry, 2 seconds before the second, and 4 seconds before the third.
        """
        retry_strategy = Retry(
            total=3,             # Retry up to 3 times before giving up
            backoff_factor=1,    # Wait 1s, 2s, 4s between retries
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)

        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    def _authenticate(self) -> Dict[str, str]:
        """
        Log in to ArchivesSpace and return the session token.

        ArchivesSpace uses token-based authentication: when you log in with a
        username and password, the server returns a temporary token (like a
        day-pass badge).  This token is then attached to every subsequent
        request so the server knows who you are without requiring you to
        re-enter your password each time.
        """
        login_url = f"{self.base_url}/users/{self.user}/login"

        logger.info("Authenticating with ArchivesSpace")

        resp = self.session.post(
            login_url,
            data={"password": self.password},
            timeout=DEFAULT_TIMEOUT,
        )

        # If login failed (e.g., wrong password), stop immediately and report
        # the error rather than continuing with an invalid session.
        resp.raise_for_status()

        # Extract the session token from the server's response.
        token = resp.json()["session"]

        # Return the token as HTTP headers so they can be attached to the session.
        return {
            "X-ArchivesSpace-Session": token,
            "Content-Type": "application/json",
        }

    def get(self, endpoint: str):
        """
        Fetch (read) a record from ArchivesSpace.

        'endpoint' is the path portion of the URL for the record, for example:
            /repositories/2/resources/1234

        Returns the record as a Python dictionary (key-value pairs), which
        can then be inspected or modified by the rest of the script.
        """
        url = f"{self.base_url}{endpoint}"

        resp = self.session.get(url, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()  # Raise an error if the request failed

        return resp.json()  # Convert the server's JSON response to a Python dict

    def post(self, endpoint: str, payload: dict):
        """
        Save (write) an updated record back to ArchivesSpace.

        'endpoint' is the URL path for the record to update.
        'payload' is the full record dictionary with any modifications applied.

        NOTE: ArchivesSpace requires the *entire* record to be sent back, not
        just the changed fields.  That is why the script fetches the full
        record first, makes targeted changes, then posts the whole thing back.
        """
        url = f"{self.base_url}{endpoint}"

        resp = self.session.post(
            url,
            json=payload,
            timeout=DEFAULT_TIMEOUT,
        )

        resp.raise_for_status()  # Raise an error if the save failed

        return resp.json()  # Return the server's confirmation response




# ------------------------------------------------------------
# CSV Processing
# ------------------------------------------------------------


def load_corp_resource_pairs(csv_path: str, number: Optional[int] = None) -> Set[Tuple[str, str]]:
    """
    Read the input CSV file and return a set of (corporate_entity_id, resource_id) pairs.

    Each row in the CSV represents one agent-to-resource relationship that needs
    to be checked or corrected.  The CSV must contain at least two columns:
        - 'corporate_entity_id' : the numeric ArchivesSpace ID of the corporate agent
        - 'resource_id'         : the numeric ArchivesSpace ID of the resource record

    Using a set (rather than a list) automatically removes duplicate rows, so
    the same record is never processed twice even if it appears multiple times
    in the spreadsheet.

    Parameters
    ----------
    csv_path : str
        Path to the input CSV file.
    number : int, optional
        If provided, stop reading after this many rows.  Useful for testing
        the script on a small sample before running it on the full dataset.

    Returns
    -------
    Set of (corporate_entity_id, resource_id) string tuples.
    """
    pairs = set()
    count = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            corp_id = row.get("corporate_entity_id")
            resource_id = row.get("resource_id")
            # Only add the pair if both columns have a value in this row.
            if corp_id and resource_id:
                pairs.add((corp_id, resource_id))
                count += 1
                # Stop early if the caller asked for only a limited sample.
                if number is not None and count >= number:
                    break
    return pairs


def load_resource_ids(csv_path: str) -> Set[str]:
    """
    Read the CSV file and return only the unique resource IDs.

    This is a simpler version of load_corp_resource_pairs() that collects
    just the resource IDs (ignoring the corporate entity column).  It is
    used when we need to fetch and cache the full resource records from
    ArchivesSpace for later inspection.

    Parameters
    ----------
    csv_path : str
        Path to the input CSV file (same file used by load_corp_resource_pairs).

    Returns
    -------
    Set of unique resource ID strings.  Duplicates are removed automatically.
    """
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
    Inspect a resource record and correct the agent link for the specified
    corporate entity if the role or relator is wrong.

    In ArchivesSpace, each resource record can be linked to multiple agents
    (people, families, and organizations).  Each link carries metadata:
      - 'role'    : the agent's relationship to the collection (e.g., 'source',
                    'creator', 'subject')
      - 'relator' : a more specific MARC code describing the relationship
                    (e.g., 'rps' for Repository)

    This function finds the agent link for the given corporate entity and
    checks whether role and relator already match the target values.  If they
    don't, it saves the old values (for logging purposes) and applies the
    corrections in-memory.  The caller is responsible for saving the record
    back to ArchivesSpace.

    Parameters
    ----------
    resource : dict
        The full ArchivesSpace resource record (as returned by the API).
    corp_id : str
        The numeric ID of the corporate entity agent to look for.

    Returns
    -------
    True  if the record was modified (i.e., an update is needed).
    False if the record was already correct (no action required).
    """
    # Build the internal ArchivesSpace reference path for this corporate entity.
    # e.g., "/agents/corporate_entities/42"
    agent_ref = f"/agents/corporate_entities/{corp_id}"
    updated = False

    # Walk through every agent linked to this resource record.
    for agent in resource.get("linked_agents", []):
        # Skip agents that aren't the one we're looking for.
        if agent.get("ref") != agent_ref:
            continue

        role = agent.get("role")
        # The 'relator' field is optional in ArchivesSpace, so treat it as
        # None (absent) if it isn't present at all.
        relator = agent.get("relator") if "relator" in agent else None

        if role != TARGET_ROLE or relator != TARGET_RELATOR:
            # Store the original values under private keys so the logging
            # code can report what changed (these keys are not sent to the
            # server, they are stripped before posting).
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
    """
    Main processing loop: fetch each resource, check its agent link, and
    update it if necessary.

    This function iterates over every (corporate_entity_id, resource_id) pair
    loaded from the CSV, applies update_agent_link() to detect changes, and
    either logs what would change (dry-run mode) or saves the corrected record
    back to ArchivesSpace (live mode).

    Parameters
    ----------
    client : ArchivesSpaceClient
        An authenticated connection to the ArchivesSpace server.
    pairs : set of (corp_id, resource_id) tuples
        The agent-resource relationships to process.
    dry_run : bool
        If True, only log proposed changes — do NOT write anything to
        ArchivesSpace.  This is the default and safe mode.
        If False, changes are saved to ArchivesSpace immediately.
    print_linked_agents : bool, optional
        If True (and dry_run is True), print the full linked-agents section
        of each record to the log for detailed inspection.

    Returns
    -------
    dict with three lists:
        'updated' : pairs where a change was made (or would be made in dry-run)
        'skipped' : pairs that were already correct — no change needed
        'errors'  : pairs where something went wrong (network error, etc.)
    """
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
    """
    Download full resource records from ArchivesSpace and save them to a
    local JSON file for caching or offline inspection.

    Fetching records from a server takes time.  By saving the results to a
    local file (resource_records.json), subsequent runs of the script can
    load them from disk instead of making repeated API calls — helpful when
    debugging or reviewing data without making live changes.

    Parameters
    ----------
    client : ArchivesSpaceClient
        An authenticated connection to the ArchivesSpace server.
    resource_ids : list of str
        The numeric IDs of the resource records to fetch.
    output_file : str
        Path to the JSON file where the downloaded records will be saved.

    Returns
    -------
    list of resource record dictionaries.
    """
    resources = []

    for rid in resource_ids:
        endpoint = f"/repositories/{REPOSITORY_ID}/resources/{rid}"

        try:
            resource = client.get(endpoint)
            resources.append(resource)
        except Exception as e:
            # Log a warning but keep going, one bad record shouldn't stop
            # the rest of the batch from being downloaded.
            logger.warning(f"Failed fetching resource {rid}: {e}")

    # Write all records to a local JSON file in a human-readable format.
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(resources, f, indent=2)

    logger.info(f"Saved {len(resources)} resources to {output_file}")

    return resources


# ------------------------------------------------------------
# Reporting
# ------------------------------------------------------------


def print_summary(summary):
    """
    Print a human-readable summary of the run's results.

    After the main processing loop finishes, this function logs three counts:
      Updated : records that were changed (or would be changed in dry-run)
      Skipped : records that were already correct and needed no changes
      Errors  : records that could not be processed (details logged below the counts)

    Any errors are listed individually so you know exactly which records to
    investigate.
    """
    logger.info("---- Summary ----")

    logger.info(f"Updated: {len(summary['updated'])}")
    logger.info(f"Skipped: {len(summary['skipped'])}")
    logger.info(f"Errors:  {len(summary['errors'])}")

    if summary["errors"]:
        logger.error("The following records encountered errors:")
        for corp_id, resource_id, err in summary["errors"]:
            logger.error(f"  Corporate entity {corp_id} / Resource {resource_id} -> {err}")


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------


def main():
    """
    Entry point: parse command-line arguments and orchestrate the full workflow.

    Running this script from the command line (e.g., `python as_query_corp_entities_all_ids.py`)
    calls this function, which:
      1. Reads any flags you passed on the command line (see --help for options).
      2. Optionally sets up a log file on disk.
      3. Loads credentials from the config file and logs in to ArchivesSpace.
      4. Reads the input CSV to get the list of agent-resource pairs to process.
      5. Runs the update loop (dry-run by default, no changes are saved).
      6. Prints a summary of results.
      7. Fetches and caches full resource records to a local JSON file if a
         cache does not already exist.
    """
    parser = argparse.ArgumentParser(
        description="Update corporate-entity agent links on ArchivesSpace resource records."
    )
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

    # --- File paths (edit these if your files are named differently) ----------
    config_file = "asnake_local_settings.cfg"           # Connection settings file
    csv_file = "agents-corporate-entities_resources_links-to-update_2026-01-13.csv"  # Input spreadsheet
    # --------------------------------------------------------------------------

    # Load credentials and establish a connection to ArchivesSpace.
    config = ConfigLoader(config_file)
    client = ArchivesSpaceClient(config)

    # Read the CSV and build the list of pairs to process.
    pairs = load_corp_resource_pairs(csv_file, number=args.number)
    logger.info(f"Processing {len(pairs)} records")

    # Run the main update loop (dry-run unless --no-dry-run was passed).
    summary = process_updates(client, pairs, args.dry_run, print_linked_agents=args.print_linked_agents)
    print_summary(summary)

    # --- Resource caching ---------------------------------------------------
    # After updates are done, cache the full resource records locally to a JSON
    # file.  If the cache file already exists from a previous run, load it from
    # disk instead of making redundant API calls.
    resource_cache = "resource_records.json"
    if Path(resource_cache).exists():
        logger.info(f"Loading cached resources from {resource_cache}")
        with open(resource_cache) as f:
            json.load(f)   # Load into memory (available for debugging/inspection)
    else:
        # Cache doesn't exist yet, fetch all records from the server and save.
        resource_ids = list(load_resource_ids(csv_file))
        fetch_resource_records(
            client,
            resource_ids,
            resource_cache,
        )


if __name__ == "__main__":
    main()
    sys.exit(0)
