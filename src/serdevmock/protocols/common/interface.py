"""プロトコル共通インターフェース"""

from abc import ABC, abstractmethod


class ProtocolEmulator(ABC):
    """プロトコルエミュレータの基底クラス"""

    @abstractmethod
    def start(self) -> None:
        """エミュレータを開始する"""
        pass

    @abstractmethod
    def stop(self) -> None:
        """エミュレータを停止する"""
        pass

    @abstractmethod
    def is_running(self) -> bool:
        """エミュレータが実行中かどうかを返す"""
        pass


class ProtocolConfig(ABC):
    """プロトコル設定の基底クラス"""

    @abstractmethod
    def validate(self) -> bool:
        """設定の妥当性を検証する"""
        pass
