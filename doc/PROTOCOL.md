# Protocol

## 1. Streaming text format

### 1.1. Request

```
{
    "route": <str mandatory Route name, eg. aether.auth.login>,
    "type": "open",
    "stream": <str mandatory Stream ID, decided by client, should be unique>,
    "session": <str optional Session ID. Only required on first message after login, but can be sent on all>,
    "message": <dict mandatory Message data, depends on operation>
}
```

### 1.2. Message event

If the request was valid, the server will respond with message(s) of the following format.
Note that more than one message may be sent, depending on request type (login, get_forum_boards, etc.).

```
{
    "message": <dict mandatory Message content. This will depend on operation>,
    "type": "message",
    "stream": <str mandatory Stream ID>
}
```

### 1.3. Error event

If error happens on server side, the server will respond with a following error structure. Note that an
error should be automatically taken as a stream closing event -- when an error happens, no further messages
will be sent in the stream and it can be safely considered as dead. Stream ID can be re-used if necessary.

```
{
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
    },
    "type": "error",
    "stream": <str mandatory Stream ID>
}
```

### 1.4. Close event

When server has transferred all the data it intends to transfer, the stream is closed with the following message.
Stream ID will match the one you set in the request. After server has sent this message, the stream should be considered
dead. Stream ID can be re-used if necessary.

```
{
    "message": {},
    "type": "close",
    "stream": <str mandatory Stream ID>
}
```
