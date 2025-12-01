# TCPソケットモード

com0comなどの外部ツールを使わずに、TCPソケット経由でserdevmockを使用する方法です。

## 概要

serdevmockをTCPサーバーとして起動し、テスト対象アプリケーションはTCPクライアントとして接続します。pyserialの`socket://`プロトコルを使えば、既存のシリアル通信コードをほぼ変更せずに使用できます。

## 使用方法

### 1. serdevmockをTCPモードで起動

```bash
serdevmock --protocol uart --port socket://localhost:5000 --config examples/at_command.json
```

### 2. テスト対象アプリケーションから接続

#### pyserialを使用している場合

```python
import serial

# socket://プロトコルを使用
ser = serial.serial_for_url('socket://localhost:5000', timeout=1)

# 通常のシリアル通信と同じように使用
ser.write(b'AT\r\n')
response = ser.read(100)
print(response)

ser.close()
```

#### 生のソケット通信

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 5000))

sock.send(b'AT\r\n')
response = sock.recv(1024)
print(response)

sock.close()
```

## メリット

- ✅ 外部ツール不要
- ✅ 完全なマルチプラットフォーム対応
- ✅ ネットワーク越しのテストも可能
- ✅ 複数クライアントの接続も可能（将来的に）

## デメリット

- ⚠️ 実際のシリアルポートではないため、一部のハードウェア依存機能は使えない
- ⚠️ テスト対象コードが`socket://`プロトコルに対応している必要がある

## 設定例

### エコーモード（TCPソケット）

```json
{
  "port": "socket://0.0.0.0:5000",
  "baudrate": 9600,
  "data_bits": 8,
  "parity": "N",
  "stop_bits": 1,
  "echo_mode": true,
  "response_rules": []
}
```

### ATコマンドエミュレータ（TCPソケット）

```json
{
  "port": "socket://0.0.0.0:5000",
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
    }
  ]
}
```

## トラブルシューティング

### ポートが既に使用されている

別のポート番号を使用してください（例: 5001, 5002など）

### ファイアウォールでブロックされる

Windowsの場合、Pythonへのアクセス許可を設定してください。
