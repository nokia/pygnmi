# pygnmi
Python tools for gNMI

## Installation
Python tools for gNMI can be used with Python 2.7 and Python3.
Please follow gRPC Installation Guide from:
https://github.com/grpc/grpc/blob/master/INSTALL.md

```
$ pip install --upgrade pip
$ pip install grpcio
$ wget https://raw.githubusercontent.com/openconfig/gnmi/master/proto/gnmi/gnmi_pb2.py
$ python gNMI_Subscribe.py --help
```

## Usage Example:

```
$ python gNMI_Subscribe.py  --server 172.20.148.52:57400 --username grpc --password NokiaGRPC --cert CAcert.pem --ciphers AES128 /state/port[port-id=1/1/1]/ethernet/statistics/out-utilization

17/04/19 23:19:09,547 Sending SubscribeRequest
subscribe {
  subscription {
    path {
      element: "state"
      element: "port[port-id=1/1/1]"
      element: "ethernet"
      element: "statistics"
      element: "out-utilization"
    }
    mode: SAMPLE
    sample_interval: 10000000000
  }
}

17/04/19 23:19:19,970 Update received
update {
  timestamp: 1492640359967583702
  prefix {
    element: "state"
    element: "port[port-id=1/1/1]"
    element: "ethernet"
    element: "statistics"
  }
  update {
    path {
      element: "out-utilization"
    }
    value {
      value: "0"
    }
  }
}

17/04/19 23:19:29,970 gNMI_Subscribe stopped by user
```
