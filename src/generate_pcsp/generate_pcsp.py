import pandas as pd
import numpy as np
import glob
from tqdm import tqdm as tqdm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import math
import warnings
import requests
import json
import os
warnings.simplefilter("ignore")


# generate pcsp file
def generate_pcsp(params, date, ply1_name, ply2_name, hand1, hand2):
    VAR = 'var.txt'
    HAND = '%s_%s.txt' % (hand1, hand2)
    PATH_TO_MODELS = '../models/'

    file_name = '%s_%s_%s_' % (date, ply1_name.replace(' ', '-'), ply2_name.replace(' ', '-'))
    file_name += '%s-%s.pcsp' % (hand1, hand2)
    file_name = os.path.join(PATH_TO_MODELS, file_name)
    # write to file
    lines = []
    with open(VAR) as f:
        lines_1 = f.readlines()
    lines_2 = []
    for i, p in enumerate(params):
        lines_2.append('#define p%d %d;\n' % (i, p))
    with open(HAND) as f:
        lines_3 = f.readlines()
    lines = lines_1 + lines_2 + lines_3
    with open(file_name, 'w') as f:
        for line in lines:
            f.write(line)


# obtain parameters
'''
12. Shot Type (1=1st serve, 2=2nd serve, 3=return, 4=rally)
13. From which court (1=deuce, 2=middle, 3=ad)
14. Shot (1~20 are forehand shots, 21~40 are backhand shots, 41 is trick shot, 99=unknown), detailed codes for all shots are:
    1-forehand, 22-backhand, 3-forehand chip/slice, 24-backhand slice, 5-forehand volley, 26-backhand volley, 7-smash, 28-backhand smash
    9-forehand drop shot, 30-backhand drop shot, 11-forehand lob, 32-backhand lob, 13-forehand half-volley, 34-backhand half-volley
    15-forhand swinging volley, 36-backhand swinging volley, 41-trick shot, 99-unknown shot
15. Direction (1=deuce court, 2=middle court, 3=ad court, 
    4=serve to wide, 
    5=serve to body, ()
    6=server to T, (middle service line)
    7=cross_court, 8=down_the_line, 9=inside_in, 10=inside_out, 99=unknown)
17. (Return) Depth(1=shallow, 2=deep, 3=very deep, 99=unknown)
21. Shot outcome(1=ace, 2=fault, 3=forced error, 4=unforced error, 5=-winner, 6=service winner, 7=no outcome)

'''
def get_params(df, hand):
    # Serve
    De_Serve = df.query('shot_type==1 and from_which_court==1') # 1st serve, deuce
    De_Serve_2nd = df.query('shot_type==2 and from_which_court==1') # 2nd serve, deuce
    Ad_Serve = df.query('shot_type==1 and from_which_court==3') # 1st serve, ad
    Ad_Serve_2nd = df.query('shot_type==2 and from_which_court==3') # 2nd serve, ad

    # Return
    De_ForeHandR = df.query('shot_type==3 and prev_shot_from_which_court==1 and shot<=20')  # return shot, deuce, forehand
    Ad_ForeHandR = df.query('shot_type==3 and prev_shot_from_which_court==3 and shot<=20') # return shot, ad, forehand
    De_BackHandR = df.query('shot_type==3 and prev_shot_from_which_court==1 and shot<=40 and shot>20') # return shot, deuce, backhand
    Ad_BackHandR = df.query('shot_type==3 and prev_shot_from_which_court==3 and shot<=40 and shot>20') # return shot, ad, backhand

    # Rally Stroke
    De_Stroke = df.query('shot_type==4 and from_which_court==1')
    Mid_Stroke = df.query('shot_type==4 and from_which_court==2')
    Ad_Stroke = df.query('shot_type==4 and from_which_court==3')

    results = []
    # Serve
    '''
    For each of the serves made by this player, we count the number of serves that are in, win, and error.
    '''
    for Serve in [De_Serve, De_Serve_2nd, Ad_Serve, Ad_Serve_2nd]:
        ServeT = Serve.query('direction==6') 
        ServeB = Serve.query('direction==5')
        ServeW = Serve.query('direction==4')
        serve_in = [len(x.query('shot_outcome==7')) for x in [ServeT, ServeB, ServeW]]
        serve_win = [len(Serve.query('shot_outcome in [1, 5, 6]'))]
        serve_err = [len(Serve.query('shot_outcome in [2, 3, 4]'))]
        results.append(serve_in + serve_win + serve_err)

    # Return
    '''
      [From which court, return depth, to which court]
    '''
    if hand == 'RH':  # RH
        directions = [[[[1], [1]], [[1], [3]], [[1], [2]]],                    # FH_[CC, DL, DM]
                      [[[2, 3], [3]], [[3], [1]], [[2], [1]], [[2, 3], [2]]],  # FH_[IO, II, CC, DM]
                      [[[2], [3]], [[1], [3]], [[1, 2], [1]], [[1, 2], [2]]],  # BH_[CC, II, IO, DM]
                      [[[3], [3]], [[3], [1]], [[3], [2]]]]                    # BH_[CC, DL, DM]
    else:  # LH
        directions = [[[[1, 2], [1]], [[1], [3]], [[2], [3]], [[1, 2], [2]]],  # FH_[IO, II, CC, DM]
                      [[[3], [3]], [[3], [1]], [[3], [2]]],                    # FH_[CC, DL, DM]
                      [[[1], [1]], [[1], [3]], [[1], [2]]],                    # BH_[CC, DL, DM]
                      [[[2], [1]], [[3], [1]], [[2, 3], [3]], [[2, 3], [2]]]]  # BH_[CC, II, IO, DM]
    for i, Return in enumerate([De_ForeHandR, Ad_ForeHandR, De_BackHandR, Ad_BackHandR]):
        shots = [Return.query('from_which_court in @dir[0] and to_which_court in @dir[1] and depth in @depth') 
                  for dir in directions[i]
                  for depth in [[1, 99], [2,3]] # Shallow/unknown, deep/very deep
                ]
        return_in = [len(x.query('shot_outcome==7')) for x in shots]
        return_win = [len(Return.query('shot_outcome in [1, 5, 6]'))]
        return_err = [len(Return.query('shot_outcome in [2, 3, 4]'))]
        results.append(return_in + return_win + return_err)

    # Rally
    if hand == 'RH':  # RH
        directions = [[[1, 3, 2], [3, 1, 2]], # de - FHCC, FHDL, FHDM, BHII, BHIO, BHDM
                      [[3, 1, 2], [1, 3, 2]], # mid - FHIO, FHCC, FHDM, BHIO, BHCC, BHDM
                      [[3, 1, 2], [3, 1, 2]]] # ad - FHIO, FHII, FHDM, BHCC, BHDL, BHDM

    else:  # LH
        directions = [[[1, 3, 2], [1, 3, 2]],  # de - FHIO, FHII, FHDM, BHCC, BHDL, BHDM
                      [[1, 3, 2], [3, 1, 2]],  # mid - FHIO, FHCC, FHDM, BHIO, BHCC, BHDM
                      [[3, 1, 2], [1, 3, 2]]]  # ad - FHCC, FHDL, FHDM, BHII, BHIO, BHDM
        
    # Build strokes
    '''
    Output:
    de_from_FH
    de_from_BH
    de_from_deep_from_FH
    de_from_deep_from_BH
    mid_from_FH
    ......
    ad_from_deep_from_BH
    '''
    Strokes = [
        Stroke.query(f'{depth} and {shot}')
        for Stroke in [De_Stroke, Mid_Stroke, Ad_Stroke] # Location stroke is being taken from
        for depth in ['prev_shot_depth in [1,99]', 'prev_shot_depth in [2,3]'] # ball came from shallow, from deep
        for shot in ['prev_shot<=20', 'prev_shot<=40 and prev_shot>20'] # ball came from forehand, from backhand
    ]

    for i, Stroke in enumerate(Strokes):
        directionIndex = i // 4
        FH_Stroke = Stroke.query('shot<=20')
        BH_Stroke = Stroke.query('shot<=40 and shot>20')
        FH_shots = [FH_Stroke.query('to_which_court==@to_dir and depth in @depth')  
                    for to_dir in directions[directionIndex][0]
                    for depth in [[1, 99], [2,3]] # shallow/unknown, deep/very deep
                  ]
        BH_shots = [BH_Stroke.query('to_which_court==@to_dir and depth in @depth') 
                    for to_dir in directions[directionIndex][1]
                    for depth in [[1, 99], [2,3]] # shallow/unknown, deep/very deep
                  ]
        shots = FH_shots + BH_shots
        FH_stroke_in = [len(x.query('shot_outcome==7')) for x in FH_shots]
        BH_stroke_in = [len(x.query('shot_outcome==7')) for x in BH_shots]
        stroke_win = [len(Stroke.query('shot_outcome in [1, 5, 6]'))]
        stroke_err = [len(Stroke.query('shot_outcome in [2, 3, 4]'))]
        results.append(FH_stroke_in + BH_stroke_in + stroke_win + stroke_err)

    return results


def generate_transition_probs(data, date, ply1_name, ply2_name):
    data_ply1 = data.query('ply1_name==@ply1_name and ply2_name==@ply2_name')
    data_ply2 = data.query('ply1_name==@ply2_name and ply2_name==@ply1_name')

    ply1_hand = data_ply1['ply1_hand'].iloc[0]
    ply2_hand = data_ply1['ply2_hand'].iloc[0]

    # get players params
    ply1_params = get_params(data_ply1, ply1_hand)
    ply2_params = get_params(data_ply2, ply2_hand)

    # sample
    params = sum(ply1_params, []) + sum(ply2_params, [])

    print(f'{date} - {ply1_name} : {ply2_name}')
    print(f'  {len(data_ply1.date.unique())} match')

    generate_pcsp(params, date, ply1_name, ply2_name, ply1_hand, ply2_hand)

# obtain shot-by-shot data
file = 'output-test.csv'
print('Reading CSV')
data = pd.read_csv(file, names=['ply1_name', 'ply2_name', 'ply1_hand', 'ply2_hand', 'ply1_points',
                                'ply2_points', 'ply1_games', 'ply2_games', 'ply1_sets', 'ply2_sets', 'date',
                                'tournament_name', 'shot_type', 'from_which_court', 'shot', 'direction',
                                'to_which_court', 'depth', 'touched_net', 'hit_at_depth', 'approach_shot',
                                'shot_outcome', 'fault_type', 'prev_shot_type', 'prev_shot_from_which_court',
                                'prev_shot', 'prev_shot_direction', 'prev_shot_to_which_court', 'prev_shot_depth',
                                'prev_shot_touched_net', 'prev_shot_hit_at_depth', 'prev_shot_approach_shot',
                                'prev_shot_outcome', 'prev_shot_fault_type', 'prev_prev_shot_type',
                                'prev_prev_shot_from_which_court', 'prev_prev_shot', 'prev_prev_shot_direction',
                                'prev_prev_shot_to_which_court', 'prev_prev_shot_depth',
                                'prev_prev_shot_touched_net', 'prev_prev_shot_hit_at_depth',
                                'prev_prev_shot_approach_shot', 'prev_prev_shot_outcome',
                                'prev_prev_shot_fault_type', 'url', 'description'])

# End date of data to process
date = '2018-12-31'
prev_date = (pd.to_datetime(date) - relativedelta(years=1)).strftime('%Y-%m-%d')

# 1. Get list of possible match-ups (unique combinations of date, ply1_name and ply2_name)
filtered_data = data.query('date>@prev_date and date<=@date')
player_pairs = set(tuple(sorted(t)) for t in zip(filtered_data['date'],
                                                 filtered_data['ply1_name'], filtered_data['ply2_name']))

# 2. For each match-up, generate pcsp file
for date, ply1_name, ply2_name in player_pairs:
    generate_transition_probs(filtered_data, date, ply1_name, ply2_name)
