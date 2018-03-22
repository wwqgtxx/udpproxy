#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
# author wwqgtxx <wwqgtxx@gmail.com>

from udpproxy.common import *


def main():
    parser = argparse.ArgumentParser(description='UPD proxy.')

    proto_group = parser.add_mutually_exclusive_group(required=True)
    proto_group.add_argument('--server', action='store_true', help='UDP server')
    proto_group.add_argument('--client', action='store_true', help='UDP client')
    proto_group.add_argument('--proxy', action='store_true', help='UDP proxy')

    parser.add_argument('-s', '--src', required=True, help='Source IP and port, i.e.: 0.0.0.0:8000')
    parser.add_argument('-d', '--dst', required=True, help='Destination IP and port, i.e.: 127.0.0.1:8888')

    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument('-q', '--quiet', action='store_true', help='Be quiet')
    output_group.add_argument('-v', '--verbose', action='store_true', help='Be loud')

    args = parser.parse_args()

    LOGGER.setLevel(logging.INFO)

    if args.quiet:
        LOGGER.setLevel(logging.CRITICAL)
    if args.verbose:
        LOGGER.setLevel(logging.NOTSET)

    if args.server:
        from udpproxy.server import udp_proxy
        udp_proxy(args.src, args.dst)
    elif args.client:
        from udpproxy.client import udp_proxy
        udp_proxy(args.src, args.dst)
    elif args.proxy:
        from udpproxy.proxy import udp_proxy
        udp_proxy(args.src, args.dst)


if __name__ == '__main__':
    main()
