"""UARTエミュレーションロジックのテスト"""

from unittest.mock import MagicMock, patch

from serdevmock.protocols.uart.config import ResponseRule, UARTConfig
from serdevmock.protocols.uart.emulator import UARTEmulator


class TestUARTEmulator:
    """UARTEmulatorのテストクラス"""

    def test_init_with_config(self) -> None:
        """設定でエミュレータを初期化できること"""
        config = UARTConfig(
            port="COM3",
            baudrate=9600,
            data_bits=8,
            parity="N",
            stop_bits=1,
            echo_mode=False,
            response_rules=[],
        )
        emulator = UARTEmulator(config)
        assert emulator.config == config
        assert emulator.is_running() is False

    @patch("serial.serial_for_url")
    def test_start_opens_serial_port(self, mock_serial_for_url: MagicMock) -> None:
        """start()でシリアルポートが開かれること"""
        config = UARTConfig(
            port="COM3",
            baudrate=9600,
            data_bits=8,
            parity="N",
            stop_bits=1,
            echo_mode=False,
            response_rules=[],
        )
        emulator = UARTEmulator(config)
        emulator.start()

        mock_serial_for_url.assert_called_once_with(
            "COM3",
            baudrate=9600,
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=1,
        )
        assert emulator.is_running() is True

    @patch("serial.serial_for_url")
    def test_stop_closes_serial_port(self, mock_serial_for_url: MagicMock) -> None:
        """stop()でシリアルポートが閉じられること"""
        config = UARTConfig(
            port="COM3",
            baudrate=9600,
            data_bits=8,
            parity="N",
            stop_bits=1,
            echo_mode=False,
            response_rules=[],
        )
        mock_instance = MagicMock()
        mock_serial_for_url.return_value = mock_instance

        emulator = UARTEmulator(config)
        emulator.start()
        emulator.stop()

        mock_instance.close.assert_called_once()
        assert emulator.is_running() is False

    @patch("serial.serial_for_url")
    def test_process_request_with_echo_mode(
        self, mock_serial_for_url: MagicMock
    ) -> None:
        """エコーモードで受信データをそのまま返すこと"""
        config = UARTConfig(
            port="COM3",
            baudrate=9600,
            data_bits=8,
            parity="N",
            stop_bits=1,
            echo_mode=True,
            response_rules=[],
        )

        mock_instance = MagicMock()
        mock_serial_for_url.return_value = mock_instance

        emulator = UARTEmulator(config)
        emulator.start()

        response = emulator._process_request(b"Hello")
        assert response == b"Hello"

    @patch("serial.serial_for_url")
    def test_process_request_with_matching_pattern(
        self, mock_serial_for_url: MagicMock
    ) -> None:
        """リクエストパターンが一致した場合に応答を返すこと"""
        rule = ResponseRule(request_pattern="AT", response_data="OK", delay_ms=0)
        config = UARTConfig(
            port="COM3",
            baudrate=9600,
            data_bits=8,
            parity="N",
            stop_bits=1,
            echo_mode=False,
            response_rules=[rule],
        )

        mock_instance = MagicMock()
        mock_serial_for_url.return_value = mock_instance

        emulator = UARTEmulator(config)
        emulator.start()

        response = emulator._process_request(b"AT")
        assert response == b"OK"

    @patch("serial.serial_for_url")
    def test_process_request_with_no_match(
        self, mock_serial_for_url: MagicMock
    ) -> None:
        """リクエストパターンが一致しない場合にNoneを返すこと"""
        rule = ResponseRule(request_pattern="AT", response_data="OK", delay_ms=0)
        config = UARTConfig(
            port="COM3",
            baudrate=9600,
            data_bits=8,
            parity="N",
            stop_bits=1,
            echo_mode=False,
            response_rules=[rule],
        )

        mock_instance = MagicMock()
        mock_serial_for_url.return_value = mock_instance

        emulator = UARTEmulator(config)
        emulator.start()

        response = emulator._process_request(b"UNKNOWN")
        assert response is None
