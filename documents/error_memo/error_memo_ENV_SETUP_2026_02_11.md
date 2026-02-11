
# 📘 Quant Lab 環境構築・トラブル対応ノウハウまとめ

以下はそのまま `ENV_SETUP.md` として保存できる内容です。

---

# Quant Lab – 環境構築 & トラブルシューティングまとめ

## 1. 基本方針

### ✔ Pythonバージョン固定

* 使用：**Python 3.12.x**
* 理由：

  * yfinance + curl_cffi + SSL が安定
  * 3.14 は依存ホイール未対応でSSL崩壊リスクあり

---

## 2. フォルダ命名ルール（重要）

### ❌ NG

* 日本語
* スペース
* 記号
* OneDrive直下

### ✅ 推奨

```
C:\work\quant_lab\
```

### 理由

* libcurl が UTF-8 パスを正しく扱えないケースがある
* curl error (77) の原因になり得る

---

## 3. 仮想環境構築手順

```bat
py -3.12 -m venv .venv
.\.venv\Scripts\activate
python -m pip install -U pip
pip install -r requirements-dev.txt  # notebooks/tests を使う場合（runtimeのみなら requirements.txt）
```

---

## 4. よくあるエラーと原因

---

### 🔥 Error 1

```
curl: (77) error setting certificate verify locations
```

### 原因

* 日本語パス
* certifi CAfileをlibcurlが読めない
* Python 3.14使用

### 解決

1. 英数字フォルダへ移動
2. venv作り直し
3. Python 3.12使用

---

### 🔥 Error 2

```
ValueError: The truth value of a Series is ambiguous
```

### 原因

* pandas Series をスカラーとして扱った

### 解決

```python
active = float(last["ATR14"]) > float(atr_thresh)
```

---

### 🔥 Error 3

yfinance列がMultiIndexになる

### 原因

* yfinanceが('Close','1306.T')のような列を返す

### 解決

```python
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)
```

---

## 5. 実装上の教訓

### ✔ データ取得直後に正規化する

* 列をflatten
* 必要列だけ抽出
* dropna()

---

### ✔ pandasは常に型を疑う

```python
type(df["Close"])
```

---

### ✔ bool()でSeriesを評価しない

NG:

```python
bool(series > threshold)
```

OK:

```python
float(value) > threshold
```

---


