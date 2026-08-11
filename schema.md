# schema — 構造ルール

このファイルは Vault の構造ルール（フロントマター仕様・ページ型・Sensitivity Level・命名規約・鮮度）を定義します。CLAUDE.md §4・§7・§8 を抽出した独立ドキュメントです。CLAUDE.md と矛盾が生じた場合は CLAUDE.md を優先し、本ファイルを更新してください。

---

## 1. 共通フロントマター（全ページ必須）

```yaml
---
type: person | trial | protocol | trigger | concept | entity | ecomap | sensitive | public-system | procedure | query | review
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources:
  - "[[raw/path/ファイル名]]"
tags:
  - 親なき後
  - 知的障害
related:
  - "[[wiki/カテゴリ/ページ名]]"
status: draft | active | review | stale
sensitivity: public | internal | sensitive | restricted
person_id: "P_001"   # 該当しないページは省略
last_confirmed: YYYY-MM-DD   # この情報が「まだ正しい」と確かめた日（§6）。現況を主張する型では推奨
confirmed_by: 記録のみ | 本人に確認 | 家族に確認 | 支援者に確認 | 実地で確認   # 確認の手段
superseded_by: "[[...]]"     # status: stale のとき。どの記録に置き換わったか
provided_by: 本人 | 家族 | 事業所 | 後見人 | 医療機関 | 行政 | 会議 | 相談支援   # 情報の出所（§7）。AI が保存先の棚から推定して付与
provided_by_detail: "GH○○（[[E_GH○○]] 参照）"   # 任意。具体名は entity 参照で
share_scope: team | consent-required | origin-only   # 宛先境界（§7）。欠落時は consent-required とみなす
source_hash: "64桁の16進（sha256）"   # 任意。sources の raw/ 原本のハッシュ。Neo4j 支援DB と同一原本を突き合わせるための橋
---
```

### フィールドの意味

| フィールド | 必須 | 説明 |
|------------|------|------|
| `type` | ○ | ページ型。配置ディレクトリと一致させる |
| `created` | ○ | 作成日（YYYY-MM-DD） |
| `updated` | ○ | 最終更新日（YYYY-MM-DD） |
| `sources` | ○ | 参照した `raw/` のソース。複数可 |
| `tags` | ○ | 横断検索用。最低1つは付与 |
| `related` | △ | 関連する `wiki/` ページ。空配列可 |
| `status` | ○ | `draft` / `active` / `review` / `stale` の4値 |
| `sensitivity` | ○ | §3 のアクセス制御レベル |
| `person_id` | △ | Neo4j 支援DB と共有する匿名化ID |
| `last_confirmed` | △ | **この情報がまだ正しいと確かめた日**。`updated`（編集した日）とは別物。現況を主張する型（§6）では欠落・期限超過が lint の WARN 対象 |
| `confirmed_by` | △ | 確認の手段（Neo4j 支援DB の source に相当）。`記録のみ` が最も弱く、`本人に確認`・`実地で確認` が最も強い |
| `superseded_by` | △ | `status: stale` のページで、置き換え先への `[[リンク]]`。stale 化の連鎖を追えるようにする |
| `provided_by` | △ | **この情報は誰から来たか**。多法人モデルの出所記録。AI が振り分け先の棚から推定して付与する（黙認方式） |
| `provided_by_detail` | △ | 提供元の具体名。entity ページ参照で書く（個人名は書かない） |
| `share_scope` | △ | **誰に渡してよいか**。`team`（支援チーム内共有可）/ `consent-required`（本人・後見人の同意要）/ `origin-only`（提供元と相談支援専門員の間に留める）。欠落時は安全側の `consent-required` 扱い |
| `source_hash` | △ | **任意**。`sources` の raw/ 原本の sha256（64桁の16進）。Vault と Neo4j 支援DB が**同一原本から出たことを識別子だけで突き合わせる**ための橋（dual-intake-routing.md §1）。単独運用（Neo4j と連携しない場合）では書かなくてよい。lint はあれば形式のみ検査し、無ければ何もしない |

> **sensitivity は「深さ」・share_scope は「宛先」の直交2軸。** 会議で共有済みの行動障害の詳細は sensitivity: sensitive かつ share_scope: team でありうる。`origin-only` のページは sensitivity によらず外部共有一覧（--allowlist）から無条件に除外される（fail-closed）。

> **`updated` と `last_confirmed` は別物。** 誤字修正でも `updated` は動くが、それは「この情報が今も正しい」ことを何も保証しない。逆に、読み返して「まだこの通り」と確かめたなら、本文を1文字も変えなくても `last_confirmed` を更新する。後の支援者・法律職が信じてよいのは `last_confirmed` のほうである。

### status の遷移

- `draft` — 作成中。レビュー前
- `active` — 現役で使われている記録
- `review` — 作者判断待ち（`wiki/reviews/` と連動）
- `stale` — 過去の仮説。本人の状態変化等で現状と乖離。**削除せず保持する**（CLAUDE.md §2-7）。置き換え先があれば `superseded_by` で示す

---

## 2. type 別の追加フィールド

### 2-1 person（本人・家族・支援者・専門職）

```yaml
person_role: principal | family | supporter | professional
date_of_birth: YYYY-MM        # 月までで十分
diagnosis_summary: "知的障害（療育手帳B1）、ASD"
current_living: "GH ○○寮"
last_confirmed: YYYY-MM-DD    # 現況（住まい・日中活動等）がまだこの通りと確かめた日（§6）
confirmed_by: 記録のみ | 本人に確認 | 家族に確認 | 支援者に確認 | 実地で確認
```

**本文構造**

- `## 人格の核`（性格・好み・嫌い・こだわり）
- `## ライフストーリー`（時系列）
- `## 現在の生活`（一日の流れ）
- `## Joy Triggers` → `[[triggers/joy/...]]` へのリンク集
- `## Distress Triggers` → `[[triggers/distress/...]]` へのリンク集
- `## 支援ネットワーク` → `[[ecomaps/...]]`
- `## 試行錯誤の記録` → `[[trials/...]]` へのリンク集
- `## 他者との関係を築く過程` → `[[trials/decision-rights-learning/...]]`、`[[protocols/others-rights-learning/...]]` へのリンク集

### 2-1b plan（サービス等利用計画）

相談支援専門員の中核文書。様式に書いた内容の**要点**と、様式には書けない**判断の過程**を残す。

```yaml
type: plan
person_id: "P_001"            # 必須
planned_on: YYYY-MM-DD        # 必須（作成・交付日）
plan_period: "2026-04 〜 2027-03"
monitoring_cycle: 3ヶ月       # 標準モニタリング期間
sensitivity: sensitive        # 必須（sensitive 以上）
provided_by: 相談支援
share_scope: team             # 計画は会議で共有される文書
```

**本文構造**：`## 本人の意向` → `## 総合的な援助方針` → `## 週間計画の要点` → `## この計画にした理由`（**ここが Wiki の付加価値**。なぜこの事業所か、何を諦め何を優先したか、本人・家族との調整の経緯）

### 2-1c monitoring（モニタリング記録）

計画に対する実施状況の確認。**鮮度更新の定期便**でもある（§6-3）。

```yaml
type: monitoring
person_id: "P_001"            # 必須
monitored_on: YYYY-MM-DD      # 必須
plan_ref: "[[PL_...]]"        # 対象計画。欠落は WARN
confirms: []                  # モニタリングで「まだ有効」と確認できた記録（person / protocol / trigger 等）
contradicts: []               # 「もう合わない」と分かった記録
sensitivity: sensitive
```

**本文構造**：`## 実施状況` → `## 本人の変化` → `## 確認できたこと・合わなくなったこと` → `## 計画変更の要否`

### 2-1d meeting（サービス担当者会議・支援者会議の回記）

多法人が集まる共有の場の記録。**provided_by の集約点**——会議で共有された情報は share_scope: team の根拠を持つ。

```yaml
type: meeting
person_ids: ["P_001"]         # 必須（複数の本人を扱う会議は列挙）
held_on: YYYY-MM-DD           # 必須
meeting_kind: サービス担当者会議 | 支援者会議 | ケース会議 | その他
attendees_orgs: ["GH（世話人）", "日中活動（サビ管）", "後見人"]   # 出席法人・役割。個人名は書かない
sensitivity: sensitive
```

**本文構造**：`## 共有された情報（提供元別）` → `## 決定事項` → `## 宿題（誰が・いつまで）`

### 2-2 trial（試行錯誤記録 — 一級市民）

```yaml
trial_outcome: success | partial | failure | inconclusive
trial_subdomain: daily-life | decision-rights-learning | crisis-response | medical | sexuality | other
trial_date: YYYY-MM-DD
person_id: "P_001"
context: "入浴拒否時の対応"
confirms: []      # この試行が「まだ有効」と裏づけた記録（protocol / trigger 等）への [[リンク]]
contradicts: []   # この試行が「もう合わない」と示した記録への [[リンク]]
```

**Trial は証拠である**（§6-3）。success で既存 protocol 通りに関わったなら、その protocol を `confirms` に書き、指し先の `last_confirmed` を試行日に更新してよい（実地で確認の最も自然な形）。failure で既存の手順・前提が崩れたなら `contradicts` に書き、指された側を見直す（`status: review`・改訂・`stale` ＋ `superseded_by`）。

**サブドメイン**

| サブドメイン | 用途 |
|---------------|------|
| `daily-life` | 食事・入浴・睡眠等の生活全般 |
| `decision-rights-learning` | 本人が他者の決定権を学ぶ過程（purpose.md §3-0 第二の柱） |
| `crisis-response` | パニック・体調急変等の緊急時対応 |
| `medical` | 医療機関受診・服薬 |
| `sexuality` | 性に関する事象（sensitivity が sensitive 以上の場合は `wiki/sensitive/` にも併載） |
| `other` | いずれにも該当しないもの |

**本文構造**

- `## 状況`（何が起きていたか）
- `## 試したこと`（具体的な対応）
- `## 結果`（事実ベースで）
- `## 学び`（次に同じ状況になったらどうするか — 仮説として）
- `## 関連する後続Trial` → 他の Trial へのリンク

> 失敗 Trial こそ詳細に記録する。`decision-rights-learning` サブドメインでは本人を加害リスクのある対象として分類してはならない（CLAUDE.md §2-12）。

### 2-3 protocol（日常運用プロトコル）

> **protocol ＝手順書（現場の呼称）。**人が読む面（宣言・報告・説明文）では「手順書」と言う。型名 `type: protocol`・ファイル接頭辞・lint の語彙は protocol のまま（Phase 8 実務者レビュー 2026-08-11。識別子の変更は DRIFT を生むため対訳のみ）。

```yaml
protocol_domain: morning | meal | bath | sleep | outing | medical | private-time | others-rights-learning | wiki-explanation
person_id: "P_001"
last_confirmed: YYYY-MM-DD    # この手順がまだ機能していると確かめた日（§6。旧称 last_validated は同義として lint が受理）
confirmed_by: 実地で確認
```

**ドメイン**

| ドメイン | 用途 |
|----------|------|
| `morning` / `meal` / `bath` / `sleep` / `outing` / `medical` / `private-time` | 日常生活の各場面 |
| `others-rights-learning` | 本人が他者の決定権を理解し尊重できるよう支援する継続的プロトコル |
| `wiki-explanation` | 本人に Wiki の存在・目的・参加機会を説明する定期プロトコル |

### 2-4 trigger（喜び・苦痛の引き金）

```yaml
trigger_type: joy | distress
trigger_modality: visual | auditory | tactile | olfactory | gustatory | social | cognitive
intensity: low | medium | high
person_id: "P_001"
last_confirmed: YYYY-MM-DD   # このトリガーが今も当てはまると確かめた日（§6）
confirmed_by: 実地で確認
```

### 2-5 ecomap（支援ネットワーク図）

```yaml
ecomap_purpose: current | handover | crisis | meeting
person_id: "P_001"
mermaid_or_svg: "mermaid"   # 既存 ecomap-generator スキルと連携
last_confirmed: YYYY-MM-DD  # この図が現状と一致すると確かめた日（§6）
confirmed_by: 記録のみ | 本人に確認 | 家族に確認 | 支援者に確認 | 実地で確認
```

### 2-6 concept（福祉概念・行動概念）

```yaml
concept_category: welfare-law | sensory | behavioral | developmental | sexuality | decision-rights
```

`decision-rights` カテゴリは「自己決定権・他者の決定権・相互尊重」に関する概念を扱う。

### 2-7 entity（事業所・行政窓口・社会資源）

```yaml
entity_category: facility | government | medical | legal | community
contact_info_ref: "raw/legal/contacts.md"
```

実在組織は実名可（公開情報）。

**連絡先は「どこに到達する番号か」で区別する**（型を問わず全ページに適用）。

| 分類 | 例 | 扱い |
|------|------|------|
| 公的機関・相談窓口の代表番号、公開された問い合わせ先 | 基幹相談支援センター代表、よりそいホットライン、市役所の部署代表メール | `wiki/` に直接記載してよい。**緊急時に参照されるページ（`procedure` 型等）ではむしろ記載すべき** |
| 本人・家族・支援者個人に到達する連絡先 | 携帯番号、個人メール（キャリアメール・フリーメール）、自宅住所 | `raw/` のみ。`wiki/` には一切書かない。lint の PII 検出対象 |

個人に到達する連絡先が必要な場合は `contact_info_ref` で `raw/` を参照する。

> この区別は、旧規定「連絡先は `raw/` に置き、`wiki/` では参照のみ」が意図より広すぎたための改訂（2026-07-26）。旧規定を文字通り適用すると、`PC_性被害時の対応フロー.md` から相談窓口の番号を削除することになり、緊急時の安全機能を損なう。保護すべきは「連絡先一般」ではなく「個人への到達経路」である。

### 2-8 sensitive（§3 のアクセス制御対象）

```yaml
sensitivity: sensitive | restricted
sensitive_domain: sexuality | criminal-risk-prevention | severe-behavior | trauma | others-rights-learning-difficulty
sensitive_purpose: "..."   # このページが何のために記録されているかを必ず明記
access_note: "本人を支援する立場にある者のみ閲覧"
last_confirmed: YYYY-MM-DD # 記述が現状に合うと読み直して確かめた日（§6。半年ごと）
confirmed_by: 記録のみ | 本人に確認 | 家族に確認 | 支援者に確認 | 実地で確認
```

**ドメイン**

| ドメイン | 内容 |
|----------|------|
| `sexuality` | 性に関する記録（双方向性で扱う。§3-3） |
| `criminal-risk-prevention` | 触法行為予防（本人を加害者にしない伴走の記録） |
| `severe-behavior` | 行動障害の詳細 |
| `trauma` | 過去のトラウマ |
| `others-rights-learning-difficulty` | 他者の決定権を理解する過程で生じた深刻な困難 |

### 2-9 public-system（公的システム）

```yaml
system_category: pension | welfare | guardianship | regional-support
last_updated_law: YYYY-MM-DD   # 法改正への追従用
```

### 2-10 procedure（手続きフロー）

```yaml
procedure_type: application | crisis | handover
person_id: "P_001"   # 個別フローの場合
```

### 2-11 query（保存された問い）

```yaml
query_date: YYYY-MM-DD
query_question: "..."
```

`query` モードで保存された分析・回答。後の ingest で他ページから参照可能にする（CLAUDE.md §3-2）。

### 2-12 review（人間判断待ち）

```yaml
priority: low | medium | high | urgent
proposed_action: Create Page | Update Existing | Defer | Discard
source: "[[raw/...]]"
context: "..."
```

アクションタイプは事前定義の4つのみ（CLAUDE.md §5-2）。

---

## 3. Sensitivity Level — アクセス制御と尊厳保護

### 3-1 4段階のレベル

| Level | 内容 | 例 | 配置 |
|-------|------|------|------|
| `public` | 一般的な情報 | 公的制度の解説、福祉概念 | `wiki/concepts/`, `wiki/public-systems/` |
| `internal` | 支援に必要だが本人特定可能 | 日常プロトコル、Joy Triggers、`others-rights-learning` プロトコル | `wiki/protocols/`, `wiki/triggers/` |
| `sensitive` | 慎重な扱いが必要 | 性に関する基礎情報、行動障害の詳細、過去のトラウマ、本人が他者の決定権を学ぶ過程の困難場面 | `wiki/sensitive/` |
| `restricted` | 極めて慎重な扱いが必要 | 性被害・性加害が現実化した具体記録、触法行為の記録、医療上の機微情報 | `wiki/sensitive/restricted/` |

### 3-2 Sensitive 領域の記述原則（双方向性のもとで）

性・行動障害・触法に関するページを書く際の必須事項（CLAUDE.md §7-2 をそのまま参照）。

1. **目的の明示**：冒頭に「このページは○○のために記録する」を必ず書く。次の三つのいずれか（または複数）を明記。
   - 本人を被害から守るため
   - 本人が他者を尊重できる主体として育つ過程に伴走するため
   - 法的論点の整理のため
2. **本人を主体とした記述**：被害者性も加害者性も固定化しない。
3. **加害・被害の二項対立を避ける**：両方向のリスクを併記する。本人を「加害リスクのある存在」として分類しない（CLAUDE.md §2-12 / A-9）。
4. **記録の更新権限**：これらのページの大幅更新は作者の明示的指示なしに行わない。
5. **後の支援者向けメッセージの併記**：「この記録を読む支援者へ」セクションを設ける。
6. **法的論点との接続**：刑法・民法の論点は `[[wiki/concepts/legal/...]]` へリンク。
7. **「模索」の明示**：他者の決定権を本人が理解する過程に確立された方法論はないことを記述に明記。

### 3-3 性に関する記述の特則（双方向性版）

詳細は CLAUDE.md §7-3 を参照。第一の柱（本人の側 — 被害から守る視点）と第二の柱（他者との関係 — 本人が他者を尊重する主体として育つ伴走）の両方で書く。

---

## 4. 命名規約

| 要素 | 接頭辞 | 例 | 備考 |
|------|--------|-----|------|
| Person | `P_` | `P_001_田中太郎.md` | ID は Neo4j 支援DB と共有。実名は `raw/` のみ |
| Plan | `PL_` | `PL_2026-04-01_P_001.md` | 交付日込み |
| Monitoring | `MO_` | `MO_2026-07-01_P_001.md` | 実施日込み |
| Meeting | `MT_` | `MT_2026-07-15_サービス担当者会議_P_001.md` | 開催日・種別込み |
| Trial（生活全般） | `T_` | `T_2026-04-15_入浴拒否対応.md` | 日付込み |
| Trial（他者の決定権学習） | `TD_` | `TD_2026-04-15_コンビニ店員との距離_P_001.md` | `decision-rights-learning` 専用 |
| Protocol | `PR_` | `PR_morning_routine_P_001.md` | Person ID に紐付け |
| Protocol（他者の決定権学習） | `PRD_` | `PRD_others-rights-learning_P_001.md` | `others-rights-learning` 専用 |
| Protocol（Wiki 説明） | `PRW_` | `PRW_wiki-explanation_P_001.md` | 本人に Wiki を説明する定期プロトコル |
| Trigger | `TG_` | `TG_joy_blue-towel_P_001.md` | Joy/Distress 明示 |
| Ecomap | `EM_` | `EM_current_P_001_2026-04.md` | 月単位スナップショット |
| Concept | `C_` | `C_感覚過敏.md` | Person 非依存 |
| Concept（決定権関連） | `CD_` | `CD_他者の決定権の相互尊重.md` | `decision-rights` カテゴリ |
| Entity | `E_` | `E_GH木町家.md` | 実在組織は実名可 |
| Sensitive | `SE_` | `SE_性的主体としての権利_P_001.md` | アクセス制御対象 |
| Sensitive（決定権学習困難） | `SED_` | `SED_対人関係困難場面_P_001.md` | `others-rights-learning-difficulty` 専用 |
| Public System | `PS_` | `PS_障害年金.md` | 制度横断 |
| Procedure | `PC_` | `PC_緊急時連絡フロー_P_001.md` | 手続きフロー |
| Query | `Q_` | `Q_2026-04-15_GH移行のタイミング.md` | 日付＋問い |
| Review | `R_` | `R_2026-04-15_001.md` | 連番 |

### Person ID の運用

- 形式: `P_001`, `P_002`, ... の 3桁ゼロパディング
- Neo4j 支援DB（`neo4j-agno-agent`）と完全に共有する
- 重大な変更（GH 移行・診断変更等）は Neo4j → Wiki の順で更新（CLAUDE.md §9-2）

---

## 5. type と配置ディレクトリの対応

| type | ディレクトリ |
|------|--------------|
| person | `wiki/persons/` |
| plan | `wiki/plans/` |
| monitoring | `wiki/monitorings/` |
| meeting | `wiki/meetings/` |
| trial | `wiki/trials/` |
| protocol | `wiki/protocols/` |
| trigger | `wiki/triggers/` |
| concept | `wiki/concepts/` |
| entity | `wiki/entities/` |
| ecomap | `wiki/ecomaps/` |
| sensitive | `wiki/sensitive/`（restricted は `wiki/sensitive/restricted/`） |
| public-system | `wiki/public-systems/` |
| procedure | `wiki/procedures/` |
| query | `wiki/queries/` |
| review | `wiki/reviews/` |

`type` フィールドと配置ディレクトリの不整合は lint の検出対象（CLAUDE.md §3-3）。

---

## 6. 鮮度 — 確認日と賞味期限（証拠・鮮度モデル）

この Wiki は「作った瞬間」ではなく「**読まれる瞬間**」——引き継ぎ・内部審査・裁判所報告の場面——に正しくなければ意味がない。本人の状態は変化するため、**現在の状態を主張する型**には賞味期限の考え方を入れる。

### 6-1 型の二分類

| 分類 | 型 | 鮮度検査 |
|------|-----|---------|
| **現在の主張**（陳腐化する） | person / protocol / trigger / ecomap / sensitive | **対象**。`last_confirmed` の欠落・期限超過を lint が WARN |
| **出来事の記録**（証拠。日付に固定される） | trial / plan / monitoring / meeting / query | **対象外**。それぞれの必須日付（trial_date / planned_on / monitored_on / held_on / query_date）が時点を固定する |

### 6-2 型別の確認の目安（staleAfter）

| type | 目安 | 理由 |
|------|------|------|
| `person` | **90日** | current_living 等の現況は変わる（旧 §3-3 読解点検「3ヶ月以上更新なしの Person」の機械化） |
| `protocol` | **90日** | 「今も機能している手順」でなければ手順の意味がない |
| `trigger` | **180日** | 本人の状態は変化する。喜び・苦痛の引き金も入れ替わる |
| `sensitive` | **180日** | 性関連等は半年ごとにレビュー（旧 §3-3 読解点検「性関連ページの最終レビュー日」の機械化） |
| `ecomap` | **30日** | 月単位スナップショットが前提 |

- 対象は `status: active` / `review` のみ（`draft`・`stale` は対象外）
- 数値を変えるときは**この表と `scripts/okf_lint.py` の `STALE_AFTER_DAYS` を同時に**直す
- `concept`・`entity`・`public-system`・`procedure` は知識ページであり対象外。制度の鮮度は `last_updated_law` と **制度ウォッチ**（法令・制度の定期監視。`docs/watchlist.md` を正典に外部の変化を検知して review に起票する）で追う。`verified_on` が365日を超えた public-system は WARN（制度ウォッチが正常稼働していれば発火しない、見張りの見張り）

### 6-3 確認・否定の連鎖（confirms / contradicts / superseded_by）

日々の Trial は既存の記録に対する**証拠**として働く（§2-2）。success → `confirms` ＋ 指し先の `last_confirmed` を試行日に更新。failure → `contradicts` ＋ 指された側を見直し（`status: review`・改訂・`stale` ＋ `superseded_by`）。これで「なぜ今の手順になったのか」を証拠ごと遡れる。

**モニタリングは鮮度更新の定期便である。** monitoring（§2-1c）の `confirms` に挙がった person / protocol / trigger は、`last_confirmed` を `monitored_on` に更新してよい（confirmed_by: 実地で確認 または 支援者に確認）。trial が日々の証拠なら、**monitoring は制度が保証する定期の証拠**——鮮度の仕組みは、相談支援の法定リズム（モニタリング周期）に乗って回る。

### 6-4 鮮度は WARN、機微は ERROR

鮮度切れは ERROR にしない。古い記録は危険信号だが、機微情報の漏出（ERROR）とは性質が違う。`--gate` は ERROR の有無だけを終了コードに反映するため、**鮮度で pre-commit・起動時ゲートは止まらない**。止めない代わりに、lint モード（CLAUDE.md §3-3）と AI の声かけ（「この情報、最近確かめましたか？」）で利用時点に見えるようにする。**確かめていないのに `last_confirmed` を更新してはならない**——既存ページへの一括バックフィルをしないのも同じ理由による。
