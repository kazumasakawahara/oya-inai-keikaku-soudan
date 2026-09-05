# log — 操作ログ（append-only）

> すべての ingest・振り分け・wiki 書き込みを AI が1エントリずつ追記します。raw/ は git 管理外のため、この log が振り分けの唯一の履歴です。

## （導入日を記入） | setup | Vault 導入
- oya-inai-keikaku-soudan テンプレート（β版・2026-09-05 更新版）から導入。
- 実施: lint 初回実行 / pre-commit 有効化 / AGENTS.md 環境調整 / 地域枠登録 / monitor 登録（→ docs/導入手順.md）
