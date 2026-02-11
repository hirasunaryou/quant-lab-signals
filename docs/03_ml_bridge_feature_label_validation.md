# ML Bridge: 特徴量・ラベル設計と検証（リーク防止）

本ドキュメントは、OHLCV から機械学習に橋渡しする際の最小実践をまとめたものです。  
対応ノートブック:
- `notebooks/09_feature_engineering_basics.ipynb`
- `notebooks/10_walk_forward_validation.ipynb`

---

## 1) Supervised framing（教師あり学習の枠組み）

時系列の分類タスクでは、**時点 t の特徴量で、t→t+1 の値動きを予測**する形が基本です。

### ラベル定義の例

1. **次日方向（next-day direction）**
   - 定義: `label_t = 1 if return_{t+1} > 0 else 0`
   - 長所: 直感的で扱いやすい
   - 注意: 小幅変動でもクラスが切り替わりノイズに敏感

2. **閾値超え（return threshold）**
   - 定義: `label_t = 1 if return_{t+1} > θ else 0`
   - 長所: 取引コストや最小期待値を意識しやすい
   - 注意: θ の選択でクラス不均衡が起きやすい

3. **分位点ラベル（quantiles）**
   - 例: 上位40%を 1、残りを 0 など
   - 長所: データ分布に適応しやすい
   - 注意: 分位点は**学習データで算出**し、検証データへ持ち込まない

---

## 2) Feature categories（特徴量カテゴリ）

以下のように「役割」で整理すると、特徴量設計が安定します。

- **Trend（トレンド）**
  - `ema_diff`（短期EMA−長期EMA）
  - ローリング平均リターン

- **Volatility（ボラティリティ）**
  - `rolling std`（5日、20日）
  - `atr`

- **Momentum（モメンタム）**
  - 1日/5日リターン
  - EMA差分の継続性

- **Mean-reversion（逆張り）**
  - 短期急騰/急落後の戻りを表す派生指標
  - （例）短期リターン乖離

- **Regime（相場状態）**
  - `range`（(High-Low)/Close）
  - `volume change`
  - 正規化指標（`ema_diff / atr`）

---

## 3) Leakage checklist（情報リーク防止チェック）

学習性能が高く見えても、リークがあると運用で再現しません。必ず以下を確認します。

- [ ] ラベルは `t+1` を参照し、**特徴量は t まで**で構築しているか
- [ ] 未来の値（例: `shift(-1)`）を特徴量に混ぜていないか
- [ ] 欠損補完で未来方向の補完（backfill）を使っていないか
- [ ] スケーリング/標準化は **train で fit、test で transform のみ**か
- [ ] 特徴選択や閾値最適化を test を見ながら実施していないか
- [ ] walk-forward の各窓で独立に再学習しているか

---

## 4) Walk-forward validation の概念

時系列ではランダム分割よりも、時間順を維持した walk-forward が推奨です。

例: `6か月 train / 1か月 test` を1か月ずつ前進

1. 先頭6か月で学習
2. 次の1か月で検証
3. 期間を1か月進めて再学習
4. 終端まで繰り返し

これにより、
- 未来混入を防ぎやすい
- 相場レジーム変化への耐性を確認しやすい
- 「平均性能」だけでなく「期間ごとの性能分散」を見られる

---

## Key takeaways

- ラベル定義は目的（方向予測・コスト考慮・分布適応）に合わせて選ぶ。  
- 特徴量はカテゴリ（trend/volatility/momentum/mean-reversion/regime）でバランスを取る。  
- 情報リーク対策は、モデル設計そのものより先に確認する。  
- walk-forward で「時系列に正しい評価」を習慣化する。

次の実装参照:
- 特徴量作成: `notebooks/09_feature_engineering_basics.ipynb`
- 検証実装: `notebooks/10_walk_forward_validation.ipynb`
