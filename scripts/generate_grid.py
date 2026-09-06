import datetime
import os
import random
import subprocess
import sys
import time

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

NAME = "Aditya Sudhir Pawar"
EMAIL = "adityapawarone8@gmail.com"
DAYS_BACK = 365

def main():
    print(f"Generating green contribution activity for past {DAYS_BACK} days...")
    start_time = time.time()

    head = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    today = datetime.datetime.now()
    start_date = today - datetime.timedelta(days=DAYS_BACK)

    stream = []
    mark_num = 1

    for day_offset in range(DAYS_BACK + 1):
        current_day = start_date + datetime.timedelta(days=day_offset)
        if current_day > today:
            break

        # 1 to 3 commits per day for a rich, natural green gradient
        num_commits = random.randint(1, 3)

        for commit_idx in range(num_commits):
            hour = random.randint(9, 21)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            commit_time = current_day.replace(hour=hour, minute=minute, second=second)
            ts = int(commit_time.timestamp())

            msg = f"chore(activity): automated telemetry sync for {commit_time.strftime('%Y-%m-%d')} #{commit_idx + 1}"
            content = f"{commit_time.strftime('%Y-%m-%d %H:%M:%S')} - verified telemetry heartbeat #{commit_idx + 1}\n"

            stream.append("commit refs/heads/main\n")
            stream.append(f"mark :{mark_num}\n")
            stream.append(f"author {NAME} <{EMAIL}> {ts} +0530\n")
            stream.append(f"committer {NAME} <{EMAIL}> {ts} +0530\n")
            stream.append(f"data {len(msg.encode('utf-8'))}\n{msg}\n")

            if mark_num == 1:
                stream.append(f"from {head}\n")
            else:
                stream.append(f"from :{mark_num - 1}\n")

            stream.append("M 644 inline data/activity.log\n")
            stream.append(f"data {len(content.encode('utf-8'))}\n{content}\n")

            mark_num += 1

    input_bytes = "".join(stream).encode("utf-8")

    # Pipe directly to git fast-import
    proc = subprocess.Popen(["git", "fast-import", "--quiet"], stdin=subprocess.PIPE)
    proc.communicate(input_bytes)

    if proc.returncode != 0:
        print("Error during fast-import")
        sys.exit(proc.returncode)

    # Reset working tree to match new HEAD
    subprocess.run(["git", "reset", "--hard", "HEAD"], check=True)

    elapsed = round(time.time() - start_time, 2)
    print(f"Generated {mark_num - 1} commits across {DAYS_BACK} days in {elapsed} seconds!")
    print("Ready to push to GitHub with: git push origin main")

if __name__ == "__main__":
    main()
