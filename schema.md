# schema — 構造ルール

このファイルは Vault の構造ルール（フロントマター仕様・ページ型・Sensitivity Level・命名規約・鮮度）を定義する**正典**です。姉妹 Vault（oya-iru-wiki）と共通の定義（フロントマター・鮮度・時点の2軸）は `schema-common.md` に置き、本ファイルはそれからの差分と本 Vault 固有の型を書きます（2026-09-04）。操作指示書（AGENTS.md）は「どう動くか」だけを定め、構造の定義は本ファイルを参照します（2026-09-05 に AGENTS.md の型・Sensitivity・命名の節を本ファイルへ統合）。矛盾が生じた場合は本ファイルを優先し、AGENTS.md を直してください。

---

## 1. 共通フロントマター（全ページ必須）

共通の定義（必須7項目・各フィールドの意味・status の遷移・二つのコールアウト）は **[[schema-common]] §A** にある。本節はそれを前提に、本 Vault の型一覧と語彙、および完成形の例だけを書く。

```yaml
---
type: person | plan | monitoring | meeting | trial | protocol | trigger | concept | entity | ecomap | sensitive | public-system | procedure | query | review
created: YYYY-MM-DD          # 記録日（不変。schema-common §A-2）
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
valid_from: YYYY-MM-DD       # この事実が成立した日（schema-common §C）。不明なら書かない
valid_until: YYYY-MM-DD      # 当てはまらなくなった日。相談支援専門員が裁定して書く
valid_until_reason: "終了の理由1行"   # valid_until を書くとき、superseded_by が無ければ必須
superseded_by: "[[...]]"     # status: stale のとき。どの記録に置き換わったか
provided_by: 本人 | 家族 | 事業所 | 後見人 | 医療機関 | 行政 | 会議 | 相談支援   # 情報の出所（schema-common.md §A-2）。AI が保存先の棚から推定して付与
provided_by_detail: "GH○○（[[E_GH○○]] 参照）"   # 任意。具体名は entity 参照で
share_scope: team | consent-required | origin-only   # 宛先境界（schema-common.md §A-2・A-3）。欠落時は consent-required とみなす
source_hash: "64桁の16進（sha256）"   # 任意。sources の raw/ 原本のハッシュ。Neo4j 支援DB と同一原本を突き合わせるための橋
---
```

### 共通からの差分（本 Vault 固有）

| 項目 | 共通（schema-common） | 本 Vault |
|------|----------------------|---------|
| 型の構成 | 継承12型（person / trial / protocol / trigger / concept / entity / ecomap / sensitive / public-system / procedure / query / review） | **15型（plan / monitoring / meeting ＋ 継承12型）**。相談支援の中核文書3型は §2-1b〜2-1d |
| `tags` の例 | Vault ごと | 親なき後 / 知的障害 |
| `confirmed_by` の語彙 | Vault ごと | 記録のみ / 本人に確認 / 家族に確認 / 支援者に確認 / 実地で確認（Neo4j 支援DB の source に相当） |
| `provided_by` の語彙 | Vault ごと | 本人 / 家族 / 事業所 / 後見人 / 医療機関 / 行政 / 会議 / 相談支援 の8値（多法人モデルの出所記録。意味は schema-common.md §A-2） |
| `review` の判断主体 | 管理者 | 作者（`wiki/reviews/` と連動） |
| `source_hash` の相手先 | 同一原本の突き合わせ | Neo4j 支援DB（連携の設計文書 dual-intake-routing.md §1 は作者環境の文書で配布物には含まれない。役割分担は docs/連携.md）。単独運用では書かなくてよい |
| `valid_from` / `valid_until` を書く人 | 人 | 相談支援専門員。AI は提案も推定もしない（§6-5） |

> `share_scope` の3値の意味と「sensitivity は深さ・share_scope は宛先」の原則は schema-common §A-2・A-3。`stale` の削除禁止は AGENTS.md §2-7 と同旨。

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

> 失敗 Trial こそ詳細に記録する。「なぜダメだったか」が次の支援者を救う。
>
> **decision-rights-learning サブドメインの特則**: このサブドメインの Trial は、本人を「加害リスクのある対象」として記述するのではなく（AGENTS.md §2-12）、本人が他者と豊かな関係を築ける主体として育つ過程として記述する。「今日、本人が店員さんに無理に話しかけようとしたが、私が『今は他のお客さんを見ている時だから、終わったらね』と言ったら待てた」のような小さな成功も、「相手が嫌がっているサインを今日は読み取れなかった。次回は事前に絵カードで距離を伝える方法を試したい」のような失敗も、ともに模索の記録として等しく価値を持つ。

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

> **others-rights-learning プロトコルの記述要点**: 本人の認知特性・コミュニケーション様式に応じた具体的な関わり方を記述する。視覚支援・SST 的アプローチ・場面ごとの絵カード・断られた経験の処理方法等。本人を矯正する手順ではなく、本人と支援者が共に学ぶ過程として書く。

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
sensitive_purpose: "..."   # 何のために記録するかを必ず明記。例: 本人を被害から守るため／本人が他者を尊重できるよう伴走するため／法的論点の整理のため
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

`query` モードで保存された分析・回答。後の ingest で他ページから参照可能にする（AGENTS.md §3-2）。

### 2-12 review（人間判断待ち）

```yaml
priority: low | medium | high | urgent
proposed_action: Create Page | Update Existing | Defer | Discard
source: "[[raw/...]]"
context: "..."
```

アクションタイプは事前定義の4つのみ（Create Page / Update Existing / Defer / Discard）。`Discard` は削除禁止（AGENTS.md §2-7）の例外として `wiki/reviews/discarded/` へ移動し、履歴を残す。発生条件と運用は docs/review-system.md。

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

性・行動障害・触法に関するページを書く際は、purpose.md §3-0 双方向性原則のもと、以下を遵守する（操作指示書 AGENTS.md §2-9 が本節を指す）。

1. **目的の明示**：冒頭に「このページは○○のために記録する」を必ず書く。具体的には次の三つのいずれか（または複数）を明記する。
   - 本人を被害から守るため
   - 本人が他者を尊重できる主体として育つ過程に伴走するため
   - 法的論点の整理のため
2. **本人を主体とした記述**：「Aさんは○○された」ではなく「Aさんに○○が起きた」「Aさんが○○の状況にあった」と記述。被害者性も加害者性も固定化しない。
3. **加害・被害の二項対立を避ける**：知的障害のある方は、加害者にも被害者にもなり得る。両方向のリスクを併記する。同時に、本人を「加害リスクのある存在」として分類することは禁ずる（AGENTS.md §2-12 / purpose.md A-9）。記述は常に本人の成長と他者との関係構築を支える方向を向く。
4. **記録の更新権限**：これらのページの大幅な更新は、作者の明示的指示なしに行わない。
5. **後の支援者向けメッセージの併記**：「この記録を読む支援者へ」セクションを設け、本人の尊厳を守る関わり方と、本人が他者の決定権を理解できるよう支援する関わり方の両方を記述する。
6. **法的論点との接続**：刑法・民法上の論点が絡む場合は、`[[wiki/concepts/legal/...]]` へリンクして概念を整理し、**個別の法的判断は弁護士等の専門職への相談につなぐ**。特に同意の概念、性的同意年齢、責任能力、合理的配慮の双方向性については丁寧に整理する。
7. **「模索」の明示**：他者の決定権を本人が理解する過程に確立された方法論はないことを記述に明記する。今この記述は仮説であり、運用しながら更新されることを明記する。

### 3-3 性に関する記述の特則（双方向性版）

性に関する記述は、purpose.md §3-0 双方向性原則の最も切実に問われる領域である。以下の双柱で書く。

**第一の柱：本人の側（被害から守る視点）**
- 医学用語ではなく日常語で書く（ただし誤解を招かない範囲で）
- 「自慰」「精通」「初潮」等の事実は明記してよいが、観察的・尊厳的に
- 過去の被害記録は事実のみ。詳細は `raw/` に留め、`wiki/` では支援上必要な範囲のみ
- 本人の境界線、嫌がるサイン、安心できる空間・関わり方
- 性的主体としての権利（恋愛・結婚・性行為・子を持つこと）を否定する記述を書かない
- 被害が起きた場合の支援要請経路（ワンストップ支援センター、基幹相談支援センター、警察障害者支援担当、産婦人科で障害者対応に理解のある医師、弁護士会人権擁護委員会等）

**第二の柱：他者との関係の側（本人が他者を尊重する主体として育つ伴走）**
- 加害リスクは「予防の観点」で記述する。ただし本人を「加害リスクのある対象」として分類しない（purpose.md A-9）
- 本人が「相手の同意」「相手の拒否」「相手の身体は相手のもの」を理解する過程の試行錯誤を、`decision-rights-learning` サブドメインの Trial として蓄積する（§2-2）
- 機能した関わり方・絵カード・動画を使った視覚支援・SST 的アプローチ・特定場面（電車内・コンビニ・公園等）での具体的対応プロトコル（§2-3）
- 本人が断られる経験を安全に積める機会の設計
- 本人が自分自身の「嫌だ」を表現できるようになる過程（これが他者の「嫌だ」を理解する基盤になる可能性）
- 責任能力論議は予防文脈で扱う。事件発生時の弁護方針論議は `raw/40_後見・法律から/` に留める

**両柱共通の原則**
- 本人の前で読み上げて恥ずかしい記述は書かない
- 興味本位の詳細記述は禁止
- すべての記述は仮説であり、本人の状態と支援者の試行錯誤の進展で更新される

---

## 4. 命名規約

| 要素 | 接頭辞 | 例 | 備考 |
|------|--------|-----|------|
| Person | `P_` | `P_001_仮名.md` | ID は Neo4j 支援DB と共有。**実名は使わず仮名で**（実名は `raw/` のみ） |
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
- Neo4j 支援DB と完全に共有する（連携環境の場合。docs/連携.md）
- 重大な変更（GH 移行・診断変更等）は Neo4j → Wiki の順で更新（AGENTS.md §4）

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

`type` フィールドと配置ディレクトリの不整合は lint の検出対象（AGENTS.md §3-3）。

---

## 6. 鮮度 — 確認日と賞味期限（証拠・鮮度モデル）

原理（型の二分類・staleAfter の基底値・確認と否定の連鎖・三分法・時点の2軸）は **[[schema-common]] §B・§C** にある。本節は本 Vault での型の割り当てと、定期便の実装だけを書く。この Wiki が正しくなければならない「読まれる瞬間」とは、引き継ぎ・内部審査・裁判所報告の場面である。

### 6-1 型の二分類（本 Vault の割り当て）

| 分類 | 型 | 鮮度検査 |
|------|-----|---------|
| **現在の主張**（陳腐化する） | person / protocol / trigger / ecomap / sensitive | **対象**。`last_confirmed` の欠落・期限超過を lint が WARN（`valid_until` が書かれたページは対象外） |
| **出来事の記録**（証拠。日付に固定される） | trial / plan / monitoring / meeting / query | **対象外**。それぞれの必須日付（trial_date / planned_on / monitored_on / held_on / query_date）が時点を固定する |

### 6-2 型別の確認の目安（staleAfter）

基底値（person 90 / protocol 90 / trigger 180 / sensitive 180 / ecomap 30）は schema-common §B-2 のとおり。**本 Vault に追加の型はない。** 数値を変えるときは schema-common の表と `scripts/okf_core.py` の `BASE_STALE_AFTER_DAYS` を同時に直す（本 Vault 固有の型を将来足すなら `scripts/okf_lint.py` の Config `stale_after_days`）。

`concept`・`entity`・`public-system`・`procedure` は知識ページであり対象外。制度の鮮度は `last_updated_law` と**制度ウォッチ**（法令・制度の定期監視。`docs/watchlist.md` を正典に外部の変化を検知して review に起票する）で追う。

### 6-3 確認・否定の連鎖と定期便（本 Vault の実装）

日々の Trial は既存の記録に対する**証拠**として働く（§2-2）。success → `confirms` ＋ 指し先の `last_confirmed` を試行日に更新。failure → `contradicts` ＋ 指された側を見直し（`status: review`・改訂・`stale` ＋ `superseded_by`）。これで「なぜ今の手順になったのか」を証拠ごと遡れる。

**モニタリングは鮮度更新の定期便である。** monitoring（§2-1c）の `confirms` に挙がった person / protocol / trigger は、`last_confirmed` を `monitored_on` に更新してよい（confirmed_by: 実地で確認 または 支援者に確認）。trial が日々の証拠なら、**monitoring は制度が保証する定期の証拠**——鮮度の仕組みは、相談支援の法定リズム（モニタリング周期）に乗って回る。

`contradicts` に挙がったページは、その事実がいつまで当てはまっていたかを相談支援専門員が裁定し、`valid_until` と `superseded_by`（または `valid_until_reason`）を書く契機になる（schema-common §B-3・§C）。lint は「contradicts で指されたが valid_until が空」を WARN で知らせる。

### 6-4 三分法

鮮度は WARN、機微は ERROR、構造矛盾は ERROR（schema-common §B-4）。`--gate` は ERROR の有無だけを終了コードに反映するため、鮮度で pre-commit・起動時ゲートは止まらない。止めない代わりに lint モード（AGENTS.md §3-3）と AI の声かけで利用時点に見えるようにする。**確かめていないのに `last_confirmed` を更新してはならない**——既存ページへの一括バックフィルをしないのも同じ理由による。

### 6-5 時点の2軸（本 Vault の運用）

- `valid_from` / `valid_until` を書くのは相談支援専門員。AI は提案も推定もしない
- 終了の契機は3つ: monitoring・trial の `contradicts`、本人・家族・事業所からの報告、定期便で「もう当てはまらない」と判断。いずれも人が裁定して書き、`superseded_by` か `valid_until_reason` を残す
- raw/ の仕分け宣言に「原本の日付」欄を持つ。原本に日付がなければ `不明` と明示し、受付日で代用しない（発生日＝事実時間、`created`＝知得時間）
- 対訳表（Wiki ↔ Neo4j 支援DB）は AGENTS.md §4
