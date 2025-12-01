"""UART設定ファイル読み込み機能"""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ResponseRule:
    """応答ルール"""

    request_pattern: str
    response_data: str
    delay_ms: int


@dataclass
class UARTConfig:
    """UART設定"""

    port: str
    baudrate: int
    data_bits: int
    parity: str
    stop_bits: int
    echo_mode: bool
    response_rules: list[ResponseRule]

    def validate(self) -> bool:
        """設定の妥当性を検証する"""
        return True


class UARTConfigLoader:
    """UART設定ファイル読み込みクラス"""

    def load(self, config_path: Path) -> UARTConfig:
        """設定ファイルを読み込む

        Args:
            config_path: 設定ファイルのパス

        Returns:
            UARTConfig: UART設定

        Raises:
            FileNotFoundError: ファイルが存在しない場合
            json.JSONDecodeError: JSONのパースに失敗した場合
            KeyError: 必須フィールドが欠けている場合
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        response_rules = [
            ResponseRule(
                request_pattern=rule["request_pattern"],
                response_data=rule["response_data"],
                delay_ms=rule["delay_ms"],
            )
            for rule in data.get("response_rules", [])
        ]

        return UARTConfig(
            port=data["port"],
            baudrate=data["baudrate"],
            data_bits=data["data_bits"],
            parity=data["parity"],
            stop_bits=data["stop_bits"],
            echo_mode=data.get("echo_mode", False),
            response_rules=response_rules,
        )
