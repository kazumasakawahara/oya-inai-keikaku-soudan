#!/usr/bin/env python3
"""
test_okf_lint.py — okf_lint.py の回帰テスト

依存ゼロ。一時ディレクトリに合成 Vault を組み立てて lint を走らせ、
「検出すべきものを検出し、検出すべきでないものを検出しない」ことを確認する。

使い方:
    python3 scripts/test_okf_lint.py

schema.md や okf_lint.py を変更したら必ず走らせること。
特に PII パターンをいじった際は、公的機関の連絡先が誤検出されないことを
このテストで担保する（2026-07-26 の §2-7 改訂で確立した区別）。
"""

import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
LINT = os.path.join(HERE, "okf_lint.py")
CORE = os.path.join(HERE, "okf_core.py")   # okf_lint.py が import する共通核。一緒にコピーする

FM = """---
type: {type}
created: 2026-07-26
updated: 2026-07-26
sources:
  - "[[raw/test]]"
tags:
  - test
status: active
sensitivity: {sens}
{extra}---
"""


def page(type_, sens, body, extra=""):
    return FM.format(type=type_, sens=sens, extra=extra) + body + "\n"


# (相対パス, 内容, そのページで検出されるべきラベルの集合)
CASES = [
    # --- 検出してはならない（公的機関の連絡先。schema.md §2-7 改訂版）---
    (
        "wiki/entities/E_公的機関.md",
        page("entity", "public",
             "代表 093-861-3045 / よりそいホットライン 0120-279-338 / "
             "問い合わせ info@city.kitakyushu.lg.jp"),
        set(),
    ),
    (
        "wiki/procedures/PC_相談窓口フロー.md",
        page("procedure", "public",
             "緊急時はワンストップ支援センター 093-582-2424 へ連絡する。"),
        set(),
    ),
    # --- 検出しなければならない（個人への到達経路）---
    (
        "wiki/entities/E_個人混入.md",
        page("entity", "public", "担当者 090-1234-5678 tanaka@gmail.com"),
        {"携帯番号", "個人メール"},
    ),
    (
        "wiki/procedures/PC_個人混入.md",
        page("procedure", "internal",
             "本人の携帯 080-9999-0000。サンシャインマンション 305号室。"),
        {"携帯番号", "集合住宅の部屋番号"},
    ),
    (
        "wiki/concepts/C_生年月日混入.md",
        page("concept", "public", "対象者は1980年5月3日生まれ。"),
        {"生年月日"},
    ),
    # --- 機微ゲート ---
    (
        "wiki/persons/P_001_public偽装.md",
        page("person", "public", "本文", extra='person_id: "P_001"\n'),
        {"個人に紐づくため", "person_id を持つが"},
    ),
    (
        "wiki/sensitive/SE_purpose欠落.md",
        page("sensitive", "restricted", "本文"),
        {"restricted は", "sensitive_purpose"},
    ),
    (
        "wiki/persons/T_配置違反.md",
        page("trial", "internal", "本文"),
        {"wiki/trials/ に置く"},
    ),
    # --- 鮮度（CRM。schema.md §6）: 確認日の欠落・超過を WARN 検出する ---
    (
        "wiki/triggers/TG_確認日なし.md",
        page("trigger", "internal", "本文"),
        {"last_confirmed"},
    ),
    (
        "wiki/protocols/PR_確認超過.md",
        page("protocol", "internal", "本文",
             extra='last_confirmed: 2020-01-01\nconfirmed_by: "実地で確認"\n'),
        {"最終確認から"},
    ),
    # --- 鮮度: 旧フィールド last_validated をエイリアスとして受理する ---
    (
        "wiki/protocols/PR_旧フィールド.md",
        page("protocol", "internal", "本文", extra="last_validated: 2999-01-01\n"),
        set(),
    ),
    # --- 鮮度: confirmed_by の未定義値を WARN する ---
    (
        "wiki/protocols/PR_確認手段不正.md",
        page("protocol", "internal", "本文",
             extra='last_confirmed: 2999-01-01\nconfirmed_by: "たぶん大丈夫"\n'),
        {"confirmed_by"},
    ),
    # --- 鮮度: 出来事の記録（plan 等）は古い日付でも鮮度検査の対象外 ---
    (
        "wiki/plans/PL_出来事は対象外.md",
        page("plan", "sensitive", "本文",
             extra='person_id: "P_001"\nplanned_on: 2020-01-01\n'
                   'sensitive_purpose: "テスト"\nprovided_by: "相談支援"\n'),
        set(),
    ),
    # --- 相談支援3型: 正しいページが通る ---
    (
        "wiki/monitorings/MO_正常.md",
        page("monitoring", "sensitive", "本文",
             extra='person_id: "P_001"\nmonitored_on: 2026-07-01\n'
                   'plan_ref: "[[PL_x]]"\nsensitive_purpose: "テスト"\n'
                   'provided_by: "相談支援"\n'),
        set(),
    ),
    (
        "wiki/meetings/MT_正常.md",
        page("meeting", "sensitive", "本文",
             extra='person_ids: ["P_001"]\nheld_on: 2026-07-15\n'
                   'sensitive_purpose: "テスト"\nprovided_by: "会議"\n'),
        set(),
    ),
    # --- 相談支援3型: ゲート（日付・person_ids・sensitive 強制）---
    (
        "wiki/meetings/MT_ids欠落.md",
        page("meeting", "sensitive", "本文",
             extra='held_on: 2026-07-15\nsensitive_purpose: "テスト"\n'),
        {"person_ids"},
    ),
    (
        "wiki/plans/PL_internal偽装.md",
        page("plan", "internal", "本文",
             extra='person_id: "P_001"\nplanned_on: 2026-04-01\nprovided_by: "相談支援"\n'),
        {"sensitive 以上が必須"},
    ),
    (
        "wiki/monitorings/MO_planref欠落.md",
        page("monitoring", "sensitive", "本文",
             extra='person_id: "P_001"\nmonitored_on: 2026-07-01\n'
                   'sensitive_purpose: "テスト"\nprovided_by: "相談支援"\n'),
        {"plan_ref"},
    ),
    # --- 出所と宛先 ---
    (
        "wiki/protocols/PR_出所不正.md",
        page("protocol", "internal", "本文",
             extra='person_id: "P_001"\nlast_confirmed: 2999-01-01\n'
                   'provided_by: "知人"\n'),
        {"provided_by"},
    ),
    # --- 撤去4型は未定義 type として弾かれる ---
    (
        "wiki/entities/EN_旧型.md",
        page("encounter", "sensitive", "本文",
             extra='person_id: "P_001"\nsensitive_purpose: "テスト"\n'),
        {"未定義の type"},
    ),
    # --- share_scope: origin-only は public でも allowlist に載らない ---
    (
        "wiki/concepts/C_共有不可.md",
        page("concept", "public", "提供元限定の一般知見",
             extra="share_scope: origin-only\n"),
        set(),
    ),
    # --- source_hash（schema.md §1。任意）: 正しい形式（64桁16進）は通る ---
    (
        "wiki/concepts/C_hash正常.md",
        page("concept", "internal", "本文",
             extra="source_hash: " + "a1b2" * 16 + "\n"),
        set(),
    ),
    # --- source_hash: 不正な形式は WARN（無ければ何も言わないのは上の既存ケース群で担保）---
    (
        "wiki/concepts/C_hash不正.md",
        page("concept", "internal", "本文",
             extra="source_hash: deadbeef\n"),
        {"source_hash"},
    ),
]


def main():
    tmp = tempfile.mkdtemp(prefix="okf_lint_test_")
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

        # allowlist が fail-closed であること（違反ページが載っていない）
        proc2 = subprocess.run(
            [sys.executable, os.path.join(tmp, "scripts", "okf_lint.py"), "--allowlist"],
            capture_output=True, text=True, cwd=tmp,
        )
        allow = proc2.stdout.split()
        for bad in ("E_個人混入.md", "C_生年月日混入.md", "P_001_public偽装.md",
                    "C_共有不可.md"):
            if any(bad in a for a in allow):
                failures.append(f"fail-open: 違反ページ {bad} が allowlist に載っている")

        if proc.returncode != 2:
            failures.append(f"終了コードが 2 でない（実際: {proc.returncode}）")

        # --gate は ERROR だけを見る（鮮度 WARN のページはゲート出力に現れず、
        # WARN のみでは 0 を返す）
        proc3 = subprocess.run(
            [sys.executable, os.path.join(tmp, "scripts", "okf_lint.py"), "--gate"],
            capture_output=True, text=True, cwd=tmp,
        )
        if proc3.returncode != 2:
            failures.append(f"--gate: ERROR ありで 2 を返すべき（実際: {proc3.returncode}）")
        for fresh_page in ("TG_確認日なし.md", "PR_確認超過.md"):
            if fresh_page in proc3.stdout:
                failures.append(f"--gate: 鮮度 WARN のページ {fresh_page} がゲート出力に混ざっている")

        # WARN のみの Vault では --gate は 0（鮮度で commit を止めない）、全チェックは 1
        tmp2 = tempfile.mkdtemp(prefix="okf_lint_test_warnonly_")
        try:
            os.makedirs(os.path.join(tmp2, "scripts"))
            shutil.copy(LINT, os.path.join(tmp2, "scripts", "okf_lint.py"))
            shutil.copy(CORE, os.path.join(tmp2, "scripts", "okf_core.py"))
            wpath = os.path.join(tmp2, "wiki", "triggers", "TG_確認日なし.md")
            os.makedirs(os.path.dirname(wpath))
            with open(wpath, "w", encoding="utf-8") as f:
                f.write(page("trigger", "internal", "本文"))
            pg = subprocess.run([sys.executable, os.path.join(tmp2, "scripts", "okf_lint.py"),
                                 "--gate"], capture_output=True, text=True, cwd=tmp2)
            pf = subprocess.run([sys.executable, os.path.join(tmp2, "scripts", "okf_lint.py")],
                                capture_output=True, text=True, cwd=tmp2)
            if pg.returncode != 0:
                failures.append(f"WARNのみ: --gate は 0 を返すべき（実際: {pg.returncode}）")
            if pf.returncode != 1:
                failures.append(f"WARNのみ: 全チェックは 1 を返すべき（実際: {pf.returncode}）")
        finally:
            shutil.rmtree(tmp2, ignore_errors=True)

        print("=== okf_lint 回帰テスト ===")
        if failures:
            for f in failures:
                print(f"  FAIL  {f}")
            print(f"\n{len(failures)} 件失敗")
            return 1
        print(f"  {len(CASES)} ケース全て合格")
        print("  - 公的機関の連絡先を誤検出しない")
        print("  - 個人への到達経路を検出する")
        print("  - 機微ゲートが機能する")
        print("  - allowlist が fail-closed である")
        print("  - 鮮度（確認日の欠落・超過・不正な確認手段）を WARN 検出する")
        print("  - last_validated を後方互換エイリアスとして受理する")
        print("  - 出来事の記録（plan / monitoring / meeting）は鮮度検査の対象外")
        print("  - 相談支援3型のゲート（sensitive 強制・日付・person_id(s)・plan_ref）が機能する")
        print("  - provided_by / share_scope の語彙を検査し、origin-only は allowlist に載らない")
        print("  - 撤去した法律職4型は未定義 type として弾かれる")
        print("  - 鮮度 WARN は --gate（commit・起動時の関所）を止めない")
        print("  - source_hash は任意（正しい64桁16進が通り、不正形式のみ WARN）")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
