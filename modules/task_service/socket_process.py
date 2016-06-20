#!/usr/bin/python
#-*- coding: utf-8 -*-

#---------------------------------------------------
# File Name: socket_thread.py
# Purpose:
# Creation Date: 06-01-2014
# Last Modified: Fri Feb 28 18:32:06 2014
# Created by:
#---------------------------------------------------

import os
import socket
import select, errno
import signal
from multiprocessing import Process

import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')

from utils import logger

from request_dispatcher import HttpRequestDispatcher
from request_dispatcher import HEADER_ERROR

class SocketProcess(Process):
    def __init__(self, listen_file, queue):
        super(self.__class__, self).__init__()
        self.queue = queue
        self.is_teminate = False
        self.listen_file = listen_file
        self.connections = {}
        self.addresses = {}
        self.__request_dispatcher = {}

    def _create_socket(self):
        listen_fd = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM, 0)
        # set SO_REUSEADDR option
        listen_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_fd.bind(self.listen_file)
        # TODO set the backlog of listen to 1024
        listen_fd.listen(1024)

        logger.info("plugin service's socket was built")

        return listen_fd

    def _close_socket(self):
        if os.access(self.listen_file, os.W_OK):
            os.remove(self.listen_file)

    def _signal_handler(self, signum, frame):
        logger.debug('Catched interrupt signal in socket process: %d', signum)
        self.is_teminate = True

    def run(self):
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGHUP, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        try:
            listen_fd = self._create_socket()

            # create epoll handler
            epoll_fd = select.epoll()
            # register the socket into epoll
            epoll_fd.register(listen_fd.fileno(), select.EPOLLIN)
            self.queue.put(0)

            self._epoll_event(listen_fd, epoll_fd)
        except socket.error as e:
            logger.error('Error occurred in prepare socket: %s', e)
            self.queue.put(1)
        except IOError as e:
            logger.debug('socket thread ended in case of: %s', e)
        finally:
            self._close_socket()

    def _epoll_event(self, listen_fd, epoll_fd):
        while not self.is_teminate:
            epoll_list = epoll_fd.poll() # do not specify time, which means wait with block
            for fd, events in epoll_list:
                if fd == listen_fd.fileno():
                    # when listen_fd was active
                    logger.info('connection comming')
                    conn, addr = listen_fd.accept()
                    #logger.info("accept connect from %s, %d, fd=%d", addr[0], addr[1], conn.fileno())
                    logger.info("accept connect from %s, fd=%d", addr, conn.fileno())
                    # set the connection to non-block
                    conn.setblocking(0)
                    # register socket read event to epoll on fd
                    epoll_fd.register(conn.fileno(), select.EPOLLIN | select.EPOLLET)
                    self._epoll_reset(conn.fileno(), conn, addr)

                    # set connection number from client
                    #self.__status.increase_connected_num()

                elif select.EPOLLIN & events:
                    # some read event is coming in
                    logger.info('data comming from fd: %d', fd)
                    self._receive_request_data(epoll_fd, fd)

                elif select.EPOLLOUT & events:
                    # any write event is coming
                    logger.info('data sending to fd: %d', fd)
                    r = self._send_response_data(epoll_fd, fd)
                    if r == -1:
                        self._epoll_unregister(epoll_fd, fd)
                    else:
                        # clear data epoll
                        self._epoll_clear_data(fd)
                        epoll_fd.modify(fd, select.EPOLLET | select.EPOLLIN)

                elif select.EPOLLRDHUP & events:
                    # any HUP event is coming
                    logger.info('signal EPOLLRDHUP coming')
                    self._epoll_unregister(epoll_fd, fd)
                    logger.info('in case of EPOLLRDHUP signal, close connection from: %s', self.addresses[fd])

                elif select.EPOLLHUP & events:
                    # any HUP event is coming
                    logger.info('signal EPOLLHUP coming')
                    self._epoll_unregister(epoll_fd, fd)
                    logger.info('in case of EPOLLHUP signal, close connection from: %s', self.addresses[fd])

    def _receive_request_data(self, epoll_fd, fd):
        try:
            # TODO receive 2048 data from active fd
            data = self.connections[fd].recv(2048)
            while data:
                self.__request_dispatcher[fd].append_data(data)
                if not self.__request_dispatcher[fd].is_already_parsed():
                    # parse data and get header options
                    r = self.__request_dispatcher[fd].do_parse()
                    if r == HEADER_ERROR :
                        # invalid header was received
                        logger.error('receive an invalid header from client: %s', self.addresses[fd])
                        epoll_fd.modify(fd, select.EPOLLET | select.EPOLLOUT)
                if self.__request_dispatcher[fd].is_body_complete():
                    # once complete received data from client, handle it
                    logger.debug('handle the request package, when complete receiving data from client')
                    self.__request_dispatcher[fd].do_handle()

                    epoll_fd.modify(fd, select.EPOLLET | select.EPOLLOUT)

                data = self.connections[fd].recv(2048)
            else:
                if self.__request_dispatcher[fd].is_nothing_received():
                    logger.info('received empty data, close connection from: %s', self.addresses[fd])
                    self._epoll_unregister(epoll_fd, fd)
                else:
                    logger.error('receive invalid data from client: %s', self.addresses[fd])
                    epoll_fd.modify(fd, select.EPOLLET | select.EPOLLOUT)
        except socket.error as e:
            # use non-block socket to receive data
            if not e.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                self._epoll_unregister(epoll_fd, fd)
                logger.info('socket exception in receiving data, close connection from: %s', self.addresses[fd])
        except Exception as e:
            if self.connections.has_key(fd):
                self._epoll_unregister(epoll_fd, fd)
            logger.error('exception in receiving data, close connection - %s', e)

    def _send_response_data(self, epoll_fd, fd):
        response = self.__request_dispatcher[fd].generate_response()
        response_length = len(response)
        try:
            length = self.connections[fd].send(response)
            while length < response_length:
                length += self.connections[fd].send(response[length:])
            return length
        except socket.error as e:
            logger.error('exception in sending data, close connection - %s', e)
            return -1

    def _epoll_unregister(self, epoll_fd, fd):
        epoll_fd.unregister(fd)
        if self.connections[fd]:
            self.connections[fd].close()
            del self.connections[fd]
        del self.addresses[fd]
        del self.__request_dispatcher[fd]
        self.__request_dispatcher[fd] = None

    def _epoll_reset(self, fd, conn=None, addr=None):
        self.connections[fd] = conn
        self.addresses[fd] = addr
        self._epoll_clear_data(fd)

    def _epoll_clear_data(self, fd):
        if self.__request_dispatcher.get(fd):
            del self.__request_dispatcher[fd]
        self.__request_dispatcher[fd] = HttpRequestDispatcher()
