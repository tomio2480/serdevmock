# PHP開発ガイドライン

PHP開発における標準的なツール構成、ルール、プロセスをまとめたドキュメント。
新規プロジェクト作成時やClaude Code起動時に参照することで、効率的な開発環境を構築できる。

## 目次

- [必須ツール](#必須ツール)
- [コーディング規約](#コーディング規約)
- [品質保証ツール](#品質保証ツール)
- [テスト環境](#テスト環境)
- [CI/CD](#cicd)
- [プロジェクト初期化手順](#プロジェクト初期化手順)
- [開発ワークフロー](#開発ワークフロー)
- [Packagist公開手順](#packagist公開手順)

## 必須ツール

### Composer

PHPの依存関係管理ツール。すべてのプロジェクトで使用する。

```bash
# インストール確認
composer --version

# 初期化
composer init
```

### PHP バージョン管理

**最低要件**: PHP 8.1以上
**推奨**: PHP 8.3以上（最新の安定版を使用）

`composer.json`で明確に指定:

```json
{
    "require": {
        "php": "^8.1"
    }
}
```

## コーディング規約

### PSR準拠

- **PSR-4**: オートローディング規約（必須）
- **PSR-12**: コーディングスタイル規約（必須）

### namespace構造

```
VendorName\PackageName\SubNamespace
```

例:
```php
namespace PhpSerial\Platform;
```

### composer.json autoload設定

```json
{
    "autoload": {
        "psr-4": {
            "VendorName\\PackageName\\": "src/"
        }
    },
    "autoload-dev": {
        "psr-4": {
            "VendorName\\PackageName\\Tests\\": "tests/"
        }
    }
}
```

## 品質保証ツール

### 必須ツールセット

#### 1. PHP-CS-Fixer

コードスタイルの自動修正ツール。

```bash
composer require --dev friendsofphp/php-cs-fixer
```

設定ファイル `.php-cs-fixer.php`:

```php
<?php

$finder = PhpCsFixer\Finder::create()
    ->in(__DIR__ . '/src')
    ->in(__DIR__ . '/tests')
    ->name('*.php')
    ->ignoreDotFiles(true)
    ->ignoreVCS(true);

return (new PhpCsFixer\Config())
    ->setRules([
        '@PSR12' => true,
        'array_syntax' => ['syntax' => 'short'],
        'single_quote' => true,
        'trailing_comma_in_multiline' => ['elements' => ['arrays']],
        'no_unused_imports' => true,
        'blank_line_after_namespace' => true,
        'blank_line_after_opening_tag' => true,
        'no_whitespace_in_blank_line' => true,
        'ordered_imports' => ['sort_algorithm' => 'alpha'],
        'return_type_declaration' => ['space_before' => 'none'],
        'declare_strict_types' => true,
    ])
    ->setFinder($finder)
    ->setRiskyAllowed(true);
```

#### 2. PHP_CodeSniffer

PSR準拠チェックツール。

```bash
composer require --dev squizlabs/php_codesniffer
```

#### 3. PHPStan

静的解析ツール。型安全性とバグ検出。

```bash
composer require --dev phpstan/phpstan
```

設定ファイル `phpstan.neon`:

```yaml
parameters:
    level: 8
    paths:
        - src
        - tests
    excludePaths:
        - tests/bootstrap.php
```

### Composerスクリプト設定

`composer.json`に以下を追加:

```json
{
    "scripts": {
        "test": "phpunit",
        "test:coverage": "phpunit --coverage-html coverage",
        "cs:check": "phpcs --standard=PSR12 src tests",
        "cs:fix": "phpcbf --standard=PSR12 src tests",
        "cs:fixer": "php-cs-fixer fix --dry-run --diff",
        "cs:fixer:fix": "php-cs-fixer fix",
        "stan": "phpstan analyse --memory-limit=256M",
        "qa": [
            "@cs:check",
            "@cs:fixer",
            "@stan",
            "@test"
        ]
    }
}
```

## テスト環境

### PHPUnit

標準的なテストフレームワーク。

```bash
composer require --dev phpunit/phpunit
```

設定ファイル `phpunit.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<phpunit xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:noNamespaceSchemaLocation="vendor/phpunit/phpunit/phpunit.xsd"
         bootstrap="tests/bootstrap.php"
         colors="true">
    <testsuites>
        <testsuite name="Test Suite">
            <directory>tests</directory>
        </testsuite>
    </testsuites>
    <source>
        <include>
            <directory>src</directory>
        </include>
    </source>
</phpunit>
```

### 環境変数管理

テスト用の環境変数は `.env` で管理。

```bash
composer require --dev vlucas/phpdotenv
```

`.env.example` を作成してリポジトリに含め、`.env` は `.gitignore` に追加。

## CI/CD

### GitHub Actions

`.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  tests:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        php: ['8.1', '8.2', '8.3', '8.4', '8.5']

    steps:
      - uses: actions/checkout@v4

      - name: Setup PHP
        uses: shivammathur/setup-php@v2
        with:
          php-version: ${{ matrix.php }}
          extensions: mbstring, xml, ctype, json
          coverage: none

      - name: Validate composer.json
        run: composer validate --strict

      - name: Install dependencies
        run: composer install --prefer-dist --no-progress

      - name: Run code style check
        run: composer cs:check

      - name: Run PHP-CS-Fixer check
        run: composer cs:fixer

      - name: Run PHPStan
        run: composer stan

      - name: Run tests
        run: composer test
```

### 必須チェック項目

1. コードスタイル（PSR-12）
2. 静的解析（PHPStan level 8）
3. ユニットテスト
4. 複数PHP版対応（8.1〜8.5）
5. クロスプラットフォーム（Ubuntu, Windows, macOS）

## プロジェクト初期化手順

### 1. Composerプロジェクト作成

```bash
composer init
```

対話形式で以下を設定:
- Package name: `vendor-name/package-name`
- Description: パッケージの説明
- Author: `Your Name <email@example.com>`
- Minimum Stability: `stable`
- License: `MIT`（または適切なライセンス）

### 2. ディレクトリ構造作成

```bash
mkdir -p src tests examples docs
```

### 3. 品質保証ツールインストール

```bash
composer require --dev phpunit/phpunit
composer require --dev friendsofphp/php-cs-fixer
composer require --dev squizlabs/php_codesniffer
composer require --dev phpstan/phpstan
```

### 4. 設定ファイル作成

- `.php-cs-fixer.php`
- `phpstan.neon`
- `phpunit.xml`
- `.gitignore`

### 5. .gitignore

```gitignore
/vendor/
/coverage/
/.phpunit.cache/
/.php-cs-fixer.cache
/var/cache/phpstan/
.env
composer.lock
```

### 6. README.md作成

必須セクション:
- 概要
- 動作環境
- インストール方法
- 基本的な使い方
- 開発方法
- ライセンス

### 7. CONTRIBUTING.md作成

開発者向けガイドライン:
- 環境構築手順
- 品質確認コマンド
- テスト実行方法
- コミット規約

## 開発ワークフロー

### 1. 機能開発前

```bash
# ブランチ作成
git checkout -b feature/new-feature

# 依存関係更新
composer install
```

### 2. 開発中

```bash
# コードスタイル自動修正
composer cs:fixer:fix

# 品質チェック
composer qa
```

### 3. コミット前

```bash
# 全品質チェック実行
composer qa

# すべて通過したらコミット
git add .
git commit -m "Add new feature"
```

### 4. プルリクエスト前

```bash
# 最新のmainブランチを取得
git fetch origin
git rebase origin/main

# 最終チェック
composer qa

# プッシュ
git push origin feature/new-feature
```

## Packagist公開手順

### 1. composer.json準備

必須メタデータを追加:

```json
{
    "name": "vendor/package",
    "description": "Package description",
    "type": "library",
    "license": "MIT",
    "homepage": "https://github.com/username/repo",
    "support": {
        "issues": "https://github.com/username/repo/issues",
        "source": "https://github.com/username/repo"
    },
    "authors": [
        {
            "name": "Your Name",
            "email": "email@example.com"
        }
    ],
    "require": {
        "php": "^8.1"
    }
}
```

### 2. バージョンタグ作成

```bash
# タグ作成
git tag -a v1.0.0 -m "Initial release v1.0.0"

# プッシュ
git push origin v1.0.0
```

### 3. Packagist登録

1. [https://packagist.org](https://packagist.org) にGitHubアカウントでサインイン
2. 「Submit」をクリック
3. リポジトリURL入力
4. 「Check」→「Submit」

### 4. 自動更新設定

GitHubのWebhook設定を確認。自動で設定されるため、通常は手動設定不要。

## PHP 8.x 新機能の活用

### Named Arguments

```php
$config = new Configuration(
    baudRate: 9600,
    dataBits: 8,
    parity: Configuration::PARITY_NONE
);
```

### Constructor Property Promotion

```php
class Configuration
{
    public function __construct(
        private int $baudRate = 9600,
        private int $dataBits = 8,
        private string $parity = self::PARITY_NONE
    ) {}
}
```

### Match式

```php
$platform = match (PHP_OS_FAMILY) {
    'Windows' => new WindowsPlatform(),
    'Linux', 'Darwin' => new UnixPlatform(),
    default => throw new RuntimeException('Unsupported OS'),
};
```

### Union Types

```php
public function read(mixed $handle, int $length): string|false
{
    return fread($handle, $length);
}
```

### Nullsafe演算子

```php
$result = $object?->method()?->property;
```

## 注意事項

### セキュリティ

- ユーザー入力は必ずバリデーション
- SQLインジェクション対策（プリペアドステートメント使用）
- XSS対策（出力時のエスケープ）
- CSRF対策（トークン検証）

### パフォーマンス

- 不要な処理の削除
- データベースクエリの最適化
- キャッシュの適切な使用
- メモリ使用量の監視

### エラーハンドリング

- 例外の適切な使用
- エラーメッセージの明確化
- ログ出力の統一

## チェックリスト

新規プロジェクト作成時:

- [ ] `composer init` 実行
- [ ] ディレクトリ構造作成（src, tests, examples, docs）
- [ ] 品質保証ツールインストール（PHP-CS-Fixer, PHPStan, PHPUnit）
- [ ] 設定ファイル作成（.php-cs-fixer.php, phpstan.neon, phpunit.xml）
- [ ] .gitignore作成
- [ ] README.md作成
- [ ] CONTRIBUTING.md作成
- [ ] GitHub Actions設定
- [ ] `composer qa` で全チェック通過
- [ ] 初回コミット

Packagist公開時:

- [ ] composer.jsonメタデータ完備
- [ ] README.md整備
- [ ] 全テスト通過
- [ ] バージョンタグ作成
- [ ] Packagist登録
- [ ] インストール確認

## 参考資料

- [PHP-FIG PSR Standards](https://www.php-fig.org/psr/)
- [PHP The Right Way](https://phptherightway.com/)
- [Composer Documentation](https://getcomposer.org/doc/)
- [PHPUnit Documentation](https://phpunit.de/documentation.html)
- [PHPStan Documentation](https://phpstan.org/user-guide/getting-started)
