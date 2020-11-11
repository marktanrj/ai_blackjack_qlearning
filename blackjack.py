import time
import random
import pickle

class DeckHelpers:
    @staticmethod
    def getCard():
        deck = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        color = ""
        if random.uniform(0, 1) <= (2/3):
            color = "black"
        else:
            color = "red"
        value = random.choice(deck)

        return (value, color)
        # return (value, "black")

    @staticmethod
    def getSumOfCards(cards):
        totalSum = 0
        for card in cards:
            if card[1] == "red":
                totalSum -= card[0]
            else:
                totalSum += card[0]
        return totalSum

class BackJackGame:
    def __init__(self, enableLog=True):
        self.done = False
        self.training = False

        self.player = None
        self.dealer = None
        self.possible_moves = ["hit", "stick"]
        self.only_stick_move = ["stick"]

        self.stats = {"win": 0, "lose": 0, "draw": 0, "playerbust":0, "dealerbust": 0}
        self.enableLog = enableLog

    def initializeTraining(self, player, dealer):
        if(isinstance(player, Qlearning) and isinstance(dealer, Dealer)):
            self.training = True
            self.player = player
            self.dealer = dealer
            

    def train(self, iterations, continueTrainingFromState=False):
        if continueTrainingFromState:
            try:
                self.player.loadQtable("blackjackAIstate")
            except Exception as error:
                print(str(error))
        if(self.training):
            for i in range(iterations):
                if self.enableLog: print("training iteration: ", i)
                if i%10000 == 0: print("training iteration: ", i)
                
                self.player.resetLastStateVariables()
                self.player.emptyCards()
                self.dealer.emptyCards()
                self.player.drawCard()
                self.dealer.drawCard()

                # AI player's turn
                playerMove = self.player.epslion_greedy(self.possible_moves)
                while playerMove == "hit":
                    self.player.drawCard()
                    is21orAbove = self.player.is21orAbove()
                    if is21orAbove:
                        playerMove = self.player.epslion_greedy(self.only_stick_move)
                    else:
                        playerMove = self.player.epslion_greedy(self.possible_moves)

                # dealer's turn
                dealerDone = self.dealer.isAbove17orBust()
                while not dealerDone:
                    self.dealer.drawCard()
                    dealerDone = self.dealer.isAbove17orBust()
                
                # evaluate
                reward = self.evaluate(self.player.cards, self.dealer.cards)
                self.player.updateQ(reward, self.possible_moves)

    def evaluate(self, playerCards, dealerCards):
        playerSum = DeckHelpers.getSumOfCards(playerCards)
        dealerSum = DeckHelpers.getSumOfCards(dealerCards)
        
        if playerSum > 21 or playerSum < 1:
            if self.enableLog: print(f"Bust - player:{playerSum}, dealer:{dealerSum}, len:{len(playerCards)}")
            self.stats["playerbust"] += 1
            return -1
        elif playerSum > dealerSum:
            if self.enableLog: print(f"Win - player:{playerSum}, dealer:{dealerSum}, len:{len(playerCards)}")
            self.stats["win"] += 1
            return 1
        elif dealerSum > 21 or dealerSum < 1:
            if self.enableLog: print(f"Dealer Bust, Player Win - player:{playerSum}, dealer:{dealerSum}, len:{len(playerCards)}")
            self.stats["dealerbust"] += 1
            return 1
        elif dealerSum > playerSum:
            if self.enableLog: print(f"Lose - player:{playerSum}, dealer:{dealerSum}, len:{len(playerCards)}")
            self.stats["lose"] += 1
            return -1
        
        self.stats["draw"] += 1
        if self.enableLog: print(f"Draw - player:{playerSum}, dealer:{dealerSum}, len:{len(playerCards)}")
        return 0

    def saveStates(self):
        self.player.saveQtable("blackjackAIstate")

    def printStats(self):
        qlen = len(self.player.Q)
        total = self.stats["win"] + self.stats["lose"] + self.stats["draw"] + self.stats["playerbust"] + self.stats["dealerbust"]
        winNum = self.stats["win"]
        lostNum = self.stats["lose"]
        drawNum = self.stats["draw"]
        playerbustNum = self.stats["playerbust"]
        dealerbustNum = self.stats["dealerbust"]
        winPercent = round(self.stats["win"] / total * 100, 2)
        losePercent = round(self.stats["lose"] / total * 100, 2)
        drawPercent = round(self.stats["draw"] / total * 100, 2)
        playerbustPercent = round(self.stats["playerbust"] / total * 100, 2)
        dealerbustPercent = round(self.stats["dealerbust"] / total * 100, 2)
        print(f"---TRAIN STATISTICS---")
        print(f"Q-Learning Table Length: {qlen}")
        print(f"Win: {winNum} rounds - {winPercent}%")
        print(f"Lose: {lostNum} rounds - {losePercent}%")
        print(f"Draw: {drawNum} rounds - {drawPercent}%")
        print(f"Player Bust: {playerbustNum} rounds - {playerbustPercent}%")
        print(f"Dealer Bust: {dealerbustNum} rounds - {dealerbustPercent}%")
        

class Player:
    def __init__(self):
        self.cards = []
        pass

    def drawCard(self):
        self.cards.append(DeckHelpers.getCard())
    
    def emptyCards(self):
        self.cards = []
    
    def is21orAbove(self):
        playerSum = DeckHelpers.getSumOfCards(self.cards)
        return playerSum >= 21

class Dealer:
    def __init__(self):
        self.cards = []
        pass

    def drawCard(self):
        self.cards.append(DeckHelpers.getCard())

    def emptyCards(self):
        self.cards = []
    
    def isAbove17orBust(self):
        dealerSum = DeckHelpers.getSumOfCards(self.cards)
        return dealerSum >= 17        


class Qlearning(Player):
    def __init__(self, epsilon=0, alpha=0.3, gamma=0.9):
        super().__init__()
        self.epsilon=epsilon
        self.alpha=alpha
        self.gamma=gamma
        self.Q = {} #Q table
        self.last_state=None
        self.q_last=0.0
        self.state_action_last=None

    def resetLastStateVariables(self):
        self.last_state = None
        self.q_last = 0.0
        self.state_action_last = None

    def epslion_greedy(self, possible_moves): #esplion greedy algorithm
        # self.last_state = tuple(self.cards)
        self.last_state = DeckHelpers.getSumOfCards(self.cards)
        if(random.random() < self.epsilon):
            move = random.choice(possible_moves)
            self.state_action_last = (self.last_state, move)
            self.q_last = self.getQ(self.last_state, move)
            return move
        else: #greedy strategy
            Q_list=[]
            for action in possible_moves:
                Q_list.append(self.getQ(self.last_state, action))
            maxQ=max(Q_list)

            if Q_list.count(maxQ) > 1:
                # more than 1 best option; choose among them randomly
                best_options = [i for i in range(len(possible_moves)) if Q_list[i] == maxQ]
                i = random.choice(best_options)
            else:
                i = Q_list.index(maxQ)
            self.state_action_last = (self.last_state, possible_moves[i])
            self.q_last = self.getQ(self.last_state, possible_moves[i])
            return possible_moves[i]


    def getQ(self, state, action): #get Q states
        if(self.Q.get((state, action))) is None:
            self.Q[(state, action)] = 0
        return self.Q.get((state, action))

    def updateQ(self, reward, possible_moves): # update Q states using Qleanning
        q_list=[]
        for moves in possible_moves:
            q_list.append(self.getQ(DeckHelpers.getSumOfCards(self.cards), moves))
        if q_list:
            max_q_next = max(q_list)
        else:
            max_q_next = 0.0
        self.Q[self.state_action_last] = self.q_last + self.alpha * ((reward + self.gamma * max_q_next) - self.q_last)

    def saveQtable(self,file_name):  #save table
        with open(file_name, 'wb') as handle:
            pickle.dump(self.Q, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def loadQtable(self,file_name): # load table
        with open(file_name, 'rb') as handle:
            self.Q = pickle.load(handle)


# Training
trainIterations = 100000
game = BackJackGame(enableLog=False)
aiPlayer = Qlearning()
dealer = Dealer()
game.initializeTraining(aiPlayer, dealer)
game.train(trainIterations, continueTrainingFromState=False)
game.printStats()
game.saveStates()

# game = BackJackGame()  # game instance
# player1 = Humanplayer()  # human player
# player2 = Qlearning()  # agent
# game.startGame(player1, player2)  # player1 is X, player2 is 0
# game.reset()  # reset
# game.render()  # render display
