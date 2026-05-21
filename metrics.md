# metrics

## /api/v0/application

```sh
curl -X 'GET' \
  'https://slskd.example.com/api/v0/application' \
  -H 'accept: application/json'

{
  "version": {
    "full": "0.25.1.0 (0.25.1.0+7961741f)",
    "current": "0.25.1.0",
    "latest": "0.25.1.0",
    "isUpdateAvailable": false,
    "isCanary": false,
    "isDevelopment": false
  },
  "pendingReconnect": false,
  "pendingRestart": false,
  "server": {
    "address": "vps.slsknet.org",
    "ipEndPoint": "208.76.170.59:2271",
    "state": "Connected, LoggedIn",
    "isConnected": true,
    "isConnecting": false,
    "isLoggedIn": true,
    "isLoggingIn": false,
    "isTransitioning": false
  },
  "connectionWatchdog": {
    "isEnabled": false,
    "isAttemptingConnection": false,
    "isAwaitingVpn": false
  },
  "vpn": {
    "isReady": false,
    "isConnected": false
  },
  "relay": {
    "mode": "Controller",
    "controller": {
      "state": "Disconnected"
    },
    "agents": []
  },
  "health": {
    "search": {
      "incoming": {
        "latency": 1.748061660740767,
        "queueDepth": 0,
        "dropRate": 0
      }
    }
  },
  "user": {
    "username": "qwuhueirghe",
    "privileges": {
      "isPrivileged": false,
      "privilegesRemaining": 0
    },
    "statistics": {
      "averageSpeed": 7253467,
      "directoryCount": 598,
      "fileCount": 5399,
      "uploadCount": 108
    }
  },
  "distributedNetwork": {
    "branchLevel": 6,
    "branchRoot": "shantih",
    "canAcceptChildren": true,
    "childLimit": 25,
    "children": [
      "cr4m3"
    ],
    "hasParent": true,
    "isBranchRoot": false,
    "parent": "HypNotiQIV"
  },
  "shares": {
    "scanPending": false,
    "scanning": false,
    "ready": true,
    "faulted": false,
    "cancelled": false,
    "scanProgress": 1,
    "hosts": [
      "local"
    ],
    "directories": 598,
    "files": 5399
  },
  "rooms": [],
  "users": []
}
```

metric keys to parse:

- current (set as label)
- isUpdateAvailable
- isCanary
- isDevelopment

- pendingReconnect
- pendingRestart

- isConnected
- isConnecting
- isLoggedIn
- isLoggingIn
- isTransitioning

- isEnabled
- isAttemptingConnection
- isAwaitingVpn

- isReady
- isConnected

- state

- latency
- queueDepth
- dropRate

- username (set as label)

- averageSpeed
- directoryCount
- fileCount
- uploadCount

- scanPending
- scanning
- ready
- faulted
- cancelled
- scanProgress

## /api/v0/conversations

```sh
curl -X 'GET' \
  'https://slskd.example.com/api/v0/conversations?includeInactive=true&unAcknowledgedOnly=false' \
  -H 'accept: application/json'

[
  {
    "username": "AnTwanChi",
    "isActive": false,
    "unAcknowledgedMessageCount": 0,
    "hasUnAcknowledgedMessages": false
  },
  {
    "username": "Cr_ckpot",
    "isActive": false,
    "unAcknowledgedMessageCount": 0,
    "hasUnAcknowledgedMessages": false
  }
]
```

- count how many conversations total
- count how many total unacknowledged message count

## /api/v0/telemetry/reports/transfers/summary

```sh
curl -X 'GET' \
  'https://slskd.example.com/api/v0/telemetry/reports/transfers/summary?start=1' \
  -H 'accept: application/json'

{
  "Download": {
    "Cancelled": {
      "totalBytes": 204983483,
      "count": 1,
      "distinctUsers": 1,
      "averageSpeed": 0,
      "averageWait": 28,
      "averageDuration": 0
    },
    "Errored": {
      "totalBytes": 6089012397,
      "count": 288,
      "distinctUsers": 1,
      "averageSpeed": 4595.404860195817,
      "averageWait": 66.5,
      "averageDuration": 49
    },
    "Succeeded": {
      "totalBytes": 1472356278,
      "count": 74,
      "distinctUsers": 1,
      "averageSpeed": 1355700.1324455894,
      "averageWait": 832.6621621621622,
      "averageDuration": 17.41891891891892
    }
  },
  "Upload": {
    "Cancelled": {
      "totalBytes": 276089863,
      "count": 1,
      "distinctUsers": 1,
      "averageSpeed": 6672082.271922457,
      "averageWait": 156,
      "averageDuration": 2
    },
    "Errored": {
      "totalBytes": 8103332694,
      "count": 138,
      "distinctUsers": 25,
      "averageSpeed": 377768.4447608767,
      "averageWait": 297.8702290076336,
      "averageDuration": 89.67175572519083
    },
    "Rejected": {
      "totalBytes": 5934460958,
      "count": 83,
      "distinctUsers": 5,
      "averageSpeed": 0,
      "averageWait": 231.96385542168676,
      "averageDuration": 0
    },
    "Succeeded": {
      "totalBytes": 181896119751,
      "count": 3441,
      "distinctUsers": 159,
      "averageSpeed": 6465114.999138142,
      "averageWait": 138.46004068584713,
      "averageDuration": 19.60767218831735
    },
    "TimedOut": {
      "totalBytes": 9001184001,
      "count": 101,
      "distinctUsers": 13,
      "averageSpeed": 14248.739732752763,
      "averageWait": 176.7029702970297,
      "averageDuration": 20.722772277227723
    }
  }
}
```

get all the metrics returned
