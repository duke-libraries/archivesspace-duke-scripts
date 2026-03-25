"""as_convert_accessrestrict_to_phystech.py

PURPOSE
-------
This script converts "Conditions Governing Access" notes (accessrestrict) to
"Physical Characteristics and Technical Requirements" notes (phystech) on
archival object records in ArchivesSpace.


WHAT IT DOES, STEP BY STEP
---------------------------
1. Reads a CSV file listing archival object URIs and note persistent IDs to
   be converted.
2. Logs in to ArchivesSpace using credentials stored in a local config file.
3. For each row in the CSV, fetches the archival object from ArchivesSpace.
4. Finds the note identified by the persistent ID in that record.
5. Verifies the note is currently an 'accessrestrict' note.  If it is already
   'phystech' (or any other type), the record is skipped with no changes.
6. Converts the note by:
     a. Changing the note type from 'accessrestrict' to 'phystech'.
     b. Removing the 'rights_restriction' block (which holds the local
        access restriction type and end date) — this field only applies to
        access restriction notes and is not appropriate on phystech notes.
7. In DRY-RUN mode (the default), logs what WOULD change but saves nothing.
   In LIVE mode (--no-dry-run), saves the corrected record back to
   ArchivesSpace.
8. Prints a summary showing how many notes were converted, skipped, or errored.

HOW TO RUN IT
-------------
  # Preview only — no changes are saved (safe to run anytime):
  python as_convert_accessrestrict_to_phystech.py

  # Apply changes for real:
  python as_convert_accessrestrict_to_phystech.py --no-dry-run

  # Process only the first 10 rows of the CSV (useful for testing):
  python as_convert_accessrestrict_to_phystech.py --number 10

  # Also write the log to a file on disk:
  python as_convert_accessrestrict_to_phystech.py --log-to-file

  # Print the full note JSON for each processed record while in dry-run:
  python as_convert_accessrestrict_to_phystech.py --print-notes

FILES NEEDED
------------
- asnake_local_settings.cfg  : Connection settings (server URL, username, password).
- accessrestrict_to_phystech_input.csv
                             : CSV listing which notes to convert.
                               Must have columns:
                                 'ao_uri'             – full ArchivesSpace URI of
    Combined with                                                   the archival object, e.g.
                                                        /repositories/2/archival_objects/12345
                                 'note_persistent_id' – the persistent ID of the
                                                        note to convert
"""

import sys
import csv
import json
import argparse
import logging
import configparser
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------

# How many seconds to wait for a response from the ArchivesSpace server before
# giving up and reporting a network error.
DEFAULT_TIMEOUT = 10

# The note type we expect to find (and will convert FROM).
SOURCE_NOTE_TYPE = "accessrestrict"

# The note type we are converting TO.
TARGET_NOTE_TYPE = "phystech"

# Default ArchivesSpace repository ID used when building URIs from record_id.
DEFAULT_REPO_ID = 2

# Maps values in the CSV 'record_type' column to the URL path segment used
# by the ArchivesSpace API.
RECORD_TYPE_MAP = {
    "archival_object": "archival_objects",
    "resource": "resources",
}

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

    Keeping credentials in a separate file (rather than hard-coded in the
    script) means you never accidentally share your password when sharing
    the script with colleagues.
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
            total=3,           # Retry up to 3 times before giving up
            backoff_factor=1,  # Wait 1s, 2s, 4s between retries
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
        request so the server knows who you are without re-entering your
        password each time.
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

        # Return the token as HTTP headers so they can be attached to all
        # future requests in this session.
        return {
            "X-ArchivesSpace-Session": token,
            "Content-Type": "application/json",
        }

    def get(self, endpoint: str) -> dict:
        """
        Fetch (read) a record from ArchivesSpace.

        'endpoint' is the path portion of the URL for the record, for example:
            /repositories/2/archival_objects/12345

        Returns the record as a Python dictionary (key-value pairs), which
        can then be inspected or modified by the rest of the script.
        """
        url = f"{self.base_url}{endpoint}"

        resp = self.session.get(url, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()  # Raise an error if the request failed

        return resp.json()  # Convert the server's JSON response to a Python dict

    def post(self, endpoint: str, payload: dict) -> dict:
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


def load_note_targets(
    csv_path: str,
    number: Optional[int] = None,
    repo_id: int = DEFAULT_REPO_ID,
) -> List[Tuple[str, str, str]]:
    """
    Read the input CSV and return a list of (record_uri, note_persistent_id,
    new_content) triples.

    Each row represents one note that should be converted from 'accessrestrict'
    to 'phystech'.  The CSV must contain these columns:
        - 'record_type'       : 'archival_object' or 'resource'
        - 'record_id'         : the numeric ArchivesSpace record ID
        - 'accessrestrict_note_to_delete_persistent_id'
                              : persistent ID of the note to convert
        - 'new_phystech_note_content'
                              : replacement text for the phystech note

    Parameters
    ----------
    csv_path : str
        Path to the input CSV file.
    number : int, optional
        If provided, stop reading after this many rows.
    repo_id : int, optional
        ArchivesSpace repository ID used when constructing URIs (default: 2).

    Returns
    -------
    List of (record_uri, note_persistent_id, new_content) string triples.
    """
    targets = []

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader):
            record_type = row.get("record_type", "").strip()
            record_id   = row.get("record_id", "").strip()
            note_pid    = row.get("accessrestrict_note_to_delete_persistent_id", "").strip()
            new_content = row.get("new_phystech_note_content", "").strip()

            if not record_type or not record_id or not note_pid:
                logger.warning(
                    f"Skipping row {i + 2}: missing 'record_type', 'record_id', "
                    f"or 'accessrestrict_note_to_delete_persistent_id'"
                )
                continue

            path_segment = RECORD_TYPE_MAP.get(record_type)
            if path_segment is None:
                logger.warning(
                    f"Skipping row {i + 2}: unknown record_type '{record_type}'"
                )
                continue

            record_uri = f"/repositories/{repo_id}/{path_segment}/{record_id}"
            targets.append((record_uri, note_pid, new_content))

            # Stop early if the caller asked for only a limited sample.
            if number is not None and len(targets) >= number:
                break

    return targets


# ------------------------------------------------------------
# Business Logic
# ------------------------------------------------------------


def convert_note(ao_record: dict, note_pid: str, new_content: str = "") -> Optional[dict]:
    """
    Find a specific note in an archival object record and convert it from
    'accessrestrict' to 'phystech', removing any local access restriction data
    and optionally replacing the note text.

    This function:
      1. Locates the note with the given persistent_id.
      2. Checks that it is currently of type 'accessrestrict'.  If not,
         returns None to signal that no change is needed (or appropriate).
      3. Changes the type to 'phystech'.
      4. Removes the 'rights_restriction' block.
      5. If new_content is provided, replaces the subnotes with a single
         note_text subnote containing the new text.

    Parameters
    ----------
    ao_record : dict
        The full archival object record fetched from ArchivesSpace.
    note_pid : str
        The persistent ID of the note to convert.
    new_content : str, optional
        Replacement text for the note's subnote content.  If empty, the
        existing subnote text is left unchanged.

    Returns
    -------
    A dictionary describing what was changed, e.g.:
        {
            "old_type": "accessrestrict",
            "new_type": "phystech",
            "old_content": "...",
            "removed_rights_restriction": { ... }   # or None if not present
        }
    Returns None if no matching note was found or if the note was not an
    'accessrestrict' note (meaning no change was made).
    """
    for note in ao_record.get("notes", []):
        if note.get("persistent_id") != note_pid:
            continue

        current_type = note.get("type")

        # If the note is already the target type, nothing to do.
        if current_type == TARGET_NOTE_TYPE:
            logger.info(
                f"Note {note_pid} is already '{TARGET_NOTE_TYPE}' — skipping."
            )
            return None

        # If it isn't an accessrestrict note either, don't touch it. It may
        # be a different kind of note that shouldn't be changed by this script.
        if current_type != SOURCE_NOTE_TYPE:
            logger.warning(
                f"Note {note_pid} has unexpected type '{current_type}' "
                f"(expected '{SOURCE_NOTE_TYPE}') — skipping to avoid unintended changes."
            )
            return None

        # --- Apply the conversion ---

        # 1. Change the note type.
        note["type"] = TARGET_NOTE_TYPE

        # 2. Remove the rights_restriction block.
        #    This block holds local_access_restriction_type and restriction
        #    end date, which are only applicable to access restriction notes.
        removed_rights_restriction = note.pop("rights_restriction", None)

        # 3. Replace the subnote content if new_content was supplied.
        old_content = None
        if new_content:
            existing = note.get("subnotes", [])
            publish = existing[0].get("publish", True) if existing else True
            old_content = existing[0].get("content", "") if existing else None
            note["subnotes"] = [
                {
                    "jsonmodel_type": "note_text",
                    "content": new_content,
                    "publish": publish,
                }
            ]

        return {
            "old_type": current_type,
            "new_type": TARGET_NOTE_TYPE,
            "old_content": old_content,
            "removed_rights_restriction": removed_rights_restriction,
        }

    # If we got here, no note with that persistent_id was found in the record.
    logger.warning(
        f"Note with persistent_id '{note_pid}' not found in archival object "
        f"'{ao_record.get('uri', '(unknown)')}'"
    )
    return None


def process_conversions(
    client: ArchivesSpaceClient,
    targets: List[Tuple[str, str]],
    dry_run: bool,
    print_notes: bool = False,
) -> dict:
    """
    Main processing loop: fetch each archival object, convert the target note,
    and save the record if changes were made.

    Parameters
    ----------
    client : ArchivesSpaceClient
        An authenticated connection to the ArchivesSpace server.
    targets : list of (ao_uri, note_persistent_id) tuples
        The notes to convert, as loaded from the input CSV.
    dry_run : bool
        If True, only log proposed changes — do NOT write anything to
        ArchivesSpace.  This is the default and safe mode.
        If False, changes are saved to ArchivesSpace immediately.
    print_notes : bool, optional
        If True (and dry_run is True), print the full notes list for each
        archival object to the log for detailed inspection.

    Returns
    -------
    dict with three lists:
        'converted' : (ao_uri, note_pid) pairs where a change was made
                      (or would be made in dry-run)
        'skipped'   : pairs where the note was already correct or not found
        'errors'    : pairs where something went wrong (network error, etc.)
    """
    summary: dict = {
        "converted": [],
        "skipped": [],
        "errors": [],
    }

    for record_uri, note_pid, new_content in targets:
        try:
            # Fetch the full record from ArchivesSpace.
            record = client.get(record_uri)

            if print_notes:
                logger.info(
                    f"Notes for {record_uri}:\n"
                    f"{json.dumps(record.get('notes', []), indent=2)}"
                )

            # Attempt the in-memory conversion.
            change = convert_note(record, note_pid, new_content)

            if change is None:
                # convert_note() already logged the reason for skipping.
                summary["skipped"].append((record_uri, note_pid))
                continue

            # Build a log message describing what changed.
            removed = change["removed_rights_restriction"]
            removed_msg = f", removed rights_restriction: {removed}" if removed else ""
            action = "Would convert" if dry_run else "Converting"
            logger.info(
                f"{action} note {note_pid} on {record_uri}: "
                f"type {change['old_type']} → {change['new_type']}, "
                f"content updated{removed_msg}"
            )

            if dry_run:
                # Show what the notes list looks like after the conversion
                # so the archivist can verify the result before going live.
                logger.info(
                    f"Notes for {record_uri} after conversion:\n"
                    f"{json.dumps(record.get('notes', []), indent=2)}"
                )
                # In dry-run mode, do not post anything back to the server.
                summary["converted"].append((record_uri, note_pid))
                continue

            # Save the modified record back to ArchivesSpace.
            client.post(record_uri, record)
            logger.info(f"Saved {record_uri}")
            summary["converted"].append((record_uri, note_pid))

        except Exception as e:
            logger.error(f"Failed processing {record_uri} / note {note_pid}: {e}")
            summary["errors"].append((record_uri, note_pid, str(e)))

    return summary


# ------------------------------------------------------------
# Reporting
# ------------------------------------------------------------


def print_summary(summary: dict) -> None:
    """
    Print a human-readable summary of the run's results.

    After the main processing loop finishes, this function logs three counts:
      Converted : notes whose type was changed (or would be changed in dry-run)
      Skipped   : notes that were already correct, not found, or wrong type
      Errors    : records that could not be processed (details logged individually)

    Any errors are listed individually so you know exactly which records to
    investigate.
    """
    logger.info("---- Summary ----")
    logger.info(f"Converted : {len(summary['converted'])}")
    logger.info(f"Skipped   : {len(summary['skipped'])}")
    logger.info(f"Errors    : {len(summary['errors'])}")

    if summary["errors"]:
        logger.error("The following records encountered errors:")
        for ao_uri, note_pid, err in summary["errors"]:
            logger.error(f"  {ao_uri} / note {note_pid} -> {err}")


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------


def main() -> None:
    """
    Entry point: parse command-line arguments and orchestrate the full workflow.

    Running this script from the command line calls this function, which:
      1. Reads any flags you passed (see --help for all options).
      2. Optionally sets up a log file on disk.
      3. Loads credentials from the config file and logs in to ArchivesSpace.
      4. Reads the input CSV to get the list of notes to convert.
      5. Runs the conversion loop (dry-run by default, no changes are saved).
      6. Prints a summary of results.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Convert 'Conditions Governing Access' (accessrestrict) notes to "
            "'Physical Characteristics and Technical Requirements' (phystech) "
            "notes on ArchivesSpace archival object records."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Preview changes without saving anything (default: enabled).",
    )
    parser.add_argument(
        "--no-dry-run",
        dest="dry_run",
        action="store_false",
        help="Apply changes for real — saves updated records to ArchivesSpace.",
    )
    parser.add_argument(
        "--number",
        type=int,
        default=None,
        help="Only process the first N rows from the CSV (useful for testing).",
    )
    parser.add_argument(
        "--print-notes",
        action="store_true",
        help=(
            "When in dry-run mode, print the full notes list for each archival "
            "object to the log for detailed inspection."
        ),
    )
    parser.add_argument(
        "--log-to-file",
        action="store_true",
        help="Write logs to as_convert_accessrestrict_to_phystech.log in addition to the console.",
    )
    parser.add_argument(
        "--csv",
        default="accRestrict.csv",
        help=(
            "Path to the input CSV file "
            "(default: accRestrict.csv)."
        ),
    )
    parser.add_argument(
        "--repo-id",
        type=int,
        default=DEFAULT_REPO_ID,
        help=f"ArchivesSpace repository ID used when building record URIs (default: {DEFAULT_REPO_ID}).",
    )
    args = parser.parse_args()

    # Optionally mirror all log output to a file on disk.
    if args.log_to_file:
        file_handler = logging.FileHandler(
            "as_convert_accessrestrict_to_phystech.log", mode="a", encoding="utf-8"
        )
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        )
        logger.addHandler(file_handler)

    if args.dry_run:
        logger.info("DRY-RUN mode enabled — no changes will be saved to ArchivesSpace.")
        logger.info("Run with --no-dry-run to apply changes for real.")

    # --- File paths -----------------------------------------------------------
    config_file = "asnake_local_settings.cfg"  # Connection settings file
    csv_file = args.csv                         # Input CSV (overridable via --csv)
    # --------------------------------------------------------------------------

    # Load credentials and establish a connection to ArchivesSpace.
    config = ConfigLoader(config_file)
    client = ArchivesSpaceClient(config)

    # Read the CSV and build the list of notes to process.
    targets = load_note_targets(csv_file, number=args.number, repo_id=args.repo_id)
    logger.info(f"Processing {len(targets)} note(s)")

    # Run the main conversion loop.
    summary = process_conversions(
        client,
        targets,
        dry_run=args.dry_run,
        print_notes=args.print_notes,
    )

    print_summary(summary)


if __name__ == "__main__":
    main()
    sys.exit(0)
