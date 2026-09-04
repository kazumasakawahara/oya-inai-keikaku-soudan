# scripts/ — 機微情報ゲートの仕組み

このディレクトリは、**宣言されたルールが実際に守られていることを機械的に確かめる**ためのものです。
2026-07-26 に構築しました。経緯の詳細は `log.md` の同日エントリ4件を参照してください。

---

## 何を守っているか

この Vault は、知的障害・精神障害のある方の支援情報を扱います。守るべき境界は2本です。

| 境界 | 内容 |
|------|------|
| **`raw/` と `wiki/`** | 実名・連絡先・原本資料は `raw/` にのみ置く。`wiki/` は `person_id` による仮名化層 |
| **`sensitivity` の4段階** | `public` だけが外部（LightRAG feed・法人サイト・職員配布）に出せる |

この2本は `schema.md` に文章で書かれていました。**しかし、書いてあることと守られていることは別です。**
2026-07-26 時点で36ページが100%準拠していましたが、それはルールが強制されていたからではなく、
丁寧に書かれてきたからでした。ページが増え、セッションが変わり、モデルが変われば崩れます。

---

## 3層構造

```
  ① 宣言        schema.md §2-7 / §5 / §7
                 何が正しいかを定義する。人間が読む
                          ↓
  ② 検証        scripts/okf_lint.py（＋ scripts/okf_core.py）
                 宣言どおりかを機械が確かめる。exit code で答える
                 okf_core.py は姉妹 Vault（oya-iru-wiki）と同一内容の共通検査。
                 正本は本リポ。okf_lint.py は本 Vault 固有の型・語彙・検査だけを持つ
                          ↓
  ③ 強制        githooks/pre-commit
                 検証を通らないコミットを作らせない
```

**3層は単独では機能しません。**

- ①だけ = 今日以前の状態。守られているかどうか誰も確かめていない
- ①+② = 実行を忘れれば無意味
- ②+③のみ（①なし）= 何が正しいかの根拠がコードに埋まり、変更理由が追えなくなる

---

## 使い方

```bash
cd ~/Obsidian/oya-inai-wiki

python3 scripts/okf_lint.py              # 全チェック（内訳・配布可能件数つき）
python3 scripts/okf_lint.py --gate       # 機微ゲートのみ。CI / フック用
python3 scripts/okf_lint.py --allowlist  # 外部配布可能ファイルの一覧
```

終了コード: `0` 違反なし / `1` WARN のみ / `2` ERROR（機微情報の漏出リスク）
※ `--gate` は ERROR の有無だけを返す（WARN では `0`）。鮮度の WARN で commit・起動時ゲートは止まらない

**鮮度検査（schema.md §6、2026-08-09 追加）**: 現在の状態を主張する型（person / protocol / trigger / sensitive / ecomap、`status: active|review` のみ）について、`last_confirmed`（旧 `last_validated` も同義として受理）の欠落・目安日数超過・`confirmed_by` の未定義値を **WARN** で報告する。出来事の記録（trial / plan / monitoring / meeting / query）は対象外。閾値は `okf_lint.py` の `STALE_AFTER_DAYS`（schema.md §6-2 と同時に変更すること）。既存ページへの `last_confirmed` の一括バックフィルは行わない——確認していないものを確認済みにしないため、WARN を確認待ちキューとして使う。

**出所と宛先（schema.md §1、2026-08-09 再設計で追加）**: `provided_by`（8値）と `share_scope`（team / consent-required / origin-only）の語彙を WARN 検査。**`share_scope: origin-only` のページは sensitivity によらず `--allowlist` から無条件除外**（fail-closed）。

### 実行されるタイミング

| 契機 | 何が走るか | 定義場所 |
|------|-----------|---------|
| セッション起動時 | `--gate` | CLAUDE.md §13 手順5 |
| lint モード | 全チェック → その後 Claude が読解点検 | CLAUDE.md §3-3 |
| `git commit` | 3関所（下記） | `githooks/pre-commit` |
| LightRAG へ derive する前 | `--allowlist` の範囲のみ | `~/.claude/skills/wiki-feed-derive/SKILL.md` |

### pre-commit の3関所

1. **`raw/` のステージを拒否** — `.gitignore` は `git add -f` で貫通できるための二重化
2. **`remote` の存在を拒否** — この Vault はローカル専用。誤 push の経路を持たない設計
3. **`okf_lint.py --gate` が ERROR なら拒否**

フックは `.git/hooks/` ではなく **版管理下の `githooks/`** に置き、`core.hooksPath` で参照しています
（フック自体を追跡・監査できるようにするため）。

---

## テスト

```bash
python3 scripts/test_okf_core.py   # 共通検査 okf_core.py の回帰テスト（25ケース＋4シナリオ。姉妹 Vault と同一内容）
python3 scripts/test_okf_lint.py   # lint の回帰テスト（23ケース＋ゲート挙動）
python3 scripts/test_core_docs.py  # 相談支援中核文書3型（plan/monitoring/meeting）のゲートテスト（9ケース）
zsh     scripts/test_precommit.sh  # 関所の動作テスト（5ケース。clean tree 必須——git reset --hard を使う）
```

> `test_precommit.sh` は日本語名の raw 棚（raw/50_医療から/）にダミーを置いて関所1を試す。
> `core.quotepath` が既定のままだと git が日本語パスをエスケープして `grep '^raw/'` を
> すり抜ける穴があり（2026-09-04 に本テストで再現・修正）、この1ケースがその再発を止める。

> **okf_core.py / test_okf_core.py を直したら姉妹 Vault へも同じ内容を届けること。**
> 片方だけ変えると、反対側の `scripts/release.sh` がハッシュ照合で「共通部分がずれています」と言う。

> `test_guardian_types.py` は 2026-08-09 の再設計（法律職4型の削除）に伴い廃止し、
> `test_core_docs.py` へ委譲するスタブになっている。次回の git 整理時に `git rm` してよい。

**`schema.md` か `okf_lint.py` を触ったら必ず走らせてください。**

### なぜテストが要るか

構築当日、合成データでの検証によって**2つの重大な欠陥**が見つかりました。どちらも
「本番36ページで違反なし」という結果からは絶対に分からないものです。

- **allowlist の fail-open** — ERROR を7件出したページが、同時に「外部配布可能」リストにも
  載っていた。ゲートとして最悪の挙動。ERROR が1件でもあれば無条件除外する fail-closed に修正
- **型による除外の穴** — 初版は公的機関の誤検出を避けるため `entity` / `public-system` /
  `procedure` を丸ごと検査対象外にしていた。結果、`entity` ページに個人の携帯番号が混入しても
  検出できなかった。判別軸を「型」から「到達先」へ作り直して解決

いずれも Phase 2 で実際の個人情報が入ってから発覚していたはずのものです。
**ゲートは、破れることを確かめて初めてゲートになります。**

---

## 既知の限界（過信しないこと）

1. **lint はワーキングツリーを検査する。ステージ内容ではない。**
   `git add` の後にファイルを書き換えると、検査対象とコミット内容がずれる可能性がある
2. **日本語の人名は検出できない。** 「田中太郎」は正規表現からは通常の文字列と区別がつかない。
   パターン検出は補助であり、**主防御は `sensitivity` の宣言と `person_id` 運用**である
3. **起動時ゲートは Claude が CLAUDE.md §13 に従うことに依存する。**
   Obsidian で人が直接編集する分には効かない。確実に効くのは commit 時のみ
4. **`restricted` の暗号化やアクセス制御はしていない。** 配置と宣言の整合を検査するだけ

---

## 変更するときの手順

1. `schema.md` を直す（何が正しいかの根拠は常にここ）
2. `okf_lint.py` を追随させる。両 Vault に共通する検査なら `okf_core.py`（正本は本リポ。姉妹 Vault へ同じ内容を届ける）
3. `test_okf_lint.py`（共通検査なら `test_okf_core.py`）に**その変更を捉えるケースを追加**する
4. 両方のテストを走らせる
5. `log.md` に経緯を残す（判断の理由を含めて。「何をしたか」だけでは後で再検討できない）

---

## 背景

構築のきっかけは Google Cloud の Open Knowledge Format (OKF) 仕様の検討でした。
検討の結論は「**OKF を導入する余地はない**」です。`schema.md` は既に OKF 相当
（`type` 必須・`sensitivity` 4段階・`status`・`created`/`updated`）を満たしており、
36ページ全数が準拠していました。

代わりに見えたのが、宣言と検証の乖離です。OKF そのものより、
「オレ流のナレッジ管理は、統一ルールが存在しないため検索も継承もしづらくなる」という
外部からの指摘のほうが実際に効きました。ここにあるのは、その指摘への回答です。
