import threading
import socket
import select
import sys
if not '/opt/mdmi/modules' in sys.path:
    sys.path.append('/opt/mdmi/modules')
from utils import logger

class BaseServiceServer(threading.Thread):
    '''Server Service class
    Attributes:
        name: Service name.
        m_host: Host name of the server.
        m_port: Host port of the server.
        recv_max: Max bytes in recevicing.
    '''
    def __init__(self, name=None, host=None, port=None, conn_limit=1024, recv_max=1024):
        assert ((host != None) and (port != None))
        self.m_host = host
        self.m_port = port
        self.m_service_name = name
        self.m_max_conn = conn_limit
        self.m_max_recv = recv_max
        threading.Thread.__init__(self) #to be a thread
        pass

    def run(self):
        '''Main steps in the service.
        please rewrite it in the subclass.
        '''
        pass

    def stop(self):
        '''Clean up steps in the service.
        please rewrite it in the subclass.
        '''
        pass

    def do_setup(self):
        '''Setup socket server service.

        Params:
            self : The object pointer.
            limit : Accpect max connections.

        Return:
            socket object.
        '''
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #set the port to be reused
            sock.bind((self.m_host, self.m_port))
            logger.debug('%s service set up socket! Address:%s, Port:%d' % (self.m_service_name, self.m_host, self.m_port))
            sock.listen(self.m_max_conn)
            return sock
        except Exception, e:
            logger.error('%s service Set up socket error! %s' % (self.m_service_name, repr(e)))
        return None
        pass

    def do_listen(self, sock, recv_handle, timeout):
        '''Linsten the port, and create one thread to handle the connection.
        
        Params:
            sock : socket fd.
            recv_handle : Function pointer.
            timeout : listen timeout.
        '''
        assert(sock != None)
        try:
            infds, outfds, errfds = select.select([sock, ], [], [], timeout)
        except Exception, e:
            logger.error('%s select error! %s' % (self.m_service_name, repr(e)))
            return -1
        if infds:
            for infd in infds:
                try:
                    conn, addr = infd.accept()
                except Exception, e:
                    logger.error('%s accept connection error! %s' % (self.m_service_name, repr(e)))
                    return -1
                handle_thread = threading.Thread(target=self._do_recv, args=(conn, addr, recv_handle, ))
                handle_thread.start()
        #Note: Close socket in the subclass.
        return 0
        pass

    def _do_recv(self, conn, addr, recv_handle):
        logger.info('%s service accept client from %s' % (self.m_service_name, repr(addr)))
        try:
            recv_data = conn.recv(self.m_max_recv)
            recv_handle(conn, recv_data)
        except Exception, e:
            logger.error('%s service recv error:%s' % (self.m_service_name, repr(e)))
        pass


class BaseServiceClient(object):
    '''Service client class.
    Attributes:
        m_client_name : Name of the client service
        m_addr : host name and port tuple.
    '''
    def __init__(self, name=None, host=None, port=None):
        assert(name and host and port)
        self.m_client_name = name
        self.m_addr = (host, port)
        pass

    def do_connect(self, timeout=None):
        '''Connect to the server
        '''
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if timeout and timeout > 0:
                sock.settimeout(timeout)
            else:
                sock.setblocking(True)
            sock.connect(self.m_addr)
        except Exception, e:
            logger.error('%s client connect failed! %s' % (self.m_client_name, repr(e)))
        return sock
        pass

