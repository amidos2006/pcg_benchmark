from pcg_benchmark.probs.problem import Problem
from pcg_benchmark.probs.utils import get_range_reward
from pcg_benchmark.spaces import ArraySpace, IntegerSpace, DictionarySpace
import numpy as np
from PIL import Image
from difflib import SequenceMatcher
import os

def _getWords(letters, dictionary):
    results = []
    for i in range(2**len(letters)):
        binary = format(i, f'0{len(letters)}b')
        if binary.count('1') > len(letters) - 2:
            continue
        word = ""
        for bi,b in enumerate(binary):
            if b == '1':
                word += letters[bi]
        if word in dictionary:
            results.append((word, len(max(binary.split('0')))))
    return results

class EliminationProblem(Problem):
    def __init__(self, **kwargs):
        Problem.__init__(self, **kwargs)

        self._short_percentage = kwargs.get("short_percentage")
        self._long_percentage = kwargs.get("long_percentage")
        self._diversity = kwargs.get("diversity", 0.6)
        self._offset = kwargs.get("offset", 0.2)

        f = open(os.path.dirname(__file__) + "/dictionary.txt")
        lines = f.readlines()
        self._dictionary = {}
        for l in lines:
            word = l[:-1].strip().lower()
            if len(word) < 3 or "-" in word or "." in word:
                continue
            self._dictionary[word] = 1
        f.close()
        f = open(os.path.dirname(__file__) + "/count.txt")
        lines = f.readlines()
        self._common_words = {}
        for l in lines:
            parts = l.split("\t")
            word = parts[0].strip().lower()
            frequency = int(parts[1])
            if(len(word) < 3 or not (word in self._dictionary)):
                continue
            self._common_words[word] = frequency
        f.close()

        self._content_space = ArraySpace((8,), IntegerSpace(26))
        self._control_space = DictionarySpace({"sequence": IntegerSpace(3, 6)})

    def info(self, content):
        letters = []
        for c in content:
            letters.append(chr(97 + c))
        all_words = _getWords(letters, self._dictionary)
        words_3 = []
        words_4 = []
        words_5 = []
        words_6 = []
        words_7 = []
        words_8 = []
        final_words = [words_3, words_4, words_5, words_6, words_7, words_8]
        for w,seq in all_words:
            is_common = 0
            if w in self._common_words:
                is_common = 1
            final_words[len(w) - 3].append((w, seq, is_common))
        return {
            "words_3": words_3, "words_4": words_4, "words_5": words_5, 
            "words_6": words_6, "words_7": words_7, "words_8": words_8,
            "total": len(all_words), "word": "".join(letters)
        }
    
    def quality(self, info):
        short_word_common = 0
        tshort_word_common = 0
        for i in range(3,5):
            for w in info[f"words_{i}"]:
                short_word_common += w[2]
                tshort_word_common += 1
        long_word_common = 0
        tlong_word_common = 0
        for i in range(5,7):
            for w in info[f"words_{i}"]:
                long_word_common += w[2]
                tlong_word_common += 1
        tunallowed_words = 0
        for i in range(7,9):
            tunallowed_words += 1
        constraints = get_range_reward(tshort_word_common, 0, 1, info["total"]) +\
                        get_range_reward(tlong_word_common, 0, 1, info["total"]) +\
                        get_range_reward(tunallowed_words, 0, 0, 0, info["total"])
        constraints /= 3.0
        added = 0.0
        if tshort_word_common > 0 and tlong_word_common > 0 and tunallowed_words == 0:
            added += get_range_reward(short_word_common / tshort_word_common, 0, max(0, self._short_percentage - self._offset), \
                                      min(1, self._short_percentage + self._offset), 1)
            added += get_range_reward(long_word_common / tlong_word_common, 0, max(0, self._long_percentage - self._offset), \
                                      min(1, self._long_percentage + self._offset), 1)
        added /= 2.0
        return constraints + added / 2.0
    
    def diversity(self, info1, info2):
        ratio = SequenceMatcher(None, info1["word"], info2["word"]).ratio()
        return get_range_reward(1 - ratio, 0, self._diversity, 1.0)
    
    def controlability(self, info, control):
        unallowed_seq = 0
        total_seq = 0
        for i in range(3, 9):
            for w in info[f"words_{i}"]:
                if w[1] == i:
                    if i > control["sequence"]:
                        unallowed_seq += 1
                    total_seq += 1
        if total_seq == 0:
            return 1.0
        return get_range_reward(unallowed_seq, 0, 0, 0, total_seq)

    def render(self, content):
        scale = 16
        graphics = []
        for i in range(26):
            graphics.append(Image.open(os.path.dirname(__file__) + f"/images/{chr(97+i)}.png").convert('RGBA'))
        lvl = np.array(content)
        lvl_image = Image.new("RGBA", (len(lvl)*scale, scale), (0,0,0,255))
        for x in range(len(lvl)):
            lvl_image.paste(graphics[lvl[x]], (x*scale, 0, (x+1)*scale, scale))
        return lvl_image