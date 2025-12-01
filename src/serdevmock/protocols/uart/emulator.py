"""UARTエミュレータのコアロジック"""

import socket
import time
from typing import Optional
from urllib.parse import urlparse

import serial

from serdevmock.protocols.common.interface import ProtocolEmulator
from serdevmock.protocols.uart.config import UARTConfig


class UARTEmulator(ProtocolEmulator):
    """UART通信デバイスエミュレータ"""

    def __init__(self, config: UARTConfig) -> None:
        """初期化

        Args:
            config: UART設定
        """
        self.config = config
        self._serial: Optional[serial.Serial] = None
        self._socket: Optional[socket.socket] = None
        self._running = False

    def start(self) -> None:
        """エミュレータを開始する"""
        # socket://で始まる場合はTCPサーバーとして起動
        if self.config.port.startswith("socket://"):
            self._start_tcp_server()
        else:
            self._serial = serial.serial_for_url(
                self.config.port,
                baudrate=self.config.baudrate,
                bytesize=self.config.data_bits,
                parity=self.config.parity,
                stopbits=self.config.stop_bits,
                timeout=1,
            )
        self._running = True

    def _start_tcp_server(self) -> None:
        """TCPサーバーとして起動する"""
        # URLをパース
        parsed = urlparse(self.config.port)
        host = parsed.hostname or "0.0.0.0"
        port = parsed.port or 5000

        # ソケットを作成
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((host, port))
        self._socket.listen(1)

    def stop(self) -> None:
        """エミュレータを停止する"""
        if self._serial and self._serial.is_open:
            self._serial.close()
        if self._socket:
            self._socket.close()
        self._running = False

    def is_running(self) -> bool:
        """エミュレータが実行中かどうかを返す"""
        return self._running

    def _process_request(self, request: bytes) -> Optional[bytes]:
        """リクエストを処理して応答を返す

        Args:
            request: 受信したリクエストデータ

        Returns:
            応答データ、一致するパターンがない場合はNone
        """
        # エコーモードの場合は受信データをそのまま返す
        if self.config.echo_mode:
            return request

        request_str = request.decode("utf-8", errors="ignore")

        for rule in self.config.response_rules:
            if rule.request_pattern in request_str:
                if rule.delay_ms > 0:
                    time.sleep(rule.delay_ms / 1000.0)
                return rule.response_data.encode("utf-8")

        return None
