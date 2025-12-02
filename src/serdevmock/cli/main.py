"""CLIメインモジュール"""

import argparse
import signal
import sys
from pathlib import Path
from typing import NoReturn

from serdevmock.protocols.uart.config import UARTConfigLoader
from serdevmock.protocols.uart.emulator import UARTEmulator
from serdevmock.utils.vport_checker import VPortToolChecker


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """コマンドライン引数を解析する

    Args:
        args: コマンドライン引数のリスト

    Returns:
        解析された引数
    """
    parser = argparse.ArgumentParser(description="シリアル通信デバイスモックツール")
    parser.add_argument(
        "--protocol",
        choices=["uart"],
        default="uart",
        help="プロトコル種別 (現在はuartのみ対応)",
    )
    parser.add_argument(
        "--port", required=True, help="シリアルポート名 (例: COM3, /dev/ttyS0)"
    )
    parser.add_argument("--config", required=True, type=Path, help="設定ファイルのパス")
    parser.add_argument(
        "--log-file", type=Path, help="ログファイルのパス（省略時は標準出力）"
    )
    return parser.parse_args(args)


def main() -> None:
    """メイン関数"""
    args = parse_args()

    if args.protocol == "uart":
        loader = UARTConfigLoader()
        config = loader.load(args.config)
        config.port = args.port
        emulator = UARTEmulator(config)
        protocol_name = "UART"
    else:
        print(f"未対応のプロトコル: {args.protocol}")
        sys.exit(1)

    def signal_handler(signum: int, frame: object) -> NoReturn:
        """シグナルハンドラ"""
        print("\nエミュレータを停止しています...")
        emulator.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print(f"{protocol_name}エミュレータを起動しています: {config.port}")
    print(f"設定ファイル: {args.config}")
    if hasattr(config, "echo_mode") and config.echo_mode:
        print("エコーモード: 有効")

    # 仮想ポートを使用する場合のみツールチェックを実行
    if not config.port.startswith("socket://"):
        checker = VPortToolChecker()
        status = checker.check()

        if status.is_installed:
            print(
                f"仮想ポートツール: {status.tool_name} "
                f"(バージョン: {status.version or '不明'})"
            )
        else:
            print("\n" + "=" * 60)
            print("警告: 仮想ポートツールが検出されませんでした")
            print("=" * 60)
            print(f"\n{status.get_install_instruction()}\n")
            print("=" * 60 + "\n")

    print("停止するにはCtrl+Cを押してください")

    emulator.start()
    emulator.run()


if __name__ == "__main__":
    main()
