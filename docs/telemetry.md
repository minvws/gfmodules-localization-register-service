All zmodule services support telemetry tracing. This is a feature that allows you to collect and analyze requests throughout all coupled zmodule services. We use [opentelemetry](https://opentelemetry.io/) in combination with [jaeger](https://www.jaegertracing.io/) to view and inspect the telemetry data.

To enable telemetry, you need to have a jaeger instance running. You can run jaeger locally using docker by running the following command:

```bash
docker run -d --name jaeger \
  -e COLLECTOR_ZIPKIN_HTTP_PORT=9411 \
  -p 5775:5775/udp \
  -p 6831:6831/udp \
  -p 6832:6832/udp \
  -p 5778:5778 \
  -p 16686:16686 \
  -p 14268:14268 \
  -p 14250:14250 \
  -p 9411:9411 \
  jaegertracing/all-in-one:latest
```

After running the command, you can access the jaeger UI by visiting http://localhost:16686. You can then enable telemetry in your zmodule services by setting the `enabled = True` in the `[telemetry]` section of the `app.conf` file.

```ini
[telemetry]
enabled = True
endpoint = http://localhost:4317
service_name = timeline
tracer_name = zmodules.service.timeline
```

The `endpoint` is the address of the jaeger instance. The `service_name` is the name of the service that will be displayed in the jaeger UI. The `tracer_name` is the name of the tracer that will be displayed in the jaeger UI.

All communication between the service and jaeger is done through GRPC.
