import sys
import json
import requests
from datetime import datetime


def log(msg):
    sys.stderr.write(f'{msg}\n')


def send2mattermost(payload):
    conf = payload.get('configuration')
    url = conf.get('url')
    if not url.startswith('https://'):
        raise ValueError("Only HTTPS URLs are allowed.")
    log_data = payload.get('result')
    headers = {
        "Content-Type": "application/json",
        "Authorization": conf.get('header'),
    }
    attachments = []

    try:
        convert_str = '\n'.join(log_data["event_message"]) if isinstance(log_data["event_message"], list) else log_data[
            "event_message"]
        if convert_str:
            attachments.append(
                {"text": f'{datetime.fromtimestamp(float(log_data["_time"]))},\n{convert_str}'})
    except:
        pass

    if conf.get('message'):
        attachments.append({"pretext": conf.get('message')})
    data = {
        "channel_id": conf.get('channel'),
        "props": {
            "attachments": attachments
        },
    }
    response = requests.post(url, headers=headers, json=data)

    if 200 <= response.status_code < 300:
        log(f"INFO action receiver responded with HTTP status={response.status_code}")
        return True
    else:
        log(f"ERROR action receiver responded with HTTP status={response.status_code}")
        return False


if __name__ == "__main__":
    log("INFO Running python %s" % (sys.version_info[0]))
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        _stdin = json.loads(sys.stdin.read())
        res = send2mattermost(_stdin)
        if res:
            log("INFO Successfully sent mattermost message")
            # sys.exit(2)
        else:
            log("FATAL Alert action failed")
    else:
        log("FATAL Unsupported execution mode (expected --execute flag)")
        sys.exit(1)
