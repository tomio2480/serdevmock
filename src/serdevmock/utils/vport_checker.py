"""仮想ポートツール検知モジュール"""

import platform
import re
import subprocess
from dataclasses import dataclass
from typing import Any, Optional

serial: Any
try:
    import serial.tools.list_ports
except ImportError:
    serial = None


@dataclass
class VPortToolStatus:
    """仮想ポートツールのステータス"""

    tool_name: str
    is_installed: bool
    version: Optional[str] = None
    platform_name: str = ""

    def get_install_instruction(self) -> str:
        """インストール手順を取得する

        Returns:
            インストール手順の文字列
        """
        if self.platform_name == "Windows":
            return (
                "com0comをインストールしてください。\n"
                "ダウンロード: https://sourceforge.net/projects/com0com/\n"
                "詳細: docs/VIRTUAL_PORTS.md を参照"
            )
        elif self.platform_name in ["Linux", "Darwin"]:
            if self.platform_name == "Linux":
                pkg_manager = "apt-get install socat または yum install socat"
            else:
                pkg_manager = "brew install socat"
            return (
                f"socatをインストールしてください。\n"
                f"コマンド: {pkg_manager}\n"
                f"詳細: docs/VIRTUAL_PORTS.md を参照"
            )
        return "未対応のプラットフォームです"


class VPortToolChecker:
    """仮想ポートツール検知クラス"""

    def check(self) -> VPortToolStatus:
        """仮想ポートツールのインストール状況を確認する

        Returns:
            VPortToolStatus: ツールのステータス
        """
        system = platform.system()

        if system == "Windows":
            return self._check_com0com()
        elif system in ["Linux", "Darwin"]:
            return self._check_socat(system)
        else:
            return VPortToolStatus(
                tool_name="unknown",
                is_installed=False,
                platform_name=system,
            )

    def _check_com0com(self) -> VPortToolStatus:
        """com0comのインストール状況を確認する

        Returns:
            VPortToolStatus: com0comのステータス
        """
        # pyserialを使ってシリアルポート一覧から検出
        try:
            if serial is None:
                return VPortToolStatus(
                    tool_name="com0com",
                    is_installed=False,
                    platform_name="Windows",
                )

            ports = list(serial.tools.list_ports.comports())
            com0com_ports = [p for p in ports if "com0com" in p.description.lower()]

            if com0com_ports:
                # バージョン情報は取得できないが、インストールされていることは確認できる
                return VPortToolStatus(
                    tool_name="com0com",
                    is_installed=True,
                    version=None,
                    platform_name="Windows",
                )
            else:
                return VPortToolStatus(
                    tool_name="com0com",
                    is_installed=False,
                    platform_name="Windows",
                )
        except Exception:
            return VPortToolStatus(
                tool_name="com0com",
                is_installed=False,
                platform_name="Windows",
            )

    def _check_socat(self, system: str) -> VPortToolStatus:
        """socatのインストール状況を確認する

        Args:
            system: プラットフォーム名

        Returns:
            VPortToolStatus: socatのステータス
        """
        try:
            result = subprocess.run(
                ["socat", "-V"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            # バージョン情報を抽出
            version = None
            if result.returncode == 0:
                match = re.search(r"version\s+(\S+)", result.stdout, re.IGNORECASE)
                if match:
                    version = match.group(1)

            return VPortToolStatus(
                tool_name="socat",
                is_installed=True,
                version=version,
                platform_name=system,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return VPortToolStatus(
                tool_name="socat",
                is_installed=False,
                platform_name=system,
            )
