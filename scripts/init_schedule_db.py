import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hannario.schedule_db import db_path_from_env, initialize_database


def main() -> None:
    db_path = db_path_from_env()
    initialize_database(db_path)
    print(f"Initialized schedule database: {db_path}")


if __name__ == "__main__":
    main()
