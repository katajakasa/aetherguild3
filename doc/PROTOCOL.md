# Protocol

## 1. Requests

### 1.1. Request (client => server)

```
{
    "type": "request",
    "route": <str mandatory Route name, eg. aether.auth.login>,
    "stream": <str mandatory Stream ID, decided by client, should be unique>,
    "session": <str optional Session ID. Only required on first message after login, but can be sent on all>,
    "message": <dict mandatory Message data, depends on operation>
}
```

### 1.2. Response event (server => client)

If the request was valid, the server will respond with message(s) of the following format.

```
{
    "type": "response",
    "stream": <str mandatory Stream ID>,
    "message": <dict mandatory Message content. This will depend on operation>,
}
```

### 1.3. Error event (server => client)

If error happens on server side, the server will respond with a following error structure.

```
{
    "type": "error",
    "stream": <str mandatory Stream ID>,
    "message": {
        "field_errors": [
            {
                "field": <str mandatory Field name>,
                "message": <str mandatory Error message>
            },
            ....
        ],
        "errors": [
            <str optional Error message>,
            ...
        ],
        "code": <int mandatory Errorcode>,
    }
}
```

## 2. Subscriptions

### 2.1. Subscribe (client => server)

Subscribes the client to a queue.

```
{
    "type": "subscribe",
    "route": <str mandatory Queue name, eg. aether.queue.forum_threads>,
    "stream": <str mandatory Stream ID, decided by client, should be unique>,
    "session": <str optional Session ID. Only required on first message after login, but can be sent on all>,
}
```

### 2.2. Unsubscribe (client => server)

Unsubscribes the client from a queue.

```
{
    "type": "unsubscribe",
    "stream": <str mandatory Stream ID, decided by client, should be unique>,
    "session": <str optional Session ID. Only required on first message after login, but can be sent on all>,
}
```

### 2.3. Message event (server => client)

Message from server to client as per subscription

```
{
    "type": "broadcast",
    "stream": <str mandatory Stream ID>,
    "message": <dict mandatory Message content. This will depend on operation>,
}
```

### 2.4. Close event (server => client)

If the server side closes the subscription, this message will be sent for all subscriptions.

```
{
    "type": "close",
    "stream": <str mandatory Stream ID>,
}
```

### 2.5. Error event (server => client)

If error happens on server side, the server will respond with a following error structure.

```
{
    "type": "error",
    "stream": <str mandatory Stream ID>,
    "message": {
        "errors": [
            <str optional Error message>,
            ...
        ],
        "code": <int mandatory Errorcode>,
    }
}
```
