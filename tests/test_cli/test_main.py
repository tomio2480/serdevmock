"""CLIインターフェースのテスト"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

from serdevmock.cli.main import main, parse_args


class TestParseArgs:
    """parse_argsのテストクラス"""

    def test_parse_args_with_required_arguments(self) -> None:
        """必須引数でコマンドライン引数を解析できること"""
        args = parse_args(["--port", "COM3", "--config", "config.json"])
        assert args.port == "COM3"
        assert args.config == Path("config.json")
        assert args.protocol == "uart"

    def test_parse_args_with_protocol(self) -> None:
        """プロトコル指定で解析できること"""
        args = parse_args(
            ["--protocol", "uart", "--port", "COM3", "--config", "config.json"]
        )
        assert args.protocol == "uart"


class TestMain:
    """mainのテストクラス"""

    @patch("serdevmock.cli.main.UARTConfigLoader")
    @patch("serdevmock.cli.main.UARTEmulator")
    def test_main_starts_uart_emulator(
        self, mock_emulator_class: MagicMock, mock_loader_class: MagicMock
    ) -> None:
        """main()がUARTエミュレータを起動すること"""
        mock_loader = MagicMock()
        mock_config = MagicMock()
        mock_config.echo_mode = False
        mock_loader.load.return_value = mock_config
        mock_loader_class.return_value = mock_loader

        mock_emulator = MagicMock()
        mock_emulator_class.return_value = mock_emulator

        test_args = ["--port", "COM3", "--config", "config.json"]
        with patch.object(sys, "argv", ["serdevmock"] + test_args):
            with patch("serdevmock.cli.main.signal.signal"):
                main()

        mock_loader.load.assert_called_once()
        mock_emulator.start.assert_called_once()
        mock_emulator.run.assert_called_once()
