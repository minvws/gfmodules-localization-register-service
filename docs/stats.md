ZModule services use stats to collect and analyze requests throughout all coupled zmodule services. These stats
are collected and stored in a statsd server. 

To enable stats, you need to have a statsd service running (found in the metadata repository), or using docker to run the following command:

```bash
docker run -d --name graphite \
  -p 8010:80 \
  -p 2003-2004:2003-2004 \
  -p 2023-2024:2023-2024 \
  -p 8125:8125/udp \
  -p 8126:8126 \
  graphiteapp/graphite-statsd 
```

This will create a graphite installation with a statsd server listening for incoming statistics metrics.
You can simply access the statsd server by using telnet to http://localhost:8186.

```ini
[stats]
enabled = True
host = 127.0.0.1
port = 8125
```


The following statistics will be monitored:

| Metric               | Description                                     |
|----------------------|-------------------------------------------------|
| `http.post.timeline` | Number of POST requests to the timeline service |
