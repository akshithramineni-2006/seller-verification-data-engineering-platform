import subprocess
import sys


def run_stage(name, module):

    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)

    result = subprocess.run(
        [sys.executable, "-m", module],
        check=True
    )

    return result


def main():

    stages = [

        ("DATA GENERATION", "app.data_generator"),

        ("BRONZE INGESTION", "app.ingest"),

        ("SILVER CLEANING", "app.clean"),

        ("DATA WAREHOUSE", "app.warehouse"),

        ("DATA QUALITY", "app.quality"),

        ("SQL ANALYTICS", "app.analytics")

    ]

    for name, module in stages:

        run_stage(name, module)

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()