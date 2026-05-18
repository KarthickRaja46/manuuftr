import argparse
import os
from pathlib import Path

from azure.core.exceptions import ClientAuthenticationError
from azure.storage.blob import BlobServiceClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

CSV_FILES = [
    "dim_plant.csv",
    "dim_line.csv",
    "dim_machine.csv",
    "dim_product.csv",
    "dim_shift.csv",
    "dim_date.csv",
    "fact_production.csv",
    "fact_downtime.csv",
]


def upload_files(connection_string: str, container_name: str = "manufacturing-data") -> None:
    try:
        container_client = BlobServiceClient.from_connection_string(connection_string).get_container_client(container_name)
    except ClientAuthenticationError:
        print("\n✗ Authentication failed when creating container client. Check your connection string.")
        raise

    print("\n⬆ Uploading files to Azure Blob Storage...\n")

    for file_name in CSV_FILES:
        file_path = DATA_DIR / file_name

        if not file_path.exists():
            print(f"✗ {file_name} not found")
            continue

        try:
            with file_path.open("rb") as data:
                container_client.upload_blob(name=file_name, data=data, overwrite=True)
                print(f"✓ Uploaded {file_name}")
        except ClientAuthenticationError:
            print("\n✗ Authentication failed while uploading. The connection string may be invalid or expired.")
            raise
        except Exception as ex:
            print(f"\n✗ Failed to upload {file_name}: {ex}")

    print("\n✅ Upload complete!")


def validate_connection_string(connection_string: str) -> bool:
    """Try listing containers to validate the provided connection string."""
    try:
        client = BlobServiceClient.from_connection_string(connection_string)
        # try a light-weight call
        _ = list(client.list_containers(name_starts_with=None, results_per_page=1))
        return True
    except ClientAuthenticationError:
        return False
    except Exception as e:
        print(f"\n✗ Error validating connection string: {e}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload manufacturing CSV files to Azure Blob Storage.")
    parser.add_argument("--connection-string", dest="connection_string", help="Azure Storage connection string")
    parser.add_argument("--container", dest="container_name", default="manufacturing-data", help="Azure Blob container name")
    args = parser.parse_args()

    connection_string = args.connection_string or os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        print("Provide the Azure Storage connection string with --connection-string or set AZURE_STORAGE_CONNECTION_STRING.")
        raise SystemExit(1)

    # validate before attempting upload
    if not validate_connection_string(connection_string):
        print("\n✗ Connection string validation failed. Check key, clock skew, or use a SAS token.")
        raise SystemExit(1)

    upload_files(connection_string, args.container_name)


if __name__ == "__main__":
    main()
