#!/usr/bin/env python3
"""
okf_lint.py — schema.md の構造ルールを機械的に検証する

依存ゼロ（Python3 標準ライブラリのみ）。PyYAML も不要。
schema.md §1〜§5 のルールを実行可能な形にしたもの。

使い方:
    python3 scripts/okf_lint.py                 # 全チェック
    python3 scripts/okf_lint.py --gate          # 配布ゲートのみ（終了コードで判定）
    python3 scripts/okf_lint.py --allowlist     # 外部配布可能ファイル一覧を出力

終了コード:
    0 = 違反なし
    1 = WARN のみ（鮮度切れ・推奨事項。作業は止めないが確認を促す）
    2 = ERROR あり（機微情報の漏出リスク。CI や pre-commit で止める想定）
    ※ --gate は ERROR の有無だけを返す（WARN では 0）。鮮度で commit は止めない

作成: 2026-07-26 / schema.md および CLAUDE.md §3-3 に基づく
改訂: 2026-08-09 鮮度検査（schema.md §6。CRM: 証拠・鮮度モデル）を追加
"""

import argparse
import datetime
import os
import re
import sys
from collections import Counter

VAULT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI = os.path.join(VAULT, "wiki")

# --- schema.md §1 / §5 -------------------------------------------------

VALID_TYPES = {
    "person", "trial", "protocol", "trigger", "concept", "entity",
    "ecomap", "sensitive", "public-system", "procedure", "query", "review",
    "plan", "monitoring", "meeting",
}

TYPE_TO_DIR = {
    "person": "persons", "trial": "trials", "protocol": "protocols",
    "trigger": "triggers", "concept": "concepts", "entity": "entities",
    "ecomap": "ecomaps", "sensitive": "sensitive",
    "public-system": "public-systems", "procedure": "procedures",
    "query": "queries", "review": "reviews",
    "plan": "plans", "monitoring": "monitorings", "meeting": "meetings",
}

VALID_STATUS = {"draft", "active", "review", "stale"}
VALID_SENSITIVITY = {"public", "internal", "sensitive", "restricted"}
SENSITIVITY_ORDER = {"public": 0, "internal": 1, "sensitive": 2, "restricted": 3}

REQUIRED_FIELDS = ["type", "created", "updated", "sources", "tags", "status", "sensitivity"]

# 個人に紐づく型。public を名乗ってはならない
PERSON_BOUND_TYPES = {"person", "trial", "protocol", "trigger", "ecomap", "sensitive",
                      "plan", "monitoring", "meeting"}

# sensitive 以上を強制する型。相談支援の中核文書（計画・モニタリング・会議録）は
# 多法人由来の本人情報を含むため internal では不十分（schema.md §2-1b〜2-1d）
REQUIRE_SENSITIVE_TYPES = {"plan", "monitoring", "meeting"}

# person_id が必須の型（meeting は person_ids を別検査）
REQUIRE_PERSON_ID = {"plan", "monitoring"}

# 型ごとに必須の日付フィールド（時系列を追うため）
DATE_FIELD = {"plan": "planned_on", "monitoring": "monitored_on",
              "meeting": "held_on"}

# --- 出所と宛先（schema.md §1・§7。多法人モデル）------------------------
#
# provided_by は「この情報は誰から来たか」、share_scope は「誰に渡してよいか」。
# sensitivity（深さ）と share_scope（宛先）は直交する2軸。
# share_scope 欠落時は安全側の consent-required とみなす。

VALID_PROVIDED_BY = {"本人", "家族", "事業所", "後見人", "医療機関", "行政", "会議", "相談支援"}
VALID_SHARE_SCOPE = {"team", "consent-required", "origin-only"}

# --- 鮮度（schema.md §6。CRM: 証拠・鮮度モデル）--------------------------
#
# `updated` は「ファイルを編集した日」、`last_confirmed` は「この情報がまだ
# 正しいと確かめた日」。現在の状態を主張する型には確認日と、型別の
# 「賞味期限」（staleAfter 相当）を設ける。
# trial / plan / monitoring / meeting / query は「出来事の記録」
# （日付必須の証拠）であり陳腐化する主張ではないため、鮮度検査の対象外。
# 鮮度切れは WARN であって ERROR ではない — 機微情報の漏出とは性質が違うため、
# commit や起動時ゲートを止めない。

STALE_AFTER_DAYS = {
    "person": 90,      # current_living 等の現況は変わる（CLAUDE.md §3-3 旧・読解点検の機械化）
    "protocol": 90,    # 3ヶ月ごとに「まだ機能しているか」を確認
    "trigger": 180,    # 本人の状態は変化する
    "sensitive": 180,  # 性関連等は半年ごとにレビュー（CLAUDE.md §3-3 旧・読解点検の機械化）
    "ecomap": 30,      # 月次スナップショットが前提
}

# 確認の手段（Neo4j 支援DB の source に相当）。「記録のみ」が最も弱い確認
VALID_CONFIRMED_BY = {"記録のみ", "本人に確認", "家族に確認", "支援者に確認", "実地で確認"}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# --- source_hash（schema.md §1。任意）------------------------------------
#
# raw/ 原本の sha256。両系（Vault と Neo4j 支援DB）が同一原本から出たことを
# 識別子だけで突き合わせるための橋（dual-intake-routing.md §1）。
# 任意フィールドなので「あれば形式を検査し、無ければ何もしない」。
# 形式不正は WARN — 突合に使えないだけで、機微情報の漏出とは性質が違う。

SOURCE_HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")

# --- PII パターン（wiki/ に出現してはならないもの。実名は raw/ のみ） ----

# --- PII パターン（schema.md §2-7 改訂版に対応）---------------------
#
# 判別軸は「型」ではなく「到達先」。公的機関の代表番号・相談窓口は
# 緊急時に必要な情報なので検出しない。個人に到達するものだけを検出する。
# これにより entity ページに個人の携帯番号が混入しても検出できる。

_PERSONAL_MAIL = (
    r"gmail\.com|yahoo\.(co\.jp|com)|outlook\.com|hotmail\.(com|co\.jp)|"
    r"icloud\.com|me\.com|live\.jp|docomo\.ne\.jp|ezweb\.ne\.jp|au\.com|"
    r"softbank\.ne\.jp|i\.softbank\.jp|ymobile\.ne\.jp|nifty\.com|excite\.co\.jp"
)

PII_PATTERNS = [
    (r"\b0[789]0-?\d{4}-?\d{4}\b", "携帯番号（個人に到達する）"),
    (r"\b[\w.+-]+@(" + _PERSONAL_MAIL + r")\b", "個人メール（キャリア・フリーメール）"),
    (r"(19|20)\d{2}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日\s*生", "生年月日（日まで）"),
    (r"療育手帳\s*(番号|No\.?)\s*[:：]?\s*[\dA-Z-]{4,}", "手帳番号"),
    (r"受給者証\s*(番号|No\.?)\s*[:：]?\s*[\d-]{6,}", "受給者証番号"),
    (r"\d{1,4}-\d{1,4}-\d{1,4}\s*(番地|号室)", "住居表示"),
    (r"[\u4e00-\u9fff\u30a0-\u30ff]{2,10}(マンション|アパート|ハイツ|コーポ)\s*\d{1,4}\s*号?室?", "集合住宅の部屋番号"),
]


def parse_frontmatter(path):
    """先頭の --- ブロックを浅くパースする。ネストは値をそのまま文字列で返す。"""
    fm, body_start = {}, 0
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        return None, "", f"読み取り失敗: {e}"

    if not lines or lines[0].strip() != "---":
        return None, "".join(lines), "フロントマターがない"

    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            body_start = i + 1
            break
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip().strip('"').strip("'")
            fm[key] = val
        elif line.startswith(("  -", "- ", "\t-")):
            # リスト項目。直前のキーに要素があることだけ記録する
            if fm:
                last = list(fm.keys())[-1]
                if fm[last] == "":
                    fm[last] = "[list]"
    else:
        return None, "".join(lines), "フロントマターが閉じていない"

    return fm, "".join(lines[body_start:]), None


def rel(path):
    return os.path.relpath(path, VAULT)


def lint():
    errors, warns, infos = [], [], []
    allowlist = []
    stats = Counter()
    today = datetime.date.today()

    if not os.path.isdir(WIKI):
        print(f"wiki/ が見つかりません: {WIKI}", file=sys.stderr)
        return ["[致命] wiki/ が見つからない"], [], [], [], Counter()

    for root, dirs, files in os.walk(WIKI):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for name in sorted(files):
            if not name.endswith(".md") or name in ("index.md", "log.md"):
                continue
            path = os.path.join(root, name)
            r = rel(path)
            fm, body, err = parse_frontmatter(path)
            n_errors_before = len(errors)

            if err:
                errors.append(f"[FM] {r}: {err}")
                continue

            # --- 必須フィールド -----------------------------------------
            for field in REQUIRED_FIELDS:
                if field not in fm or fm[field] == "":
                    errors.append(f"[必須] {r}: `{field}` がない")

            t = fm.get("type", "")
            sens = fm.get("sensitivity", "")
            status = fm.get("status", "")
            stats[f"type:{t}"] += 1
            stats[f"sensitivity:{sens}"] += 1

            # --- 値の妥当性 ---------------------------------------------
            if t and t not in VALID_TYPES:
                errors.append(f"[type] {r}: 未定義の type `{t}`")
            if sens and sens not in VALID_SENSITIVITY:
                errors.append(f"[sensitivity] {r}: 未定義の値 `{sens}`")
            if status and status not in VALID_STATUS:
                warns.append(f"[status] {r}: 未定義の値 `{status}`")

            # --- type と配置ディレクトリの一致（schema.md §5）-----------
            if t in TYPE_TO_DIR:
                expected = TYPE_TO_DIR[t]
                parts = os.path.relpath(path, WIKI).split(os.sep)
                if parts[0] != expected:
                    errors.append(
                        f"[配置] {r}: type `{t}` は wiki/{expected}/ に置く（現在 wiki/{parts[0]}/）"
                    )

            # --- ★ 機微ゲート（本スクリプトの中核）----------------------
            # 個人に紐づく型が public を名乗るのは設計上ありえない
            if t in PERSON_BOUND_TYPES and sens == "public":
                errors.append(
                    f"[ゲート] {r}: type `{t}` は個人に紐づくため sensitivity: public にできない"
                )

            # person_id を持つページが public を名乗るのも同様
            if fm.get("person_id") and sens == "public":
                errors.append(f"[ゲート] {r}: person_id を持つが sensitivity: public になっている")

            # restricted は wiki/sensitive/restricted/ 配下のみ
            if sens == "restricted" and "sensitive/restricted" not in r.replace(os.sep, "/"):
                errors.append(f"[ゲート] {r}: restricted は wiki/sensitive/restricted/ に置く")

            # sensitive 以上は sensitive_purpose 必須（schema.md §2-8）
            if SENSITIVITY_ORDER.get(sens, 0) >= 2 and not fm.get("sensitive_purpose"):
                errors.append(f"[ゲート] {r}: sensitive 以上は `sensitive_purpose` の明記が必須")

            # --- ★ 相談支援の中核文書は sensitive 以上を強制 ---
            if t in REQUIRE_SENSITIVE_TYPES:
                if SENSITIVITY_ORDER.get(sens, 0) < 2:
                    errors.append(
                        f"[ゲート] {r}: type `{t}` は sensitivity: sensitive 以上が必須"
                        f"（現在 `{sens}`）")
                if t in REQUIRE_PERSON_ID and not fm.get("person_id"):
                    errors.append(f"[必須] {r}: type `{t}` には `person_id` が必須")
                if t == "meeting" and not fm.get("person_ids"):
                    errors.append(f"[必須] {r}: type `meeting` には `person_ids` が必須。誰の会議か追えない")
                df = DATE_FIELD.get(t)
                if df and not fm.get(df):
                    errors.append(
                        f"[必須] {r}: type `{t}` には `{df}` が必須。時系列を追えない")
            if t == "monitoring" and not fm.get("plan_ref"):
                warns.append(f"[中核文書] {r}: `plan_ref`（対象計画への参照）がない")

            # --- ★ 出所と宛先（schema.md §1・§7）------------------------
            pb = fm.get("provided_by", "")
            if pb and pb not in VALID_PROVIDED_BY:
                warns.append(
                    f"[出所] {r}: `provided_by` が未定義の値 `{pb}`"
                    f"（本人 / 家族 / 事業所 / 後見人 / 医療機関 / 行政 / 会議 / 相談支援）")
            ss_val = fm.get("share_scope", "")
            if ss_val and ss_val not in VALID_SHARE_SCOPE:
                warns.append(
                    f"[宛先] {r}: `share_scope` が未定義の値 `{ss_val}`"
                    f"（team / consent-required / origin-only）")
            if (fm.get("person_id") or fm.get("person_ids")) and not pb:
                warns.append(f"[出所] {r}: 個人に紐づくページに `provided_by` がない（新規ページから徐々に）")

            # --- ★ source_hash の形式検査（schema.md §1。任意）----------
            sh = fm.get("source_hash", "")
            if sh and not SOURCE_HASH_RE.match(sh):
                warns.append(
                    f"[出所] {r}: `source_hash` が sha256 の形式（64桁の16進）でない: `{sh}`")

            # --- ★ 鮮度検査（schema.md §6）---------------------------
            # 編集した日(updated)ではなく「確かめた日(last_confirmed)」を見る。
            # last_validated は旧フィールド名（protocol）の後方互換エイリアス。
            if t in STALE_AFTER_DAYS and status in ("active", "review"):
                limit = STALE_AFTER_DAYS[t]
                lc = fm.get("last_confirmed") or fm.get("last_validated")
                if not lc:
                    warns.append(
                        f"[鮮度] {r}: `last_confirmed`（最終確認日）がない。"
                        f"type `{t}` の目安は{limit}日ごとの確認")
                elif not DATE_RE.match(lc):
                    warns.append(f"[鮮度] {r}: `last_confirmed` が YYYY-MM-DD 形式でない: `{lc}`")
                else:
                    try:
                        age = (today - datetime.date.fromisoformat(lc)).days
                    except ValueError:
                        age = None
                        warns.append(f"[鮮度] {r}: `last_confirmed` が日付として不正: `{lc}`")
                    if age is not None and age > limit:
                        warns.append(
                            f"[鮮度] {r}: 最終確認から{age}日（目安 {limit}日）。"
                            f"内容がまだ正しいか、本人・家族・現場で確認を")
            cb = fm.get("confirmed_by", "")
            if cb and cb not in VALID_CONFIRMED_BY:
                warns.append(
                    f"[確認手段] {r}: `confirmed_by` が未定義の値 `{cb}`"
                    f"（記録のみ / 本人に確認 / 家族に確認 / 支援者に確認 / 実地で確認）")

            # --- PII パターン検出 -----------------------------------
            # public / internal のみ検査。型による除外はしない（schema.md §2-7）。
            if SENSITIVITY_ORDER.get(sens, 0) <= 1:
                for pat, label in PII_PATTERNS:
                    if re.search(pat, body):
                        errors.append(f"[PII] {r}: {label} が本文にある（raw/ に置くべき内容）")

            # --- 外部配布ゲート -----------------------------------------
            # 外部に出してよいのは public のみ。ERROR が1件でも出たページ、
            # および share_scope: origin-only のページは無条件で除外（fail-closed）。
            if sens == "public" and status in ("active", "review") \
                    and fm.get("share_scope", "") != "origin-only" \
                    and len(errors) == n_errors_before:
                allowlist.append(r)

            # --- 鮮度（schema.md §2-9 last_updated_law の活用）----------
            if t == "public-system" and not fm.get("last_updated_law"):
                warns.append(f"[鮮度] {r}: public-system に `last_updated_law` がない")
            if t == "public-system":
                vo = fm.get("verified_on", "")
                if vo and DATE_RE.match(vo):
                    try:
                        vo_age = (today - datetime.date.fromisoformat(vo)).days
                        if vo_age > 365:
                            warns.append(
                                f"[鮮度] {r}: `verified_on` から{vo_age}日。制度ウォッチの"
                                f"点検漏れの可能性（docs/watchlist.md を確認）")
                    except ValueError:
                        pass
            if status == "stale":
                if fm.get("superseded_by"):
                    infos.append(f"[stale] {r} → 置き換え先: {fm['superseded_by']}")
                else:
                    infos.append(f"[stale] {r}（`superseded_by` 未記載 — どの記録に置き換わったか追えない）")

    return errors, warns, infos, allowlist, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", action="store_true", help="機微ゲートの結果だけを終了コードで返す")
    ap.add_argument("--allowlist", action="store_true", help="外部配布可能ファイル一覧を出力")
    args = ap.parse_args()

    errors, warns, infos, allowlist, stats = lint()

    if args.allowlist:
        for p in allowlist:
            print(p)
        return 0

    total = sum(v for k, v in stats.items() if k.startswith("type:"))
    print(f"=== okf_lint: {total} ページを検査 ===\n")

    if errors:
        print(f"■ ERROR ({len(errors)}件) — 機微情報の漏出リスク。要修正")
        for e in errors:
            print(f"  {e}")
        print()
    if warns and not args.gate:
        print(f"■ WARN ({len(warns)}件)")
        for w in warns:
            print(f"  {w}")
        print()
    if infos and not args.gate:
        print(f"■ INFO ({len(infos)}件)")
        for i in infos:
            print(f"  {i}")
        print()

    if not args.gate:
        print("■ 内訳")
        for k in sorted(stats):
            print(f"  {k}: {stats[k]}")
        print(f"\n■ 外部配布可能（sensitivity: public かつ active/review）: {len(allowlist)} 件")
        print("  → LightRAG feed / 法人サイト / 職員配布に出せるのはこの範囲のみ")

    if errors:
        return 2
    if args.gate:
        # ゲートは機微情報（ERROR）だけを見る。鮮度等の WARN で
        # commit や起動時ゲートを止めない（schema.md §6）
        return 0
    if warns:
        return 1
    print("\n違反なし。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
