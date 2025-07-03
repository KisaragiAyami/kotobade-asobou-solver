import math
import re
import time
import pickle
import os
import csv
import sys
from collections import defaultdict
from functools import lru_cache

# ベースマッピング: かなを基本形に変換（濁点・半濁点・小文字を無視）
base_map = {
    'あ': 'あ', 'い': 'い', 'う': 'う', 'え': 'え', 'お': 'お',
    'か': 'か', 'き': 'き', 'く': 'く', 'け': 'け', 'こ': 'こ',
    'さ': 'さ', 'し': 'し', 'す': 'す', 'せ': 'せ', 'そ': 'そ',
    'た': 'た', 'ち': 'ち', 'つ': 'つ', 'て': 'て', 'と': 'と',
    'な': 'な', 'に': 'に', 'ぬ': 'ぬ', 'ね': 'ね', 'の': 'の',
    'は': 'は', 'ひ': 'ひ', 'ふ': 'ふ', 'へ': 'へ', 'ほ': 'ほ',
    'ま': 'ま', 'み': 'み', 'む': 'む', 'め': 'め', 'も': 'も',
    'や': 'や', 'ゆ': 'ゆ', 'よ': 'よ',
    'ら': 'ら', 'り': 'り', 'る': 'る', 'れ': 'れ', 'ろ': 'ろ',
    'わ': 'わ', 'を': 'を',
    'ん': 'ん', 'ー': 'ー',
    'が': 'か', 'ぎ': 'き', 'ぐ': 'く', 'げ': 'け', 'ご': 'こ',
    'ざ': 'さ', 'じ': 'し', 'ず': 'す', 'ぜ': 'せ', 'ぞ': 'そ',
    'だ': 'た', 'ぢ': 'ち', 'づ': 'つ', 'で': 'て', 'ど': 'と',
    'ば': 'は', 'び': 'ひ', 'ぶ': 'ふ', 'べ': 'へ', 'ぼ': 'ほ',
    'ぱ': 'は', 'ぴ': 'ひ', 'ぷ': 'ふ', 'ぺ': 'へ', 'ぽ': 'ほ',
    'ぁ': 'あ', 'ぃ': 'い', 'ぅ': 'う', 'ぇ': 'え', 'ぉ': 'お',
    'ゃ': 'や', 'ゅ': 'ゆ', 'ょ': 'よ',
    'っ': 'つ',
    'ゎ': 'わ', 'ゕ': 'か', 'ゖ': 'け'
}

# 行グループ (行)
row_groups = {
    'あ': ['あ', 'い', 'う', 'え', 'お'],
    'か': ['か', 'き', 'く', 'け', 'こ', 'が', 'ぎ', 'ぐ', 'げ', 'ご'],
    'さ': ['さ', 'し', 'す', 'せ', 'そ', 'ざ', 'じ', 'ず', 'ぜ', 'ぞ'],
    'た': ['た', 'ち', 'つ', 'て', 'と', 'だ', 'ぢ', 'づ', 'で', 'ど'],
    'な': ['な', 'に', 'ぬ', 'ね', 'の'],
    'は': ['は', 'ひ', 'ふ', 'へ', 'ほ', 'ば', 'び', 'ぶ', 'べ', 'ぼ', 'ぱ', 'ぴ', 'ぷ', 'ぺ', 'ぽ'],
    'ま': ['ま', 'み', 'む', 'め', 'も'],
    'や': ['や', 'ゆ', 'よ', 'ゃ', 'ゅ', 'ょ'],
    'ら': ['ら', 'り', 'る', 'れ', 'ろ'],
    'わ': ['わ', 'を', 'ゎ']
}

# 段グループ (段)
col_groups = {
    'あ': ['あ', 'か', 'さ', 'た', 'な', 'は', 'ま', 'や', 'ら', 'わ', 'が', 'ざ', 'だ', 'ば', 'ぱ', 'ゃ'],
    'い': ['い', 'き', 'し', 'ち', 'に', 'ひ', 'み', 'り', 'ぎ', 'じ', 'ぢ', 'び', 'ぴ'],
    'う': ['う', 'く', 'す', 'つ', 'ぬ', 'ふ', 'む', 'ゆ', 'る', 'ぐ', 'ず', 'づ', 'ぶ', 'ぷ', 'ゅ', 'っ'],
    'え': ['え', 'け', 'せ', 'て', 'ね', 'へ', 'め', 'れ', 'げ', 'ぜ', 'で', 'べ', 'ぺ'],
    'お': ['お', 'こ', 'そ', 'と', 'の', 'ほ', 'も', 'よ', 'ろ', 'を', 'ご', 'ぞ', 'ど', 'ぼ', 'ぽ', 'ょ']
}

# 行/段のマッピングを作成
row_map = {}
for row_id, kanas in row_groups.items():
    for kana in kanas:
        row_map[kana] = row_id

col_map = {}
for col_id, kanas in col_groups.items():
    for kana in kanas:
        col_map[kana] = col_id

def get_base(kana):
    """かなの基本形を取得（見つからない場合はそのまま）"""
    return base_map.get(kana, kana)

def get_row(kana):
    """行識別子を取得（ん/ーの場合はNone）"""
    base = get_base(kana)
    if base in ['ん', 'ー']:
        return None
    return row_map.get(base, None)

def get_col(kana):
    """段識別子を取得（ん/ーの場合はNone）"""
    base = get_base(kana)
    if base in ['ん', 'ー']:
        return None
    return col_map.get(base, None)

def is_variant(a, b):
    """aがbの変種か確認（基本形が同じで異なる文字）"""
    if a == b:
        return False
    return get_base(a) == get_base(b)

def get_feedback(guess, answer):
    """推測と正解を比較してフィードバックを計算"""
    n = len(guess)
    feedback = [0] * n
    freq = defaultdict(int)
    
    # 正解のかな頻度マップ（完全一致を除く）
    for k in answer:
        freq[k] += 1

    # 第一パス: 完全一致をチェック (4)
    for i in range(n):
        if guess[i] == answer[i]:
            feedback[i] = 4
            freq[answer[i]] -= 1  # 出現回数を消費

    # 第二パス: 変種をチェック (5)
    for i in range(n):
        if feedback[i] != 0:  # 既に一致した位置はスキップ
            continue
        if is_variant(guess[i], answer[i]):
            feedback[i] = 5

    # 第三パス: 存在をチェック (3)
    for i in range(n):
        if feedback[i] != 0:  # 既に一致した位置はスキップ
            continue
        if freq.get(guess[i], 0) > 0:
            feedback[i] = 3
            freq[guess[i]] -= 1  # 出現回数を消費

    # 第四パス: 同じ行(1)または段(2)をチェック
    for i in range(n):
        if feedback[i] != 0:  # 既に一致した位置はスキップ
            continue
            
        row_g = get_row(guess[i])
        row_a = get_row(answer[i])
        col_g = get_col(guess[i])
        col_a = get_col(answer[i])
        
        if row_g is not None and row_a is not None and row_g == row_a:
            feedback[i] = 1
        elif col_g is not None and col_a is not None and col_g == col_a:
            feedback[i] = 2
        else:
            feedback[i] = 0
    
    return tuple(feedback)

# フィードバック計算のキャッシュ
@lru_cache(maxsize=100000)
def get_feedback_cached(guess, answer):
    """キャッシュ付きのget_feedback"""
    return get_feedback(guess, answer)

def load_wordlist(filename):
    """TSファイルから単語リストを読み込み"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    # 正規表現で単語を抽出
    words = re.findall(r"'(?:\\.|[^'])*'", content)
    words = [w[1:-1] for w in words]  # クォートを除去
    return words

def entropy(probabilities):
    """確率分布のエントロピーを計算"""
    return -sum(p * math.log2(p) for p in probabilities if p > 0)

class EntropySolver:
    def __init__(self, wordlist_file="wordlist.ts", cache_file="solver_cache.pkl"):
        self.full_list = load_wordlist(wordlist_file)
        self.cache_file = cache_file
        self.candidates = self.full_list.copy()
        self.precomputed_first_guess = None
        self.feedback_cache = {}
        self.pattern_cache = {}
        self.frequency_dict = self.load_frequency_data("freq.csv")
        
        # 事前計算済み初手推測を読み込み
        self.load_cache()
    
    def load_frequency_data(self, filename):
        """CSVファイルから単語頻度データを読み込み"""
        frequency_dict = {}
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        word = row['word'].strip()
                        try:
                            frequency = float(row['freq'])
                            frequency_dict[word] = frequency
                        except (KeyError, ValueError):
                            continue
                print(f"頻度データを{len(frequency_dict)}語読み込みました")
            except Exception as e:
                print(f"頻度データ読み込みエラー: {e}")
        else:
            print(f"頻度ファイル {filename} が見つかりません。アルファベット順で表示します。")
        return frequency_dict
    
    def load_cache(self):
        """事前計算済みデータを読み込み"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                    self.precomputed_first_guess = cache_data.get('first_guess')
                    if self.precomputed_first_guess:
                        guess, gain = self.precomputed_first_guess
                        print(f"事前計算済み初手推測: {guess} ({gain:.4f} bits)")
            except Exception as e:
                print(f"キャッシュ読み込みエラー: {e}")
                self.precomputed_first_guess = None
    
    def save_cache(self):
        """将来の実行のために事前計算データを保存"""
        cache_data = {'first_guess': self.precomputed_first_guess}
        with open(self.cache_file, 'wb') as f:
            pickle.dump(cache_data, f)
    
    def precompute_first_guess(self):
        """最適な初手推測を事前計算してキャッシュに保存"""
        if self.precomputed_first_guess:
            return self.precomputed_first_guess
            
        total_words = len(self.full_list)
        print(f"最適な初手推測を{total_words}語で計算中（数分かかります）...")
        start_time = time.time()
        last_print_time = start_time
        
        best_guess = None
        best_gain = -1
        
        for idx, guess in enumerate(self.full_list):
            pattern_counts = defaultdict(int)
            
            for answer in self.full_list:
                fb = get_feedback_cached(guess, answer)
                pattern_counts[fb] += 1
                
            gain = 0
            total = total_words
            for count in pattern_counts.values():
                if count > 0:
                    p_val = count / total
                    gain += p_val * math.log2(total / count)
                
            # より良い推測が見つかったら更新
            if gain > best_gain:
                best_gain = gain
                best_guess = guess
                print(f"  新記録: {best_guess} ({gain:.4f} bits)")
            
            # 2秒ごとに進捗を表示
            current_time = time.time()
            if current_time - last_print_time >= 2:
                elapsed = current_time - start_time
                percent_complete = (idx + 1) / total_words * 100
                words_per_sec = (idx + 1) / elapsed
                est_total_time = total_words / words_per_sec
                est_remaining = est_total_time - elapsed
                
                print(f"  進捗: {idx+1}/{total_words}語 ({percent_complete:.1f}%) - "
                      f"経過時間: {elapsed:.0f}秒, 残り時間: ~{est_remaining:.0f}秒, "
                      f"速度: {words_per_sec:.1f} 語/秒")
                
                # 現在の最良推測を表示
                if best_guess:
                    print(f"    現在の最良: {best_guess} ({best_gain:.4f} bits)")
                
                last_print_time = current_time
        
        self.precomputed_first_guess = (best_guess, best_gain)
        self.save_cache()
        
        elapsed = time.time() - start_time
        print(f"事前計算完了: {elapsed:.1f}秒")
        print(f"最適初手推測: {best_guess} ({best_gain:.4f} bits)")
        
        return best_guess, best_gain
    
    def expected_information_gain(self, guess, candidates):
        """推測の期待情報ゲインを計算"""
        pattern_counts = defaultdict(int)
        total = len(candidates)
        
        # キャッシュがあれば使用
        cache_key = (guess, tuple(candidates))
        if cache_key in self.pattern_cache:
            pattern_counts = self.pattern_cache[cache_key]
        else:
            for answer in candidates:
                # キャッシュがあれば使用
                cache_fb_key = (guess, answer)
                if cache_fb_key in self.feedback_cache:
                    fb = self.feedback_cache[cache_fb_key]
                else:
                    fb = get_feedback_cached(guess, answer)
                    self.feedback_cache[cache_fb_key] = fb
                pattern_counts[fb] += 1
            self.pattern_cache[cache_key] = pattern_counts
        
        # 情報ゲインを計算
        gain = 0
        for count in pattern_counts.values():
            if count > 0:
                p_val = count / total
                gain += p_val * math.log2(total / count)
        
        return gain
    
    def find_best_guess(self, candidates):
        """情報理論を用いて最良の推測を見つける"""
        candidate_count = len(candidates)
        # 候補が1つだけならそれを返す
        if candidate_count == 1:
            return candidates[0], 0
        
        best_guess = None
        best_gain = -1
        start_time = time.time()
        
        # 評価する推測候補を決定
        if candidate_count <= 200:
            guess_set = candidates
        else:
            # 候補が多い場合は全単語を評価
            guess_set = self.full_list
        
        guess_count = len(guess_set)
        print(f"  候補{guess_count}件を評価中...")
        
        # 全ての推測候補を評価
        for idx, guess in enumerate(guess_set):
            gain = self.expected_information_gain(guess, candidates)
            
            if gain > best_gain:
                best_gain = gain
                best_guess = guess
            
            # 10%ごとに進捗を表示
            if (idx + 1) % max(1, guess_count // 10) == 0:
                elapsed = time.time() - start_time
                print(f"    進捗: {idx+1}/{guess_count}件 ({(idx+1)/guess_count*100:.1f}%)")
        
        elapsed = time.time() - start_time
        print(f"  {guess_count}件の評価完了: {elapsed:.2f}秒")
        return best_guess, best_gain
    
    def filter_candidates(self, guess, feedback, candidates):
        """フィードバックに基づいて候補をフィルタリング"""
        new_candidates = []
        for word in candidates:
            if get_feedback_cached(guess, word) == feedback:
                new_candidates.append(word)
        return new_candidates
    
    def sort_candidates(self, candidates):
        """頻度（ない場合は0）とアルファベット順で候補をソート"""
        return sorted(
            candidates,
            key=lambda word: (
                -self.frequency_dict.get(word, 0),  # 頻度の高い順
                word  # アルファベット順
            )
        )
    
    def display_candidates(self, candidates):
        """頻度情報付きで候補を表示"""
        candidate_count = len(candidates)
        sorted_candidates = self.sort_candidates(candidates)
        
        if candidate_count == 1:
            print("  唯一の候補:")
        else:
            print(f"  全{candidate_count}候補 (頻度順):")
            
        for word in sorted_candidates:
            frequency = self.frequency_dict.get(word, 0)
            if frequency > 0:
                print(f"    {word} (頻度: {frequency})")
            else:
                print(f"    {word} (頻度: 0 - レアワード)")
    
    def run(self):
        """メインの解決ループ"""
        total_words = len(self.full_list)
        print(f"単語を{total_words}語読み込みました")
        
        if self.frequency_dict:
            known = sum(1 for word in self.full_list if word in self.frequency_dict)
            known_percent = known/total_words*100
            print(f"頻度データ: {total_words}語中{known}語 ({known_percent:.1f}%)")
        print("ソルバーを開始します...")
        
        # 初手推測の処理
        if not self.precomputed_first_guess:
            print("事前計算済み初手推測が見つかりません")
            first_guess, first_gain = self.precompute_first_guess()
        else:
            first_guess, first_gain = self.precomputed_first_guess
            print(f"事前計算済み初手推測を使用: {first_guess} ({first_gain:.4f} bits)")
        
        # 初手推測
        print(f"\n=== 第1ラウンド ===")
        print(f"推奨初手推測: {first_guess}")
        user_guess = input("実際の初手推測を入力（Enterで推奨を使用）: ").strip()
        
        if not user_guess:
            user_guess = first_guess
        elif user_guess not in self.full_list:
            print("単語リストにありません。推奨を使用します")
            user_guess = first_guess
        
        # 初手推測のフィードバックを取得
        feedback_str = input("初手推測のフィードバック（4桁）: ").strip()
        feedback_tuple = self.parse_feedback(feedback_str)
        
        # 候補をフィルタリング
        self.candidates = self.filter_candidates(user_guess, feedback_tuple, self.candidates)
        candidate_count = len(self.candidates)
        print(f"  {candidate_count}候補が残っています")
        
        # 50候補以下なら全て表示
        if 0 < candidate_count <= 50:
            self.display_candidates(self.candidates)
        
        # 以降の推測
        round_num = 2
        while candidate_count > 1:
            print(f"\n=== 第{round_num}ラウンド ===")
            print(f"  {candidate_count}候補が残っています")
            
            # 最良の推測を見つける
            start_time = time.time()
            best_guess, gain = self.find_best_guess(self.candidates)
            elapsed = time.time() - start_time
            
            # 評価後に候補を表示（推奨前）
            if 0 < candidate_count <= 50:
                self.display_candidates(self.candidates)
            
            print(f"推奨推測: {best_guess} (期待情報ゲイン: {gain:.4f} bits)")
            user_guess = input("推測を入力（Enterで推奨を使用）: ").strip()
            
            if not user_guess:
                user_guess = best_guess
            elif user_guess not in self.full_list:
                print("単語リストにありません。推奨を使用します")
                user_guess = best_guess
            
            # フィードバックを取得
            feedback_str = input("フィードバック（4桁）: ").strip()
            feedback_tuple = self.parse_feedback(feedback_str)
            
            # 候補をフィルタリング
            prev_count = candidate_count
            self.candidates = self.filter_candidates(user_guess, feedback_tuple, self.candidates)
            candidate_count = len(self.candidates)
            removed = prev_count - candidate_count
            
            print(f"  {removed}候補を除外, {candidate_count}候補が残っています")
            
            # 50候補以下なら全て表示
            if 0 < candidate_count <= 50:
                self.display_candidates(self.candidates)
            
            round_num += 1
        
        # 最終結果
        if candidate_count == 1:
            solution = self.candidates[0]
            frequency = self.frequency_dict.get(solution, 0)
            print(f"\n解答が見つかりました: {solution}")
            if frequency > 0:
                print(f"  頻度: {frequency}")
            else:
                print("  頻度: 0 (レアワード)")
        else:
            print("\n解答が見つかりませんでした。原因:")
            print("- 一貫性のないフィードバックが入力された")
            print("- 単語が元のリストにない")
            if candidate_count > 0:
                print(f"残りの{candidate_count}候補: {', '.join(self.candidates)}")
    
    def parse_feedback(self, feedback_str):
        """フィードバック文字列をタプルに変換"""
        if len(feedback_str) != 4 or not feedback_str.isdigit():
            print("無効なフォーマットです。'0000'を使用します")
            return (0, 0, 0, 0)
        return tuple(int(d) for d in feedback_str)

# ソルバーを実行
if __name__ == "__main__":
    print("=== 「言葉で遊ぼう」ソルバー ===")
    print("情報理論最適化版")
    print("-------------------------------------")
    print("フィードバック記号:")
    print("0. 灰色: 単語に含まれない文字")
    print("1. 上下矢印: 同じ行の仮名が同じ位置に存在")
    print("2. 左右矢印: 同じ列の仮名が同じ位置に存在")
    print("3. 黄色: 別の位置に存在する文字")
    print("4. 緑色: 正正しい位置の文字")
    print("5. 黄緑丸: 変種が同じ位置に存在 (濁点・半濁点・小文字)")
    print("-------------------------------------")
    
    solver = EntropySolver()
    solver.run()