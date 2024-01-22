from queue import Empty, Queue
import socket
from threading import Thread
import time
from typing import Callable

from loguru import logger

from n9010a_controller.utils import Signal

class SocketClient:
    received = Signal(bytes)
    transmited = Signal(bytes)
    disconnected = Signal()
    connected = Signal()
    def __init__(self, host: str = '', port: int = -1) -> None:
        self._host: str = host
        self._port: int = port
        self._socket: socket.socket
        self._running_flag = False
        self._thread: Thread
        self._connection_status: bool = False
        self._tx_queue = Queue()

    def _routine(self) -> None:
        try:
            while self._running_flag:
                handler = None
                try:
                    tx_data, handler = self._tx_queue.get_nowait()
                    logger.debug(f'sending: {tx_data}')
                    self._socket.send(tx_data)
                except Empty:
                    pass
                try:
                    msg: bytes = self._socket.recv(1024)
                    if not msg:
                        break
                    logger.debug(f"answer: < {msg}")
                    self.received.emit(msg)
                    if handler:
                        handler(msg)
                except TimeoutError:
                    pass
                time.sleep(0.1)
        except ConnectionResetError as err:
            logger.error(f'Lost connection with server: {err}')
        except ConnectionAbortedError:
            logger.info('Disconnected from server')
            return None
        logger.info('Lost connection with server. Trying to reconnect.')
        self.disconnect()
        self.connect()

    def _connect_routine(self) -> bool:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(0.2)
        try:
            self._socket.connect((self._host, self._port))
            self._connection_status = True
            logger.success(f'Connected to server {self._host}:{self._port}')
            self.connected.emit()
        except ConnectionRefusedError:
            logger.error(f'Can not connect to {self._host}:{self._port}. Trying to reconect')
            return False
        except ConnectionResetError as err:
            logger.error(f'\nLost connection with server: {err}')
            self.disconnect()
            return False
        except TimeoutError:
            logger.error('Timeout error! Probably incorrect ip/port or '\
                         'device is not powered on')
            return False

        self._running_flag = True
        self._thread = Thread(name='N9010A_routine', target=self._routine,
                              daemon=True)
        self._thread.start()
        return True

    def connect(self, host: str | None = None, port: int | None = None) -> bool:
        self._host = host if host else self._host
        self._port = port if port else self._port
        return self._connect_routine()
        # while not self._connect_routine():
        #     time.sleep(1)
        # return True

    def disconnect(self) -> None:
        if self._running_flag:
            self._connection_status = False
            self._running_flag = False
            time.sleep(0.2)
            self._socket.close()
            self.disconnected.emit()

    def send(self, data: tuple[bytes, Callable | None]) -> None:
        if self._connection_status:
            self._tx_queue.put_nowait(data)


if __name__ == "__main__":
    # server = SocketServer('localhost', 8083)
    # server.start_server()
    client = SocketClient("localhost", 4000)
    try:
        client.connect()
        while True:
            in_data = input('>')
            client.send((in_data.encode('utf-8'), None))
    except KeyboardInterrupt:
        client.disconnect()
        # server.stop()
        print('shutdown')
