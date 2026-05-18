import argparse
import getpass
import os
from pathlib import Path

from generate_manufacturing_data import main as generate_main
from upload_to_azure import upload_files

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate manufacturing data and upload it to Azure Blob Storage.")
    parser.add_argument("--connection-string", dest="connection_string", help="Azure Storage connection string (optional, env preferred)")
    parser.add_argument("--container", dest="container_name", default="manufacturing-data", help="Azure Blob container name")
    parser.add_argument("--skip-generate", dest="skip_generate", action="store_true", help="Skip generating new data files")
    parser.add_argument("--skip-upload", dest="skip_upload", action="store_true", help="Skip uploading files to Azure")
    parser.add_argument("--days", dest="days", type=int, default=None, help="Number of new days to append when generating incremental facts")
    parser.add_argument("--reset", dest="reset", action="store_true", help="Regenerate the dataset from scratch")
    parser.add_argument("--force-dims", dest="force_dims", action="store_true", help="Regenerate dimension tables even if they already exist")
    args = parser.parse_args()

    # Prefer environment variable for safe key handling
    connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING") or args.connection_string

    if not args.skip_generate:
        print("\n=== STEP 1: Generate manufacturing data ===\n")
        generate_main(days=args.days, reset=args.reset, force_dims=args.force_dims)

    # Default behavior: upload (unless user explicitly opts out)
    if args.skip_upload:
        print("\n=== Upload skipped. ===")
        return

    # If no connection string in env or arg, prompt securely (will not be saved)
    if not connection_string:
        print("\nAZURE_STORAGE_CONNECTION_STRING not found in environment.")
        prompt = getpass.getpass("Enter Azure Storage connection string (input hidden, press Enter to abort): ")
        if not prompt:
            print("Aborting: no connection string provided.")
            raise SystemExit(1)
        connection_string = prompt

    if not DATA_DIR.exists():
        print(f"\nData folder not found: {DATA_DIR}")
        raise SystemExit(1)

    print("\n=== STEP 2: Upload generated CSV files to Azure ===\n")
    upload_files(connection_string, args.container_name)


if __name__ == "__main__":
    main()
