from game_manager import GameMaster
import sys

# train the bot
def train(eps=50):
    print(f"training for {eps} games")
    
    wins = 0
    
    for i in range(eps):
        # 2 q learning bots
        gm = GameMaster(human_count=0, computer_count=2, use_q_learning=True)
        gm.play_game(verbose=False)
        
        # check who won
        s1 = gm.player_scores[0]
        s2 = gm.player_scores[1]
        
        if s1 > s2:
            wins += 1
            
        if (i + 1) % 10 == 0:
            print(f"game {i+1} done. win rate: {wins/(i+1)}")

    print("done training")

if __name__ == "__main__":
    n = 50
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    train(n)
