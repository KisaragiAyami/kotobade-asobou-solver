import math
import re
import time
import pickle
import os
import csv
import sys
from collections import defaultdict
from functools import lru_cache
import inflect  # For proper pluralisation
import unicodedata  # For normalising Unicode characters

# Create inflection engine for pluralisation
p = inflect.engine()

# Base mapping: converts kana to base form (ignoring dakuten/handakuten, small to big)
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

# Row groups (行)
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

# Column groups (段)
col_groups = {
    'あ': ['あ', 'か', 'さ', 'た', 'な', 'は', 'ま', 'や', 'ら', 'わ', 'が', 'ざ', 'だ', 'ば', 'ぱ', 'ゃ'],
    'い': ['い', 'き', 'し', 'ち', 'に', 'ひ', 'み', 'り', 'ぎ', 'じ', 'ぢ', 'び', 'ぴ'],
    'う': ['う', 'く', 'す', 'つ', 'ぬ', 'ふ', 'む', 'ゆ', 'る', 'ぐ', 'ず', 'づ', 'ぶ', 'ぷ', 'ゅ', 'っ'],
    'え': ['え', 'け', 'せ', 'て', 'ね', 'へ', 'め', 'れ', 'げ', 'ぜ', 'で', 'べ', 'ぺ'],
    'お': ['お', 'こ', 'そ', 'と', 'の', 'ほ', 'も', 'よ', 'ろ', 'を', 'ご', 'ぞ', 'ど', 'ぼ', 'ぽ', 'ょ']
}

# Create mappings for row/column from groups
row_map = {}
for row_id, kanas in row_groups.items():
    for kana in kanas:
        row_map[kana] = row_id

col_map = {}
for col_id, kanas in col_groups.items():
    for kana in kanas:
        col_map[kana] = col_id

def get_base(kana):
    """Get base form of kana using base_map, fallback to itself if not found"""
    return base_map.get(kana, kana)

def get_row(kana):
    """Get row identifier for kana, returns None for ん/ー"""
    base = get_base(kana)
    if base in ['ん', 'ー']:
        return None
    return row_map.get(base, None)

def get_col(kana):
    """Get column identifier for kana, returns None for ん/ー"""
    base = get_base(kana)
    if base in ['ん', 'ー']:
        return None
    return col_map.get(base, None)

def is_variant(a, b):
    """Check if a is a variant of b (same base, not identical)"""
    if a == b:
        return False
    return get_base(a) == get_base(b)

def get_feedback(guess, answer):
    """Calculate feedback for a guess compared to the actual answer"""
    n = len(guess)
    feedback = [0] * n
    freq = defaultdict(int)
    
    # Create frequency map for answer kanas (excluding exact matches)
    for k in answer:
        freq[k] += 1

    # First pass: check for exact matches (4)
    for i in range(n):
        if guess[i] == answer[i]:
            feedback[i] = 4
            freq[answer[i]] -= 1  # Consume this occurrence

    # Second pass: check for variants at position (5)
    for i in range(n):
        if feedback[i] != 0:  # Skip already matched positions
            continue
        if is_variant(guess[i], answer[i]):
            feedback[i] = 5

    # Third pass: check for presence in answer (3)
    for i in range(n):
        if feedback[i] != 0:  # Skip already matched positions
            continue
        if freq.get(guess[i], 0) > 0:
            feedback[i] = 3
            freq[guess[i]] -= 1  # Consume this occurrence

    # Fourth pass: check for same row (1) or column (2)
    for i in range(n):
        if feedback[i] != 0:  # Skip already matched positions
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

# Caching for feedback calculations
@lru_cache(maxsize=100000)
def get_feedback_cached(guess, answer):
    """Cached version of get_feedback"""
    return get_feedback(guess, answer)

def load_wordlist(filename):
    """Load word list from a .ts file"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    # Extract words using regex
    words = re.findall(r"'(?:\\.|[^'])*'", content)
    words = [w[1:-1] for w in words]  # Remove quotes
    return words

def entropy(probabilities):
    """Calculate entropy of a probability distribution"""
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
        
        # Try to load precomputed first guess
        self.load_cache()
    
    def load_frequency_data(self, filename):
        """Load word frequency data from a CSV file"""
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
                print(f"Loaded frequency data for {p.no('word', len(frequency_dict))}")
            except Exception as e:
                print(f"Error loading frequency data: {e}")
        else:
            print(f"Frequency file {filename} not found. Using alphabetical sorting.")
        return frequency_dict
    
    def load_cache(self):
        """Load precomputed data if available"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                    self.precomputed_first_guess = cache_data.get('first_guess')
                    if self.precomputed_first_guess:
                        guess, gain = self.precomputed_first_guess
                        print(f"Loaded precomputed first guess: {guess} ({gain:.4f} bits)")
            except Exception as e:
                print(f"Error loading cache: {e}")
                self.precomputed_first_guess = None
    
    def save_cache(self):
        """Save precomputed data for future runs"""
        cache_data = {'first_guess': self.precomputed_first_guess}
        with open(self.cache_file, 'wb') as f:
            pickle.dump(cache_data, f)
    
    def precompute_first_guess(self):
        """Precompute the optimal first guess and save to cache"""
        if self.precomputed_first_guess:
            return self.precomputed_first_guess
            
        total_words = len(self.full_list)
        print(f"Precomputing optimal first guess over {p.no('word', total_words)} (this may take several minutes)...")
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
                
            # Update best guess if we found a better one
            if gain > best_gain:
                best_gain = gain
                best_guess = guess
                print(f"  New best: {best_guess} ({gain:.4f} bits)")
            
            # Print progress every 2 seconds
            current_time = time.time()
            if current_time - last_print_time >= 2:
                elapsed = current_time - start_time
                percent_complete = (idx + 1) / total_words * 100
                words_per_sec = (idx + 1) / elapsed
                est_total_time = total_words / words_per_sec
                est_remaining = est_total_time - elapsed
                
                print(f"  Processed {p.no('word', idx+1)} of {p.no('word', total_words)} ({percent_complete:.1f}%) - "
                      f"Elapsed: {elapsed:.0f}s, Remaining: ~{est_remaining:.0f}s, "
                      f"Speed: {words_per_sec:.1f} words/sec")
                
                # Print current best even if it hasn't changed
                if best_guess:
                    print(f"    Current best: {best_guess} ({best_gain:.4f} bits)")
                
                last_print_time = current_time
        
        self.precomputed_first_guess = (best_guess, best_gain)
        self.save_cache()
        
        elapsed = time.time() - start_time
        print(f"Precomputation completed in {elapsed:.1f} seconds")
        print(f"Optimal first guess: {best_guess} ({best_gain:.4f} bits)")
        
        return best_guess, best_gain
    
    def expected_information_gain(self, guess, candidates):
        """Calculate expected information gain for a guess"""
        pattern_counts = defaultdict(int)
        total = len(candidates)
        
        # Use cached patterns if available
        cache_key = (guess, tuple(candidates))
        if cache_key in self.pattern_cache:
            pattern_counts = self.pattern_cache[cache_key]
        else:
            for answer in candidates:
                # Use cached feedback if available
                cache_fb_key = (guess, answer)
                if cache_fb_key in self.feedback_cache:
                    fb = self.feedback_cache[cache_fb_key]
                else:
                    fb = get_feedback_cached(guess, answer)
                    self.feedback_cache[cache_fb_key] = fb
                pattern_counts[fb] += 1
            self.pattern_cache[cache_key] = pattern_counts
        
        # Calculate information gain
        gain = 0
        for count in pattern_counts.values():
            if count > 0:
                p_val = count / total
                gain += p_val * math.log2(total / count)
        
        return gain
    
    def find_best_guess(self, candidates):
        """Find the best guess using information theory"""
        candidate_count = len(candidates)
        # For very small candidate sets, just return the first candidate
        if candidate_count == 1:
            return candidates[0], 0
        
        best_guess = None
        best_gain = -1
        start_time = time.time()
        
        # Determine which words to evaluate as potential guesses
        # Always evaluate all candidates when feasible
        if candidate_count <= 200:
            guess_set = candidates
        else:
            # For large candidate sets, evaluate entire dictionary
            # but this might be slow - we'll provide progress updates
            guess_set = self.full_list
        
        guess_count = len(guess_set)
        print(f"  Evaluating {p.no('potential guess', guess_count)}...")
        
        # Evaluate all possible guesses in the guess set
        for idx, guess in enumerate(guess_set):
            gain = self.expected_information_gain(guess, candidates)
            
            if gain > best_gain:
                best_gain = gain
                best_guess = guess
            
            # Print progress every 10% of the way
            if (idx + 1) % max(1, guess_count // 10) == 0:
                elapsed = time.time() - start_time
                print(f"    Processed {p.no('guess', idx+1)} of {p.no('guess', guess_count)} "
                      f"({(idx+1)/guess_count*100:.1f}%)")
        
        elapsed = time.time() - start_time
        print(f"  Evaluated {p.no('guess', guess_count)} in {elapsed:.2f} seconds")
        return best_guess, best_gain
    
    def filter_candidates(self, guess, feedback, candidates):
        """Filter candidates based on feedback"""
        new_candidates = []
        for word in candidates:
            if get_feedback_cached(guess, word) == feedback:
                new_candidates.append(word)
        return new_candidates
    
    def sort_candidates(self, candidates):
        """Sort candidates by frequency (missing = 0) then alphabetically"""
        # Sort by frequency descending, then alphabetically
        return sorted(
            candidates,
            key=lambda word: (
                -self.frequency_dict.get(word, 0),  # Higher frequency first
                word  # Then alphabetical
            )
        )
    
    def display_candidates(self, candidates):
        """Display candidates with frequency information"""
        candidate_count = len(candidates)
        sorted_candidates = self.sort_candidates(candidates)
        
        if candidate_count == 1:
            print("  The only possible solution:")
        else:
            print(f"  All {p.no('possible solution', candidate_count)} (sorted by frequency):")
            
        for word in sorted_candidates:
            # Get frequency or 0 if missing
            frequency = self.frequency_dict.get(word, 0)
            # Add indicator for missing frequency data
            if frequency > 0:
                print(f"    {word} (freq: {frequency})")
            else:
                print(f"    {word} (freq: 0 - rare word)")
    
    def run(self):
        """Main solving loop"""
        total_words = len(self.full_list)
        print(f"Loaded {p.no('word', total_words)}")
        
        if self.frequency_dict:
            known = sum(1 for word in self.full_list if word in self.frequency_dict)
            known_percent = known/total_words*100
            print(f"Frequency data available for {p.no('word', known)} out of "
                  f"{p.no('word', total_words)} ({known_percent:.1f}%)")
        print("Starting solver...")
        
        # First guess handling
        if not self.precomputed_first_guess:
            print("No precomputed first guess found.")
            first_guess, first_gain = self.precompute_first_guess()
        else:
            first_guess, first_gain = self.precomputed_first_guess
            print(f"Using precomputed first guess: {first_guess} ({first_gain:.4f} bits)")
        
        # First guess
        print(f"\n=== ROUND 1 ===")
        print(f"Recommended first guess: {first_guess}")
        user_guess = input("Enter your actual first guess (or press Enter to use recommendation): ").strip()
        
        if not user_guess:
            user_guess = first_guess
        elif user_guess not in self.full_list:
            print("Word not in list, using recommendation instead")
            user_guess = first_guess
        
        # Get feedback for first guess
        feedback_str = input("Enter feedback for first guess (4 digits): ").strip()
        feedback_tuple = self.parse_feedback(feedback_str)
        
        # Filter candidates
        self.candidates = self.filter_candidates(user_guess, feedback_tuple, self.candidates)
        candidate_count = len(self.candidates)
        print(f"  {p.no('candidate', candidate_count)} remain{'s' if candidate_count == 1 else ''}")
        
        # Show all candidates when <= 50 remain
        if 0 < candidate_count <= 50:
            self.display_candidates(self.candidates)
        
        # Subsequent guesses
        round_num = 2
        while candidate_count > 1:
            print(f"\n=== ROUND {round_num} ===")
            print(f"  {p.no('candidate', candidate_count)} remain{'s' if candidate_count == 1 else ''}")
            
            # Find best guess
            start_time = time.time()
            best_guess, gain = self.find_best_guess(self.candidates)
            elapsed = time.time() - start_time
            
            # Show candidates AFTER evaluation but BEFORE recommendation
            if 0 < candidate_count <= 50:
                self.display_candidates(self.candidates)
            
            print(f"Recommended guess: {best_guess} (expected gain: {gain:.4f} bits)")
            user_guess = input("Enter your guess (or press Enter to use recommendation): ").strip()
            
            if not user_guess:
                user_guess = best_guess
            elif user_guess not in self.full_list:
                print("Word not in list, using recommendation instead")
                user_guess = best_guess
            
            # Get feedback
            feedback_str = input("Enter feedback (4 digits): ").strip()
            feedback_tuple = self.parse_feedback(feedback_str)
            
            # Filter candidates
            prev_count = candidate_count
            self.candidates = self.filter_candidates(user_guess, feedback_tuple, self.candidates)
            candidate_count = len(self.candidates)
            removed = prev_count - candidate_count
            
            # Proper pluralisation for removal message
            print(f"  Removed {p.no('candidate', removed)}, {p.no('candidate', candidate_count)} remain{'s' if candidate_count == 1 else ''}")
            
            # Show all candidates when <= 50 remain
            if 0 < candidate_count <= 50:
                self.display_candidates(self.candidates)
            
            round_num += 1
        
        # Final result
        if candidate_count == 1:
            solution = self.candidates[0]
            frequency = self.frequency_dict.get(solution, 0)
            print(f"\nSOLUTION FOUND: {solution}")
            if frequency > 0:
                print(f"  Frequency: {frequency}")
            else:
                print("  Frequency: 0 (rare word)")
        else:
            print("\nNo solution found! Possible reasons:")
            print("- Inconsistent feedback provided")
            print("- Word not in original list")
            if candidate_count > 0:
                print(f"Remaining {p.no('candidate', candidate_count)}: {', '.join(self.candidates)}")
    
    def parse_feedback(self, feedback_str):
        """Parse feedback string into tuple"""
        if len(feedback_str) != 4 or not feedback_str.isdigit():
            print("Invalid feedback format. Using '0000'")
            return (0, 0, 0, 0)
        return tuple(int(d) for d in feedback_str)

# Run the solver
if __name__ == "__main__":
    print("=== 4-Kana Japanese Word Game Solver ===")
    print("Information Theory Optimised Version")  # British spelling
    print("-------------------------------------")
    print("Feedback Encoding:")
    print("0. Grey square    : Kana not in target")
    print("1. Vertical arrows: Same row (行) as target kana")
    print("2. Horizontal arrows: Same column (段) as target kana")
    print("3. Yellow square  : Kana exists elsewhere in target")
    print("4. Green square   : Correct kana & position")
    print("5. Lime circle    : Variant exists in target position")
    print("-------------------------------------")
    print("Note: Variants include dakuten (か→が), handakuten (は→ぱ),")
    print("      and small kana (つ→っ)")
    print("-------------------------------------")
    
    # Check for required libraries
    try:
        import inflect
    except ImportError:
        print("Error: The 'inflect' library is required.")
        print("Please install it with: pip install inflect")
        sys.exit(1)
    
    solver = EntropySolver()
    solver.run()
