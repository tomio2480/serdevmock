# Windows クイックスタートガイド

serdevmockをWindowsで使用するためのセットアップガイドです。

## 前提条件

- Python 3.11以上がインストール済み
- pipが使用可能

## 1. serdevmockのインストール

```bash
cd c:\Users\owner\OneDrive\ドキュメント\Works\serial-device-emulator
pip install -e .
```

## 2. com0comのインストール

### ダウンロード

[com0com公式サイト](https://sourceforge.net/projects/com0com/)から最新版をダウンロードします。

### インストール手順

1. ダウンロードしたインストーラを実行
2. インストールウィザードに従ってインストール
3. インストール完了後、「Setup Command Prompt」を起動

### 仮想ポートペアの作成

Setup Command Promptで以下のコマンドを実行:

```cmd
install PortName=COM10 PortName=COM11
```

これでCOM10とCOM11の仮想ポートペアが作成されます。

### 作成されたポートの確認

```bash
python -c "import serial.tools.list_ports; [print(f'{p.device}: {p.description}') for p in serial.tools.list_ports.comports()]"
```

出力例:
```
COM10: com0com - serial port emulator (COM10)
COM11: com0com - serial port emulator (COM11)
```

## 3. 設定ファイルの準備

### エコーモード用設定

`examples/echo_mode_win.json`:

```json
{
  "port": "COM10",
  "baudrate": 9600,
  "data_bits": 8,
  "parity": "N",
  "stop_bits": 1,
  "echo_mode": true,
  "response_rules": []
}
```

### ATコマンドエミュレータ用設定

`examples/at_command_win.json`:

```json
{
  "port": "COM10",
  "baudrate": 9600,
  "data_bits": 8,
  "parity": "N",
  "stop_bits": 1,
  "echo_mode": false,
  "response_rules": [
    {
      "request_pattern": "AT",
      "response_data": "OK\r\n",
      "delay_ms": 100
    },
    {
      "request_pattern": "ATI",
      "response_data": "serdevmock v1.0\r\n",
      "delay_ms": 50
    }
  ]
}
```

## 4. serdevmockの起動

```bash
serdevmock --protocol uart --port COM10 --config examples/echo_mode_win.json
```

出力:
```
UARTエミュレータを起動しています: COM10
設定ファイル: examples\echo_mode_win.json
エコーモード: 有効
停止するにはCtrl+Cを押してください
```

## 5. テスト

### TeraTerm等のターミナルソフトでテスト

1. TeraTerm（またはPuTTY）を起動
2. シリアル接続でCOM11を選択
3. ボーレート9600、データビット8、パリティなし、ストップビット1に設定
4. 文字を入力すると、エコーバックされることを確認

### Pythonスクリプトでテスト

```python
import serial
import time

# COM11に接続（serdevmockはCOM10で待機）
ser = serial.Serial('COM11', 9600, timeout=1)
time.sleep(1)

# データ送信
ser.write(b'Hello\n')

# 応答受信
response = ser.read(100)
print(f'受信: {response}')

ser.close()
```

## トラブルシューティング

### ポートが開けない

- com0comが正しくインストールされているか確認
- 他のアプリケーションがポートを使用していないか確認
- デバイスマネージャーでポートが認識されているか確認

### 文字化けする

- ボーレート、データビット、パリティ、ストップビットの設定を確認
- エンコーディングを確認（通常はASCII）

### 応答がない

- serdevmockが起動しているか確認
- 正しいポート番号（COM11）に接続しているか確認
- 設定ファイルの応答ルールが正しいか確認
