"""CLIインターフェースのテスト"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

from serdevmock.cli.main import main, parse_args
from serdevmock.utils.vport_checker import VPortToolStatus


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

    @patch("serdevmock.cli.main.VPortToolChecker")
    @patch("serdevmock.cli.main.UARTConfigLoader")
    @patch("serdevmock.cli.main.UARTEmulator")
    def test_main_starts_uart_emulator(
        self,
        mock_emulator_class: MagicMock,
        mock_loader_class: MagicMock,
        mock_checker_class: MagicMock,
    ) -> None:
        """main()がUARTエミュレータを起動すること"""
        mock_loader = MagicMock()
        mock_config = MagicMock()
        mock_config.echo_mode = False
        mock_config.port = "COM3"
        mock_loader.load.return_value = mock_config
        mock_loader_class.return_value = mock_loader

        mock_emulator = MagicMock()
        mock_emulator_class.return_value = mock_emulator

        # 仮想ポートツールチェッカーをモック
        mock_checker = MagicMock()
        mock_status = VPortToolStatus(
            tool_name="com0com", is_installed=True, version=None
        )
        mock_checker.check.return_value = mock_status
        mock_checker_class.return_value = mock_checker

        test_args = ["--port", "COM3", "--config", "config.json"]
        with patch.object(sys, "argv", ["serdevmock"] + test_args):
            with patch("serdevmock.cli.main.signal.signal"):
                main()

        mock_loader.load.assert_called_once()
        mock_emulator.start.assert_called_once()
        mock_emulator.run.assert_called_once()

    @patch("serdevmock.cli.main.VPortToolChecker")
    @patch("serdevmock.cli.main.UARTConfigLoader")
    @patch("serdevmock.cli.main.UARTEmulator")
    @patch("builtins.print")
    def test_main_warns_when_vport_tool_not_installed(
        self,
        mock_print: MagicMock,
        mock_emulator_class: MagicMock,
        mock_loader_class: MagicMock,
        mock_checker_class: MagicMock,
    ) -> None:
        """仮想ポートツールが未インストールの場合に警告を表示すること"""
        mock_loader = MagicMock()
        mock_config = MagicMock()
        mock_config.echo_mode = False
        mock_config.port = "COM3"
        mock_loader.load.return_value = mock_config
        mock_loader_class.return_value = mock_loader

        mock_emulator = MagicMock()
        mock_emulator_class.return_value = mock_emulator

        # 仮想ポートツールが未インストール
        mock_checker = MagicMock()
        mock_status = VPortToolStatus(
            tool_name="com0com",
            is_installed=False,
            platform_name="Windows",
        )
        mock_checker.check.return_value = mock_status
        mock_checker_class.return_value = mock_checker

        test_args = ["--port", "COM3", "--config", "config.json"]
        with patch.object(sys, "argv", ["serdevmock"] + test_args):
            with patch("serdevmock.cli.main.signal.signal"):
                main()

        # 警告メッセージが表示されること
        warning_printed = any(
            "警告" in str(call) or "インストール" in str(call)
            for call in mock_print.call_args_list
        )
        assert warning_printed

    @patch("serdevmock.cli.main.VPortToolChecker")
    @patch("serdevmock.cli.main.UARTConfigLoader")
    @patch("serdevmock.cli.main.UARTEmulator")
    def test_main_skips_check_for_socket_mode(
        self,
        mock_emulator_class: MagicMock,
        mock_loader_class: MagicMock,
        mock_checker_class: MagicMock,
    ) -> None:
        """socket://モードの場合は仮想ポートチェックをスキップすること"""
        mock_loader = MagicMock()
        mock_config = MagicMock()
        mock_config.echo_mode = False
        mock_config.port = "socket://0.0.0.0:5000"
        mock_loader.load.return_value = mock_config
        mock_loader_class.return_value = mock_loader

        mock_emulator = MagicMock()
        mock_emulator_class.return_value = mock_emulator

        mock_checker = MagicMock()
        mock_checker_class.return_value = mock_checker

        test_args = ["--port", "socket://0.0.0.0:5000", "--config", "config.json"]
        with patch.object(sys, "argv", ["serdevmock"] + test_args):
            with patch("serdevmock.cli.main.signal.signal"):
                main()

        # socket://モードの場合はチェックを呼ばない
        mock_checker.check.assert_not_called()
