"""仮想ポートツール検知機能のテスト"""

import platform
from unittest.mock import MagicMock, patch

from serdevmock.utils.vport_checker import VPortToolChecker, VPortToolStatus


class TestVPortToolChecker:
    """VPortToolCheckerのテストクラス"""

    @patch("platform.system")
    @patch("subprocess.run")
    def test_check_windows_com0com_installed(
        self, mock_run: MagicMock, mock_system: MagicMock
    ) -> None:
        """Windowsでcom0comがインストールされている場合"""
        mock_system.return_value = "Windows"
        mock_run.return_value = MagicMock(
            returncode=0, stdout="com0com version 3.0.0.0"
        )

        checker = VPortToolChecker()
        status = checker.check()

        assert status.tool_name == "com0com"
        assert status.is_installed is True
        assert status.version == "3.0.0.0"

    @patch("platform.system")
    @patch("subprocess.run")
    def test_check_windows_com0com_not_installed(
        self, mock_run: MagicMock, mock_system: MagicMock
    ) -> None:
        """Windowsでcom0comがインストールされていない場合"""
        mock_system.return_value = "Windows"
        mock_run.side_effect = FileNotFoundError()

        checker = VPortToolChecker()
        status = checker.check()

        assert status.tool_name == "com0com"
        assert status.is_installed is False
        assert status.version is None

    @patch("platform.system")
    @patch("subprocess.run")
    def test_check_linux_socat_installed(
        self, mock_run: MagicMock, mock_system: MagicMock
    ) -> None:
        """Linuxでsocatがインストールされている場合"""
        mock_system.return_value = "Linux"
        mock_run.return_value = MagicMock(
            returncode=0, stdout="socat version 1.7.4.1"
        )

        checker = VPortToolChecker()
        status = checker.check()

        assert status.tool_name == "socat"
        assert status.is_installed is True
        assert status.version == "1.7.4.1"

    @patch("platform.system")
    @patch("subprocess.run")
    def test_check_linux_socat_not_installed(
        self, mock_run: MagicMock, mock_system: MagicMock
    ) -> None:
        """Linuxでsocatがインストールされていない場合"""
        mock_system.return_value = "Linux"
        mock_run.side_effect = FileNotFoundError()

        checker = VPortToolChecker()
        status = checker.check()

        assert status.tool_name == "socat"
        assert status.is_installed is False
        assert status.version is None

    @patch("platform.system")
    @patch("subprocess.run")
    def test_check_macos_socat_installed(
        self, mock_run: MagicMock, mock_system: MagicMock
    ) -> None:
        """macOSでsocatがインストールされている場合"""
        mock_system.return_value = "Darwin"
        mock_run.return_value = MagicMock(
            returncode=0, stdout="socat version 1.8.0.0"
        )

        checker = VPortToolChecker()
        status = checker.check()

        assert status.tool_name == "socat"
        assert status.is_installed is True
        assert status.version == "1.8.0.0"

    @patch("platform.system")
    @patch("subprocess.run")
    def test_get_install_instruction_windows(
        self, mock_run: MagicMock, mock_system: MagicMock
    ) -> None:
        """Windowsでインストール手順を取得できること"""
        mock_system.return_value = "Windows"
        mock_run.side_effect = FileNotFoundError()

        checker = VPortToolChecker()
        status = checker.check()

        instruction = status.get_install_instruction()
        assert "com0com" in instruction
        assert "sourceforge.net" in instruction

    @patch("platform.system")
    @patch("subprocess.run")
    def test_get_install_instruction_linux(
        self, mock_run: MagicMock, mock_system: MagicMock
    ) -> None:
        """Linuxでインストール手順を取得できること"""
        mock_system.return_value = "Linux"
        mock_run.side_effect = FileNotFoundError()

        checker = VPortToolChecker()
        status = checker.check()

        instruction = status.get_install_instruction()
        assert "socat" in instruction
        assert "apt-get" in instruction or "yum" in instruction
