import subprocess
import sys
from datetime import datetime


def run_stage(index, total, name, module):

    print("\n" + "=" * 70)
    print(f"[{index}/{total}] {name}")
    print("=" * 70)

    start = datetime.now()

    try:
        subprocess.run(
            [sys.executable, "-m", module],
            check=True
        )

        elapsed = datetime.now() - start
        print(f"\n[{index}/{total}] {name} - SUCCESS")
        print(f"Duration: {elapsed}")

    except subprocess.CalledProcessError as error:

        print(f"\n[{index}/{total}] {name} - FAILED")
        print(f"Exit code: {error.returncode}")
        print("Pipeline stopped.")

        raise


def main():

    stages = [
        ("DATA GENERATION", "app.data_generator"),
        ("BRONZE INGESTION", "app.ingest"),
        ("SILVER CLEANING", "app.clean"),
        ("DATA WAREHOUSE", "app.warehouse"),
        ("DATA QUALITY", "app.quality"),
        ("SQL ANALYTICS", "app.analytics")
    ]

    total = len(stages)

    print("\n" + "=" * 70)
    print("SELLER VERIFICATION DATA ENGINEERING PIPELINE")
    print("=" * 70)

    start = datetime.now()

    for index, (name, module) in enumerate(stages, start=1):
        run_stage(index, total, name, module)

    elapsed = datetime.now() - start

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print(f"Total duration: {elapsed}")


if __name__ == "__main__":
    main()