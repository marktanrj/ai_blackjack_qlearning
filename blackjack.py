import time
import random
import pickle

class DeckHelpers:
    @staticmethod
    def getBlackCard():
        # get black card for start of the game
        deck = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        value = random.choice(deck)
        color = "black"
        return (value, color)
    
    @staticmethod
    def getCard():
        # get random card from deck
        deck = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        color = ""
        if random.uniform(0, 1) <= 2/3:
            color = "black"
        else:
            color = "red"
        value = random.choice(deck)

        return (value, color)

    @staticmethod
    def getSumOfCards(cards):
        # sum all the cards in a player's stack
        totalSum = 0
        for card in cards:
            if card[1] == "red":
                totalSum -= card[0]
            else:
                totalSum += card[0]
        return totalSum

class Player:
    def __init__(self):
        self.cards = []
        pass

    def drawCard(self):
        self.cards.append(DeckHelpers.getCard())
    
    def drawBlackCard(self):
        self.cards.append(DeckHelpers.getBlackCard())

    def emptyCards(self):
        self.cards = []
    
    def is21AboveOrBelow1(self):
        playerSum = DeckHelpers.getSumOfCards(self.cards)
        return (playerSum >= 21 or playerSum < 1)
    
    def promptAction(self):
        playerInput = input("What would you like to do? Hit or Stick? (h/s)\n")
        while playerInput != "h" and playerInput != "s":
            playerInput = input("What would you like to do? Hit or Stick? (h/s)\n")
        print("You have inputted: ", playerInput)
        return playerInput
    
    def displayCards(self):
        print("Your cards: ", self.cards)
        print("Sum of cards: ", DeckHelpers.getSumOfCards(self.cards))

class Dealer:
    def __init__(self):
        self.cards = []
        pass

    def drawCard(self):
        self.cards.append(DeckHelpers.getCard())
    
    def drawBlackCard(self):
        self.cards.append(DeckHelpers.getBlackCard())

    def emptyCards(self):
        self.cards = []
    
    def isAbove17orBust(self):
        dealerSum = DeckHelpers.getSumOfCards(self.cards)
        return dealerSum >= 17        

class Qlearning(Player):
    def __init__(self, epsilon=0.1, alpha=0.3, gamma=0.9):
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

class BackJackGame:
    def __init__(self, enableLog=True):
        self.isTraining = False
        self.player = None
        self.dealer = None
        self.possible_moves = ["hit", "stick"]
        self.only_stick_move = ["stick"]

        self.stats = {"win": 0, "lose": 0, "draw": 0, "playerbust":0, "dealerbust": 0}
        self.enableLog = enableLog

    def initializeTraining(self, player, dealer):
        if(isinstance(player, Qlearning) and isinstance(dealer, Dealer)):
            self.isTraining = True
            self.player = player
            self.dealer = dealer
            
    def train(self, iterations, loadPreviousState=False):
        if not self.isTraining:
            return print("initializeTraining() before train()")
        if loadPreviousState:
            try:
                self.player.loadQtable("blackjackAIstate")
            except Exception as error:
                print(str(error))
        for i in range(iterations):
            if self.enableLog: print("training iteration: ", i)
            if i%10000 == 0: print("training iteration: ", i)
            
            self.player.resetLastStateVariables()
            self.player.emptyCards()
            self.dealer.emptyCards()
            self.player.drawBlackCard()
            self.dealer.drawBlackCard()

            # AI player's turn
            playerMove = self.player.epslion_greedy(self.possible_moves)
            is21AboveOrBelow1 = self.player.is21AboveOrBelow1()
            while not is21AboveOrBelow1 and playerMove == "hit":
                self.player.drawCard()
                playerMove = self.player.epslion_greedy(self.possible_moves)
                is21AboveOrBelow1 = self.player.is21AboveOrBelow1()
                    
            # dealer's turn
            dealerDone = self.dealer.isAbove17orBust()
            while not dealerDone:
                self.dealer.drawCard()
                dealerDone = self.dealer.isAbove17orBust()
            
            # evaluate
            reward = self.evaluate(self.player.cards, self.dealer.cards)
            self.player.updateQ(reward, self.possible_moves)

        self.isTraining = False

    def evaluate(self, playerCards, dealerCards):
        playerSum = DeckHelpers.getSumOfCards(playerCards)
        dealerSum = DeckHelpers.getSumOfCards(dealerCards)
        
        # returns reward
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

    # This function lets human play against trained AI. This is not needed for training.
    def startGameWithHuman(self, player, dealer):
        if isinstance(player, Player) and isinstance(dealer, Qlearning):
            self.player = player
            self.dealer = dealer

            try:
                self.dealer.loadQtable("blackjackAIstate")
            except Exception as error:
                print(str(error))

            self.player.emptyCards()
            self.dealer.emptyCards()
            self.player.drawBlackCard()
            self.dealer.drawBlackCard()

            # player's turn
            self.player.displayCards()
            playerInput = self.player.promptAction()
            is21AboveOrBelow1 = self.player.is21AboveOrBelow1()
            while not is21AboveOrBelow1 and playerInput == "h":
                self.player.drawCard()
                self.player.displayCards()
                is21AboveOrBelow1 = self.player.is21AboveOrBelow1()
                if DeckHelpers.getSumOfCards(self.player.cards) > 21 or DeckHelpers.getSumOfCards(self.player.cards) < 1: 
                    print("You busted!")
                elif DeckHelpers.getSumOfCards(self.player.cards) == 21:
                    print("You Win!")
                else:
                    playerInput = self.player.promptAction()
                
            # ai's turn
            dealerMove = self.dealer.epslion_greedy(self.possible_moves)
            while dealerMove == "hit":
                self.dealer.drawCard()
                is21AboveOrBelow1 = self.dealer.is21AboveOrBelow1()
                if is21AboveOrBelow1:
                    dealerMove = self.dealer.epslion_greedy(self.only_stick_move)
                else:
                    dealerMove = self.dealer.epslion_greedy(self.possible_moves)

            # evaluate game
            self.evaluate(self.player.cards, self.dealer.cards)

    def printStats(self):
        qlen = len(self.player.Q)
        total = self.stats["win"] + self.stats["lose"] + self.stats["draw"] + self.stats["playerbust"] + self.stats["dealerbust"]
        winNum = self.stats["win"]
        winPercent = round(self.stats["win"] / total * 100, 2)
        lostNum = self.stats["lose"]
        losePercent = round(self.stats["lose"] / total * 100, 2)
        drawNum = self.stats["draw"]
        drawPercent = round(self.stats["draw"] / total * 100, 2)
        playerbustNum = self.stats["playerbust"]
        playerbustPercent = round(self.stats["playerbust"] / total * 100, 2)
        dealerbustNum = self.stats["dealerbust"]
        dealerbustPercent = round(self.stats["dealerbust"] / total * 100, 2)
        totalWins = self.stats["win"] + self.stats["dealerbust"]
        totalWinsPercent = round(totalWins / total * 100, 2)
        totalLoses = self.stats["lose"] + self.stats["playerbust"]
        totalLosesPercent = round(totalLoses / total * 100, 2)

        print(f"---TRAIN STATISTICS---")
        print(f"Total Rounds: {total}")
        print(f"Q-Learning Table Length: {qlen}")
        print(f"Player Win: {winNum} rounds - {winPercent}%")
        print(f"Player Lose: {lostNum} rounds - {losePercent}%")
        print(f"Draw: {drawNum} rounds - {drawPercent}%")
        print(f"Player Bust: {playerbustNum} rounds - {playerbustPercent}%")
        print(f"Dealer Bust: {dealerbustNum} rounds - {dealerbustPercent}%")
        print(f"---SUMMARY---")
        print(f"Total Wins (Win + Dealer Bust): {totalWins} rounds - {totalWinsPercent}%")
        print(f"Total Loses (Lose + Player Bust): {totalLoses} rounds - {totalLosesPercent}%")
        print(f"Draw: {drawNum} rounds - {drawPercent}%")

## Training
trainIterations = 10000
game = BackJackGame(enableLog=False) #enableLog prints log for every iteration
aiPlayer = Qlearning()
dealer = Dealer()
game.initializeTraining(aiPlayer, dealer)
game.train(trainIterations, loadPreviousState=True) # set loadPreviousState to True to continue training, False to overwrite
game.printStats()
game.saveStates() # save trained state

## Play against AI - This is independent of above code, uncomment to play with AI
# game = BackJackGame(enableLog=True)  # game instance
# humanPlayer = Player()  # human player
# aiDealer = Qlearning()  # agent
# game.startGameWithHuman(humanPlayer, aiDealer)
