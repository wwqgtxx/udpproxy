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

    address_cache_by_uuid = LRUCache(LRU_SIZE, delete_handle=delete_handle, use_lock=False)
    uuid_cache_by_address = LRUCache(LRU_SIZE, delete_handle=delete_handle, use_lock=False)

    self_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self_socket.bind(ip_to_tuple(src))

    server_address = ip_to_tuple(dst)

    while True:
        try:
            data, address = self_socket.recvfrom(BUFFER_SIZE)
            # LOGGER.info((len(data),address))

            if address == server_address:
                client_uuid = data[:16]
                data = data[16:]
                client_address = address_cache_by_uuid.get(client_uuid, None)
                if client_address is not None:
                    uuid_cache_by_address.flush(client_address)
                    self_socket.sendto(data, client_address)
            else:
                client_uuid = uuid_cache_by_address.get(address, None)
                if client_uuid is None:
                    client_uuid = uuid.uuid4()
                    LOGGER.info("new uuid for incoming:%s", client_uuid)
                    client_uuid = client_uuid.bytes
                    address_cache_by_uuid[client_uuid] = address
                    uuid_cache_by_address[address] = client_uuid
                else:
                    address_cache_by_uuid.flush(client_uuid)

                data = client_uuid + data
                self_socket.sendto(data, server_address)

        except:
            LOGGER.exception("error")
