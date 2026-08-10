#!/usr/bin/env python3
"""
test_core_docs.py — 相談支援の中核文書3型（plan / monitoring / meeting）のゲート検査

旧 test_guardian_types.py（後見4型のゲート担保）の後継。2026-08-09 の
相談支援専門員モデル再設計（docs/redesign-tech-spec.md）に伴い改修した。
依存ゼロ。一時ディレクトリに合成ページを組み立てて lint を走らせる。

担保すること:
  - 正しい3型のページが「通る」（機能が存在しないときにテストが合格しない担保）
  - sensitivity 不足・日付欠落・person_id(s) 欠落・配置違反・public 偽装が「止まる」

使い方:
    python3 scripts/test_core_docs.py
"""

import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
LINT = os.path.join(HERE, "okf_lint.py")

FM = """---
type: {type}
created: 2026-08-09
updated: 2026-08-09
sources: []
tags:
  - test
status: active
sensitivity: {sens}
sensitive_purpose: "テスト"
{extra}---
本文
"""


def page(type_, sens, extra=""):
    return FM.format(type=type_, sens=sens, extra=extra)


# (相対パス, 内容, 期待ラベル集合。空集合=違反なしで通るべき)
CASES = [
    # --- 通るべきケース（これが無いと「機能が存在しなくても合格」になる）---
    ("wiki/plans/PL_2026-04-01_P_001.md",
     page("plan", "sensitive",
          'person_id: "P_001"\nplanned_on: 2026-04-01\nprovided_by: "相談支援"\nshare_scope: team\n'),
     set()),
    ("wiki/monitorings/MO_2026-07-01_P_001.md",
     page("monitoring", "sensitive",
          'person_id: "P_001"\nmonitored_on: 2026-07-01\nplan_ref: "[[PL_2026-04-01_P_001]]"\nprovided_by: "相談支援"\n'),
     set()),
    ("wiki/meetings/MT_2026-07-15_P_001.md",
     page("meeting", "sensitive",
          'person_ids: ["P_001", "P_002"]\nheld_on: 2026-07-15\nprovided_by: "会議"\n'),
     set()),
    # --- 止まるべきケース ---
    ("wiki/plans/PL_日付欠落.md",
     page("plan", "sensitive", 'person_id: "P_001"\nprovided_by: "相談支援"\n'),
     {"planned_on"}),
    ("wiki/plans/PL_person欠落.md",
     page("plan", "sensitive", 'planned_on: 2026-04-01\nprovided_by: "相談支援"\n'),
     {"person_id"}),
    ("wiki/monitorings/MO_internal偽装.md",
     page("monitoring", "internal",
          'person_id: "P_001"\nmonitored_on: 2026-07-01\nplan_ref: "[[PL_x]]"\nprovided_by: "相談支援"\n'),
     {"sensitive 以上が必須"}),
    ("wiki/meetings/MT_ids欠落.md",
     page("meeting", "sensitive", 'held_on: 2026-07-15\nprovided_by: "会議"\n'),
     {"person_ids"}),
    ("wiki/meetings/MT_public偽装.md",
     page("meeting", "public",
          'person_ids: ["P_001"]\nheld_on: 2026-07-15\nprovided_by: "会議"\n'),
     {"個人に紐づくため"}),
    ("wiki/protocols/PL_配置違反.md",
     page("plan", "sensitive",
          'person_id: "P_001"\nplanned_on: 2026-04-01\nprovided_by: "相談支援"\n'),
     {"wiki/plans/ に置く"}),
]


def main():
    tmp = tempfile.mkdtemp(prefix="core_docs_test_")
    try:
        os.makedirs(os.path.join(tmp, "scripts"))
        shutil.copy(LINT, os.path.join(tmp, "scripts", "okf_lint.py"))
        for relpath, content, _ in CASES:
            full = os.path.join(tmp, relpath)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8") as f:
                f.write(content)

        proc = subprocess.run(
            [sys.executable, os.path.join(tmp, "scripts", "okf_lint.py")],
            capture_output=True, text=True, cwd=tmp,
        )
        out = proc.stdout

        failures = []
        for relpath, _, expected in CASES:
            name = os.path.basename(relpath)
            lines = [l for l in out.splitlines() if name in l and ("ERROR" not in l)]
            found = "\n".join(lines)
            for label in expected:
                if label not in found:
                    failures.append(f"未検出: {name} に「{label}」が出るはずが出ていない")
            if not expected and lines:
                failures.append(f"誤検出: {name} は違反なしのはずが検出された\n      {found}")

        print("=== 相談支援中核文書（plan / monitoring / meeting）ゲートテスト ===")
        if failures:
            for f in failures:
                print(f"  FAIL  {f}")
            print(f"\n{len(failures)} 件失敗")
            return 1
        print(f"  {len(CASES)} ケース全て合格")
        print("  - 正しい3型のページが通る")
        print("  - 日付フィールド欠落で止まる（時系列を追えなくなるため）")
        print("  - person_id / person_ids 欠落・配置違反・sensitive 未満・public 偽装で止まる")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
