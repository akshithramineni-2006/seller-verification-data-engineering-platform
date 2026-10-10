
import logging
import subprocess
import sys
from datetime import datetime
from time import perf_counter

from app.logger import logger


def run_stage(index, total, name, module):
    print("\n" + "=" * 70)
    print(f"[{index}/{total}] {name}")
    print("=" * 70)

    logger.info(
        "Stage %s/%s started: %s | module=%s",
        index,
        total,
        name,
        module,
    )

    start = perf_counter()

    try:
        subprocess.run(
            [sys.executable, "-m", module],
            check=True,
        )

        elapsed = perf_counter() - start

        print(f"\n[{index}/{total}] {name} - SUCCESS")
        print(f"Duration: {elapsed:.2f} seconds")

        logger.info(
            "Stage %s/%s succeeded: %s | duration=%.2f seconds",
            index,
            total,
            name,
            elapsed,
        )

        return elapsed

    except subprocess.CalledProcessError as error:
        elapsed = perf_counter() - start

        print(f"\n[{index}/{total}] {name} - FAILED")
        print(f"Exit code: {error.returncode}")
        print("Pipeline stopped.")

        logger.error(
            "Stage %s/%s failed: %s | exit_code=%s | duration=%.2f seconds",
            index,
            total,
            name,
            error.returncode,
            elapsed,
        )

        raise


def main():
    stages = [
        ("DATA GENERATION", "app.data_generator"),
        ("BRONZE INGESTION", "app.ingest"),
        ("SILVER CLEANING", "app.clean"),
        ("DATA WAREHOUSE", "app.warehouse"),
        ("DATA QUALITY", "app.quality"),
        ("SQL ANALYTICS", "app.analytics"),
    ]

    total = len(stages)
    completed = 0
    pipeline_start = perf_counter()
    start_time = datetime.now().astimezone().isoformat(timespec="seconds")

    print("\n" + "=" * 70)
    print("SELLER VERIFICATION DATA ENGINEERING PIPELINE")
    print("=" * 70)

    logger.info("Pipeline started | start_time=%s", start_time)

    try:
        for index, (name, module) in enumerate(stages, start=1):
            run_stage(index, total, name, module)
            completed += 1

    except subprocess.CalledProcessError:
        elapsed = perf_counter() - pipeline_start

        print("\n" + "=" * 70)
        print("PIPELINE FAILED")
        print("=" * 70)
        print(f"Completed stages: {completed}/{total}")
        print(f"Total duration: {elapsed:.2f} seconds")

        logger.error(
            "Pipeline failed | completed_stages=%s/%s | duration=%.2f seconds",
            completed,
            total,
            elapsed,
        )

        raise

    elapsed = perf_counter() - pipeline_start

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print(f"Completed stages: {completed}/{total}")
    print(f"Total duration: {elapsed:.2f} seconds")

    logger.info(
        "Pipeline completed successfully | completed_stages=%s/%s | duration=%.2f seconds",
        completed,
        total,
        elapsed,
    )


if __name__ == "__main__":
    main()
