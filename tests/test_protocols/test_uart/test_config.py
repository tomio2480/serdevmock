"""UART設定ファイル読み込み機能のテスト"""

import json
import tempfile
from pathlib import Path

from serdevmock.protocols.uart.config import UARTConfig, UARTConfigLoader


class TestUARTConfigLoader:
    """UARTConfigLoaderのテストクラス"""

    def test_load_valid_config(self) -> None:
        """有効な設定ファイルを読み込めること"""
        config_data = {
            "port": "COM3",
            "baudrate": 9600,
            "data_bits": 8,
            "parity": "N",
            "stop_bits": 1,
            "echo_mode": False,
            "response_rules": [
                {
                    "request_pattern": "AT",
                    "response_data": "OK",
                    "delay_ms": 100,
                }
            ],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = Path(f.name)

        try:
            loader = UARTConfigLoader()
            config = loader.load(config_path)

            assert config.port == "COM3"
            assert config.baudrate == 9600
            assert config.data_bits == 8
            assert config.parity == "N"
            assert config.stop_bits == 1
            assert config.echo_mode is False
            assert len(config.response_rules) == 1
            assert config.response_rules[0].request_pattern == "AT"
            assert config.response_rules[0].response_data == "OK"
            assert config.response_rules[0].delay_ms == 100
        finally:
            config_path.unlink()

    def test_load_config_with_echo_mode(self) -> None:
        """エコーモード有効の設定ファイルを読み込めること"""
        config_data = {
            "port": "COM3",
            "baudrate": 9600,
            "data_bits": 8,
            "parity": "N",
            "stop_bits": 1,
            "echo_mode": True,
            "response_rules": [],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = Path(f.name)

        try:
            loader = UARTConfigLoader()
            config = loader.load(config_path)

            assert config.echo_mode is True
        finally:
            config_path.unlink()

    def test_load_config_without_echo_mode(self) -> None:
        """echo_modeが省略された場合はFalseになること"""
        config_data = {
            "port": "COM3",
            "baudrate": 9600,
            "data_bits": 8,
            "parity": "N",
            "stop_bits": 1,
            "response_rules": [],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = Path(f.name)

        try:
            loader = UARTConfigLoader()
            config = loader.load(config_path)

            assert config.echo_mode is False
        finally:
            config_path.unlink()


class TestUARTConfig:
    """UARTConfigのテストクラス"""

    def test_create_config(self) -> None:
        """UART設定を作成できること"""
        config = UARTConfig(
            port="COM3",
            baudrate=9600,
            data_bits=8,
            parity="N",
            stop_bits=1,
            echo_mode=False,
            response_rules=[],
        )

        assert config.port == "COM3"
        assert config.echo_mode is False
        assert config.validate() is True
