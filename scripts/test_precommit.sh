#!/bin/zsh
# githooks/pre-commit の3つの関所が実際にコミットを止めることを検証する。
# 検証後は必ず元の状態へ戻す（trap でクリーンアップを保証）。
# 前提: 作業ツリーがクリーンであること（コミット済み）。git reset --hard を使う。
# 対象: このスクリプトが置かれたリポジトリ自身（配布テンプレート）。
#       作者の実運用 Vault へは cd しない（旧版は ~/Obsidian/oya-inai-wiki を巻き戻していた）。
# 骨組み: oya-iru-wiki/scripts/test_precommit.sh（2026-08-13 版。日本語の棚名で関所1を試す）
cd "$(dirname "$0")/.." || exit 1

if [ -n "$(git status --porcelain)" ]; then
  echo "作業ツリーがクリーンではありません。コミットしてから実行してください。"
  exit 1
fi

# 日本語名の棚を使う。core.quotepath 既定のままだと git がパスをエスケープして
# grep '^raw/' をすり抜ける（親いる版で 2026-08-13 に検出した穴）。
SHELF="raw/50_医療から"

BEFORE=$(git rev-parse HEAD)
cleanup() {
  git reset -q HEAD -- . 2>/dev/null
  git checkout -q -- . 2>/dev/null
  rm -f wiki/persons/P_TEST_違反.md wiki/persons/P_TEST_清浄.md "$SHELF/test_dummy.md"
  git remote remove testremote 2>/dev/null
  git reset -q --hard "$BEFORE" 2>/dev/null
  git clean -qfd wiki/persons 2>/dev/null
}
trap cleanup EXIT

pass=0; fail=0
check() { # $1=名前 $2=期待(block|allow) $3=実際の終了コード
  if [ "$2" = "block" ] && [ "$3" -ne 0 ]; then echo "  OK   $1 → 阻止した"; pass=$((pass+1))
  elif [ "$2" = "allow" ] && [ "$3" -eq 0 ]; then echo "  OK   $1 → 通した"; pass=$((pass+1))
  else echo "  FAIL $1 → 期待:$2 だが exit=$3"; fail=$((fail+1)); fi
}

echo "=== pre-commit 関所テスト（oya-inai-keikaku-soudan）==="

# --- 関所1: raw/ の中身を -f で強制ステージ（日本語名の棚）---
echo "ダミー診断書" > "$SHELF/test_dummy.md"
git add -f "$SHELF/test_dummy.md" 2>/dev/null
git -c commit.gpgsign=false commit -q -m "test raw" >/dev/null 2>&1
check "関所1 raw/ の強制ステージ（日本語の棚名）" block $?
git reset -q HEAD -- raw/ 2>/dev/null
rm -f "$SHELF/test_dummy.md"

# --- 関所1b: raw/ 棚の README は骨格として通ること ---
echo "" >> "$SHELF/README.md"
git add "$SHELF/README.md"
git -c commit.gpgsign=false commit -q -m "test raw readme" >/dev/null 2>&1
check "関所1b 棚README は許可" allow $?
git reset -q --hard "$BEFORE" 2>/dev/null

# --- 関所2: remote × 個人紐づけページ（lint 的には清浄なページ）---
git remote add testremote https://example.invalid/x.git 2>/dev/null
cat > wiki/persons/P_TEST_清浄.md <<'EOF'
---
type: person
created: 2026-09-04
updated: 2026-09-04
sources:
  - "[[raw/test]]"
tags:
  - test
status: draft
sensitivity: internal
person_id: "P_TEST"
provided_by: "家族"
---
清浄なテストページ。
EOF
git add wiki/persons/P_TEST_清浄.md
git -c commit.gpgsign=false commit -q -m "test remote" >/dev/null 2>&1
check "関所2 remote × 個人ページ" block $?
git remote remove testremote 2>/dev/null
git reset -q HEAD -- wiki/persons 2>/dev/null
rm -f wiki/persons/P_TEST_清浄.md

# --- 関所3: lint ERROR（機微ゲート違反ページ）---
cat > wiki/persons/P_TEST_違反.md <<'EOF'
---
type: person
created: 2026-09-04
updated: 2026-09-04
sources:
  - "[[raw/test]]"
tags:
  - test
status: active
sensitivity: public
person_id: "P_TEST"
---
本人の携帯 090-0000-1111。1980年5月3日生。
EOF
git add wiki/persons/P_TEST_違反.md
git -c commit.gpgsign=false commit -q -m "test lint" >/dev/null 2>&1
check "関所3 機微ゲート違反" block $?
git reset -q HEAD -- wiki/persons 2>/dev/null
rm -f wiki/persons/P_TEST_違反.md

# --- 正常系: 違反のない変更は通ること ---
echo "" >> log.md
git add log.md
git -c commit.gpgsign=false commit -q -m "test clean commit" >/dev/null 2>&1
check "正常系 違反なしの変更" allow $?

echo
echo "合格 $pass / 失敗 $fail"
[ "$fail" -eq 0 ] && echo "全関所が機能している" || echo "★ 関所に穴がある"
[ "$fail" -eq 0 ]
