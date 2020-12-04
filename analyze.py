# -*- coding: utf-8 -*-

from GestureTypingGAT import GestureTypingSuggestion
import time
import math

import logging

# set alpha
gts = GestureTypingSuggestion()


def get_words_to_check(fileName):
    words =[]
    with open(fileName) as f_r:
        lines = f_r.read().splitlines()
        for line in lines:
            line = line.lower()
            words.append(line)
    return words


def interpolate_path(path, num):

    for x, y in path:
        a = 1


def analyze(words, alpha):
    # 11
    match_order_count = [0,0,0,0,
                         0,0,0,0,
                         0,0,0,0,
                         0,0,0,0]
    match_order_max = -1
    gts.set_alpha(alpha)
    result_writer = open('result' + str(alpha)+'.csv', 'w')
    result_writer.write('matchOrder,score,procTime,TARGET\n')

    num_suggestion = 100
    num = 1
    print('start-- time consumed: ' + str(time.time() - analyze_start_time))

    total_num = len(words)
    progress = 0
    progress_check = 0
    max_process_time = 0
    min_process_time = 10000
    mean_process_time = 0
    start_time_block = time.time()
    for word in words:

        start_time = time.time()
        num = num + 1
        isHit = False
        positions = gts.convert_sequence_to_path(word)
        start_time = time.time()
        #suggestions = gts.get_suggestions_from_position_by_angle(positions, num_suggestion, word)
        suggestions = gts.get_suggestions_from_position_normalized(positions, num_suggestion, word)
        process_time = time.time() - start_time

        if process_time < min_process_time:
            min_process_time = process_time
        if process_time > max_process_time:
            max_process_time = process_time

        mean_process_time = mean_process_time + process_time
        #print(suggestions)

        suggestion_list = ''
        match_order= -1
        match_score = 0
        order = -1
        for score, suggestion, frequency in suggestions:
            suggestion_list = suggestion_list + ',' + suggestion

            order = order + 1
            if suggestion == word:
                isHit = True
                match_order = order
                match_score = score



        if isHit:
            if match_order_max < match_order:
                match_order_max = match_order
            if match_order < 5:
                match_order_count[match_order + 1] = match_order_count[match_order+1] + 1
            else:
                order_check = math.floor(match_order / 10)
                match_order_count[5 + order_check] = match_order_count[5 + order_check]  + 1
            print(match_order, word,  '  -- time: ' + str(time.time() - start_time))
        else:
            match_order_count[0] = match_order_count[0] + 1
            print('[' + str(num) + ']  ' + word + '  -- time: ' + str(time.time() - start_time))

        if num % 20 == 0:
            print('Alpha: ' + str(alpha) + ' -- ' + str(num) + ' / ' + str(total_num) + ' -- time consumed: ' + str(time.time() - start_time_block))
            start_time_block = time.time()

        '''
        progress_check = progress_check + num / total_num
        if progress_check > 1:
            print('PROGRESS: ', round((num / total_num) * 100), '%    -- time consumed: ' + str(time.time() - analyze_start_time))
            progress_check = 0
        '''

        result_writer.write(str(match_order) + ',' +  str(match_score) +',' +str(process_time) + ',' + word + ',' + suggestion_list + '\n')



    result_writer.close()
    print(alpha, 'PROCESS DURATION ---', math.floor(mean_process_time), 's')
    print('Average', mean_process_time / total_num)
    print('min: ', min_process_time)
    print('Max: ', max_process_time)
    print('Top Most: ', match_order_count[1])
    print('No Hit: ', match_order_count[0])
    print('Max: ', match_order_max)
    #gts.get_suggestions_from_position(positions, 10)
    return match_order_count, match_order_max

if __name__ == '__main__':

    analyze_start_time = time.time()

    words = get_words_to_check('words_to_check.csv')


    words = list(filter(lambda w: len(w) > 1, words))

    result_writer = open('total.csv', 'w')
    result_writer.write('Alpha,Not Hit,1st,2nd,3rd,4th,5th,10,20,30,40,50,60,70,80,90,100,Max\n')

    alphas = [0.95]
    #alphas = [1, 0.99, 0.98, 0.97,0.95,0.9,0.7,0.5,0.3,0.1,0.05]
    for alpha in alphas:
        words = ['less']
        match_order_count, match_order_max =  analyze(words, alpha)
        result_writer.write(str(alpha))
        for order in match_order_count:
            result_writer.write(',' + str(order))
        result_writer.write(','+str(match_order_max))
        result_writer.write('\n')



    result_writer.close()
    gts.shutdown()