# Mattermost APP for Splunk

[send_mattermost_alert](https://splunkbase.splunk.com/app/6890)

Now an app that can push splunk log alert result or custom message to a Mattermost channel.
## Install

- Can install by `splunk_mattermost.tar.gz`.
- Or move folder to `/opt/splunk/etc/apps `.
### First, create an alert.

- If you want to push the alert result to a Mattermost channel, you need the `event_message` field,
- By using this search, we can monitor the Splunk log.
- Search grouping by thread_id ensures that messages are correctly and completely captured.
![img.png](img/img.png)

```
index=_internal source="/opt/splunk/var/log/splunk/splunkd.log"
|stats values(event_message) as event_message min(_time) as _time by thread_id
|table _time, event_message, thread_id
```

- Trigger `For each result`.
- Throttle `thread_id`.
- Suppressing time is optional and can be chosen based on your preferences.

![img1.png](img/img1.png)

### Alert be like

![img2.png](img/img2.png)
