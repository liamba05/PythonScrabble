from game.scrabble_players import ComputerPlayer
from collections import namedtuple
import random
import pickle
import os

class QLearningPlayer(ComputerPlayer):
    def __init__(self, id, init_tiles, rulebook, name=None):
        super().__init__(id, init_tiles, rulebook, name)
        self.w_file = 'q_weights.pkl'
        self.eps = 0.01
        self.lr = 0.01
        self.gamma = 0.9
        self.w = self.load_w()
        
        self.last_s = None
        self.last_score = 0
        self.last_feats = None
        self.last_q = 0

    def load_w(self):
        if os.path.exists(self.w_file):
            try:
                with open(self.w_file, 'rb') as f:
                    return pickle.load(f)
            except:
                pass
        # default weights
        return {'score': 1.0, 'leave': -0.5, 'bal': -0.5, 'bias': 0.0}

    def save_w(self):
        with open(self.w_file, 'wb') as f:
            pickle.dump(self.w, f)

    def get_feats(self, move, board, tiles):
        # score
        s = self.rulebook.score_move(move, board)
        
        # tiles left
        rem = self.rem_tiles(move, board, tiles)
        
        # penalty for bad tiles left
        l_score = sum([self.rulebook.tile_scores.get(t, 0) for t in rem])
        
        # balance vowels/cons
        vowels = set('AEIOU')
        n_v = sum(1 for t in rem if t in vowels)
        # ideal is like 40-50%
        bal = abs(n_v - len(rem) * 0.45)

        return {'score': s, 'leave': l_score, 'bal': bal, 'bias': 1.0}

    def rem_tiles(self, move, board, tiles):
        # figure out what tiles are left
        y, x = move.coords
        is_d = (move.dir == 'D')
        is_r = (move.dir == 'R')
        
        copy = list(tiles)
        
        for i, l in enumerate(move.word):
            # check board
            b_char = board[y + i*is_d][x + i*is_r]
            if b_char == ' ':
                # used from rack
                if l.islower(): 
                    if '?' in copy: copy.remove('?')
                else:
                    if l in copy: copy.remove(l)
                    elif '?' in copy: copy.remove('?')
        return copy

    def calc_q(self, feats):
        return sum(self.w[k] * feats[k] for k in feats)

    def get_move(self, board):
        # get valid moves
        locs = self.get_valid_locations(board)
        Move = namedtuple('move', 'coords dir word')
        moves = []
        
        for l in locs:
            words = self.find_words(fixed_tiles=l.fixed, min_length=max(2, l.min), max_length=l.max)
            moves += [Move(l.coords, l.dir, w) for w in words]

        if not moves:
             return Move((-1, -1), '', '')

        # score moves
        scored = []
        for m in moves:
            f = self.get_feats(m, board, self.tiles)
            # ignore bad moves
            if f['score'] > 0:
                q = self.calc_q(f)
                scored.append((m, q, f))

        if not scored:
             return Move((-1, -1), '', '')

        # epsilon greedy
        if random.random() < self.eps:
            sel = random.choice(scored)
        else:
            sel = max(scored, key=lambda x: x[1])

        move, q, f = sel

        # update weights
        if self.last_feats:
            max_q = max(m[1] for m in scored) if scored else 0
            
            # diff
            delta = (self.last_score + self.gamma * max_q) - self.last_q
            
            # update
            for k in self.w:
                if k in self.last_feats:
                    self.w[k] += self.lr * delta * self.last_feats[k]

        # save for next time
        self.last_feats = f
        self.last_score = f['score']
        self.last_q = q
        
        self.word_hist.append(move.word)
        self.score_hist.append(f['score'])

        return move

    def end_game(self, adj):
        # final update
        if self.last_feats:
             delta = (self.last_score + adj) - self.last_q
             for k in self.w:
                if k in self.last_feats:
                    self.w[k] += self.lr * delta * self.last_feats[k]
        self.save_w()
