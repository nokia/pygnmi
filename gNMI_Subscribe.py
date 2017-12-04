#!/usr/bin/python

##############################################################################
#                                                                            #
#  gNMI_Subscribe.py                                                         #
#                                                                            #
#  History Change Log:                                                       #
#                                                                            #
#    1.0  [SW]  2017/06/02    first version                                  #
#    1.1  [SW]  2017/07/06    timeout behavior improved                      #
#    1.2  [SW]  2017/08/08    logging improved, options added                #
#    1.3  [SW]  2017/12/04    support for gNMI v0.4                          #
#                                                                            #
#  Objective:                                                                #
#                                                                            #
#    Testing tool for the gNMI (GRPC Network Management Interface) in Python #
#                                                                            #
#  Features supported:                                                       #
#                                                                            #
#    - gNMI Subscribe (based on Nokia SROS 15.0 TLM feature-set)             #
#    - secure and insecure mode                                              #
#    - multiple subscriptions paths                                          #
#                                                                            #
#  Not yet supported:                                                        #
#                                                                            #
#    - Disable server name verification against TLS cert (opt: noHostCheck)  #
#    - Disable cert validation against root certificate (InsecureSkipVerify) #
#                                                                            #
#  License:                                                                  #
#                                                                            #
#    Licensed under the MIT license                                          #
#    See LICENSE.md delivered with this project for more information.        #
#                                                                            #
#  Author:                                                                   #
#                                                                            #
#    Sven Wisotzky                                                           #
#    mail:  sven.wisotzky(at)nokia.com                                       #
##############################################################################

"""
gNMI Subscribe Client in Python Version 1.2
Copyright (C) 2017 Nokia. All Rights Reserved.
"""

__title__   = "gNMI_Subscribe"
__version__ = "1.2"
__status__  = "released"
__author__  = "Sven Wisotzky"
__date__    = "2017 August 8th"

##############################################################################

import argparse
import re
import sys
import os
import logging
import time

##############################################################################

def list_from_path(path='/'):
    if path:
        if path[0]=='/':
            if path[-1]=='/':
                return re.split('''/(?=(?:[^\[\]]|\[[^\[\]]+\])*$)''', path)[1:-1]
            else:
                return re.split('''/(?=(?:[^\[\]]|\[[^\[\]]+\])*$)''', path)[1:]
        else:
            if path[-1]=='/':
                return re.split('''/(?=(?:[^\[\]]|\[[^\[\]]+\])*$)''', path)[:-1]
            else:
                return re.split('''/(?=(?:[^\[\]]|\[[^\[\]]+\])*$)''', path)
    return []


def path_from_string(path='/'):
    mypath = []

    for e in list_from_path(path):
        eName = e.split("[", 1)[0]
        eKeys = re.findall('\[(.*?)\]', e)
        dKeys = dict(x.split('=', 1) for x in eKeys)
        mypath.append(gnmi_pb2.PathElem(name=eName, key=dKeys))

    return gnmi_pb2.Path(elem=mypath)


def gen_request( opt ):
    mysubs = []
    for path in opt.xpaths:
        mypath = path_from_string(path)
        mysub = gnmi_pb2.Subscription(path=mypath, mode=opt.submode, suppress_redundant=opt.suppress, sample_interval=opt.interval*1000000000, heartbeat_interval=opt.heartbeat)
        mysubs.append(mysub)

    if opt.prefix:
        myprefix = path_from_string(opt.prefix)
    else:
        myprefix = None

    if opt.qos:
        myqos = gnmi_pb2.QOSMarking(marking=opt.qos)
    else:
        myqos = None

    mysblist = gnmi_pb2.SubscriptionList(prefix=myprefix, mode=opt.mode, allow_aggregation=opt.aggregate, encoding=opt.encoding, subscription=mysubs, use_aliases=opt.use_alias, qos=myqos)
    mysubreq = gnmi_pb2.SubscribeRequest( subscribe=mysblist )

    log.info('Sending SubscribeRequest\n'+str(mysubreq))
    yield mysubreq

##############################################################################

if __name__ == '__main__':
    prog = os.path.splitext(os.path.basename(sys.argv[0]))[0]

    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version=prog+' '+__version__)

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-q', '--quiet',   action='store_true', help='disable logging')
    group.add_argument('-v', '--verbose', action='count', help='enhanced logging')
    group = parser.add_argument_group()
    group.add_argument('--server', default='localhost:57400', help='server/port (default: localhost:57400)')
    group.add_argument('--username', default='admin', help='username (default: admin)')
    group.add_argument('--password', default='admin', help='password (default: admin)')
    group.add_argument('--cert', metavar='<filename>',  help='CA root certificate')
    group.add_argument('--tls', action='store_true', help='enable TLS security')
    group.add_argument('--ciphers', help='override environment "GRPC_SSL_CIPHER_SUITES"')
    group.add_argument('--altName', help='subjectAltName/CN override for server host validation')
    group.add_argument('--noHostCheck',  action='store_true', help='disable server host validation')

    group = parser.add_argument_group()
    group.add_argument('--logfile', metavar='<filename>', type=argparse.FileType('wb', 0), default='-', help='Specify the logfile (default: <stdout>)')
    group.add_argument('--stats', action='store_true', help='collect stats')

    group = parser.add_argument_group()
    group.add_argument('--interval', default=10, type=int, help='sample interval (default: 10s)')
    group.add_argument('--timeout', type=int, help='subscription duration in seconds (default: none)')
    group.add_argument('--heartbeat', type=int, help='heartbeat interval (default: none)')
    group.add_argument('--aggregate', action='store_true', help='allow aggregation')
    group.add_argument('--suppress', action='store_true', help='suppress redundant')
    group.add_argument('--submode', default=2, type=int, help='subscription mode [TARGET_DEFINED, ON_CHANGE, SAMPLE]')
    group.add_argument('--mode', default=0, type=int, help='[STREAM, ONCE, POLL]')
    group.add_argument('--encoding', default=0, type=int, help='[JSON, BYTES, PROTO, ASCII, JSON_IETF]')
    group.add_argument('--qos', default=0, type=int, help='[JSON, BYTES, PROTO, ASCII, JSON_IETF]')
    group.add_argument('--use_alias',  action='store_true', help='use alias') 
    group.add_argument('--prefix', default='', help='gRPC path prefix (default: none)')
    group.add_argument('xpaths', nargs=argparse.REMAINDER, help='path(s) to subscriber (default: /)')
    options = parser.parse_args()

    if len(options.xpaths)==0:
        options.xpaths=['/']

    if options.ciphers:
        os.environ["GRPC_SSL_CIPHER_SUITES"] = options.ciphers

    #  setup logging

    if options.quiet:
        loghandler = logging.NullHandler()
        loglevel = logging.NOTSET
    else:
        if options.verbose==None:
            logformat = '%(asctime)s,%(msecs)-3d %(message)s'
        else:
            logformat = '%(asctime)s,%(msecs)-3d %(levelname)-8s %(threadName)s %(message)s'

        if options.verbose==None or options.verbose==1:
            loglevel = logging.INFO
        else:
            loglevel = logging.DEBUG

        # For supported GRPC trace options check:
        #   https://github.com/grpc/grpc/blob/master/doc/environment_variables.md

        if options.verbose==3:
          os.environ["GRPC_TRACE"] = "all"
          os.environ["GRPC_VERBOSITY"] = "ERROR"

        if options.verbose==4:
          os.environ["GRPC_TRACE"] = "api,call_error,channel,connectivity_state,op_failure"
          os.environ["GRPC_VERBOSITY"] = "INFO"

        if options.verbose==5:
          os.environ["GRPC_TRACE"] = "all"
          os.environ["GRPC_VERBOSITY"] = "INFO"

        if options.verbose==6:
          os.environ["GRPC_TRACE"] = "all"
          os.environ["GRPC_VERBOSITY"] = "DEBUG"

        timeformat = '%y/%m/%d %H:%M:%S'
        loghandler = logging.StreamHandler(options.logfile)
        loghandler.setFormatter(logging.Formatter(logformat, timeformat))

    log = logging.getLogger(prog)
    log.setLevel(loglevel)
    log.addHandler(loghandler)

    try:
        import grpc
        import gnmi_pb2
    except ImportError as err:
        log.error(str(err))
        quit()

    if options.tls or options.cert:
        log.debug("Create SSL Channel")
        if options.cert:
            cred = grpc.ssl_channel_credentials(root_certificates=open(options.cert).read())
            opts = []
            if options.altName:
                opts.append(('grpc.ssl_target_name_override', options.altName,))
            if options.noHostCheck:
                log.error('Disable server name verification against TLS cert is not yet supported!')
                # TODO: Clarify how to setup gRPC with SSLContext using check_hostname:=False

            channel = grpc.secure_channel(options.server, cred, opts)
        else:
            log.error('Disable cert validation against root certificate (InsecureSkipVerify) is not yet supported!')
            # TODO: Clarify how to setup gRPC with SSLContext using verify_mode:=CERT_NONE

            cred = grpc.ssl_channel_credentials(root_certificates=None, private_key=None, certificate_chain=None)
            channel = grpc.secure_channel(options.server, cred)

    else:
        log.info("Create insecure Channel")
        channel = grpc.insecure_channel(options.server)

    log.debug("Create gNMI stub")
    stub = gnmi_pb2.gNMIStub(channel)

    req_iterator = gen_request( options )
    metadata = [('username',options.username), ('password', options.password)]

    msgs = 0
    upds = 0
    secs = 0
    start = 0

    try:
        responses = stub.Subscribe(req_iterator, options.timeout, metadata=metadata)
        for response in responses:
            if response.HasField('sync_response'):
                log.debug('Sync Response received\n'+str(response))
                secs += time.time() - start
                start = 0
                if options.stats:
                    log.info("%d updates and %d messages within %1.2f seconds", upds, msgs, secs)
                    log.info("Statistics: %5.0f upd/sec, %5.0f msg/sec", upds/secs, msgs/secs)
            elif response.HasField('error'):
                log.error('gNMI Error '+str(response.error.code)+' received\n'+str(response.error.message))
            elif response.HasField('update'):
                if start==0:
                    start=time.time()
                msgs += 1
                upds += len(response.update.update)
                if not options.stats:
                    log.info('Update received\n'+str(response))
            else:
                log.error('Unknown response received:\n'+str(response))

    except KeyboardInterrupt:
        log.info("%s stopped by user", prog)

    except grpc.RpcError as x:
        log.error("grpc.RpcError received:\n%s", x.details)

    except Exception as err:
        log.error(err)

    if (msgs>1):
        log.info("%d update messages received", msgs)

# EOF

