"""Keep the published Postman collections in sync with the JSON files in this repo.

.github/postman-sync.json maps each collection file to the UID of its published
Postman collection.

Commands
  sync (default)  Update each published collection from its file through the
                  Postman API (PUT /collections/{uid}). Items keep their IDs, so
                  requests are updated in place.
  pull            Download each published collection and write it to its file,
                  so changes made in Postman can be reviewed and committed.

Safety checks before `sync` updates a collection:
  * The file's info._postman_id must match the target collection UID.
  * Drift check: each item in the published collection must match the file at
    BASE_SHA (the last synced version), or a version of the file in this change
    (the file being synced, or any commit after BASE_SHA, such as a commit that
    ran `pull`). Otherwise someone changed it in Postman since the last sync,
    and the run stops and lists the changed items instead of overwriting them.
    Set ALLOW_OVERWRITE=true to overwrite anyway.
  * The update must not remove more than MAX_REMOVED_RATIO of the existing
    items. Set ALLOW_BULK_REMOVE=true to override.

Environment
  POSTMAN_API_KEY    required
  DRY_RUN=true       run the checks without updating Postman
  BASE_SHA           commit to compare the published collection with (sync only)
  ALLOW_OVERWRITE    see drift check
  ALLOW_BULK_REMOVE  see removal check
  POSTMAN_SYNC_MAP   mapping file (default .github/postman-sync.json)
"""
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

API = "https://api.getpostman.com/collections/"
MAX_REMOVED_RATIO = 0.2
# Fields that Postman adds on export or in API responses. They aren't content.
METADATA_INFO_KEYS = {"_exporter_id", "_collection_link", "createdAt", "updatedAt", "lastUpdatedBy", "fork", "uid"}
IGNORED_FOR_COMPARE = {"id", "uid", "_postman_id", "responseTime", "disableBodyPruning"} | METADATA_INFO_KEYS


def call(method, uid, key, body=None):
    req = urllib.request.Request(
        API + uid,
        method=method,
        data=None if body is None else json.dumps(body).encode(),
        headers={"X-Api-Key": key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as err:
        detail = err.read().decode(errors="replace")[:500]
        sys.exit(f"{method} {uid} failed: HTTP {err.code} {detail}")


def clean(collection):
    """Remove metadata so the collection can be sent to the API or saved to a file."""
    info = collection.get("info", {})
    for k in METADATA_INFO_KEYS:
        info.pop(k, None)

    def strip_uids(obj):
        if isinstance(obj, dict):
            obj.pop("uid", None)
            for value in obj.values():
                strip_uids(value)
        elif isinstance(obj, list):
            for value in obj:
                strip_uids(value)

    strip_uids(collection.get("item", []))
    return collection


def item_ids(items, out=None):
    out = set() if out is None else out
    for it in items:
        if it.get("id"):
            out.add(it["id"])
        for resp in it.get("response") or []:
            if resp.get("id"):
                out.add(resp["id"])
        if "item" in it:
            item_ids(it["item"], out)
    return out


def normalize(value):
    """Reduce a collection to its content, so formatting and metadata don't count as changes."""
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            # Postman's own "_postman_*" fields (for example _postman_previewlanguage,
            # which Postman fills in when it saves a response) are display settings.
            if k in IGNORED_FOR_COMPARE or k.startswith("_postman_"):
                continue
            if k == "url" and isinstance(v, dict) and "raw" in v:
                v = v["raw"]
            if k == "raw" and isinstance(v, str):
                try:
                    v = json.loads(v)
                except ValueError:
                    pass
            v = normalize(v)
            if v not in ({}, [], None, ""):
                out[k] = v
        return out
    if isinstance(value, list):
        return [normalize(v) for v in value]
    return value


def flatten(items, prefix=""):
    """Map 'Folder/Request' paths to each item's content, without its child items."""
    out = {}
    for it in items:
        path = f"{prefix}/{it.get('name', '')}"
        while path in out:
            path += "*"
        out[path] = normalize({k: v for k, v in it.items() if k != "item"})
        if "item" in it:
            out.update(flatten(it["item"], path))
    return out


def top_level(collection):
    return normalize({k: v for k, v in collection.items() if k != "item"})


def differences(published, baseline, pulled=()):
    """List the items in the published collection that were changed outside GitHub.

    An item counts as changed if it differs from the baseline (the last synced
    version) and also from every version in `pulled` (versions of the file that are
    part of this change, for example a commit that ran the pull command). So an
    edit made in Postman and then pulled into GitHub isn't reported.
    """
    a, b = flatten(published.get("item", [])), flatten(baseline.get("item", []))
    accepted = [flatten(v.get("item", [])) for v in pulled]
    changes = []
    for p in sorted(a.keys() | b.keys()):
        current = a.get(p)
        if current == b.get(p) or any(current == v.get(p) for v in accepted):
            continue
        kind = "added in Postman:  " if p not in b else "removed in Postman:" if p not in a else "changed in Postman:"
        changes.append(f"  {kind} {p}")
    top = top_level(published)
    if top != top_level(baseline) and all(top != top_level(v) for v in pulled):
        changes.append("  changed in Postman: (collection settings, description, auth, or variables)")
    return changes


def file_at(sha, path):
    if not sha or set(sha) == {"0"}:
        return None
    result = subprocess.run(["git", "show", f"{sha}:{path}"], capture_output=True, text=True)
    return json.loads(result.stdout) if result.returncode == 0 else None


def versions_since(base_sha, path):
    """Versions of the file in the commits after base_sha, newest first."""
    result = subprocess.run(["git", "rev-list", f"{base_sha}..HEAD", "--", path], capture_output=True, text=True)
    commits = result.stdout.split() if result.returncode == 0 else []
    return [v for v in (file_at(sha, path) for sha in commits) if v is not None]


def drift_check(path, uid, published, base_sha, allow_overwrite, current_file):
    baseline = file_at(base_sha, path)
    if baseline is None or not uid.endswith(baseline.get("info", {}).get("_postman_id") or "-"):
        print(f"Drift check skipped: no earlier version of {path} for this collection at {base_sha or 'BASE_SHA'}.")
        return
    changes = differences(published, baseline, [current_file] + versions_since(base_sha, path))
    if not changes:
        print("Drift check passed: the published collection has no changes made outside GitHub.")
        return
    report = "\n".join(changes[:50]) + ("\n  ..." if len(changes) > 50 else "")
    message = (f"The published collection was changed in Postman since the last sync "
               f"({len(changes)} items):\n{report}\n"
               "To keep these changes, run `python3 .github/scripts/postman_sync.py pull` on a branch "
               "from main, commit the result, and merge it in a pull request with a merge commit.")
    if allow_overwrite:
        print(message + "\nALLOW_OVERWRITE=true: overwriting them.")
    else:
        sys.exit(message + "\nStopped without changing Postman. Set ALLOW_OVERWRITE=true to overwrite them.")


def sync(path, uid, key, env):
    with open(path, encoding="utf-8") as fh:
        collection = clean(json.load(fh))
    file_id = collection.get("info", {}).get("_postman_id")
    if not file_id or not uid.endswith(file_id):
        sys.exit(f"{path}: info._postman_id {file_id!r} doesn't match target {uid}")

    published = call("GET", uid, key)["collection"]
    drift_check(path, uid, published, env["base_sha"], env["allow_overwrite"], collection)

    before, local = item_ids(published["item"]), item_ids(collection["item"])
    removed, added = before - local, local - before
    print(f"{path} -> {uid}: {len(before)} items in Postman, {len(local)} in file, "
          f"{len(added)} to add, {len(removed)} to remove")
    if before and len(removed) / len(before) > MAX_REMOVED_RATIO and not env["allow_bulk_remove"]:
        sys.exit(f"Refusing: the update would remove {len(removed)} of {len(before)} items "
                 f"(more than {MAX_REMOVED_RATIO:.0%}). Item IDs probably don't match. "
                 "Run the pull command to refresh the file, or set ALLOW_BULK_REMOVE=true.")
    if env["dry_run"]:
        print("Dry run: no changes made.")
        return

    call("PUT", uid, key, {"collection": collection})
    after = item_ids(call("GET", uid, key)["collection"]["item"])
    missing = local - after
    if missing:
        sys.exit(f"After the update, {len(missing)} item IDs from the file are missing in Postman.")
    print(f"Updated. {len(after)} items, all IDs from the file kept.")


def pull(path, uid, key):
    published = clean(call("GET", uid, key)["collection"])
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(published, fh, indent=2, ensure_ascii=False)
    print(f"Wrote {uid} to {path}. Review the changes with `git diff`.")


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else "sync"
    if command not in ("sync", "pull"):
        sys.exit("Usage: postman_sync.py [sync|pull]")
    key = os.environ.get("POSTMAN_API_KEY")
    if not key:
        sys.exit("POSTMAN_API_KEY is not set.")
    flag = lambda name: os.environ.get(name, "false").lower() == "true"
    env = {
        "dry_run": flag("DRY_RUN"),
        "allow_overwrite": flag("ALLOW_OVERWRITE"),
        "allow_bulk_remove": flag("ALLOW_BULK_REMOVE"),
        "base_sha": os.environ.get("BASE_SHA", ""),
    }
    with open(os.environ.get("POSTMAN_SYNC_MAP", ".github/postman-sync.json"), encoding="utf-8") as fh:
        mapping = json.load(fh)
    for path, uid in mapping.items():
        if command == "pull":
            pull(path, uid, key)
        else:
            sync(path, uid, key, env)


if __name__ == "__main__":
    main()
