#!/usr/bin/env python3
import argparse
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path


def api(token, method, params):
    url = f"https://api.telegram.org/bot{token}/{method}?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            payload = json.load(response)
    except Exception:
        # Never expose a Bot API URL because it contains the token.
        raise RuntimeError(f"Telegram API request failed: {method}") from None
    if not payload.get("ok"):
        raise RuntimeError(payload.get("description", "Telegram API rejected request"))
    return payload["result"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--mode", choices=("channel", "agent_chat"), required=True)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--token-env", default="SANCTIONS_TELEGRAM_BOT_TOKEN")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        token = os.environ.get(args.token_env)
        if not token:
            raise SystemExit(f"Missing environment variable: {args.token_env}")
        bot = api(token, "getMe", {})
        chat = api(token, "getChat", {"chat_id": args.destination})
        if args.mode == "channel":
            member = api(token, "getChatMember", {"chat_id": args.destination, "user_id": bot["id"]})
            if member.get("status") not in {"administrator", "creator"} or member.get("can_post_messages") is False:
                raise SystemExit("Bot is not allowed to post to this channel")
        api(token, "sendMessage", {"chat_id": args.destination, "text": "Sanctions monitor delivery test: OK"})
        print(f"Verified Telegram destination type: {chat.get('type', 'unknown')}")
    data = {
        "delivery": {
            "mode": args.mode,
            "destination": args.destination,
            "bot_token_env": args.token_env,
            "queued_activation_policy": "review",
        },
        "database": "./runtime/sanctions.sqlite3",
        "output_directory": "./runtime/documents",
    }
    path = Path(args.config)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Configuration written: {path}")


if __name__ == "__main__":
    main()
