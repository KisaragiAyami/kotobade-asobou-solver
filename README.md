# Ayami's Kotobade Asobou Solver

## Overview
This repository contains an information theory-based solver for [Kotobade Asobou](https://taximanli.github.io/kotobade-asobou/). The solver intelligently recommends guesses to minimise the number of attempts needed to find the solution word.
Inspired by [3blue1brown's similar approach to solving Wordle](https://www.youtube.com/watch?v=v68zYyaEmEA).

The solver:
1. Precomputes the optimal first guess using entropy maximisation
2. Uses expected information gain to select subsequent guesses
3. Filters possible solutions based on game feedback
4. Supports frequency-based candidate sorting
5. Caches computations for improved performance

## Game Rules
- Guess 4-kana words that exist in the word list
- After each guess, you'll receive per-position feedback
- Refine your guess using the feedback
- If your guess is correct, the game is over and you win the game

## Prerequisites
- Python 3.6+
### Required Libraries
- inflect

## Installation
Install the required libraries using:
```bash
pip install inflect
```

## Running the Solver

1. Download the repository
2. Run the solver:
```bash
python main.py
```

3. Follow the prompts:
   - For first guess: Press Enter to use the recommendation or type your own
   - Enter 4-digit feedback after each guess (e.g., `4012`)
   - Continue until a solution is found

## File Descriptions
| File | Purpose |
|------|---------|
| `main.py` | Main solver implementation |
| `wordlist.ts` | 4-kana word list (required) |
| `freq.csv` | Optional word frequency data |
| `solver_cache.pkl` | Auto-generated first guess cache |

## Feedback Encoding
| Symbol | Code | Meaning |
|--------|------|---------|
| ⬛ | 0 | Kana not in target |
| ↕️ | 1 | Same row (行) as target |
| ↔️ | 2 | Same column (段) as target |
| 🟨 | 3 | Kana elsewhere in target |
| 🟩 | 4 | Correct kana & position |
| 🟢 | 5 | Variant in target position |

## Example Session
```
=== 4-Kana Japanese Word Game Solver ===
Information Theory Optimised Version
-------------------------------------
Feedback Encoding:
0. Grey square    : Kana not in target
1. Vertical arrows: Same row (行) as target kana
2. Horizontal arrows: Same column (段) as target kana
3. Yellow square  : Kana exists elsewhere in target
4. Green square   : Correct kana & position
5. Lime circle    : Variant exists in target position
-------------------------------------
Note: Variants include dakuten (か→が), handakuten (は→ぱ),
      and small kana (つ→っ)
-------------------------------------
Loaded frequency data for 21692 words
Loaded precomputed first guess: かいたく (7.1004 bits)
Loaded 36021 words
Frequency data available for 18194 words out of 36021 words (50.5%)
Starting solver...
Using precomputed first guess: かいたく (7.1004 bits)

=== ROUND 1 ===
Recommended first guess: かいたく
Enter your actual first guess (or press Enter to use recommendation):
Enter feedback for first guess (4 digits): 0320
  577 candidates remain

=== ROUND 2 ===
  577 candidates remain
  Evaluating 36021 potential guesses...
    Processed 3602 guesses of 36021 guesses (10.0%)
    Processed 7204 guesses of 36021 guesses (20.0%)
    Processed 10806 guesses of 36021 guesses (30.0%)
    Processed 14408 guesses of 36021 guesses (40.0%)
    Processed 18010 guesses of 36021 guesses (50.0%)
    Processed 21612 guesses of 36021 guesses (60.0%)
    Processed 25214 guesses of 36021 guesses (70.0%)
    Processed 28816 guesses of 36021 guesses (80.0%)
    Processed 32418 guesses of 36021 guesses (90.0%)
    Processed 36020 guesses of 36021 guesses (100.0%)
  Evaluated 36021 guesses in 225.55 seconds
Recommended guess: しつばん (expected gain: 5.1228 bits)
Enter your guess (or press Enter to use recommendation):
Enter feedback (4 digits): 1020
  Removed 560 candidates, 17 candidates remain
  All 17 possible solutions (sorted by frequency):
    すまない (freq: 2204.0)
    せきざい (freq: 1931.0)
    せきさい (freq: 1787.0)
    すじあい (freq: 741.0)
    すあらい (freq: 12.0)
    そらあい (freq: 3.0)
    すぎわい (freq: 2.0)
    すぎあい (freq: 0 - rare word)
    すぎざい (freq: 0 - rare word)
    すげない (freq: 0 - rare word)
    ずがない (freq: 0 - rare word)
    せきがい (freq: 0 - rare word)
    せめあい (freq: 0 - rare word)
    せりあい (freq: 0 - rare word)
    ぜひない (freq: 0 - rare word)
    ぜろさい (freq: 0 - rare word)
    そのさい (freq: 0 - rare word)

=== ROUND 3 ===
  17 candidates remain
  Evaluating 17 potential guesses...
    Processed 1 guess of 17 guesses (5.9%)
    Processed 2 guesses of 17 guesses (11.8%)
    Processed 3 guesses of 17 guesses (17.6%)
    Processed 4 guesses of 17 guesses (23.5%)
    Processed 5 guesses of 17 guesses (29.4%)
    Processed 6 guesses of 17 guesses (35.3%)
    Processed 7 guesses of 17 guesses (41.2%)
    Processed 8 guesses of 17 guesses (47.1%)
    Processed 9 guesses of 17 guesses (52.9%)
    Processed 10 guesses of 17 guesses (58.8%)
    Processed 11 guesses of 17 guesses (64.7%)
    Processed 12 guesses of 17 guesses (70.6%)
    Processed 13 guesses of 17 guesses (76.5%)
    Processed 14 guesses of 17 guesses (82.4%)
    Processed 15 guesses of 17 guesses (88.2%)
    Processed 16 guesses of 17 guesses (94.1%)
    Processed 17 guesses of 17 guesses (100.0%)
  Evaluated 17 guesses in 0.00 seconds
  All 17 possible solutions (sorted by frequency):
    すまない (freq: 2204.0)
    せきざい (freq: 1931.0)
    せきさい (freq: 1787.0)
    すじあい (freq: 741.0)
    すあらい (freq: 12.0)
    そらあい (freq: 3.0)
    すぎわい (freq: 2.0)
    すぎあい (freq: 0 - rare word)
    すぎざい (freq: 0 - rare word)
    すげない (freq: 0 - rare word)
    ずがない (freq: 0 - rare word)
    せきがい (freq: 0 - rare word)
    せめあい (freq: 0 - rare word)
    せりあい (freq: 0 - rare word)
    ぜひない (freq: 0 - rare word)
    ぜろさい (freq: 0 - rare word)
    そのさい (freq: 0 - rare word)
Recommended guess: せきさい (expected gain: 3.5725 bits)
Enter your guess (or press Enter to use recommendation): すまない
Enter feedback (4 digits): 4444
  Removed 16 candidates, 1 candidate remains
  The only possible solution:
    すまない (freq: 2204.0)

SOLUTION FOUND: すまない
  Frequency: 2204.0
```

## Customisation
- **Word List**: Modify `wordlist.ts` with a list of 4-kana words
- **Frequency Data**: Add `freq.csv` with `word,freq` columns for better sorting
- **First Guess**: Delete `solver_cache.pkl` to recompute optimal first guess. This took ~3 hours during my first computation.

---

# 「言葉で遊ぼう」ソルバー

## 概要
このリポジトリは、[言葉で遊ぼう](https://taximanli.github.io/kotobade-asobou/)ゲーム向けのソルバーです。情報理論を活用し、単語を推測する際の試行回数を最小化する推測を提案します。  
[3blue1brownのWordle解法](https://www.youtube.com/watch?v=v68zYyaEmEA)に着想を得た手法を使用しています。

主な特徴:
1. **初手推測の事前計算**: エントロピー最大化に基づく最適な初手を事前に計算
2. **推測選択アルゴリズム**: 期待情報ゲインを最大化する推測を自動選択
3. **候補絞り込み**: ゲームのフィードバックをもとに候補単語を動的にフィルタリング
4. **候補の優先順位付け**: 単語の使用頻度データに基づくソート機能
5. **パフォーマンス最適化**: 計算結果のキャッシュによる高速処理

## ゲームルール
- 4文字のひらがな単語を推測
- 各推測後に位置ごとのフィードバックが得られる
- フィードバックを手がかりに候補を絞り込み
- 正解単語を入力で勝利

## 動作環境
- Python 3.6 以上
### 必須ライブラリ
- inflect

## インストール方法
必要なライブラリをインストール:
```bash
pip install inflect
```

## 使い方

1. リポジトリをダウンロード
2. ソルバーを起動:
```bash
python main-jp.py
```
3. プロンプトに従って操作:
   - 初回推測: Enterキーで推奨単語を使用、もしくは任意の単語を入力
   - フィードバックを4桁の数字で入力 (例: `4012`)
   - 正解が出るまで繰り返し

## ファイル構成
| ファイル名 | 説明 |
|------------|------|
| `main-jp.py` | 日本語版ソルバーのメイン実装 |
| `wordlist.ts` | かな4文字単語リスト (必須) |
| `freq.csv` | 単語使用頻度データ (任意) |
| `solver_cache.pkl` | 初手推測キャッシュ (自動生成) |

## フィードバックの見方
| 記号 | コード | 意味 |
|------|-------|------|
| ⬛ | 0 | 単語に含まれない文字 |
| ↕️ | 1 | 同じ行の仮名が同じ位置に存在 |
| ↔️ | 2 | 同じ列の仮名が同じ位置に存在 |
| 🟨 | 3 | 別の位置に存在する文字 |
| 🟩 | 4 | 正しい位置の文字 |
| 🟢 | 5 | 変種が同じ位置に存在 (濁点・半濁点・小文字) |

## カスタマイズ方法
- **単語リスト**: `wordlist.ts` を編集して使用単語を変更
- **頻度データ**: `freq.csv` に `単語,頻度` 形式でデータ追加
- **初手推測の再計算**: `solver_cache.pkl` を削除すると再生成 (初回計算目安: 約3時間)