from scipy.spatial.distance import euclidean
from fastdtw import fastdtw

import numpy as np
import math
import time
import ray


ray.init()


class GestureTypingSuggestion():
    def __init__(self):
        self.interpolation_size = 32

        self.keyboard_layout = [
            'qwertyuiop',
            'asdfghjkl',
            'zxcvbnm'
        ]
        self.key_position = self.set_key_position()

        self.word_list = self.set_word_list()
        self.word_and_path_list = []
        for word, frequency in self.word_list:
            interpolated_word_path = self.convert_word_to_interpolated_path(word)
            self.word_and_path_list.append((word, frequency, interpolated_word_path))

    def set_key_position(self):
        key_position = {}
        for row in range(len(self.keyboard_layout)):
            for col in range(len(self.keyboard_layout[row])):
                char = self.keyboard_layout[row][col]
                position = [col + 0.5 + row * 0.5, row + 0.5]
                key_position[char] = position
        return key_position

    def set_word_list(self):
        word_list = []
        with open('word_list.txt', 'r') as word_list_file:
            lines = word_list_file.read().splitlines()
            for line in lines:
                items = line.split('\t')
                word_list.append((items[0], int(items[1])))
        return word_list

    def convert_word_to_path(self, word):
        paths = []
        for i in range(len(word)):
            key = word[i]
            key_position = self.key_position[key]
            if i > 0:
                if key != word[i - 1]:
                    paths.append(key_position)
            else:
                paths.append(key_position)
        return paths

    def get_dist(self, pre, cur):
        dist_x = math.pow(cur[0] - pre[0], 2)
        dist_y = math.pow(cur[1] - pre[1], 2)
        return math.sqrt(dist_x + dist_y)

    def get_total_dist_from_path(self, paths):
        total_dist = 0

        if len(paths) > 1:
            for i, path in enumerate(paths):
                if i > 0:
                    pre_path = paths[i - 1]
                    dist = self.get_dist(pre_path, path)
                    total_dist = total_dist + dist

        return total_dist

    def up_sampling(self, datas):
        interpolated_datas = []

        if len(datas) >= self.interpolation_size:
            return interpolated_datas

        if len(datas) > 1:
            total_dist = self.get_total_dist_from_path(datas)
            unit_dist = total_dist / (self.interpolation_size - 1)
            temp_dist = 0
            for i, cur_data in enumerate(datas):
                if i > 0:
                    pre_data = datas[i - 1]
                    dist = self.get_dist(pre_data, cur_data)
                    if temp_dist != 0:
                        datas_num = int((dist - (unit_dist - temp_dist)) / unit_dist)
                        ratio = (unit_dist - temp_dist) / dist
                        start_data = [
                            pre_data[0] + (cur_data[0] - pre_data[0]) * ratio,
                            pre_data[1] + (cur_data[1] - pre_data[1]) * ratio,
                        ]
                        interpolated_datas.append(start_data)
                        for j in range(datas_num):
                            ratio = unit_dist * (j + 1) / dist
                            data_x = start_data[0] + (cur_data[0] - pre_data[0]) * ratio
                            data_y = start_data[1] + (cur_data[1] - pre_data[1]) * ratio
                            interpolated_datas.append([data_x, data_y])
                        temp_dist = (dist - (unit_dist - temp_dist)) - (datas_num * unit_dist)
                    else:
                        datas_num = int(dist / unit_dist)
                        start_data = pre_data
                        interpolated_datas.append(start_data)
                        for j in range(datas_num):
                            ratio = unit_dist * (j + 1) / dist
                            data_x = start_data[0] + (cur_data[0] - pre_data[0]) * ratio
                            data_y = start_data[1] + (cur_data[1] - pre_data[1]) * ratio
                            interpolated_datas.append([data_x, data_y])
                        temp_dist = dist - (datas_num * unit_dist)
            if self.get_dist(datas[-1], interpolated_datas[-1]) > 0.001:
                interpolated_datas.append(datas[-1])
        elif len(datas) == 1:
            for i in range(self.interpolation_size):
                interpolated_datas.append(datas[0])

        return interpolated_datas

    def down_sampling(self, datas):
        interpolated_datas = []

        if len(datas) <= self.interpolation_size:
            return interpolated_datas

        total_dist = self.get_total_dist_from_path(datas)
        unit_dist = total_dist / (self.interpolation_size - 1)
        accum_dist = 0
        min_dist = 1
        min_dist_cand = [0, 0]
        for i, cur_data in enumerate(datas):
            if i == len(datas) - 1:
                interpolated_datas.append(cur_data)
            elif i > 0:
                pre_data = datas[i - 1]
                dist = self.get_dist(pre_data, cur_data)
                accum_dist = accum_dist + dist
                ratio = accum_dist / unit_dist
                if abs(len(interpolated_datas) - ratio) < min_dist:
                    min_dist = abs(len(interpolated_datas) - ratio)
                    min_dist_cand = cur_data
                else:
                    interpolated_datas.append(min_dist_cand)
                    min_dist = 1 
            elif i == 0:
                interpolated_datas.append(cur_data)

        return interpolated_datas

    def convert_word_to_interpolated_path(self, word):
        paths = self.convert_word_to_path(word)

        interpolated_paths = []
        if len(paths) < self.interpolation_size:
            interpolated_paths = self.up_sampling(paths)
        elif len(paths) == self.interpolation_size:
            interpolated_paths = paths
        elif len(paths) > self.interpolation_size:
            interpolated_paths = self.down_sampling(paths)

        return np.array(interpolated_paths)

    @ray.remote
    def get_distance_from_dtw(target_path, word_path, word, frequency):
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

    def convert_position_to_interpolated_path(self, position):
        interpolated_paths = []
        if len(position) < self.interpolation_size:
            interpolated_paths = self.up_sampling(position)
        elif len(position) == self.interpolation_size:
            interpolated_paths = position
        elif len(position) > self.interpolation_size:
            interpolated_paths = self.down_sampling(position)

        return np.array(interpolated_paths)

    def get_closest_keys_from_position(self, position):
        key_list = []
        for char, value in self.key_position.items():
            dist = self.get_dist(position, value)
            if dist <= math.sqrt(2):
                key_list.append([dist, char])
        key_list.sort()
        return [item[1] for item in key_list[:2]]

    def get_suggestions_from_position(self, position, suggest_num):
        target_path = self.convert_position_to_interpolated_path(position)
        closest_first_key = self.get_closest_keys_from_position(target_path[0])[0]
        closest_last_keys = self.get_closest_keys_from_position(target_path[-1])

        target_word_and_path_list = list(
            filter(
                lambda word_and_path: (
                    (word_and_path[0][0] == closest_first_key) and
                    (word_and_path[0][-1] in closest_last_keys)
                ),
                self.word_and_path_list
            )
        )
        results = ray.get([
            self.get_distance_from_dtw.remote(
                target_path, word_path,
                word, frequency
            )
            for word, frequency, word_path in target_word_and_path_list
        ])
        results.sort()
        results = self.get_score(results)
        results.sort(reverse=True)
        return results[:suggest_num]
