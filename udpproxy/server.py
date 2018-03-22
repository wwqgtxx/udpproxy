#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
# author wwqgtxx <wwqgtxx@gmail.com>

from .common import *
from .lru_cache import *


def udp_proxy(src, dst):
    """Run UDP proxy.

    Arguments:
    src -- Source IP address and port string. I.e.: '0.0.0.0:8000'
    dst -- Destination IP address and port. I.e.: '127.0.0.1:8888'
    """

    socket_cache_by_uuid = LRUCache(LRU_SIZE, delete_handle=delete_handle, use_lock=False)
    info_cache_by_socket = LRUCache(LRU_SIZE, delete_handle=delete_handle, use_lock=False)

    self_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self_socket.bind(ip_to_tuple(src))

    server_address = ip_to_tuple(dst)

    while True:
        sockets = [self_socket]
        sockets.extend(socket_cache_by_uuid.values())
        s_read, _, _ = select.select(sockets, [], [])
        for s in s_read:
            try:
                data, address = s.recvfrom(BUFFER_SIZE)

                if address != server_address:
                    client_uuid = data[:16]
                    data = data[16:]
                    client_socket = socket_cache_by_uuid.get(client_uuid, None)
                    if client_socket is None:
                        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        LOGGER.info("get new uuid incoming:%s", uuid.UUID(bytes=client_uuid))
                        LOGGER.info("new socket to remote:%s", client_socket)

                        socket_cache_by_uuid[client_uuid] = client_socket
                        info_cache_by_socket[client_socket] = {"uuid": client_uuid, "address": address}
                    else:
                        info_cache_by_socket.flush(client_socket)
                    client_socket.sendto(data, server_address)
                else:
                    sc = info_cache_by_socket.get(s,None)
                    if sc is not None:
                        client_uuid = sc["uuid"]
                        client_address = sc["address"]
                        socket_cache_by_uuid.flush(client_uuid)
                        data = client_uuid + data
                        self_socket.sendto(data, client_address)

            except:
                LOGGER.exception("error")
