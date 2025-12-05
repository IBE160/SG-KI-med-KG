import json
from pathlib import Path
from app.main import app
import os
import sys

from dotenv import load_dotenv

load_dotenv()


def generate_openapi_schema(output_file):
    if not output_file:
        print(
            "Error: No output file specified. Provide it as an argument or set OPENAPI_OUTPUT_FILE env var."
        )
        sys.exit(1)

    schema = app.openapi()
    output_path = Path(output_file)

    updated_schema = remove_operation_id_tag(schema)

    output_path.write_text(json.dumps(updated_schema, indent=2))
    print(f"OpenAPI schema saved to {output_file}")


def remove_operation_id_tag(schema):
    """
    Removes the tag prefix from the operation IDs in the OpenAPI schema.

    This cleans up the OpenAPI operation IDs that are used by the frontend
    client generator to create the names of the functions. The modified
    schema is then returned.
    """
    for path_data in schema["paths"].values():
        for operation in path_data.values():
            if "tags" in operation and len(operation["tags"]) > 0:
                tag = operation["tags"][0]
                operation_id = operation["operationId"]
                to_remove = f"{tag}-"
                # Only remove if the operationId actually starts with the tag
                if operation_id.startswith(to_remove):
                    new_operation_id = operation_id[len(to_remove) :]
                    operation["operationId"] = new_operation_id
    return schema


if __name__ == "__main__":
    # Priority: 1. Command line arg, 2. Env var, 3. Default
    if len(sys.argv) > 1:
        OUTPUT_FILE = sys.argv[1]
    else:
        OUTPUT_FILE = os.getenv("OPENAPI_OUTPUT_FILE", "../frontend/openapi.json")

    generate_openapi_schema(OUTPUT_FILE)
