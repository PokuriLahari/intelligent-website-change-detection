import difflib


def compute_diff(old_content, new_content):
    old_lines = old_content.splitlines()
    new_lines = new_content.splitlines()
    diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=""))
    return diff


def extract_changes(diff):
    added = []
    removed = []

    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            added.append(line[1:].strip())
        elif line.startswith("-") and not line.startswith("---"):
            removed.append(line[1:].strip())

    return added, removed


def classify_change(diff, old_content):
    added, removed = extract_changes(diff)

    # Rule 1: Volume threshold
    total_lines = len(old_content.splitlines()) or 1
    change_ratio = (len(added) + len(removed)) / total_lines

    # Rule 2: High-value keyword in changed lines
    keywords = ["price", "$", "€", "launch", "new", "removed",
                 "deprecated", "update", "sale", "discount", "free", "limited"]
    changed_text = " ".join(added + removed).lower()
    keyword_hit = any(k in changed_text for k in keywords)

    if change_ratio > 0.10 or (len(added) + len(removed)) > 20:
        return "major"
    elif keyword_hit or (len(added) + len(removed)) > 3:
        return "minor"
    else:
        return "none"


def get_change_stats(diff, old_content):
    added, removed = extract_changes(diff)

    total_lines = len(old_content.splitlines()) or 1
    total_changes = len(added) + len(removed)
    change_percent = (total_changes / total_lines) * 100

    return {
        "added": len(added),
        "removed": len(removed),
        "total_changes": total_changes,
        "change_percent": round(change_percent, 2)
    }


def format_diff_preview(diff, max_lines=20):
    """Returns a readable string preview of the diff for alerts and logs."""
    preview = []
    count = 0

    for line in diff:
        if count >= max_lines:
            preview.append(f"... and {len(diff) - count} more lines")
            break
        if line.startswith("+") and not line.startswith("+++"):
            preview.append(f"  ADDED   → {line[1:].strip()}")
            count += 1
        elif line.startswith("-") and not line.startswith("---"):
            preview.append(f"  REMOVED → {line[1:].strip()}")
            count += 1

    return "\n".join(preview) if preview else "No visible changes."