import time
import yaml
import csv
from pathlib import Path
from transcoder import Transcoder
import bitstream_bindings as bs
from bitstream import BitstreamIO

def transcode(config_path, sequences, segment_ids, output_csv):
# Load base config
    with open(config_path, "r") as f:
        base_config = yaml.safe_load(f)

    # Load rate config
    rate_config_path = base_config.get("rate-config", "rate/R1.yaml")
    with open(rate_config_path, "r") as f:
        rate_config = yaml.safe_load(f)

    base_config.update(rate_config)

    results = []

    for seq in sequences:
        for sid in segment_ids:
            filename = f"{seq}_r5_segment{sid}.bin"
            in_path = str(Path(base_config["input_dir"]) / filename)
            out_path = str(Path(base_config["output_dir"]) / f"{seq}_segment{sid}_out.bin")

            # Update config
            config = base_config.copy()
            config["in_path"] = in_path
            config["out_path"] = out_path

            # Transcode
            t0 = time.time()
            transcoder = Transcoder(config)
            transcoder.transcode(in_path, out_path, config)
            duration = time.time() - t0

            results.append({
                "sequence": seq,
                "segment_id": sid,
                "in_path": in_path,
                "out_path": out_path,
                "time_sec": round(duration, 4),
            })
            print(f"Finished {filename} in {duration:.2f}s")

    # Save to CSV
    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    sequences = ["soldier", "longdress", "loot", "redandblack"]  
    segment_ids = list(range(20))

    # Kvazaar
    config_path = "/app/configs/test_config_kvazaar.yaml"
    output_csv = "/app/results/transcode_times_kvazaar.csv"
    transcode(config_path, sequences, segment_ids, output_csv)

    # x265
    config_path = "/app/configs/test_config_x265.yaml"
    output_csv = "/app/results/transcode_times_x265.csv"
    transcode(config_path, sequences, segment_ids, output_csv)