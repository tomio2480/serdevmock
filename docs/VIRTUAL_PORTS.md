# 仮想シリアルポートの作成方法

このドキュメントでは、各OS環境で仮想シリアルポートペアを作成する方法を説明します。

## 概要

仮想シリアルポートペアを使用することで、実際のハードウェアデバイスなしでシリアル通信のテストができます。

**構成:**
```
アプリケーション → ポートA ← [仮想ペア] → ポートB ← serdevmock
```

- アプリケーションは`ポートA`に接続
- serdevmockは`ポートB`に接続
- 両者は仮想的にペアリングされており、データが相互に転送される

## Windows環境

### com0comの使用

#### インストール

1. [com0com公式サイト](https://sourceforge.net/projects/com0com/)から最新版をダウンロード
2. インストーラを実行
3. インストールウィザードに従ってインストール

#### 仮想ポートペアの作成

1. 「Setup Command Prompt」を管理者として起動
2. 以下のコマンドを実行:

```cmd
install PortName=COM10 PortName=COM11
```

これで`COM10`と`COM11`がペアとして作成されます。

#### 確認

```bash
python -c "import serial.tools.list_ports; [print(f'{p.device}: {p.description}') for p in serial.tools.list_ports.comports()]"
```

出力例:
```
COM10: com0com - serial port emulator (COM10)
COM11: com0com - serial port emulator (COM11)
```

#### 使用方法

```bash
# serdevmockを起動
serdevmock --protocol uart --port COM11 --config examples/echo_mode_win.json

# アプリケーションはCOM10に接続
```

#### ポートペアの削除

```cmd
remove 0
```

詳細は[QUICKSTART_WINDOWS.md](QUICKSTART_WINDOWS.md)を参照してください。

## Linux環境

### socatの使用

#### インストール

```bash
# Debian/Ubuntu
sudo apt-get install socat

# RHEL/CentOS/Fedora
sudo yum install socat

# Arch Linux
sudo pacman -S socat
```

#### 仮想ポートペアの作成

```bash
socat -d -d pty,raw,echo=0 pty,raw,echo=0
```

出力例:
```
2024/12/02 10:00:00 socat[12345] N PTY is /dev/pts/2
2024/12/02 10:00:00 socat[12345] N PTY is /dev/pts/3
```

この例では、`/dev/pts/2`と`/dev/pts/3`がペアとして作成されます。

**注意:** socatを終了すると仮想ポートも削除されます。

#### バックグラウンド実行

```bash
# バックグラウンドで実行
socat -d -d pty,raw,echo=0,link=/tmp/vport1 pty,raw,echo=0,link=/tmp/vport2 &

# プロセスID確認
echo $!
```

これで`/tmp/vport1`と`/tmp/vport2`という名前でアクセスできます。

#### 使用方法

**ターミナル1: socatを起動**
```bash
socat -d -d pty,raw,echo=0 pty,raw,echo=0
# 出力されたポート名をメモ（例: /dev/pts/2 と /dev/pts/3）
```

**ターミナル2: serdevmockを起動**
```bash
serdevmock --protocol uart --port /dev/pts/3 --config examples/echo_mode.json
```

**ターミナル3: アプリケーションを実行**
```bash
# アプリケーションは /dev/pts/2 に接続
```

#### 停止

```bash
# バックグラウンドプロセスを停止
kill <プロセスID>

# または、フォアグラウンドの場合
Ctrl+C
```

## macOS環境

### socatの使用

#### インストール

Homebrewを使用してインストール:

```bash
brew install socat
```

#### 仮想ポートペアの作成

Linuxと同じ方法で作成できます:

```bash
socat -d -d pty,raw,echo=0 pty,raw,echo=0
```

出力例:
```
2024/12/02 10:00:00 socat[12345] N PTY is /dev/ttys002
2024/12/02 10:00:00 socat[12345] N PTY is /dev/ttys003
```

#### シンボリックリンクの作成

より使いやすい名前を付けることもできます:

```bash
socat -d -d pty,raw,echo=0,link=/tmp/vport1 pty,raw,echo=0,link=/tmp/vport2
```

#### 使用方法

**ターミナル1: socatを起動**
```bash
socat -d -d pty,raw,echo=0 pty,raw,echo=0
# 出力されたポート名をメモ（例: /dev/ttys002 と /dev/ttys003）
```

**ターミナル2: serdevmockを起動**
```bash
serdevmock --protocol uart --port /dev/ttys003 --config examples/echo_mode.json
```

**ターミナル3: アプリケーションを実行**
```bash
# アプリケーションは /dev/ttys002 に接続
```

## 比較表

| 項目 | Windows (com0com) | Linux/macOS (socat) |
|------|-------------------|---------------------|
| インストール | 1回のみ | 1回のみ |
| ポート作成 | 永続的 | socatプロセス実行中のみ |
| ポート名 | COM10, COM11など | /dev/pts/N, /dev/ttysNなど |
| 管理者権限 | インストール時のみ | 不要 |
| 自動起動 | 可能 | systemd/launchd設定が必要 |

## トラブルシューティング

### Windows

#### ポートが開けない
- デバイスマネージャーでポートが認識されているか確認
- 他のアプリケーションがポートを使用していないか確認
- com0comを再インストール

### Linux/macOS

#### Permission denied
```bash
# ユーザーをdialoutグループに追加（Linux）
sudo usermod -a -G dialout $USER

# 再ログインが必要
```

#### ポートが見つからない
- socatが実行中か確認
- 正しいポート名を使用しているか確認

#### socatが終了してしまう
- `-d -d`オプションでデバッグ出力を確認
- `pty,raw,echo=0`の設定を確認

## 自動起動の設定

### Linux (systemd)

`/etc/systemd/system/socat-vport.service`:
```ini
[Unit]
Description=Virtual Serial Port Pair
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/socat -d -d pty,raw,echo=0,link=/tmp/vport1 pty,raw,echo=0,link=/tmp/vport2
Restart=always

[Install]
WantedBy=multi-user.target
```

有効化:
```bash
sudo systemctl enable socat-vport
sudo systemctl start socat-vport
```

### macOS (launchd)

`~/Library/LaunchAgents/com.user.socat.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.socat</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/socat</string>
        <string>-d</string>
        <string>-d</string>
        <string>pty,raw,echo=0,link=/tmp/vport1</string>
        <string>pty,raw,echo=0,link=/tmp/vport2</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

有効化:
```bash
launchctl load ~/Library/LaunchAgents/com.user.socat.plist
```

## まとめ

各OSで仮想シリアルポートペアを作成することで、実際のハードウェアなしでシリアル通信のテストが可能になります。

- **Windows**: com0comで永続的なポートペアを作成
- **Linux/macOS**: socatで一時的または永続的なポートペアを作成

これらのツールとserdevmockを組み合わせることで、クロスプラットフォームなシリアルデバイスエミュレーション環境が構築できます。
