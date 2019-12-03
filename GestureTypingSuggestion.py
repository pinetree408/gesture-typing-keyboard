import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
import math
import multiprocessing


class GestureTypingSuggestion():
    def __init__(self):
        self.keyboard_layout = [
            'qwertyuiop',
            'asdfghjkl',
            'zxcvbnm'
        ]
        self.key_position = self.set_key_position()

        self.word_list = self.set_word_list()
        self.word_and_path_list = []
        for word, frequency in self.word_list:
            word_path = self.convert_sequence_to_path(word)
            self.word_and_path_list.append((word, frequency, word_path))

    def set_key_position(self):
        key_position = {}
        for row in range(len(self.keyboard_layout)):
            for col in range(len(self.keyboard_layout[row])):
                char = self.keyboard_layout[row][col]
                position = [col+0.5+row*0.5, row+0.5]
                key_position[char] = position
        return key_position

    def get_closest_keys_from_key(self, key):
        key_list = []
        point = self.key_position[key]
        for char, value in self.key_position.items():
            dist_x = math.pow(point[0]-value[0], 2)
            dist_y = math.pow(point[1]-value[1], 2)
            dist = math.sqrt(dist_x+dist_y)
            if dist <= math.sqrt(2):
                key_list.append(char)
        return key_list

    def get_closest_keys_from_position(self, position):
        key_list = []
        for char, value in self.key_position.items():
            dist_x = math.pow(position[0]-value[0], 2)
            dist_y = math.pow(position[1]-value[1], 2)
            dist = math.sqrt(dist_x+dist_y)
            if dist <= math.sqrt(2):
                key_list.append([dist, char])
        key_list.sort()
        return [item[1] for item in key_list[:2]]

    def set_word_list(self):
        word_list = []
        with open('word_list.txt', 'r') as word_list_file:
            lines = word_list_file.read().splitlines()
            for line in lines:
                items = line.split('\t')
                word_list.append((items[0], int(items[1])))
        return word_list

    def convert_sequence_to_path(self, sequence):
        path = []
        for i in range(len(sequence)):
            key = sequence[i]
            if i > 0:
                if key != sequence[i-1]:
                    path.append(self.key_position[key])
            else:
                path.append(self.key_position[key])
        return np.array(path)

    def get_distance_from_dtw(self, item):
        target_path = item[0]
        word_path = item[1]
        word = item[2]
        frequency = item[3]
        distance, path = fastdtw(target_path, word_path, dist=euclidean)
        return [distance, word, frequency]

    def get_score(self, results):
        alpha = 0.95
        sum_r = 0.0
        sum_n = 0.0
        for result in results:
            r = 1.0/(1.0+result[0])
            sum_r = sum_r+r
            n = result[2]
            sum_n = sum_n+n
        for result in results:
            r = 1.0/(1.0+result[0])
            n = result[2]
            result[0] = (alpha*r/sum_r)+((1-alpha)*n/sum_n)
        return results

    def convert_position_to_path(self, position):
        target_list = []
        for i, point in enumerate(position):
            min_dist = len(self.keyboard_layout)*len(self.keyboard_layout[0])
            target_key = ''
            for key, value in self.key_position.items():
                dist_x = math.pow(point[0]-value[0], 2)
                dist_y = math.pow(point[1]-value[1], 2)
                dist = math.sqrt(dist_x+dist_y)
                if min_dist > dist:
                    min_dist = dist
                    target_key = key
            if len(target_list) != 0:
                if target_list[len(target_list)-1][0] == target_key:
                    if target_list[len(target_list)-1][2] > min_dist:
                        target_list[len(target_list)-1] = [
                            target_key, point, min_dist
                        ]
                else:
                    target_list.append([target_key, point, min_dist])
            else:
                target_list.append([target_key, point, min_dist])

        target = ''.join([target_item[0] for target_item in target_list])
        target_path = [target_item[1] for target_item in target_list]
        return (target, target_path)

    def get_suggestions_from_position(self, poistion, suggest_num):
        target, target_path = self.convert_position_to_path(poistion)
        closest_key = self.get_closest_keys_from_position(target_path[-1])
        target_word_and_path_list = list(
            filter(
                lambda word_and_path: (
                    (word_and_path[0][0] == target[0]) and\
                    (word_and_path[0][-1] in closest_key)
                ),
                self.word_and_path_list
            )
        )
        num_cores = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(num_cores)
        target_list = [
            [target_path, word_path, word, frequency]
            for word, frequency, word_path in target_word_and_path_list
        ]
        results = pool.map(self.get_distance_from_dtw, target_list)
        results.sort()
        results = self.get_score(results)
        results.sort(reverse=True)
        return results[:suggest_num]

    def get_suggestions_from_key(self, target, suggest_num):
        target_path = self.convert_sequence_to_path(target)
        closest_key = self.get_closest_keys_from_key(target[-1])
        target_word_and_path_list = list(
            filter(
                lambda word_and_path: (
                    (word_and_path[0][0] == target[0]) and\
                    (word_and_path[0][-1] in closest_key)
                ),
                self.word_and_path_list
            )
        )
        num_cores = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(num_cores)
        target_list = [
            [target_path, word_path, word, frequency]
            for word, frequency, word_path in target_word_and_path_list
        ]
        results = pool.map(self.get_distance_from_dtw, target_list)
        results.sort()
        results = self.get_score(results)
        results.sort(reverse=True)
        return results[:suggest_num]
