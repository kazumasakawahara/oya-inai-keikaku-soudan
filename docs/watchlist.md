# watchlist — 制度ウォッチ監視対象台帳

- 作成: 2026-08-10（R4。ADR-R6 に基づく）
- **このファイルが制度ウォッチの正典**です。監視ツール（firecrawl monitor 等）はこの台帳に従属し、いつでも差し替え可能です（ツール中立）。
- 巡回頻度: **月次を基本**とし、報酬改定期・法改正施行期（例年 1〜4月）は週次に密度を上げる
- 点検で変更を検知したら: ① 取得内容を `raw/60_行政・制度/` に保存（出所 URL・取得日付き）→ ② review 型ページを起票（発生条件「制度改正の検知」）→ ③ 使い手の判断で該当 PS_ ページと `last_updated_law` / `verified_on` を更新。**機械は起票まで、判断と反映は人間**。

---

## 1. 全国共通・主要8制度（初期監視対象。2026-08-10 確定）

URL はすべて 2026-08-10 に実在確認済み。

**monitor の登録（導入時に実施）**: firecrawl monitor を使う場合の実地の知見です（他ツールでも可 — 本台帳はツール中立）。
1. §1 の 14 URL を1つの monitor にまとめて登録する（推定 28 credits/月）
2. **作成時の scheduleText は "daily at 9:00" 等しか受け付けない**ため、いったん daily で作成し、直後に monitor_update で cron `0 9 1 * *`（毎月1日 9:00 / Asia/Tokyo）へ変更する。daily のままだと約 840 credits/月かかる
3. goal 判定をオンにし、「法改正・報酬改定・新しい通知/資料の追加・制度運用の変更・様式の改定」を意味のある変更とする（誤字・レイアウト変更は除外）
4. 登録後、下表の monitor ID 列と「最終点検」列を記入する
5. 初回実行（monitor_run）はベースライン取得。**差分検知が発火するのは2巡目以降**

| # | 対応 PS_ ページ | 監視対象（一次情報源） | URL | monitor ID | 最終点検 |
|---|---|---|---|---|---|
| 1 | PS_障害者手帳制度 | 厚労省: 身体障害者手帳 | https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/hukushi_kaigo/shougaishahukushi/shougaishatechou/index.html | （未登録） | — |
| 2 | PS_障害年金手当 | 日本年金機構: 障害年金の制度 | https://www.nenkin.go.jp/service/jukyu/seido/shougainenkin/index.html | （未登録） | — |
| 2b | 〃 | 厚労省: 特別障害者手当 | https://www.mhlw.go.jp/bunya/shougaihoken/jidou/tokubetsu.html | （未登録） | — |
| 3 | PS_障害福祉サービス体系 | 厚労省: 障害福祉サービス等（総合） | https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/hukushi_kaigo/shougaishahukushi/service/index.html | （未登録） | — |
| 3b | 〃 | 厚労省: 令和8年度障害福祉サービス等報酬改定 | https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000202214_00013.html | （未登録） | — |
| 3c | 〃／PS_基幹相談支援センター | e-Gov: 障害者総合支援法（条文） | https://elaws.e-gov.go.jp/document?lawid=417AC0000000123 | （未登録） | — |
| 4 | PS_自立支援医療 | 厚労省: 自立支援医療 | https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/hukushi_kaigo/shougaishahukushi/jiritsu/index.html | （未登録） | — |
| 5 | PS_成年後見制度 | 厚労省: 成年後見はやわかり（制度ポータル） | https://guardianship.mhlw.go.jp/ | （未登録） | — |
| 6 | PS_日常生活自立支援事業 | 厚労省: 日常生活自立支援事業 | https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/hukushi_kaigo/seikatsuhogo/chiiki-fukusi-yougo/index.html | （未登録） | — |
| 7 | PS_障害者虐待防止法 | 厚労省: 障害者虐待防止法 | https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/hukushi_kaigo/shougaishahukushi/gyakutaiboushi/index.html | （未登録） | — |
| 7b | 〃 | 厚労省: 同・通知/関連資料 | https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/hukushi_kaigo/shougaishahukushi/gyakutaiboushi/tsuuchi.html | （未登録） | — |
| 8 | PS_障害者差別解消法 | 内閣府: 障害者差別解消法（法律・関連ページ） | https://www8.cao.go.jp/shougai/suishin/law_h25-65.html | （未登録） | — |
| 8b | 〃 | 内閣府: 差別解消の推進に関する基本方針 | https://www8.cao.go.jp/shougai/suishin/sabekai/kihonhoushin/honbun.html | （未登録） | — |

**特別障害給付金**（PS_特別障害給付金 がある場合）: https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/hukushi_kaigo/shougaishahukushi/kyuhukin/index.html （未登録）

## 2. 地域枠（初期は空 — 導入時にあなたの自治体を登録してください）

利用者の所在地に関する監視対象は配布物に焼き込みません。導入時に、AI と一緒に次の形式で追加してください（→ 追加手順は §4）。

| 対応ページ | 監視対象 | URL | monitor ID | 最終点検 |
|---|---|---|---|---|
| （記入例）障害福祉サービス体系（○○市の記入例） | ○○市: 障害福祉のページ | https://…（あなたの自治体の該当ページ） | — | — |

<!-- 地域枠の行はこの下に追加 -->

## 3. 月次点検の手順

1. monitor の検知結果を確認する（firecrawl monitor_check。未登録の間は各 URL を目視／AI に巡回依頼）
2. 変更があった対象は、取得内容を `raw/60_行政・制度/` に保存（ファイル名に取得日、冒頭に出所 URL）
3. `templates/review.md` で review を起票（発生条件: 制度改正の検知 / proposed_action: Update Existing が基本）
4. 使い手が判断 → 該当 PS_ ページを更新し、`last_updated_law`（改正の施行日）と `verified_on`（確認日）を更新
5. 改正が個別支援に及ぶ場合（例: 報酬改定が利用計画に影響）は、関連する plan / person への波及を review で提案
6. 本台帳の「最終点検」列を更新

> lint は public-system の `verified_on` が365日を超えると WARN を出します（見張りの見張り）。この WARN が出たら、本台帳の点検が止まっている合図です。

## 4. 地域枠の追加手順（導入時・約10分）

1. あなたの自治体名＋「障害福祉」で公式サイトの該当ページを探す（AI に「○○市の障害福祉のページを watchlist に登録して」と頼めば、検索→URL 確認→本台帳への追記まで行います）
2. §2 の表に1行追加（対応する地域版 PS_/E_ ページがあればリンク）
3. monitor を登録し、monitor ID を記入
4. 手帳（療育手帳は自治体運用）・医療費助成など、自治体差の大きい制度を優先する

## 5. 変更履歴

- （導入日を記入）: 本 Vault に導入。地域枠の登録・monitor 登録を実施
- 2026-08-10: 配布版初版。全国共通8制度（＋関連 URL 5件）。URL 実在確認済み。本家 Vault で monitor 登録・1巡目試運転済み（取得→raw/60 保存→review 起票のフローを実証）
