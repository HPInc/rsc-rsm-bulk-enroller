# Copyright 2024 HP Development Company, L.P.
# SPDX-License-Identifier: MIT
'''Functions for discovering RSCs using zeroconf'''

import time
from typing import List, Union
import logging
from zeroconf import ServiceBrowser, ServiceListener, Zeroconf, ServiceInfo
from rscbulkenrollment.rsc import rsc as rscpkg

infos = []

class MyListener(ServiceListener):
    '''Listener for discovery'''

    def __init__(self, rsc: List[rscpkg.RSC]) -> None:
        self.rsc = rsc

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        '''Listens to add service events'''
        info: Union[ServiceInfo, None] = zc.get_service_info(type_, name)
        logging.debug("add_service: %s", info)
        if (info is not None and
            info.addresses is not None and
            len(info.addresses) > 0):
            self.rsc.append(rscpkg.RSC('.'.join([str(a) for a in info.addresses[0]]), "", ""))
            logging.info("RSC service at '%s' discovered. Address: %s",
                         info.server.rstrip('.') if info.server is not None else name,
                         self.rsc[-1].address)

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        '''Listens to remove service events'''

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        '''Listens to update service events'''

def discover_rscs() -> List[rscpkg.RSC]:
    '''Discovers RSCs using zeroconf'''
    rsc: List[rscpkg.RSC] = []
    zeroconf = Zeroconf()
    listener = MyListener(rsc)
    browser = ServiceBrowser(zeroconf, "_rsc._tcp.local.", listener)
    try:
        time.sleep(5)
        browser.cancel()
    finally:
        zeroconf.close()
    return rsc
