import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
import math
import ray
from rdp import rdp
import matplotlib.pyplot as plt


class GestureTypingSuggestion():
    isCornerAngle = True
    isNormalize = False
    isVisualize = False
    alpha = 0.95
    #for language model



    def set_alpha(self, alpha):
        self.alpha = alpha

    # have to explicitly shutdown the ray worker
    def shutdown(self):
        ray.shutdown()

    def __init__(self):
        ray.init()
        self.keyboard_layout = [
            'qwertyuiop',
            'asdfghjkl',
            'zxcvbnm'
        ]
        self.key_position = self.set_key_position()

        self.word_list = self.set_word_list()
        self.word_and_path_list = []
        self.word_angle_list = []
        for word, frequency in self.word_list:
            if len(word) > 1:
                word_path = self.convert_sequence_to_path(word)
                if self.isCornerAngle:
                    angle_sequence = self.get_corner_angle_sequence_from_position(word_path)
                else:
                    angle_sequence = self.get_angle_sequence_from_position(word_path)

                '''
                if self.isNormalize:
                    self.word_and_path_list.append((word, frequency, self.normalize(word_path), len(angle_sequence)))
                else:
                    self.word_and_path_list.append((word, frequency, word_path, len(angle_sequence)))
                '''
                self.word_and_path_list.append((word, frequency, word_path, len(angle_sequence)))
                self.word_angle_list.append((word, frequency, angle_sequence, len(angle_sequence)))


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
            if key != sequence[i-1]:
                path.append(self.key_position[key])
            else:
                path.append(self.key_position[key])
        return np.array(path)


    def get_score(self, results):
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
            result[0] = (self.alpha*r/sum_r)+((1-self.alpha)*n/sum_n)
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


    def normalize(self, positions):
        minX = 999
        minY = 999
        maxX = -999
        maxY = - 999
        for x,y in positions:
            if x < minX:
                minX = x
            else:
                if x > maxX:
                    maxX = x
            if y < minY:
                minY  = y
            else:
                if y > maxY:
                    maxY = y
        lenX = maxX - minX
        lenY = maxY - minY

        if(lenX > lenY):
            maxLen = lenX
        else:
            maxLen = lenY

        if maxLen == 0:
            maxLen = 1

        normalized = []
        for x, y in positions:
            normalized.append( [(x-positions[0][0])/maxLen, (y-positions[0][1])/maxLen] )
        return normalized




    min_angle = 15
    def get_angle_sequence_from_position(self, positions):
        #print(positions)
        positions = self.normalize(positions)
        #print(positions)
        positions = np.diff(positions, axis= 0)
        np.insert(positions, 0, 0)
        #print(positions)
        simplified_trajectory = rdp(positions, epsilon=0.3)
        #minimum angle = 15 degree
        #print(simplified_trajectory)
        # Compute the direction vectors on the simplified_trajectory.
        directions = np.diff(simplified_trajectory, axis=0)
        xs = simplified_trajectory.T[0]
        ys = simplified_trajectory.T[1]

        angle_sequence= np.rad2deg(np.arctan2(xs,ys))
        #idx = np.where(np.abs(angle_sequence) > self.min_angle)[0] + 1
        # Select the index of the points with the greatest theta.
        # Large theta is associated with greatest change in direction.
        #sequence = list(filter(lambda angle: np.abs(angle) < self.min_angle, angle_sequence))
        sequence = []
        sequence.append(0)
        for angle in angle_sequence:
            if np.abs(angle) > self.min_angle:
                sequence.append(angle)
        sequence.append(0)
        #print(sequence)

        return sequence

    def get_corner_angle_sequence_from_position(self, positions):
        #print(positions)
        if self.isNormalize:
            positions = self.normalize(positions)
        #positions = np.diff(positions, axis= 0)
        #np.insert(positions, 0, 0)
        #print(positions)
        simplified_trajectory = rdp(positions, epsilon=0.3)
        #minimum angle = 15 degree
        #print(simplified_trajectory)
        # Compute the direction vectors on the simplified_trajectory.

        simplified_trajectory = np.array(simplified_trajectory)
        xs = simplified_trajectory.T[0]
        ys = simplified_trajectory.T[1]

        angle_sequence= np.rad2deg(np.arctan2(xs,ys))
        angle_sequence = np.array(angle_sequence)
        positions = np.array(positions)
        #idx = np.where(np.abs(angle_sequence) > self.min_angle)[0] + 1
        # Select the index of the points with the greatest theta                .
        # Large theta is associated with greatest change in direction.
        #sequence = list(filter(lambda angle: np.abs(angle) < self.min_angle, angle_sequence))
        sequence = []
        sequence.append(0)
        for angle in angle_sequence:
            if np.abs(angle) > self.min_angle:
                sequence.append(angle)
        #sequence = list(np.diff(sequence))
        sequence.append(0)
        #print(sequence)

        if self.isVisualize:
            print(positions)
            self.visualize_path(positions, simplified_trajectory, angle_sequence)
        return sequence
    @ray.remote
    def get_distance_from_dtw(target_path, word_path, word, frequency):
        distance, path = fastdtw(target_path, word_path, dist=euclidean)
        return [distance, word, frequency]

    @ray.remote
    def get_angle_distance_from_dtw(target_path, word_path, word, frequency):
        distance, path = fastdtw(target_path, word_path, dist=euclidean)
        return [distance, word, frequency]

    def get_suggestions_from_position_by_angle(self, position, suggest_num):
        target, target_path = self.convert_position_to_path(position)
        #closest_key = self.get_closest_keys_from_position(target_path[-1])
        first_letter_neighbor = self.get_closest_keys_from_key(target[0])
        #print(first_letter_neighbor)
        if self.isCornerAngle:
            angle_sequence = self.get_corner_angle_sequence_from_position(position)
        else:
            angle_sequence = self.get_angle_sequence_from_position(position)
        print(angle_sequence)
        target_word_and_path_list = list(
            filter(
            lambda word_and_path: (
                (word_and_path[0][0] in first_letter_neighbor) and (np.abs(len(angle_sequence) - word_and_path[3]) < 2)
            ),
            self.word_angle_list
            )
        )
        results = ray.get([
            self.get_angle_distance_from_dtw.remote(
            angle_sequence, target_angle_sequence,
            word, frequency
            )
            for word, frequency, target_angle_sequence, num_corner in target_word_and_path_list
        ])
        results.sort()
        results = self.get_score(results)
        results.sort(reverse=True)




        return results[:suggest_num]

    def visualize_path(self, trajectory, simplified, corners):
        sx, sy = simplified.T
        x, y = trajectory.T

        # Visualize trajectory and its simplified version.
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(x, y, 'r--', label='trajectory')
        ax.plot(sx, sy, 'b-', label='simplified trajectory')
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.legend(loc='best')

        # Select the index of the points with the greatest theta.
        # Large theta is associated with greatest change in direction.
        idx = np.where(np.abs(corners) > self.min_angle)[0]
        print(idx)

        try:

            # Visualize valuable turning points on the simplified trjectory.
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.plot(sx, sy, 'gx-', label='simplified trajectory')
            ax.plot(sx[idx], sy[idx], 'ro', markersize=7, label='turning points')
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.legend(loc='best')
            plt.show()
        except:
            print('exception')

    def get_suggestions_from_position_normalized(self, position, suggest_num, letters):


        normalized_positions = self.normalize(position)
        print(letters)
        print(position)
        print(normalized_positions)

        if self.isCornerAngle:
            angle_sequence = self.get_corner_angle_sequence_from_position(position)
        else:
            angle_sequence = self.get_angle_sequence_from_position(position)

        #target, target_path = self.convert_position_to_path(normalized_positions)
        first_letter_neighbor = self.get_closest_keys_from_key(letters[0])
        #closest_key = self.get_closest_keys_from_position(target_path[0])
        target_word_and_path_list = list(
            filter(
            lambda word_and_path: (
                (word_and_path[0][0] in first_letter_neighbor) and (np.abs(len(angle_sequence) - word_and_path[3]) < 2)
                #(word_and_path[0][0] == letters[0])
                #(word_and_path[0][-1] in closest_key)
            ),
            self.word_and_path_list
            )
        )
        print(len(target_word_and_path_list))
        results = ray.get([
            self.get_distance_from_dtw.remote(
            normalized_positions, word_path,
            word, frequency
            )
            for word, frequency, word_path, num_corner in target_word_and_path_list
        ])
        results.sort()
        results = self.get_score(results)
        results.sort(reverse=True)
        return results[:suggest_num]

    def get_suggestions_from_position(self, position, suggest_num):
        target, target_path = self.convert_position_to_path(position)
        closest_key = self.get_closest_keys_from_position(target_path[-1])
        #closest_key = self.get_closest_keys_from_position(target_path[0])
        target_word_and_path_list = list(
            filter(
            lambda word_and_path: (
                #(word_and_path[0][0] in closest_key)
                (word_and_path[0][0] == target[0]) and\
                (word_and_path[0][-1] in closest_key)
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

