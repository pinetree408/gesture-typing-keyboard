import re
p = re.compile('[a-z]+')

def is_english_word(sequence):
    pure_char_list = p.findall(sequence)
    if len(pure_char_list) == 1:
        if len(pure_char_list[0]) == len(sequence):
            return True
        else:
            return False
    else:
        return False

phrases_unique_word_list = []
with open('phrases.txt') as f_r:
    lines = f_r.read().splitlines()
    for line in lines:
        line = line.lower()
        temp_word_list = line.split(' ')
        for word in temp_word_list:
            if is_english_word(word) and not word in phrases_unique_word_list:
                phrases_unique_word_list.append(word)
print(len(phrases_unique_word_list))

word_list = []
with open('raw_word_list.txt', 'r') as f_r:
    word_dict = {}
    lines = f_r.read().splitlines()
    for line in lines:
        temp_word_list = line.split('\t')
        word = temp_word_list[0].lower()
        freq = int(temp_word_list[1])
        if is_english_word(word):
            if word in word_dict:
                word_dict[word] = word_dict[word] + freq
            else:
                word_dict[word] = freq
    word_dict_list = []
    for key, value in word_dict.items():
        temp = [value, key]
        word_dict_list.append(temp)
    word_dict_list.sort(reverse=True)
    print(len(word_dict_list))
    print(word_dict_list[:5])

    idx_list = []
    for unique_word in phrases_unique_word_list:
        is_unique_word_in_list = False
        for i, item in enumerate(word_dict_list):
            if item[1] == unique_word:
                idx_list.append(i)
                is_unique_word_in_list = True
                break
        if not is_unique_word_in_list:
            print("There is no unique word in the raw word list")
    print(len(idx_list))
    print(idx_list[:5])

    word_list_size = 10000
    for i, item in enumerate(word_dict_list):
        if i < word_list_size:
            word_list.append(item)
        else:
            if i in idx_list:
                if i == max(idx_list):
                    print(item)
                word_list.append(item)
        if i == max(idx_list):
            break
print(len(word_list))

with open('word_list.txt', 'w') as f_w:
    for word in word_list:
        f_w.write(word[1] + '\t' + str(word[0]) + '\n')
