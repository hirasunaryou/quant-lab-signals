# 05. iPhone連携計画（通知ダッシュボード向け）

関連Notebook:
- [`notebooks/12_strategy_report.ipynb`](../notebooks/12_strategy_report.ipynb)

> 目的: 研究ノートの出力を、将来の iPhone ダッシュボードで読める形に標準化する。  
> 制約: 本フェーズで**実ブローカー執行は行わない**（Signal と Executor を分離）。

## 1) モバイル向け JSON 契約（最小必須フィールド）

以下は日次更新の `strategy_report.json` 想定です。

```json
{
  "meta": {
    "symbol": "SPY",
    "as_of": "2026-02-10",
    "timezone": "America/New_York",
    "version": "v1"
  },
  "signal": {
    "action": "BUY",
    "confidence": 0.64,
    "position_target": 0.75,
    "reason_codes": ["ema_trend_up", "atr_normal"]
  },
  "risk": {
    "max_drawdown": -0.182,
    "ann_vol": 0.143,
    "turnover_20d": 5.8
  },
  "performance": {
    "cum_return": 0.217,
    "ytd_return": 0.046,
    "win_rate": 0.53,
    "avg_trade_return": 0.004
  },
  "regime": {
    "vol_regime": "mid",
    "trend_regime": "bull",
    "signal_frequency_20d": 3
  },
  "alerts": [
    {
      "type": "BUY",
      "message": "EMA trend up with acceptable ATR",
      "scheduled_at": "2026-02-10T21:05:00Z"
    }
  ]
}
```

### 設計メモ

- `signal.action` は `BUY | SELL | HOLD` を保持しても、通知対象は BUY/SELL のみ
- `reason_codes` は UI の説明責任を補助（ブラックボックス化を防ぐ）
- `risk` と `performance` は同一画面で見せ、過剰楽観を避ける

## 2) 配信更新の選択肢（iCloud / API / GitHub Raw）

### A. iCloud Drive 同期

- 構成: ローカルで JSON 生成 → iCloud Drive フォルダへ保存 → Shortcuts/アプリで読込
- 長所: 個人運用で構築が早い、サーバ不要
- 短所: 同期遅延・競合編集・権限トラブルに注意

### B. 軽量 API（将来）

- 構成: JSON を API サーバへ POST、iPhone は GET
- 長所: バージョン管理・認証・将来拡張が容易
- 短所: 運用コスト、監視、認証実装が必要

### C. GitHub Raw 配信

- 構成: JSON をリポジトリにコミットし `raw.githubusercontent.com` で配信
- 長所: 履歴管理が明確、デバッグ容易
- 短所: 公開範囲に注意（Private + token 管理）、更新遅延があり得る

## 3) 通知ロジック（BUY/SELLのみ、日次スケジュール）

### ルール

- 通知対象: `action in {BUY, SELL}` のみ
- HOLD は通知しない（ノイズ抑制）
- 1日1回の定刻実行（例: 現地引け後 + 数分）
- 同一シグナルの重複通知は抑制（前日と同じ action ならスキップ）

### 擬似フロー

1. 日次バッチでレポート JSON 更新
2. `current_action != previous_action` を確認
3. BUY/SELL かつ変化ありなら通知キュー追加
4. 通知送信後、`last_notified_action` と時刻を記録

## 4) 次フェーズへの実装メモ

- Notebook 12 のレポート生成ロジックを `src/` の純粋関数へ移管し再利用性を上げる
- JSON スキーマを固定し、後方互換を意識して `meta.version` を更新
- Executor 層（実発注）は別モジュール・別権限で管理し、研究コードと分離する

## 5) 重要な境界（再確認）

- 本ドキュメントは**シグナル可視化・通知設計**まで
- 実ブローカー接続、注文再送、ポジション照合は対象外
- まずはペーパートレード運用で、通知品質と人間の意思決定プロセスを整える
