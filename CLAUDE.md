# oya-inai-keikaku-soudan — 親なき後支援の知識グラフ運用マニュアル

このファイルは本 Vault で作業する AI エージェント（Claude Desktop / Claude Code 等）への操作指示書です。

> **導入者向け注記（β版）**: 本ファイルは作者の実運用 Vault から骨格を配布したもので、一部の節は作者の環境（Vault 名 `oya-inai-wiki`・Neo4j 支援DB・独自スキル群・filesystem MCP）を前提にしています。導入時に docs/導入手順.md Step 3 に従って、§9（Neo4j 連携）・§10（スキル連携）・§14（ファイル操作ツール）とパス表記をあなたの環境にあわせて調整してください。設計文書（docs/redesign-*.md）への参照は本家 Vault のもので、配布物には含まれていません。

> **この Vault の一人称は「相談支援専門員」です。** 計画相談を担う者と具体的支援を行う者（GH・日中活動・成年後見人等）は別法人に属し、本人に関する情報は親からの聴き取り・支援者会議・各事業所からの提供・計画とモニタリングという形で、すべて**相談支援専門員という結節点**を経由して集まります。本 Vault はその結節点に集まる情報を、本人単位の暗黙知として編むための装置です（設計の経緯は docs/redesign-requirements.md）。

KarpathyのLLM Wikiパターンを骨格に、`~/Dev-Work/llm_wiki`（kazumasakawahara/ja-llm-wiki）の発展形態（purpose.md、2段階Chain-of-Thought、4シグナル知識グラフ、Louvainコミュニティ検出、グラフインサイト）を取り込み、**知的障害のある本人の人生に伴走する暗黙知を、トライアンドエラーの記録ごと形式知化する**ためのコンパイル型ナレッジグラフを構築・維持します。

> このVaultは、お金を残す代わりに「人格と日常のプロトコル」を残すための装置です。多額の財産が逆に本人を危険に晒すという認識のもと、障害年金・生活保護・成年後見・地域生活支援といった公的システムをベースに、お金をかけずに本人がQOL高く生きるための知識を、支援者の交代を超えて引き継ぐことを目的とします。

> **重要**: 本ファイルは`purpose.md`と一体で機能します。すべての操作前に`purpose.md`を読み、特に§3-0「本人と他者の決定権は、それぞれの主体に帰属し続け、互いに尊重される」根本原則を確認してください。purpose.mdが「なぜ存在するか」を、本ファイルが「どう動くか」を定めます。

> **配置に関する注記**: 本Vaultは`~/Obsidian/`直下に配置された独立Vaultです。`~/Obsidian/data-wiki/`（法令・制度の業務知識）、`~/Obsidian/my-knowledge/`（内省・思考実験）、`~/Obsidian/my-research/`（外部論文・調査基地）等と並列の独立した運用体系を持ちます。機微情報（性・触法・行動障害等）を扱うため、git管理・バックアップ・アクセス制御の単位を他Vaultから独立させる設計上の判断です。

---

## §0 設計哲学（このVaultが他と異なる理由）

### 0-0 双方向の決定権の尊重（根本原則）

本Vaultは`purpose.md` §3-0の根本原則を起点とする。

**第一の柱**: 本人がいかなる状態にあっても、本人に関することについては本人に決める権利がある。Vaultは意思決定支援の素材であって、意思決定の代替ではない。

**第二の柱**: 本人と関わるすべての人にも、本人と同じように、自分に関することを自分で決める権利がある。本人がこの相互性を理解できるよう支援者が模索することは、特に**性・対人関係**の領域で本人の人生に決定的な影響を与える。

二つの柱は対立するものではなく、一つの原則の二側面である。本Vaultのすべての記述・運用・判断は、この双方向性を起点とする。

### 0-1 暗黙知こそが最大の資産である

親が日々の生活で蓄積してきた「この子はこうすると落ち着く」「この支援者とは相性が良い」といった経験知は、医療カルテにも福祉計画書にも書かれません。しかし**これがなくなった瞬間、本人の生活の質は崩壊します**。このVaultは、その暗黙知を本人が言語化できるかどうかに関わらず、観察者の言葉で記録する場所です。

### 0-2 失敗の記録は成功の記録より価値が高い

「入浴を無理強いしたら3日尾を引いた」「この職員とは合わなかった」といった失敗事例は、次の支援者にとって最も貴重な情報です。このVaultでは**Trial記録（試行錯誤の記録）をentityやconceptと同等の一級市民として扱います**。失敗を恥として隠すのではなく、知的資産として明示的に蓄積します。

### 0-3 「正解」を書こうとしない

本人の状態は変化します。10年前に有効だった対応が今は通用しないことも多い。このVaultのページは**「現時点での仮説」**として書かれ、新しい経験で更新され続けることを前提とします。`status: stale`への遷移は失敗ではなく、知識が更新された証です。

### 0-4 性・行動障害・触法を双方向性のもとで扱う

これまでの支援現場では「触れにくい話題」として封印されてきた領域こそ、親なき後に本人を最も傷つけるリスクが集中する場所です。このVaultでは以下の双方向性のもとに正面から記録します（§7参照）。

- **本人の側**: 性的主体としての権利、被害を防ぐための境界線・支援要請経路、行動障害の引き金となる感覚過敏
- **他者との関係の側**: 本人が他者の同意・拒否・身体・空間を尊重できる主体として育つ過程、機能した関わり方・視覚支援・SST的アプローチ、特定場面での対応プロトコル

加害予防は本人を「危険な存在」として扱うことではなく、本人が他者と豊かな関係を築ける主体として育つことへの伴走です。

### 0-5 「模索」の記録こそが中核的価値

§0-0第二の柱が問う「本人に他者の決定権をどう理解してもらうか」には、確立された方法論が存在しません。本人の認知特性・コミュニケーション様式・過去の経験に応じて、現場の支援者一人ひとりが試行錯誤の中で見つけていくしかない領域です。だからこそ、その**模索の過程**をTrial記録およびProtocol記録として継続的に蓄積することが、本Vaultの中核的価値となります。

### 0-6 Neo4j支援DBとの相補関係

`neo4j-agno-agent`（親なき後支援DB、port 7474/7687）が「行政が要求する構造化情報（受給者証・医療情報・支援計画）」を担うのに対し、このVaultは「行政書類には書けない人格と日常」を担います。両者は**Person.id（または匿名化ID）をキーとして相互参照**します（§9参照）。

### 0-7 リンクから自然に立ち現れる構造を尊重する

事前に定義したカテゴリは出発点に過ぎません。`~/Dev-Work/llm_wiki`のLouvainコミュニティ検出が示すように、**ページ間のリンクトポロジーから自然に立ち現れるクラスタ**こそ、親が無意識に守ってきた支援パターンの正体である可能性があります。Schemaに縛られず、グラフ構造から知識領域を発見することを許容します。

---

## §1 Vault構造

```
~/Obsidian/oya-inai-wiki/
├── CLAUDE.md                 ← 本ファイル（操作マニュアル）
├── purpose.md                ← Wikiの魂。なぜこのVaultが存在するか
├── schema.md                 ← 構造ルール（人物・ページ型・命名規約）
├── index.md                  ← 全ページカタログ（ingest毎に自動更新）
├── log.md                    ← 操作ログ（append-only）
├── overview.md               ← 俯瞰ダッシュボード
├── docs/                     ← watchlist（制度ウォッチ台帳）・導入手順
├── raw/                      ← 生ソース（append-only — 内容の書き換え・削除は絶対禁止）
│   │                            振り分けは AI が提案し、無応答なら AI の判断で行う（黙認方式・§2-1）
│   ├── 10_本人・家族から/    ← 聴き取りメモ・本人の作品・家族提供の資料
│   ├── 20_会議/              ← サービス担当者会議・支援者会議の記録と配布資料
│   ├── 30_事業所から/        ← GH・日中活動等の支援記録・ヒヤリハット（事業所ごとにサブフォルダ可）
│   ├── 40_後見・法律から/    ← 成年後見人の報告・審判書・契約書
│   ├── 50_医療から/          ← 診断書・処方・意見書
│   ├── 60_行政・制度/        ← 受給者証・手帳・年金・行政通知・制度資料（制度ウォッチの保存先）
│   ├── 70_自分の作成物/      ← サービス等利用計画・モニタリング報告の提出版（原本）
│   └── 90_assets/            ← その他バイナリ・写真動画
├── wiki/                     ← LLM生成ページ（編集対象）
│   ├── persons/              ← 本人・家族・支援者の人物ページ（中心）
│   ├── plans/                ← サービス等利用計画（要点と判断の過程）
│   ├── monitorings/          ← モニタリング記録（鮮度更新の定期便）
│   ├── meetings/             ← サービス担当者会議・支援者会議の回記
│   ├── trials/               ← トライアンドエラー記録（一級市民）
│   ├── protocols/            ← 日常運用プロトコル（朝・食事・入浴・睡眠・他者の決定権を学ぶ過程・等）
│   ├── triggers/             ← Joy/Distress triggers（喜びと苦痛の引き金）
│   ├── concepts/             ← 福祉概念・行動概念・感覚特性
│   ├── entities/             ← 事業所・行政窓口・医療機関・社会資源
│   ├── ecomaps/              ← 支援ネットワーク図（現況・移行先候補）
│   ├── sensitive/            ← 性・触法・行動障害（§7のアクセス制御対象）
│   ├── public-systems/       ← 障害年金・生活保護・成年後見等の公的システム
│   ├── procedures/           ← 申請手続き・緊急時対応フロー
│   ├── queries/              ← queryモードで保存した分析・回答
│   └── reviews/              ← 人間判断待ち項目(§5レビューシステム)
├── templates/                ← 各ページ型の雛形
└── .obsidian/                ← Obsidian設定
```

### 受付箱（Vault の外）

Vault の**外**に受付箱を1つ置く。既定は `~/Desktop/受付箱`（別の場所に置く場合はデスクトップにショートカットを1つ）。

- 使い手は、聞き取り資料・提供資料・様式の写しを**受付箱に置くだけ**。ここが原本の唯一の入口である
- AI は受付箱を読み、§3-1 Step 0 の宣言に従って**原本を `raw/` の該当する棚へ移動**する。コピーではなく移動なので、受付箱は処理が済めば空になる
- **受付箱を `raw/` の下や Vault の中に作らない。**`raw/` は追記専用（§2-1）で、入った時点で取り消せない。受付箱を外に置くことで、置き間違いを記録前に取り消せる境界が生まれる
- **削除という操作を運用に含めない。**受付箱は「中身が棚へ移ることで空になる」
- filesystem MCP に見せるフォルダは **Vault ／ スキルの置き場所 ／ 受付箱** の3つ（docs/導入手順.md Step 1）

> **重要**：このCLAUDE.mdが配置された時点では、上記ディレクトリは未作成です。作者と相談しながら段階的に作成します。一度に全部作らない。

---

## §2 絶対遵守のガードレール

1. **`raw/`は追記専用（append-only）。** 既存ファイルの**内容の書き換え・削除は禁止**（生ソースを失うと取り返せない）。新規ファイルの受け入れ保存と、棚の間違いの**振り分け直し（内容無変更の移動）**は、AI が振り分け先を**宣言**し（質問しない）、訂正がなければそのまま実行してよい（黙認方式）。迷っても「未分類」を作らず最有力の棚に置き、判断根拠を log.md に残す。すべての振り分け・移動を log.md に記録する（raw/ は git 管理外のため log が唯一の履歴）。frontmatter の `provided_by` は保存先の棚から推定して付与し、`share_scope` は明示がなければ `consent-required`。**インテーク時に使い手へ尋ねるのは、どうしても必要な場合でも1点まで。**
2. **`wiki/`への書き込み前に必ず作者の承認を得る。** 承認なしの書き込みは禁止。
3. **個人情報の取り扱いは§7のSensitivity Levelに従う。** 実名・住所・電話番号等は`raw/`に留め、`wiki/`では匿名化IDで参照する。
4. **5ページ以上の同時変更は事前に一覧提示。** 一括書き込み禁止。
5. **矛盾するソースは両論併記 + `> [!warning]`コールアウト。** 勝手に正誤判断しない。本人の状態は変化するため、過去の記録と現在の記録の矛盾は「変化の証拠」として保存する。
6. **大量更新時はバックアップ。** 影響範囲を`wiki.backup_YYYYMMDD/`にコピーしてから実行。
7. **削除は禁止。** 不要ページは`status: stale`に変更し、移動を提案する。失敗の記録こそ将来の財産。
8. **本人の尊厳を損なう表現の禁止。** 「問題行動」「困った子」「手のかかる」等の評価的表現は使わない。代わりに「◯◯のときに××する傾向がある」と事実ベースで記述する。
9. **性・触法に関する記述は§7のプロトコルに従う。** 興味本位の詳細記述は禁止。「本人を守るため」「本人が他者を尊重できるよう支援するため」の情報のみ記録する。
10. **Neo4j支援DBとの整合性。** Person IDが食い違う変更は事前に作者に報告する。
11. **本人の自己決定権を他者の決定権を侵す根拠にしてはならない。** 「本人がそうしたいと言っているから」は、相手が嫌がっている行為（身体接触・追跡・関係の強要等）を正当化しない。purpose.md A-6を直接反映する。
12. **本人を「加害リスクのあるケース」として分類してはならない。** リスクスコアリング・脅威としての記述は禁止。記述は常に本人の成長と他者との関係構築を支える方向を向く。purpose.md A-9を直接反映する。

---

## §3 4つの動作モード

### 3-1 ingest（取り込み）— 2段階Chain-of-Thought

受付箱のファイル・自然な会話・添付ファイル・`raw/`に配置済みのソースを、Wikiに統合する。

**Step 0: 振り分け宣言（インテーク）**

**まず受付箱（§1）を見る。**受付箱にファイルがあれば、あるいは会話や添付でソースが到着したら、保存先を**宣言して**（「事業所からの支援記録として `raw/30_事業所から/GH○○/` に保存します」）raw/ へ保存する。訂正があれば従い、なければそのまま進む（§2-1 黙認方式）。棚から `provided_by` を推定し、`share_scope` は明示がなければ `consent-required`。振り分けを log.md に1行記録。受付箱から取り込む場合はコピーではなく**移動**する（原本を1つに保ち、受付箱を空に戻すため）。

**Step 1: Analysis（分析）**

1. ソースを精読し、`purpose.md`をコンテキストとして読み込む（特に§3-0双方向性原則を確認）
2. 既存`index.md`と突き合わせて以下を抽出：
   - 言及されている人物（本人・家族・支援者・関わる他者）
   - 試行された対応とその結果（成功・失敗の両方）
   - 言及された概念・引き金・プロトコル
   - **本人が他者の決定権を学ぶ過程に関する記述**（特に対人関係・性に関する場面）
   - 既存ページとの接続点
   - 既存ページとの矛盾・緊張関係
   - Sensitivity Level判定（§7）
3. 統合計画（作成/更新/矛盾の一覧、Sensitivity Level別の分類）を作者に提示
4. **「Obsidianに保存してよいですか？」で明示的承認を得る**

**Step 2: Generation（生成）**

5. 承認後、`templates/`を元にページ生成・既存ページ追記
6. 生成時にcross-reference（`[[wikilink]]`）を埋め込む
7. `index.md`、`log.md`、`overview.md`を更新
8. 人間判断が必要な項目は`wiki/reviews/`に積む（§5）
9. 完了サマリー（作成N件・更新N件・矛盾フラグN件・レビュー項目N件）を報告

### 3-2 query（照会）

Wiki内を横断検索して質問に回答する。

1. `purpose.md`と`index.md`を読み、関連ページを特定
2. 関連ページを精読して回答を合成（`[[...]]`で引用）
3. **回答が価値ある場合**、「この回答を`wiki/queries/`に保存しますか？」と確認
4. 保存時は`templates/query.md`を雛形に使用し、後のingestで他ページから参照可能にする

### 3-3 lint（健全性チェック）

定期的にWikiの健全性を点検する。

**必ず最初に `scripts/okf_lint.py` を実行する。** 目視や記憶による点検から始めてはならない。

```bash
cd ~/Obsidian/oya-inai-wiki && python3 scripts/okf_lint.py
```

依存パッケージなし（Python3標準ライブラリのみ）。終了コードは `0`=違反なし / `1`=WARNのみ / `2`=ERROR（機微情報の漏出リスク）。

| オプション | 用途 |
|------------|------|
| （なし） | 全チェック＋内訳＋配布可能件数 |
| `--gate` | 機微ゲートのみ。CI・pre-commit 用 |
| `--allowlist` | 外部配布可能ファイルの一覧を標準出力へ |

**スクリプトが機械的に検証する項目**（schema.md §1〜§5 に対応）：

- 必須フロントマター7項目（`type` / `created` / `updated` / `sources` / `tags` / `status` / `sensitivity`）の欠損
- `type` / `status` / `sensitivity` の値が定義域内にあるか
- `type` と配置ディレクトリの一致（schema.md §5）
- **機微ゲート**（本スクリプトの中核。§7 を実行可能にしたもの）
  - 個人に紐づく型（`person` / `trial` / `protocol` / `trigger` / `ecomap` / `sensitive` / `plan` / `monitoring` / `meeting`）が `sensitivity: public` を名乗っていないか
  - 相談支援の中核文書3型（`plan` / `monitoring` / `meeting`）の sensitive 強制・日付必須（planned_on / monitored_on / held_on）・person_id(s) 必須
  - `provided_by` / `share_scope` の語彙（出所と宛先。schema.md §1・§7）。**`share_scope: origin-only` のページは sensitivity によらず allowlist から無条件除外**
  - `person_id` を持つページが `public` になっていないか
  - `restricted` が `wiki/sensitive/restricted/` 配下にあるか
  - `sensitive` 以上に `sensitive_purpose` が明記されているか
  - 本文への PII 混入（携帯番号・生年月日・手帳番号・受給者証番号・住居表示）
- `public-system` の `last_updated_law` 欠損（法改正追従用）
- **鮮度**（schema.md §6。証拠・鮮度モデル）
  - 現在の状態を主張する型（`person` / `protocol` / `trigger` / `sensitive` / `ecomap`、`status: active|review`）の `last_confirmed`（最終確認日）の欠落
  - 型別の目安超過（person・protocol: 90日 / trigger・sensitive: 180日 / ecomap: 30日）
  - `confirmed_by` の未定義値（記録のみ / 本人に確認 / 家族に確認 / 支援者に確認 / 実地で確認）
  - ※ 旧フィールド `last_validated` は `last_confirmed` の同義として受理。出来事の記録（trial / plan / monitoring / meeting / query）は対象外。public-system は `verified_on` 365日超で WARN（制度ウォッチの点検漏れ検知）

**鮮度 WARN の扱い**：鮮度は WARN であって ERROR ではない。`--gate` は ERROR の有無だけを終了コードに返すため、**鮮度切れで pre-commit・起動時ゲートは止まらない**。[鮮度] WARN を見つけたら作者に平易に伝え（「P_001 の入浴プロトコル、最終確認が4ヶ月前です。今も機能していますか？」）、**作者が確かめたと答えた場合にのみ** `last_confirmed` と `confirmed_by` を更新する。尋ねずに勝手に更新してはならない——確認していないものを確認済みにするのは、この仕組み全体への裏切りである。Trial を記録した際は、既存 protocol・trigger への `confirms` / `contradicts` を作者に尋ねて記入し、success で protocol 通りなら指し先の `last_confirmed` を試行日に更新することを提案する（schema.md §2-2・§6-3）。**monitoring を記録した際は必ず**「今回のモニタリングで確認できた記録はどれですか」と尋ね、`confirms` に挙がったページの `last_confirmed` を `monitored_on` に更新することを提案する——モニタリングは鮮度更新の定期便である。

**外部配布ゲート**：`--allowlist` が返すのは `sensitivity: public` かつ `status: active|review` のページのみ。ERROR が1件でも出たページは無条件で除外される（fail-closed）。LightRAG feed への投入・法人サイトへの転載・職員への配布は、**この一覧の範囲を超えてはならない**。

**スクリプトが検証しない項目**（Claude が読解で点検する）：

- 孤立ページ（インバウンドリンクなし）
- 矛盾フラグ（`> [!warning]`）の未解消一覧
- `status: stale`の放置ページ
- **疎なコミュニティ**（凝集度低・要追加調査）
- **ブリッジノード**（複数領域を結ぶ重要ノード）
- **Trialページの分布偏り**（成功記録ばかり、失敗記録ばかり）
- **`decision-rights-learning`サブドメインのTrial蓄積状況**（半年以上記録なしは要注意。purpose.md G-8の達成度指標）
- **加害リスク分類的記述の混入**（A-9違反の検出）
- ※ 旧項目「3ヶ月以上更新されていないPersonページ」「性関連ページの最終レビュー日」は、`last_confirmed` の鮮度検査として機械化済み（2026-08-09）

> スクリプトが `0` を返しても、上記の読解項目は別途点検すること。逆に、スクリプトが `2` を返した場合は読解に進む前にまず ERROR を解消する。

### 3-4 graph-insight（グラフ洞察）— 発展機能

`~/Dev-Work/llm_wiki`の機能を活用する場合、または`scripts/`で実装する場合：

- **意外なつながりの検出**：コミュニティをまたぐエッジ、タイプをまたぐリンク
- **知識のギャップ検出**：孤立Personページ、疎な支援ネットワーク
- **Louvainコミュニティ検出**：事前定義カテゴリと独立に、リンクから自然に立ち現れる支援パターンを発見

---

## §4 ページフォーマット

### 4-1 共通フロントマター（全ページ必須）

```yaml
---
type: person | plan | monitoring | meeting | trial | protocol | trigger | concept | entity | ecomap | sensitive | public-system | procedure | query | review
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
sensitivity: public | internal | sensitive | restricted   # §7参照
person_id: "P_001"   # 匿名化ID（Neo4j支援DBと共有）。該当しないページは省略
last_confirmed: YYYY-MM-DD   # まだ正しいと確かめた日（schema.md §6）
confirmed_by: 記録のみ | 本人に確認 | 家族に確認 | 支援者に確認 | 実地で確認
provided_by: 本人 | 家族 | 事業所 | 後見人 | 医療機関 | 行政 | 会議 | 相談支援   # 出所（AI が棚から推定）
share_scope: team | consent-required | origin-only   # 宛先境界。欠落時は consent-required 扱い
---
```

> 正式な定義（型別の追加フィールド・鮮度・命名・配置）は schema.md。本節は抜粋である。

### 4-2 type別の追加フィールド

#### type: person（人物ページ — 中心）
```yaml
person_role: principal | family | supporter | professional   # 本人 / 家族 / 支援者 / 専門職
date_of_birth: YYYY-MM   # 月までで十分。日は省略可
diagnosis_summary: "知的障害（療育手帳B1）、ASD"   # 詳細は raw/medical/ に
current_living: "GH ○○寮"
```

本文構造：
- `## 人格の核`（性格・好み・嫌い・こだわり）
- `## ライフストーリー`（時系列）
- `## 現在の生活`（一日の流れ）
- `## Joy Triggers`（→`[[triggers/joy/...]]`へのリンク集）
- `## Distress Triggers`（→`[[triggers/distress/...]]`へのリンク集）
- `## 支援ネットワーク`（→`[[ecomaps/...]]`）
- `## 試行錯誤の記録`（→`[[trials/...]]`へのリンク集）
- `## 他者との関係を築く過程`（→`[[trials/decision-rights-learning/...]]`、`[[protocols/others-rights-learning/...]]`へのリンク集。本人が他者の同意・拒否・身体・空間を尊重できる主体として育つ過程の記録）

#### type: plan / monitoring / meeting（相談支援の中核文書 — schema.md §2-1b〜2-1d）

3型とも**出来事の記録**（日付必須・sensitive 以上必須・person_id(s) 必須・鮮度検査対象外）。様式の写しは raw/70_自分の作成物/（会議資料は raw/20_会議/）に置き、Wiki には要点と**様式に書けない判断の過程**を残す。monitoring の `confirms` / `contradicts` は個人系ページの `last_confirmed` を更新する定期便として機能する。雛形は `templates/plan.md` / `templates/monitoring.md` / `templates/meeting.md`。

#### type: trial（試行錯誤記録 — 一級市民）
```yaml
trial_outcome: success | partial | failure | inconclusive
trial_subdomain: daily-life | decision-rights-learning | crisis-response | medical | sexuality | other
   # daily-life: 生活全般のトライアンドエラー（食事・入浴・睡眠等）
   # decision-rights-learning: 本人が他者の決定権を学ぶ過程の試行錯誤（purpose.md §3-0第二の柱）
   # crisis-response: パニック・体調急変等の緊急時対応
   # medical: 医療機関受診・服薬等
   # sexuality: 性に関する事象（sensitivityがsensitive以上の場合はsensitiveカテゴリへも併載）
trial_date: YYYY-MM-DD
person_id: "P_001"
context: "入浴拒否時の対応"
```

本文構造：
- `## 状況`（何が起きていたか）
- `## 試したこと`（具体的な対応）
- `## 結果`（事実ベースで）
- `## 学び`（次に同じ状況になったらどうするか — 仮説として）
- `## 関連する後続Trial`（→他のTrialへのリンク）

> **重要**：失敗Trialこそ詳細に記録する。「なぜダメだったか」が次の支援者を救う。
>
> **decision-rights-learningサブドメインの特則**: このサブドメインのTrialは、本人を「加害リスクのある対象」として記述するのではなく、本人が他者と豊かな関係を築ける主体として育つ過程として記述する。「今日、本人が店員さんに無理に話しかけようとしたが、私が『今は他のお客さんを見ている時だから、終わったらね』と言ったら待てた」のような小さな成功も、「相手が嫌がっているサインを今日は読み取れなかった。次回は事前に絵カードで距離を伝える方法を試したい」のような失敗も、ともに模索の記録として等しく価値を持つ。

#### type: protocol（日常運用プロトコル）
```yaml
protocol_domain: morning | meal | bath | sleep | outing | medical | private-time | others-rights-learning | wiki-explanation
   # others-rights-learning: 本人が他者の決定権を理解し尊重できるよう支援する継続的プロトコル
   # wiki-explanation: 本人にWikiの存在・目的・参加機会を説明する定期的プロトコル
person_id: "P_001"
last_validated: YYYY-MM-DD   # 最後にこのプロトコルが有効と確認された日
```

> **others-rights-learningプロトコルの記述要点**: 本人の認知特性・コミュニケーション様式に応じた具体的な関わり方を記述する。視覚支援・SST的アプローチ・場面ごとの絵カード・断られた経験の処理方法等。本人を矯正する手順ではなく、本人と支援者が共に学ぶ過程として書く。

#### type: trigger（喜び・苦痛の引き金）
```yaml
trigger_type: joy | distress
trigger_modality: visual | auditory | tactile | olfactory | gustatory | social | cognitive
intensity: low | medium | high
person_id: "P_001"
```

#### type: ecomap（支援ネットワーク図）
```yaml
ecomap_purpose: current | handover | crisis | meeting   # 現況 / 引き継ぎ用 / 緊急時 / 支援会議用
person_id: "P_001"
mermaid_or_svg: "mermaid"   # 既存ecomap-generatorスキル連携
```

#### type: sensitive（§7のアクセス制御対象）
```yaml
sensitivity: sensitive | restricted
sensitive_domain: sexuality | criminal-risk-prevention | severe-behavior | trauma | others-rights-learning-difficulty
   # sexuality: 性に関する記録（双方向性で扱う。§7-3）
   # criminal-risk-prevention: 触法行為予防（本人を加害者にしない伴走の記録）
   # severe-behavior: 行動障害の詳細
   # trauma: 過去のトラウマ
   # others-rights-learning-difficulty: 本人が他者の決定権を理解する過程で生じた深刻な困難（性・対人で他者を傷つけるおそれが現実化した場面等）
sensitive_purpose: "このページが何のために記録されているかを明記。例: 本人を被害から守るため/本人が他者を尊重できるよう伴走するため/法的論点の整理のため"
access_note: "本人を支援する立場にある者のみ閲覧"
```

#### type: entity（事業所・行政窓口・社会資源）
```yaml
entity_category: facility | government | medical | legal | community
contact_info_ref: "raw/legal/contacts.md"   # 連絡先は raw/ に
```

#### type: concept（福祉概念・行動概念）
```yaml
concept_category: welfare-law | sensory | behavioral | developmental | sexuality | decision-rights
   # decision-rights: 自己決定権・他者の決定権・相互尊重に関する概念
```

#### type: public-system（公的システム）
```yaml
system_category: pension | welfare | guardianship | regional-support
last_updated_law: YYYY-MM-DD   # 法改正への追従用
```

---

## §5 レビューシステム（非同期Human-in-the-Loop）

`~/Dev-Work/llm_wiki`のレビューシステムを参考に、ingest中に人間判断が必要な項目を`wiki/reviews/`に積む。

### 5-1 レビュー項目の発生条件

- 本人の状態に関する重要な変化（医学的にも生活的にも）
- 既存記録と矛盾する情報
- Sensitivity Level判定が曖昧な情報
- 加害・被害が疑われる記述
- 触法行為に関する記述
- **本人が他者の決定権を理解する過程で生じた深刻な困難**（特に性・対人関係で他者を傷つけるおそれが現実化した場面）
- 親御さんの感情的な内容（記録すべきか、本人に渡るべきか判断要）
- 法律相談が必要そうな論点（専門職への相談を促す文脈で）
- **制度改正の検知**（制度ウォッチ。docs/watchlist.md の監視対象に変更があった場合）
- **振り分けの判断根拠に自信がない場合**（黙認方式で保存したが確認してほしいもの）
- **A-9違反の疑い**（本人を加害リスクのあるケースとして分類するような記述の混入）

### 5-2 レビュー項目のアクションタイプ

事前定義された4つのみ（LLMが勝手にアクションを発明しない）：

- `Create Page`：新規ページ化する
- `Update Existing`：既存ページに追記する
- `Defer`：保留（理由を記述）
- `Discard`：記録しない（理由を必須記述、§2の削除禁止の例外として`reviews/discarded/`に移動して履歴は残す）

### 5-3 レビュー項目の構造

```yaml
---
type: review
created: YYYY-MM-DD
priority: low | medium | high | urgent
proposed_action: Create Page | Update Existing | Defer | Discard
source: "[[raw/...]]"
context: "..."
---
```

---

## §6 4シグナル関連性モデル（グラフ拡張時）

`~/Dev-Work/llm_wiki`デスクトップアプリでこのVaultを開く場合、または独自スクリプトで実装する場合、以下の4シグナルでページ間関連性を計算する。

| シグナル | 重み | 説明 |
|----------|------|------|
| Direct link | ×3.0 | `[[wikilink]]`で直接リンクされたページ |
| Source overlap | ×4.0 | 同一の`raw/`ソースを共有するページ |
| Adamic-Adar | ×1.5 | 共通の隣接ノードを共有するページ |
| Type affinity | ×1.0 | 同一ページタイプ間のボーナス |

**特に重要なシグナル**：
- Source overlap：同じインタビュー記録から複数のTrialやTriggerが派生した場合、それらは強く関連する
- Type affinity：Personノード同士、Trialノード同士の関連を強める
- **decision-rights-learningサブドメインのTrialとothers-rights-learningプロトコルの関連性**: 同一Personに紐づくこれら両者は、模索の経時的記録として強く接続される

---

## §7 Sensitivity Level — アクセス制御と尊厳保護

### 7-1 4段階のSensitivity Level

| Level | 内容 | 例 | 配置 |
|-------|------|------|------|
| `public` | 一般的な情報 | 公的制度の解説、福祉概念 | `wiki/concepts/`, `wiki/public-systems/` |
| `internal` | 支援に必要だが本人特定可能 | 日常プロトコル、Joy Triggers、others-rights-learningプロトコル | `wiki/protocols/`, `wiki/triggers/` |
| `sensitive` | 慎重な扱いが必要 | 性に関する基礎情報、行動障害の詳細、過去のトラウマ、本人が他者の決定権を学ぶ過程の困難場面 | `wiki/sensitive/` |
| `restricted` | 極めて慎重な扱いが必要 | 性被害・性加害が現実化した具体記録、触法行為の記録、医療上の機微情報 | `wiki/sensitive/restricted/` |

### 7-2 Sensitive領域の記述原則（双方向性のもとで）

性・行動障害・触法に関するページを書く際は、purpose.md §3-0双方向性原則のもと、以下を遵守：

1. **目的の明示**：冒頭に「このページは○○のために記録する」を必ず書く。具体的には次の三つのいずれか（または複数）を明記する。
   - 本人を被害から守るため
   - 本人が他者を尊重できる主体として育つ過程に伴走するため
   - 法的論点の整理のため

2. **本人を主体とした記述**：「Aさんは○○された」ではなく「Aさんに○○が起きた」「Aさんが○○の状況にあった」と記述。被害者性も加害者性も固定化しない。

3. **加害・被害の二項対立を避ける**：知的障害のある方は、加害者にも被害者にもなり得る。両方向のリスクを併記する。同時に、本人を「加害リスクのある存在」として分類することは禁ずる（A-9）。記述は常に本人の成長と他者との関係構築を支える方向を向く。

4. **記録の更新権限**：これらのページの大幅な更新は、作者の明示的指示なしに行わない。

5. **後の支援者向けメッセージの併記**：「この記録を読む支援者へ」セクションを設け、本人の尊厳を守る関わり方と、本人が他者の決定権を理解できるよう支援する関わり方の両方を記述する。

6. **法的論点との接続**：刑法・民法上の論点が絡む場合は、`[[wiki/concepts/legal/...]]`へリンクして概念を整理し、**個別の法的判断は弁護士等の専門職への相談につなぐ**。特に同意の概念、性的同意年齢、責任能力、合理的配慮の双方向性については丁寧に整理する。

7. **「模索」の明示**：他者の決定権を本人が理解する過程に確立された方法論はないことを記述に明記する。今この記述は仮説であり、運用しながら更新されることを明記する。

### 7-3 性に関する記述の特則(双方向性版)

性に関する記述は、purpose.md §3-0双方向性原則の最も切実に問われる領域である。以下の双柱で書く。

**第一の柱：本人の側（被害から守る視点）**
- 医学用語ではなく日常語で書く（ただし誤解を招かない範囲で）
- 「自慰」「精通」「初潮」等の事実は明記してよいが、観察的・尊厳的に
- 過去の被害記録は事実のみ。詳細は`raw/`に留め、`wiki/`では支援上必要な範囲のみ
- 本人の境界線、嫌がるサイン、安心できる空間・関わり方
- 性的主体としての権利（恋愛・結婚・性行為・子を持つこと）を否定する記述を書かない
- 被害が起きた場合の支援要請経路（ワンストップ支援センター、基幹相談支援センター、警察障害者支援担当、産婦人科で障害者対応に理解のある医師、弁護士会人権擁護委員会等）

**第二の柱：他者との関係の側（本人が他者を尊重する主体として育つ伴走）**
- 加害リスクは「予防の観点」で記述する。ただし本人を「加害リスクのある対象」として分類しない（A-9）。
- 本人が「相手の同意」「相手の拒否」「相手の身体は相手のもの」を理解する過程の試行錯誤を、`decision-rights-learning`サブドメインのTrialとして蓄積する
- 機能した関わり方・絵カード・動画を使った視覚支援・SST的アプローチ・特定場面（電車内・コンビニ・公園等）での具体的対応プロトコル
- 本人が断られる経験を安全に積める機会の設計
- 本人が自分自身の「嫌だ」を表現できるようになる過程（これが他者の「嫌だ」を理解する基盤になる可能性）
- 責任能力論議は予防文脈で扱う。事件発生時の弁護方針論議は`raw/legal/`に留める

**両柱共通の原則**
- 本人の前で読み上げて恥ずかしい記述は書かない
- 興味本位の詳細記述は禁止
- すべての記述は仮説であり、本人の状態と支援者の試行錯誤の進展で更新される

---

## §8 命名規約

| 要素 | 接頭辞 | 例 | 備考 |
|------|--------|-----|------|
| Person | `P_` | `P_001_仮名.md` | IDはNeo4j支援DBと共有。**実名は使わず仮名で**（実名はraw/のみ） |
| Plan | `PL_` | `PL_2026-04-01_P_001.md` | 交付日込み |
| Monitoring | `MO_` | `MO_2026-07-01_P_001.md` | 実施日込み |
| Meeting | `MT_` | `MT_2026-07-15_サービス担当者会議_P_001.md` | 開催日・種別込み |
| Trial（生活全般） | `T_` | `T_2026-04-15_入浴拒否対応.md` | 日付込みで時系列追跡 |
| Trial（他者の決定権学習） | `TD_` | `TD_2026-04-15_コンビニ店員との距離_P_001.md` | decision-rights-learningサブドメイン専用接頭辞 |
| Protocol | `PR_` | `PR_morning_routine_P_001.md` | Person IDに紐付け |
| Protocol（他者の決定権学習） | `PRD_` | `PRD_others-rights-learning_P_001.md` | others-rights-learningプロトコル専用接頭辞 |
| Protocol（Wiki説明） | `PRW_` | `PRW_wiki-explanation_P_001.md` | 本人にWikiを説明する定期プロトコル |
| Trigger | `TG_` | `TG_joy_blue-towel_P_001.md` | Joy/Distress明示 |
| Ecomap | `EM_` | `EM_current_P_001_2026-04.md` | 月単位スナップショット |
| Concept | `C_` | `C_感覚過敏.md` | Person非依存 |
| Concept（決定権関連） | `CD_` | `CD_他者の決定権の相互尊重.md` | decision-rightsカテゴリ専用 |
| Entity | `E_` | `E_GH木町家.md` | 実在組織は実名可（公開情報） |
| Sensitive | `SE_` | `SE_性的主体としての権利_P_001.md` | アクセス制御対象 |
| Sensitive（決定権学習困難） | `SED_` | `SED_対人関係困難場面_P_001.md` | others-rights-learning-difficulty専用 |
| Public System | `PS_` | `PS_障害年金.md` | 制度横断 |
| Procedure | `PC_` | `PC_緊急時連絡フロー_P_001.md` | 手続きフロー |
| Query | `Q_` | `Q_2026-04-15_GH移行のタイミング.md` | 日付+問い |
| Review | `R_` | `R_2026-04-15_001.md` | 連番 |

---

## §9 他Vault・Neo4j支援DBとの連携

### 9-1 役割分担

| 領域 | 担当 | 配置 |
|------|------|------|
| 構造化情報（受給者証・診断・支援計画） | Neo4j支援DB | `neo4j-agno-agent`コンテナ |
| 関係性のグラフクエリ（誰が誰を支援しているか） | Neo4j支援DB | 同上 |
| 暗黙知・経験知・感覚的記述 | oya-inai-wiki（本Vault） | `~/Obsidian/oya-inai-wiki/` |
| トライアンドエラーのナラティブ（生活全般） | oya-inai-wiki（本Vault） | 同上 |
| 他者の決定権を本人が理解する過程の模索記録 | oya-inai-wiki（本Vault） | 同上 |
| 計画・モニタリング・会議録の一次記録（判断過程含む） | oya-inai-wiki（本Vault） | 同上 |
| 制度改正の監視（制度ウォッチ→review 起票） | 制度ウォッチ＋本Vault | `docs/watchlist.md` を正典に |
| 法令・制度の業務知識 | data-wiki | `~/Obsidian/data-wiki/` |
| 内省・思考実験 | my-knowledge | `~/Obsidian/my-knowledge/` |
| 外部論文・調査基地 | my-research | `~/Obsidian/my-research/` |

### 9-2 Neo4j支援DBとの連携プロトコル

- Person IDは両システムで共有（`P_001`形式）
- Wikiの`person_id`フロントマターからNeo4jへ参照
- Neo4jのPersonノードに`wiki_path: "wiki/persons/P_001_..."`プロパティを持たせて逆引き
- 重大な変更（GH移行・診断変更等）は両方を更新。先にNeo4jを更新し、Wikiでナラティブを補完する順序

### 9-3 docker起動チェック

Neo4j参照前に必ず`docker ps --filter name=support-db-neo4j`で稼働確認。停止時は作者への許可取得不要で起動可（user preferences §3に基づく）。セッション終了時に停止。

---

## §10 既存スキルとの連携

| スキル | 用途 |
|--------|------|
| `ecomap-generator` | `wiki/ecomaps/`配下のページ生成・更新 |
| `provider-search` | `wiki/entities/`配下の事業所情報の最新化 |
| `wamnet-provider-sync` | 北九州市福祉サービス事業者の同期 |
| `inheritance-calculator` | 親なき後の財産承継シミュレーション |
| `neo4j-support-db` | 構造化データの読み書き |
| `wiki-crystallize` | 長い対話を1ページに濃縮 |
| `wiki-ingest` | `raw/`からのバッチ取り込み |
| `wiki-integrate` | 新規ページのグラフ統合 |
| `wiki-lint` | 健全性チェック（§3-3を補完） |
| `wiki-query-hybrid` | LightRAG連携のハイブリッド検索 |
| `onboarding-wizard` | Neo4j側7本柱インテークと本Vaultの対応（構造化はDB・物語はWiki） |
| `visit-prep` | 訪問前ブリーフィング（Neo4j構造情報＋本Vaultのprotocol/trigger） |
| `docx`, `pdf` | 引き継ぎ書・成年後見申立書類等の生成 |
| `html-to-pdf` | エコマップHTMLのPDF化 |

---

## §11 段階的構築のロードマップ

このCLAUDE.mdが配置された時点で、Vaultはまだ空です。作者と相談しながら以下の順で構築します。

### Phase 1: 骨格（1週間）
1. `purpose.md`を共同で起草（このVaultの魂）— **完了**
2. `schema.md`を本ファイルから抽出して独立させる
3. `templates/`に各ページ型の雛形を配置
4. パイロット対象（最初の1人）を選定

### Phase 2: パイロット（2〜4週間）
5. パイロット対象のPersonページ作成
6. その方のJoy/Distress Trigger 各5〜10件
7. 主要Protocol（朝・食事・入浴・睡眠）4〜6件
8. 過去のTrial記録 5〜10件（成功・失敗両方、**生活全般のサブドメイン**）
9. 現況Ecomap作成（既存`ecomap-generator`スキル活用）

### Phase 3: 双方向性Sensitive層導入（慎重に）
10. パイロット対象の`sensitive/`領域を作者と相談しながら少しずつ
11. **第一の柱**: 性的主体としての権利、本人を被害から守る支援、行動上の課題、必要な支援
12. **第二の柱**: 本人が他者の決定権を理解する過程に伴走するための記録（`others-rights-learning`プロトコル、`decision-rights-learning`サブドメインのTrial）
13. `wiki-explanation`プロトコル（本人にWikiを説明する定期プロセス）の設計

### Phase 4: 横展開
14. 2人目以降への展開
15. Concept・Entity・Public Systemの整備（特に`decision-rights`カテゴリの充実）
16. グラフ可視化・Louvainコミュニティ検出の活用

### Phase 5: 引き継ぎ運用
17. 親御さん・支援者からの口述記録（`raw/interviews/`）の継続的取り込み
18. 定期lintとレビュー
19. 引き継ぎパッケージ生成（特定支援者向けのエクスポート）

---

## §12 作者へのお願い

このVaultは、相談支援の実務・システム開発・福祉実践の視点が交差する場所です。AIが暴走しやすい領域でもあるため、以下を徹底します。

1. **書き込みは必ず承認を得る。** 5ファイル超は事前一覧。
2. **Sensitive領域は作者の明示的指示なしに大幅更新しない。** 特に第二の柱（他者の決定権学習）の記録は、本人を加害リスクのある存在として分類してしまう危険を内包するため、最も慎重に扱う。
3. **本人の尊厳を損なう表現を見つけたら、作者が指摘する前にClaudeから提起する。**
4. **失敗を記録することへの心理的抵抗を、作者も私も持っている。** 互いに励まし合いながら書く。
5. **このCLAUDE.md自体も生きたドキュメント。** 運用しながら気づいた点は更新する。バージョン管理は`log.md`に記録。
6. **「模索」の姿勢を保つ。** 特にdecision-rights-learning領域では、確立された方法論がないことを忘れず、現場の試行錯誤を権威化しない記述を心がける。

---

## §13 起動時の挙動

新しいセッションでこのVaultに入った際、Claudeは以下を順に実行：

1. このCLAUDE.mdを読み込む
2. `purpose.md`を読む（特に§3-0双方向性原則を確認）
3. `index.md`の冒頭を確認（存在すれば）
4. `log.md`の最新3エントリを確認（存在すれば）
5. **`python3 scripts/okf_lint.py --gate` を実行する（必須）**
   - 終了コード `2` なら、作業に入る前に ERROR を作者に報告する。機微情報の漏出リスクが未解消のまま ingest や query に進むことはしない
   - `--gate` が見るのは ERROR（機微）のみ。鮮度の WARN はここでは止めない——全チェック（lint モード）で拾い、§3-3「鮮度 WARN の扱い」に従って作者に確認を促す
   - 本Vaultは git 管理下にあり、`git config core.hooksPath githooks` で pre-commit 関所も有効化できる。ただし日常運用は commit を伴わないことが多いため、この起動時チェックを省略してはならない
6. 作者に「今日は何モードで作業しますか？（ingest / query / lint / graph-insight / セットアップ）」を尋ねる

---

## §14 ファイル操作ツールの選択原則

Mac側ファイル（このVaultを含むローカルファイル）を操作する際は、**必ず filesystem MCP ツールを使う**。Dockerコンテナ内の `bash_tool` / `str_replace` / `view` / `create_file` は Mac ファイルにアクセスできない（user preferences §1）。

### 14-1 ツール選択マトリックス

| 状況 | ツール | 補足 |
|------|------|------|
| **部分編集（数箇所の差し替え）** | `filesystem:edit_file` ★第一選択 | `oldText`/`newText` ペアを複数含められる。`dryRun: true` で diff 事前確認可 |
| **新規ファイル作成** | `filesystem:write_file` | 作成・上書き |
| **大幅な構造変更（例：セクション全体を書き換え）** | `filesystem:write_file` | やむを得ず全文書き換え |
| **ファイル全体の読み取り** | `filesystem:read_file` | 小さいファイルのみ |
| **大きいファイルの一部読み取り** | `filesystem:read_file(head=N)` / `(tail=N)` | フロントマターだけ、末尾エントリだけ等 |
| **複数ファイル同時読み取り** | `filesystem:read_multiple_files` | 状況把握・照合に便利 |
| **ディレクトリ一覧** | `filesystem:list_directory` | |
| **ディレクトリツリー** | `filesystem:directory_tree` | 階層把握 |
| **ファイル検索** | `filesystem:search_files` | パターン検索 |

### 14-2 トークン効率の原則

1. **`edit_file` を第一選択にする**。`write_file` はファイル全体の入出力でトークンを消費するため、軽微な修正には使わない。
2. **読み取りも最小限に**。`head` / `tail` / `view_range` で必要部分だけ取得する。
3. **`dryRun: true` で事前検証**。重要ファイル（CLAUDE.md ・ purpose.md ・ schema.md ・ index.md 等）を編集する際は、必ず `dryRun` で diff を確認してから本適用する。

### 14-3 edit_file の記法上の注意

- `oldText` は**ファイル内で完全一致し、単一に特定できる**文字列であること。同じ表現が複数箇所にある場合は、前後文脈を含めてユニークにする。
- 複数箇所の編集は `edits` 配列にまとめて一回で適用する（トークン効率もよい）。
- 描画上の行番号・先頭タブは含めない（表示上の装飾のため）。生の内容のみをコピーする。

### 14-4 例外ケース

- **バイナリ（docx / pdf / xlsx / png 等）**: filesystem MCP はテキスト専用のため、バイナリの Mac への保存は作者が手動でダウンロードリンクを経由して貼り付ける。Claude 側では `/mnt/user-data/outputs/` に生成し `present_files` で提示する。
- **ダウンロードしたバイナリを raw/ に配置後、内容を wiki に取り込む場合**: バイナリ自体は filesystem MCP で読めないため、Claude が生成したドキュメントの内容を記憶している限りそれをソースとする。記憶にない場合は作者にテキスト抽出済みファイルを並置してもらうよう依頼する。

---

*このVaultは、お金では買えないものを残すための装置です。本人がこの世界で笑顔でいられる時間を、一秒でも長く確保するために。そして本人が他者と豊かな関係を築ける主体として育つことに、現場の支援者一人ひとりの模索が伴走できるように。*

*作成日: 2026-04-28*
*最終更新: 2026-08-09（相談支援専門員モデルへ再設計：一人称の宣言・raw/ 提供主体別8棚と黙認方式・plan / monitoring / meeting の3型・provided_by / share_scope・制度ウォッチ。同日、鮮度検査（証拠・鮮度モデル）も導入。経緯は docs/ の要件書・技術仕様・ADR と log.md を参照）*
*管理者: 作者（相談支援・福祉システム開発）*
