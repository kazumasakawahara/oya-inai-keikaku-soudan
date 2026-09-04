#!/usr/bin/env python3
"""
okf_lint.py — schema.md の構造ルールを機械的に検証する（oya-inai-keikaku-soudan 版）

依存ゼロ（Python3 標準ライブラリのみ）。PyYAML も不要。
共通検査は同じフォルダの okf_core.py（姉妹 Vault と同一内容。正本は本リポ）。
このファイルには**本 Vault 固有の型・語彙・検査だけ**を書く。

使い方:
    python3 scripts/okf_lint.py                 # 全チェック
    python3 scripts/okf_lint.py --gate          # 配布ゲートのみ（終了コードで判定）
    python3 scripts/okf_lint.py --allowlist     # 外部配布可能ファイル一覧を出力

終了コード:
    0 = 違反なし
    1 = WARN のみ（鮮度切れ・推奨事項。作業は止めないが確認を促す）
    2 = ERROR あり（機微情報の漏出リスク。CI や pre-commit で止める想定）
    ※ --gate は ERROR の有無だけを返す（WARN では 0）。鮮度で commit は止めない

本 Vault 固有:
    - plan / monitoring / meeting の3型（相談支援の中核文書。schema.md §2-1b〜2-1d）
      sensitive 以上を強制・person_id(s) 必須・日付必須・monitoring の plan_ref 推奨
    - provided_by に「後見人」「会議」「相談支援」、confirmed_by に「家族に確認」

作成: 2026-07-26 / 改訂: 2026-08-09 鮮度検査 / 2026-09-04 共通部分を okf_core.py へ分離
"""

import sys

import okf_core as core

VAULT = core.vault_root(__file__)

# 後方互換の再公開（release.sh の公開前点検などが okf_lint.PII_PATTERNS を参照する）
PII_PATTERNS = core.PII_PATTERNS
parse_frontmatter = core.parse_frontmatter

# --- 本 Vault 固有の型（schema.md §2-1b〜2-1d）--------------------------

VAULT_TYPES = ("plan", "monitoring", "meeting")

# sensitive 以上を強制する型。相談支援の中核文書（計画・モニタリング・会議録）は
# 多法人由来の本人情報を含むため internal では不十分
REQUIRE_SENSITIVE_TYPES = VAULT_TYPES


def check_core_docs(page, report):
    """相談支援の中核文書3型のゲート（本 Vault 固有）。"""
    t, fm, r = page.type, page.fm, page.rel
    if t in REQUIRE_SENSITIVE_TYPES:
        if core.SENSITIVITY_ORDER.get(page.sens, 0) < 2:
            report.errors.append(
                f"[ゲート] {r}: type `{t}` は sensitivity: sensitive 以上が必須"
                f"（現在 `{page.sens}`）")
        if t == "meeting" and not fm.get("person_ids"):
            report.errors.append(
                f"[必須] {r}: type `meeting` には `person_ids` が必須。誰の会議か追えない")
    if t == "monitoring" and not fm.get("plan_ref"):
        report.warns.append(f"[中核文書] {r}: `plan_ref`（対象計画への参照）がない")


CONFIG = core.Config(
    types=core.BASE_TYPES + VAULT_TYPES,
    type_to_dir={**core.BASE_TYPE_TO_DIR,
                 "plan": "plans", "monitoring": "monitorings", "meeting": "meetings"},
    person_bound_types=core.BASE_PERSON_BOUND_TYPES + VAULT_TYPES,
    require_person_id=("plan", "monitoring"),   # meeting は person_ids を check_core_docs で検査
    date_field={"plan": "planned_on", "monitoring": "monitored_on", "meeting": "held_on"},
    provided_by=("本人", "家族", "事業所", "後見人", "医療機関", "行政", "会議", "相談支援"),
    confirmed_by=("記録のみ", "本人に確認", "家族に確認", "支援者に確認", "実地で確認"),
    stale_after_days=core.BASE_STALE_AFTER_DAYS,   # plan / monitoring / meeting は出来事の記録。対象外
    allowlist_note="→ LightRAG feed / 法人サイト / 職員配布に出せるのはこの範囲のみ",
    confirm_advice="本人・家族・現場で確認を",
    page_check=check_core_docs,
)


def lint():
    rep = core.lint(VAULT, CONFIG)
    return rep.errors, rep.warns, rep.infos, rep.allowlist, rep.stats


def main():
    return core.main(VAULT, CONFIG)


if __name__ == "__main__":
    sys.exit(main())
