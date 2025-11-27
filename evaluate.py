from game_manager import GameMaster
from game.q_learning_player import QLearningPlayer
import matplotlib.pyplot as plt

#Allows for only evaluation to run
import builtins
builtins.input = lambda *args, **kwargs: "CPU"

num_games = 300
def evaluate(num_games):
    #Initialize a q_learning_player and baseline win counter
    q_learning_wins = 0
    win_rates = []
    baseline_wins = 0
    for i in range(num_games):
        match = GameMaster(human_count=0, computer_count=2, use_q_learning=False)
        match.reset_game()
        #Generates 7 tiles
        q_player = QLearningPlayer(id=1, init_tiles=match.bag.grab(7), rulebook=match.rulebook)
        match.players[0] = q_player
        match.play_game(verbose=False)

        q_score = match.player_scores[0]
        baseline_score = match.player_scores[1]
        if q_score > baseline_score:
            q_learning_wins += 1
        else:
            baseline_wins += 1
        #Keeps track of progress every 10 games
        if (i+1) % 10 == 0:
            completed_games = i + 1
            win_rate = (q_learning_wins / completed_games) * 100
            win_rates.append(win_rate)
            print(f"{completed_games}/{num_games} games; Win rate: {win_rate:.1f}%")
    total_win_rate = (q_learning_wins/num_games) * 100
    print(f"Q-learning average win rate: {total_win_rate:.1f}%")
    print(f"Computer average win rate: ({100 - total_win_rate:.1f}%)")
    return win_rates
rates = evaluate(300)
x = [i for i in range(10, 301, 10)]

#Plotting win rate over time
plt.plot(x, rates, color='red')
plt.xlabel("Game Number")
plt.ylabel("Win Rate %")
plt.title("Q-learning Win Rates Over Time")
plt.show()

if __name__ == '__main__':
    evaluate(300)