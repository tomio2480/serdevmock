"""TCPソケットモードのテストクライアント

使用方法:
1. ターミナル1でserdevmockを起動:
   serdevmock --protocol uart --port socket://0.0.0.0:5000 --config examples/at_command_socket.json

2. ターミナル2でこのスクリプトを実行:
   python examples/test_socket_client.py
"""

import serial
import time


def test_with_pyserial():
    """pyserialのsocket://プロトコルを使用したテスト"""
    print("=== pyserial socket://プロトコルでテスト ===")

    # socket://プロトコルで接続
    ser = serial.serial_for_url('socket://localhost:5000', timeout=1)
    time.sleep(0.5)

    # ATコマンドテスト
    commands = [
        b'AT\r\n',
        b'ATI\r\n',
        b'AT+CGMI\r\n',
        b'AT+CGMM\r\n',
    ]

    for cmd in commands:
        print(f"\n送信: {cmd.decode('utf-8').strip()}")
        ser.write(cmd)
        time.sleep(0.2)

        response = ser.read(100)
        print(f"受信: {response.decode('utf-8', errors='ignore').strip()}")

    ser.close()
    print("\n接続を閉じました")


def test_with_socket():
    """生のソケット通信を使用したテスト"""
    print("\n\n=== 生のソケット通信でテスト ===")

    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 5000))
    sock.settimeout(1.0)

    # ATコマンドテスト
    commands = [
        b'AT\r\n',
        b'ATI\r\n',
    ]

    for cmd in commands:
        print(f"\n送信: {cmd.decode('utf-8').strip()}")
        sock.send(cmd)
        time.sleep(0.2)

        try:
            response = sock.recv(1024)
            print(f"受信: {response.decode('utf-8', errors='ignore').strip()}")
        except socket.timeout:
            print("タイムアウト")

    sock.close()
    print("\n接続を閉じました")


if __name__ == "__main__":
    try:
        test_with_pyserial()
        test_with_socket()
    except ConnectionRefusedError:
        print("\nエラー: serdevmockに接続できません")
        print("serdevmockが起動しているか確認してください:")
        print("  serdevmock --protocol uart --port socket://0.0.0.0:5000 --config examples/at_command_socket.json")
    except Exception as e:
        print(f"\nエラー: {e}")
