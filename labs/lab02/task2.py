import logging
import json
import hashlib
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class FileRecord:
    path: str
    sha256: str
    size: int
    modified: str


def compute_sha256(file_path: Path) -> str:
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
    except PermissionError:
        logging.error(
            f"Помилка доступу (PermissionError). Немає прав для читання: {file_path}"
        )
        return ""
    except FileNotFoundError:
        logging.error(f"Файл не знайдено (FileNotFoundError): {file_path}")
        return ""
    except OSError as e:
        logging.error(f"Системна помилка при читанні файлу {file_path}: {e}")
        return ""
    return hash_sha256.hexdigest()


def scan_directory(directory: Path) -> dict:
    records = {}
    try:
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                try:
                    rel_path = str(file_path.relative_to(directory)).replace("\\", "/")
                    file_hash = compute_sha256(file_path)
                    stat = file_path.stat()
                    modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
                    records[rel_path] = FileRecord(
                        path=rel_path,
                        sha256=file_hash,
                        size=stat.st_size,
                        modified=modified,
                    )
                except PermissionError:
                    logging.warning(
                        f"Пропущено файл через відсутність прав доступу: {file_path}"
                    )
                except OSError as e:
                    logging.warning(f"Не вдалося обробити файл {file_path}: {e}")
    except Exception as e:
        logging.error(f"Критична помилка при скануванні директорії {directory}: {e}")

    return records


def generate_baseline(directory: Path, baseline_file: Path):
    logging.info(f"Scanning directory: {directory.resolve()}")
    records = scan_directory(directory)

    try:
        with open(baseline_file, "w", encoding="utf-8") as f:
            json.dump([asdict(record) for record in records.values()], f, indent=2)
        logging.info(f"Baseline successfully generated at {baseline_file}")
    except PermissionError:
        logging.error(f"Немає прав на запис у файл еталону: {baseline_file}")
    except OSError as e:
        logging.error(f"Помилка вводу/виводу при збереженні еталонного файлу: {e}")


def check_integrity(directory: Path, baseline_file: Path):
    logging.info(f"Loading baseline file: {baseline_file}")

    if not baseline_file.exists():
        logging.error("Baseline file does not exist. Run generate mode first.")
        return

    try:
        with open(baseline_file, "r", encoding="utf-8") as f:
            baseline_data = json.load(f)
    except json.JSONDecodeError as e:
        logging.error(f"Помилка формату JSON у файлі еталону {baseline_file}: {e}")
        return
    except PermissionError:
        logging.error(f"Немає прав на читання файлу еталону: {baseline_file}")
        return
    except Exception as e:
        logging.error(f"Не вдалося прочитати файл еталону: {e}")
        return

    baseline_records = {item["path"]: FileRecord(**item) for item in baseline_data}

    logging.info(f"Scanning directory: {directory.resolve()}")
    current_records = scan_directory(directory)

    unchanged = []
    modified = []
    created = []
    deleted = []

    for rel_path, current_record in current_records.items():
        if rel_path in baseline_records:
            if current_record.sha256 == baseline_records[rel_path].sha256:
                unchanged.append(rel_path)
            else:
                modified.append(
                    (rel_path, baseline_records[rel_path].sha256, current_record.sha256)
                )
        else:
            created.append(current_record)

    for rel_path in baseline_records:
        if rel_path not in current_records:
            deleted.append(rel_path)

    print("\n=== File Integrity Inspection Summary ===")
    print(f"Total monitored files : {len(current_records)}")
    print(f"Unchanged files       : {len(unchanged)}")
    print(f"Modified files        : {len(modified)}")
    print(f"Created files         : {len(created)}")
    print(f"Deleted files         : {len(deleted)}\n")

    if modified or created or deleted:
        print("=== Detected Anomalies ===")
        for path, old_hash, new_hash in modified:
            print(f"[MODIFIED] {path}")
            print(f"  Expected SHA-256 : {old_hash}")
            print(f"  Actual SHA-256   : {new_hash}")

        for record in created:
            print(f"[CREATED]  {record.path} (Size: {record.size} B)")

        for path in deleted:
            print(f"[DELETED]  {path}")

        logging.warning(
            "Security alerts detected! Anomalies found in monitored directory."
        )
    else:
        print("=== No Anomalies Detected ===")
        logging.info("All files match the baseline.")


def run_fim(args):
    log_format = "[%(levelname)s] %(message)s"
    handlers = [logging.StreamHandler()]
    if args.log_file:
        try:
            handlers.append(logging.FileHandler(args.log_file, encoding="utf-8"))
        except OSError as e:
            print(f"[ERROR] Не вдалося створити лог-файл {args.log_file}: {e}")
            return

    logging.basicConfig(level=logging.INFO, format=log_format, handlers=handlers)

    dir_path = Path(args.dir)
    baseline_path = Path(args.baseline)

    if not dir_path.exists() or not dir_path.is_dir():
        logging.error(f"Directory {dir_path} does not exist or is not a directory.")
        return

    if args.mode == "generate":
        generate_baseline(dir_path, baseline_path)
    elif args.mode == "check":
        check_integrity(dir_path, baseline_path)
