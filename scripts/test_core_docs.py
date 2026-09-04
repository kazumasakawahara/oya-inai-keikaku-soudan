#!/usr/bin/env python3
"""
test_core_docs.py — 相談支援の中核文書3型（plan / monitoring / meeting）のゲート検査

旧 test_guardian_types.py（後見4型のゲート担保）の後継。2026-08-09 の
相談支援専門員モデル再設計（docs/redesign-tech-spec.md）に伴い改修した。
依存ゼロ。一時ディレクトリに合成ページを組み立てて lint を走らせる。

担保すること:
  - 正しい3型のページが「通る」（機能が存在しないときにテストが合格しない担保）
  - sensitivity 不足・日付欠落・person_id(s) 欠落・配置違反・public 偽装が「止まる」
  - 配布物全体で「CLAUDE.md §N-M」「AGENTS.md §N-M」の参照先が実在する（2026-09-05 柱5で追加。
    操作文書の減量で節が移動・消滅したとき、他の文書からの参照が宙に浮くのを止める）

使い方:
    python3 scripts/test_core_docs.py
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
LINT = os.path.join(HERE, "okf_lint.py")
CORE = os.path.join(HERE, "okf_core.py")   # okf_lint.py が import する共通核。一緒にコピーする

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


# ---------------------------------------------------------------------------
# 参照先検査: 配布物のどこかに書かれた「CLAUDE.md §N-M」「AGENTS.md §N」が、
# 実際にその文書の節（## §N）・小節（### N-M）・節内の番号付き項目（N. …）として
# 存在するかを確かめる。開発メタ文書（HANDOVER / docs/phase-common-* / release.sh）は
# 過去の節番号を歴史として持つので対象外。
# ---------------------------------------------------------------------------
ROOT = os.path.dirname(HERE)
TARGETS = ("CLAUDE.md", "AGENTS.md")
EXCLUDE_RE = re.compile(r"^(HANDOVER\.md|docs/phase-common-|scripts/release\.sh)")
SKIP_DIRS = {".git", "raw", ".obsidian", "node_modules", "__pycache__"}
TEXT_EXT = {".md", ".py", ".sh", ".html", ".txt", ".yaml", ".yml", ".json", ""}
FILE_TOKEN = re.compile(r"[\w.-]+\.md")
SEC_TOKEN = re.compile(r"§(\d+)(?:-(\d+[a-z]?))?")


def section_map(path):
    """文書の見出し集合を返す: {'3', '3-1', '2-7', ...}"""
    have = set()
    current = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^## §(\d+)", line)
            if m:
                current = m.group(1)
                have.add(current)
                continue
            m = re.match(r"^### (\d+)-(\d+[a-z]?)", line)
            if m:
                have.add(f"{m.group(1)}-{m.group(2)}")
                continue
            m = re.match(r"^\s*(\d+)\.\s", line)
            if m and current:
                have.add(f"{current}-{m.group(1)}")
    return have


def iter_dist_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, ROOT)
            if EXCLUDE_RE.match(rel):
                continue
            if os.path.splitext(name)[1] not in TEXT_EXT:
                continue
            yield rel, full


def refs_in_line(line, self_name):
    """行の中の § 参照を、直前に現れた .md ファイル名に帰属させて返す。
    ファイル名が無ければ self_name（その行を含む文書自身）への参照とみなす。"""
    out = []
    owner = self_name
    pos = 0
    events = sorted(
        [(m.start(), "file", m.group(0)) for m in FILE_TOKEN.finditer(line)]
        + [(m.start(), "sec", m) for m in SEC_TOKEN.finditer(line)]
    )
    for _, kind, val in events:
        if kind == "file":
            owner = os.path.basename(val)
        elif owner in TARGETS:
            sec = val.group(1) + (f"-{val.group(2)}" if val.group(2) else "")
            out.append((owner, sec))
    return out


def check_section_refs():
    maps = {}
    for name in TARGETS:
        path = os.path.join(ROOT, name)
        if os.path.exists(path):
            maps[name] = section_map(path)
    failures = []
    checked = 0
    for rel, full in iter_dist_files():
        self_name = os.path.basename(rel) if os.path.basename(rel) in TARGETS else None
        try:
            with open(full, encoding="utf-8") as f:
                lines = f.read().splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for i, line in enumerate(lines, 1):
            if self_name is None and not any(t in line for t in TARGETS):
                continue
            for owner, sec in refs_in_line(line, self_name):
                checked += 1
                if owner not in maps:
                    failures.append(f"{rel}:{i}: {owner} が存在しない（§{sec} を参照）")
                elif sec not in maps[owner]:
                    failures.append(f"{rel}:{i}: {owner} §{sec} が存在しない")
    return checked, failures


def main():
    tmp = tempfile.mkdtemp(prefix="core_docs_test_")
    try:
        os.makedirs(os.path.join(tmp, "scripts"))
        shutil.copy(LINT, os.path.join(tmp, "scripts", "okf_lint.py"))
        shutil.copy(CORE, os.path.join(tmp, "scripts", "okf_core.py"))
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
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("=== 操作文書の節参照テスト（CLAUDE.md § / AGENTS.md §） ===")
    checked, ref_failures = check_section_refs()
    if ref_failures:
        for f in ref_failures:
            print(f"  FAIL  {f}")
        print(f"\n{len(ref_failures)} 件の参照先が存在しない（{checked} 件検査）")
        return 1
    print(f"  {checked} 件の参照がすべて実在する節を指している")
    return 0


if __name__ == "__main__":
    sys.exit(main())
