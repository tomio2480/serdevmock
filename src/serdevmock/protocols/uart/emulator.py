"""UARTエミュレータのコアロジック"""

import time
from typing import Optional

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
        self._running = False

    def start(self) -> None:
        """エミュレータを開始する"""
        self._serial = serial.serial_for_url(
            self.config.port,
            baudrate=self.config.baudrate,
            bytesize=self.config.data_bits,
            parity=self.config.parity,
            stopbits=self.config.stop_bits,
            timeout=1,
        )
        self._running = True

    def stop(self) -> None:
        """エミュレータを停止する"""
        if self._serial and self._serial.is_open:
            self._serial.close()
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
