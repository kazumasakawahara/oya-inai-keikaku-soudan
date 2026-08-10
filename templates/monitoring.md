---
type: monitoring
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources:
  - "[[raw/70_自分の作成物/...]]"
tags:
  - 親なき後
  - モニタリング
related: []
status: active
sensitivity: sensitive
sensitive_purpose: "計画に対する実施状況と本人の変化を時系列で残す"
person_id: "P_XXX"
monitored_on: YYYY-MM-DD
plan_ref: "[[PL_..._P_XXX]]"   # 対象計画
confirms: []      # 今回のモニタリングで「まだ有効」と確認できた記録（person / protocol / trigger 等）
contradicts: []   # 「もう合わない」と分かった記録
provided_by: 相談支援
share_scope: team
---

# 【モニタリング】{{本人の呼び名}}（YYYY-MM-DD 実施）

## 実施状況

（計画どおりに使えているか。事業所ごとの状況）

## 本人の変化

（前回からの変化。事実ベースで）

## 確認できたこと・合わなくなったこと

> **モニタリングは鮮度更新の定期便です**（[[schema]] §6-3）。
> ここで「まだこの通り」と確認できた記録は frontmatter の `confirms` に挙げ、
> その記録の `last_confirmed` を今日の日付に更新します（confirmed_by: 実地で確認／支援者に確認）。
> 合わなくなった記録は `contradicts` に挙げ、見直し（review・改訂・stale化）につなげます。

- 確認できた: [[PR_..._P_XXX]]（例：入浴の手順は機能している）
- 合わなくなった: （あれば）

## 計画変更の要否

（不要／軽微な調整／再作成。理由）
