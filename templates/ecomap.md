---
type: ecomap
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources:
  - "[[raw/...]]"
tags:
  - 親なき後
  - エコマップ
related: []
status: draft
sensitivity: internal
person_id: "P_XXX"
ecomap_purpose: current     # current | handover | crisis | meeting
mermaid_or_svg: "mermaid"
---

# {{本人氏名}} のエコマップ — {{用途}} ({{YYYY-MM}})

> エコマップは支援ネットワークのスナップショットです。月単位で更新し、本人を取り巻く関係性の変化を時系列で追えるようにします。
> 既存の `ecomap-generator` スキルと連携可能（CLAUDE.md §10）。

## 用途

- [ ] current — 現況把握
- [ ] handover — 引き継ぎ用
- [ ] crisis — 緊急時連絡網
- [ ] meeting — 支援会議資料

## ネットワーク図

```mermaid
graph TD
    Person[P_XXX 本人]

    %% 家族
    Family1[家族1]

    %% 福祉サービス
    GH[GH ○○寮]
    DayService[生活介護 △△]
    Consultant[相談支援 □□]

    %% 医療
    Hospital[主治医]

    %% 行政
    City[市区町村窓口]

    Person --- Family1
    Person --- GH
    Person --- DayService
    Person --- Consultant
    Person --- Hospital
    GH --- Consultant
    DayService --- Consultant
    Consultant --- City
```

## 関係性の質（凡例）

- 太線: 強い関係（日常的に密に関わる）
- 細線: 通常の関係
- 点線: 弱い関係 / 緊張関係
- 双方向矢印: 相互的な関係
- 一方向矢印: 一方的な支援・依存

## ノード詳細

### 本人 P_XXX
→ [[P_XXX_氏名]]

### 関わる人物・組織

- [[E_GH...]]: 居住の場
- [[E_...]]: 日中活動
- ...

## 変化点（前回スナップショットからの差分）

（前月との変更がある場合に記載。新規追加・関係性変化・終了等）

## 想定される将来の移行

（今後追加・変更が予想されるノード。例: 親なき後の引き継ぎ先候補）
