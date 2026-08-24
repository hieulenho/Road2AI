from __future__ import annotations

import argparse
import getpass
import json

import requests


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--base-url", default="https://leaderboard.aiguru.com.vn")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    session = requests.Session()
    token_response = session.post(
        f"{base}/api/api-token-auth/",
        data={"username": args.username, "password": getpass.getpass("Password: ")},
        timeout=30,
    )
    token_response.raise_for_status()
    session.headers.update({"Authorization": f"Token {token_response.json()['token']}"})
    leaderboard = session.get(base + "/api/leaderboards/91/", timeout=30)
    leaderboard.raise_for_status()
    rows = leaderboard.json().get("submissions", [])
    compact = []
    for row in rows:
        scores = {item.get("column_key"): item.get("score") for item in row.get("scores", [])}
        compact.append({
            "id": row.get("id"),
            "owner": row.get("owner"),
            "display_name": row.get("display_name"),
            "execution": scores.get("EXECUTION_ACCURACY"),
            "answer": scores.get("ANSWER_ACCURACY"),
            "created_when": row.get("created_when"),
            "detailed_result": row.get("detailed_result"),
        })
    print(json.dumps({"leaderboard_rows": compact}, ensure_ascii=False))

    endpoints = (
        "/api/leaderboards/91/results/",
        "/api/leaderboards/91/entries/",
        "/api/leaderboards/91/submissions/",
        "/api/phases/40/leaderboard/",
        "/api/competitions/14/leaderboard/",
    )
    for endpoint in endpoints:
        response = session.get(base + endpoint, timeout=30)
        text = response.text
        try:
            payload = response.json()
            if isinstance(payload, dict):
                preview: object = {"keys": sorted(payload), "value": payload}
            else:
                preview = payload
            rendered = json.dumps(preview, ensure_ascii=False)
        except Exception:
            rendered = text
        print(json.dumps({
            "endpoint": endpoint,
            "status": response.status_code,
            "content_type": response.headers.get("content-type"),
            "preview": rendered[:4000],
        }, ensure_ascii=False))

    # Probe only normal, authenticated API routes.  Print field names and
    # non-sensitive visibility metadata; never print storage URLs or tokens.
    for endpoint in ("/api/submissions/2231/", "/api/submissions/2231/get_details/"):
        response = session.get(base + endpoint, timeout=30)
        try:
            payload = response.json()
        except Exception:
            payload = None
        if isinstance(payload, dict):
            safe = {
                "keys": sorted(payload),
                "id": payload.get("id"),
                "owner": payload.get("owner"),
                "status": payload.get("status"),
                "is_public": payload.get("is_public"),
                "is_shared": payload.get("is_shared"),
                "public": payload.get("public"),
                "has_prediction_result": bool(payload.get("prediction_result")),
                "has_scoring_result": bool(payload.get("scoring_result")),
                "has_data": bool(payload.get("data")),
            }
        else:
            safe = {"body_preview": response.text[:300]}
        print(json.dumps({
            "endpoint": endpoint,
            "status": response.status_code,
            "safe": safe,
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
