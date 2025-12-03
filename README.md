# serdevmock

シリアル通信デバイスのモックツールです。
実際のハードウェアデバイスがなくても、UART/SPI/I2C等のシリアル通信を行うライブラリやアプリケーションの開発および自動テストを可能にします。

## 目次

- [特徴](#特徴)
- [動作環境](#動作環境)
- [インストール](#インストール)
- [使い方](#使い方)
- [設定ファイル](#設定ファイル)
- [開発](#開発)
- [アーキテクチャ](#アーキテクチャ)
- [ライセンス](#ライセンス)

## 特徴

- プロトコル別のモジュール設計（現在はUARTに対応、将来的にSPI/I2Cに対応予定）
- JSONベースの設定ファイルで柔軟な応答ルールを定義
- エコーモード（受信データをそのまま返送）
- リクエストパターンに応じた自動応答
- 応答遅延のシミュレーション
- クロスプラットフォーム対応（Windows, Linux, macOS）
- 軽量で高速な動作

## 動作環境

- Python 3.11以上
- pyserial 3.5以上

## インストール

### pipからインストール（推奨）

```bash
pip install serdevmock
```

### 開発版インストール

```bash
git clone https://github.com/tomio2480/serdevmock.git
cd serdevmock
pip install -e ".[dev]"
```

## 使い方

### 仮想COMポートの準備

serdevmockを使用するには、仮想COMポートペアを作成するか、TCPソケットモードを使用します。

**詳細は [docs/VIRTUAL_PORTS.md](docs/VIRTUAL_PORTS.md) を参照してください。**

#### 方法1: TCPソケットモード（pyserial対応アプリケーション向け）

外部ツール不要で、すべてのOSで動作します。

**注意:** 一部のシリアル通信ライブラリは`socket://`プロトコルに対応していません。その場合は方法2を使用してください。

```bash
# serdevmockをソケットモードで起動
serdevmock --protocol uart --port socket://0.0.0.0:5000 --config examples/echo_mode_socket.json

# 別のターミナルでテスト
python examples/test_socket_client.py
```

詳細は [docs/SOCKET_MODE.md](docs/SOCKET_MODE.md) を参照してください。

#### 方法2: 仮想COMポートペア（推奨・すべてのアプリケーション対応）

実際のCOMポート名を使用したい場合や、既存のシリアル通信ライブラリをそのまま使いたい場合はこの方法を推奨します。

**Windows: com0com**
```bash
# 仮想ポートペアを作成（初回のみ）
install PortName=COM10 PortName=COM11
```

**Linux/macOS: socat**
```bash
# 仮想シリアルポートペアを作成
socat -d -d pty,raw,echo=0 pty,raw,echo=0
# 出力例:
# 2024/12/02 10:00:00 socat[12345] N PTY is /dev/pts/2
# 2024/12/02 10:00:00 socat[12345] N PTY is /dev/pts/3
```

各OSでの詳細な手順、トラブルシューティング、自動起動設定は [docs/VIRTUAL_PORTS.md](docs/VIRTUAL_PORTS.md) を参照してください。

### 基本的な使用方法

```bash
# UARTエミュレータを起動
serdevmock --protocol uart --port COM10 --config examples/at_command.json
```

### オプション

- `--protocol`: プロトコル種別（現在は`uart`のみ対応、デフォルト: `uart`）
- `--port`: シリアルポート名（必須）
  - Windows: `COM3`, `COM4` など
  - Linux/macOS: `/dev/ttyS0`, `/dev/ttyUSB0`, `/dev/pts/N` など
  - TCPソケット: `socket://0.0.0.0:5000` など（マルチプラットフォーム対応）
- `--config`: 設定ファイルのパス（必須）
- `--log-file`: ログファイルのパス（省略時は標準出力）

### 停止方法

`Ctrl+C` を押してエミュレータを停止します。

## 設定ファイル

JSON形式で応答ルールを定義します。

### ATコマンドエミュレータの例

```json
{
  "port": "COM3",
  "baudrate": 9600,
  "data_bits": 8,
  "parity": "N",
  "stop_bits": 1,
  "echo_mode": false,
  "response_rules": [
    {
      "request_pattern": "AT",
      "response_data": "OK",
      "delay_ms": 100
    },
    {
      "request_pattern": "ATI",
      "response_data": "serdevmock v1.0",
      "delay_ms": 50
    }
  ]
}
```

### エコーモードの例

```json
{
  "port": "COM3",
  "baudrate": 9600,
  "data_bits": 8,
  "parity": "N",
  "stop_bits": 1,
  "echo_mode": true,
  "response_rules": []
}
```

### パラメータ説明

#### UART設定

- `port`: シリアルポート名
- `baudrate`: ボーレート（例: 9600, 115200）
- `data_bits`: データビット数（通常8）
- `parity`: パリティ（"N": なし, "E": 偶数, "O": 奇数）
- `stop_bits`: ストップビット数（通常1または2）
- `echo_mode`: エコーモード（`true`: 受信データをそのまま返送、`false`: 応答ルールを使用）

#### 応答ルール

- `request_pattern`: 受信待機するデータパターン（文字列）
- `response_data`: パターン一致時に送信する応答データ（文字列）
- `delay_ms`: リクエスト受信から応答送信までの遅延時間（ミリ秒）

## 開発

### 開発環境のセットアップ

```bash
# リポジトリのクローン
git clone <repository-url>
cd serdevmock

# 開発依存パッケージのインストール
pip install -e ".[dev]"
```

### テストの実行

```bash
# 全テスト実行
pytest

# カバレッジ付きテスト実行
pytest --cov=src/serdevmock --cov-report=html
```

### コード品質チェック

#### ローカルでの CI チェック（推奨）

GitHub Actions で実行される品質チェックをローカルで実行できます。

```powershell
# すべてのチェックを一括実行
.\check.ps1 all

# 個別のチェック実行
.\check.ps1 black   # コードフォーマットチェック
.\check.ps1 flake8  # コードスタイルチェック
.\check.ps1 mypy    # 型チェック
.\check.ps1 pytest  # テスト実行
```

#### 手動での品質チェック

```bash
# コードフォーマット
black src tests

# リンター
flake8 src tests

# 型チェック
mypy src

# 全品質チェック実行
black src tests && flake8 src tests && mypy src && pytest
```

### ディレクトリ構造

```
serdevmock/
├── src/
│   └── serdevmock/
│       ├── __init__.py
│       ├── cli/                # CLIインターフェース
│       └── protocols/          # プロトコル実装
│           ├── common/         # 共通インターフェース
│           ├── uart/           # UART実装
│           ├── spi/            # SPI実装（将来対応予定）
│           └── i2c/            # I2C実装（将来対応予定）
├── tests/                      # テストコード
├── examples/                   # サンプル設定ファイル
├── pyproject.toml              # プロジェクト設定
└── README.md
```

## アーキテクチャ

### プロトコル別モジュール設計

serdevmockは、異なる通信プロトコル（UART、SPI、I2C等）を独立したモジュールとして実装する設計になっています。

#### 共通インターフェース

すべてのプロトコルエミュレータは共通インターフェース（`ProtocolEmulator`）を実装します。

```python
from serdevmock.protocols.common.interface import ProtocolEmulator

class UARTEmulator(ProtocolEmulator):
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def is_running(self) -> bool: ...
```

#### 新しいプロトコルの追加方法

1. `src/serdevmock/protocols/<protocol_name>/` ディレクトリを作成
2. `config.py` で設定クラスを実装
3. `emulator.py` で `ProtocolEmulator` を継承したエミュレータクラスを実装
4. `src/serdevmock/cli/main.py` にプロトコル選択ロジックを追加

この設計により、各プロトコルの実装は互いに独立しており、メンテナンスコストを低く保つことができます。

## ライセンス

MIT License
