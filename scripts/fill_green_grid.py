import datetime
import os
import random
import subprocess
import sys

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

NAME = "Aditya Sudhir Pawar"
EMAIL = "adityapawarone8@gmail.com"
DAYS_BACK = 365  # Fill the past 365 days

def main():
    print(f"🚀 Lightning-Fast Green Grid Generator for {NAME} <{EMAIL}>")
    print(f"Target: Backfilling past {DAYS_BACK} days into contribution calendar...")

    # Ensure activity log exists
    os.makedirs("data", exist_ok=True)
    log_file = os.path.join("data", "activity.log")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"Initiated green grid activity timeline: {datetime.datetime.now().isoformat()}\n")

    # Stage data/activity.log and obtain in-memory git tree hash
    subprocess.run(["git", "add", "data/activity.log"], check=True)
    tree_hash = subprocess.check_output(["git", "write-tree"]).decode().strip()
    parent_commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()

    today = datetime.datetime.now()
    start_date = today - datetime.timedelta(days=DAYS_BACK)

    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = NAME
    env["GIT_AUTHOR_EMAIL"] = EMAIL
    env["GIT_COMMITTER_NAME"] = NAME
    env["GIT_COMMITTER_EMAIL"] = EMAIL

    total_commits = 0

    for day_offset in range(DAYS_BACK + 1):
        current_day = start_date + datetime.timedelta(days=day_offset)
        if current_day > today:
            break

        # 1 to 4 commits per day for a vibrant multi-shade green activity board
        num_commits = random.randint(1, 4)

        for commit_idx in range(num_commits):
            hour = random.randint(9, 21)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            commit_time = current_day.replace(hour=hour, minute=minute, second=second)
            date_str = commit_time.strftime("%Y-%m-%d %H:%M:%S +0530")

            env["GIT_AUTHOR_DATE"] = date_str
            env["GIT_COMMITTER_DATE"] = date_str

            msg = f"chore(telemetry): automated activity sync for {commit_time.strftime('%Y-%m-%d')} #{commit_idx + 1}"
            cmd = ["git", "commit-tree", tree_hash, "-p", parent_commit, "-m", msg]
            parent_commit = subprocess.check_output(cmd, env=env).decode().strip()
            total_commits += 1

    # Update HEAD ref to the tip of our new commit chain
    subprocess.run(["git", "update-ref", "refs/heads/main", parent_commit], check=True)
    subprocess.run(["git", "reset", "--hard", "HEAD"], check=True)

    print(f"\n🎉 SUCCESS! Generated {total_commits} historical commits across the past {DAYS_BACK} days.")
    print("Now pushing to GitHub to illuminate your entire contribution calendar green...")

if __name__ == "__main__":
    main()
