# Domain Logs Service

Live streaming of domain/application logs to clients over **SSE** or
**WebSocket**.

## Pipeline

```
collector (LogCollector)  ->  tailer  ->  service.stream()  ->  SSE / WebSocket  ->  client
```

- **Collectors** (`collectors/base.py`) are pluggable sources (file tail,
  journald, message bus). Implement the `LogCollector` protocol and register it.
- **Tailer** (`streaming/tailer.py`) turns a source into an async stream of
  `LogEntryOut`.
- **Transports** (`streaming/sse.py`, `streaming/websocket.py`) deliver the
  stream to clients.

## Endpoints

| Method | Path                                      | Transport |
| ------ | ----------------------------------------- | --------- |
| GET    | `/domain-logs/sources/{source_id}/stream` | SSE       |
| WS     | `/domain-logs/sources/{source_id}/ws`     | WebSocket |

## Configuration

`DomainLogsSettings` (`DOMAIN_LOGS_` env prefix) in [`config.py`](config.py):
heartbeat interval and buffer sizing.

## Models

`LogSource` and `LogEntry` in [`models.py`](models.py).
