# pygnmi
Python tools for gNMI

## Installation
Python tools for gNMI can be used with Python 2.7 and Python3.
Please follow gRPC Installation Guide from:
https://github.com/grpc/grpc/blob/master/INSTALL.md

```
$ pip install --upgrade pip
$ pip install grpcio
$ curl -O https://raw.githubusercontent.com/openconfig/gnmi/c5b444cd3ab8af669d0b8934f47a41ed6a985cdc/proto/gnmi/gnmi_pb2.py
$ python gNMI_Subscribe.py --help
```

## Usage Example:

```
$ python gNMI_Subscribe.py  --server 192.168.33.2:57400 --username grpc --password Nokia4gnmi --cert CAcert.pem --ciphers AES128 /state/port[port-id=1/1/1]/ethernet/statistics/out-utilization
17/12/04 16:02:43,160 Sending SubscribeRequest
subscribe {
  subscription {
    path {
      elem {
        name: "state"
      }
      elem {
        name: "port"
        key {
          key: "port-id"
          value: "1/1/1"
        }
      }
      elem {
        name: "ethernet"
      }
      elem {
        name: "statistics"
      }
      elem {
        name: "out-utilization"
      }
    }
    mode: SAMPLE
    sample_interval: 10000000000
  }
}

17/12/04 16:02:54,532 Update received
update {
  timestamp: 1512399461394858020
  prefix {
    elem {
      name: "state"
    }
    elem {
      name: "port"
      key {
        key: "port-id"
        value: "1/1/1"
      }
    }
    elem {
      name: "ethernet"
    }
    elem {
      name: "statistics"
    }
  }
  update {
    path {
      elem {
        name: "out-utilization"
      }
    }
    val {
      json_val: "0"
    }
  }
}


^C
17/12/04 16:03:04,511 gNMI_Subscribe stopped by user
```
