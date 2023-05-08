import sys
import json
import requests
from datetime import datetime

"""
index=_internal source="/opt/splunk/var/log/splunk/splunkd.log" log_level="ERROR"  
|stats values(event_message) as event_message min(_time) as _time by thread_id
| where like(event_message, "%"+"sendaction.py"+"%") 
| table _time, event_message, thread_id
"""

"""
[TRAPA_sendalert_monitor]
action.mattermost = 1
alert.digest_mode = 0
alert.suppress = 1
alert.suppress.fields = thread_id
alert.suppress.period = 60m
alert.track = 0
counttype = number of events
cron_schedule = */1 * * * *
dispatch.earliest_time = -15m
dispatch.latest_time = now
enableSched = 1
quantity = 0
relation = greater than
search = index=_internal source="/opt/splunk/var/log/splunk/splunkd.log" log_level="ERROR"  \
|stats values(event_message) as event_message min(_time) as _time by thread_id\
| where like(event_message, "%"+"sendaction.py"+"%") \
| table _time, event_message, thread_id
"""


def log(msg):
    sys.stderr.write(f'{msg}\n')


def send2mattermost(payload):
    conf = payload.get('configuration')
    url = conf.get('url')
    log_data = payload.get('result')
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {conf.get('token')}",
    }
    convert_str = '\n'.join(log_data["event_message"]) if isinstance(log_data["event_message"], list) else log_data[
        "event_message"]
    data = {
        "channel_id": conf.get('channel'),
        "props": {
            "attachments": [
                {"text": f'{datetime.fromtimestamp(float(log_data["_time"]))},\n{convert_str}'}
            ]
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
