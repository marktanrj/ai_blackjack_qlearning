import pygame
import random
import time
import pickle

# humman player


class Humanplayer:
    pass

# randomplayer player


class Randomplayer:
    def __init__(self):
        pass

    def move(self, possiblemoves):
        return random.choice(possiblemoves)


class TicTacToe:
    def __init__(self, traning=False):
        self.board = [' ']*9

        self.done = False
        self.humman = None
        self.computer = None
        self.humanTurn = None
        self.training = traning
        self.player1 = None
        self.player2 = None
        self.aiplayer = None
        self.isAI = False
        # if not training display
        if(not self.training):
            pygame.init()
            self.ttt = pygame.display.set_mode((250, 250))
            pygame.display.set_caption('Tic-Tac-Toe')

    # reset the game
    def reset(self):
        if(self.training):
            self.board = [' '] * 9
            return

        self.board = [' '] * 9
        self.humanTurn = random.choice([True, False])

        self.surface = pygame.Surface(self.ttt.get_size())
        self.surface = self.surface.convert()
        self.surface.fill((250, 250, 250))
        # horizontal line
        pygame.draw.line(self.surface, (0, 0, 0), (75, 0), (75, 225), 2)
        pygame.draw.line(self.surface, (0, 0, 0), (150, 0), (150, 225), 2)
        # veritical line
        pygame.draw.line(self.surface, (0, 0, 0), (0, 75), (225, 75), 2)
        pygame.draw.line(self.surface, (0, 0, 0), (0, 150), (225, 150), 2)

   # evaluate function
    def evaluate(self, ch):
        # "rows checking"
        for i in range(3):
            if (ch == self.board[i * 3] == self.board[i * 3 + 1] and self.board[i * 3 + 1] == self.board[i * 3 + 2]):
                return 1.0, True
        # "col checking"
        for i in range(3):
            if (ch == self.board[i + 0] == self.board[i + 3] and self.board[i + 3] == self.board[i + 6]):
                return 1.0, True
        # diagonal checking
        if (ch == self.board[0] == self.board[4] and self.board[4] == self.board[8]):
            return 1.0, True

        if (ch == self.board[2] == self.board[4] and self.board[4] == self.board[6]):
            return 1.0, True
        # "if filled draw"
        if not any(c == ' ' for c in self.board):
            return 0.5, True

        return 0.0, False

    # return remaining possible moves
    def possible_moves(self):
        return [moves + 1 for moves, v in enumerate(self.board) if v == ' ']

    # take next step and return reward
    def step(self, isX, move):
        if(isX):
            ch = 'X'
        else:
            ch = '0'
        if(self.board[move-1] != ' '):  # try to over write
            return -5, True

        self.board[move-1] = ch
        reward, done = self.evaluate(ch)
        return reward, done

    # draw move on window
    def drawMove(self, pos, isX):
        row = int((pos-1)/3)
        col = (pos-1) % 3

        centerX = ((col) * 75) + 32
        centerY = ((row) * 75) + 32

        reward, done = self.step(isX, pos)  # next step
        if(reward == -5):  # overlap
            #print('Invalid move')
            font = pygame.font.Font(None, 18)
            text = font.render('Invalid move! Press any key to reset', 1, (10, 10, 10))
            self.surface.fill((250, 250, 250), (0, 300, 300, 25))
            self.surface.blit(text, (10, 230))

            return reward, done

        if (isX):  # playerX so draw x
            font = pygame.font.Font(None, 24)
            text = font.render('X', 1, (10, 10, 10))
            self.surface.fill((250, 250, 250), (0, 300, 300, 25))
            self.surface.blit(text, (centerX, centerY))
            self.board[pos-1] = 'X'

            if(self.humman and reward == 1):  # if playerX is humman and won, display humman won
                #print('Humman won! in X')
                font = pygame.font.Font(None, 18)
                text = font.render('Humman won! Press any key to continue', 1, (10, 10, 10))
                self.surface.fill((250, 250, 250), (0, 300, 300, 25))
                self.surface.blit(text, (10, 230))

            elif (self.computer and reward == 1):  # if playerX is computer and won, display computer won
                #print('computer won! in X')
                font = pygame.font.Font(None, 18)
                text = font.render('computer won! Press any key to continue', 1, (10, 10, 10))
                self.surface.fill((250, 250, 250), (0, 300, 300, 25))
                self.surface.blit(text, (10, 230))

        else:  # playerO so draw O
            font = pygame.font.Font(None, 24)
            text = font.render('O', 1, (10, 10, 10))

            self.surface.fill((250, 250, 250), (0, 300, 300, 25))
            self.surface.blit(text, (centerX, centerY))
            self.board[pos-1] = '0'

            if (not self.humman and reward == 1):  # if playerO is humman and won, display humman won
                #print('Humman won! in O')
                font = pygame.font.Font(None, 18)
                text = font.render('Humman won!. Press any key to continue', 1, (10, 10, 10))
                self.surface.fill((250, 250, 250), (0, 300, 300, 25))
                self.surface.blit(text, (10, 230))

            elif (not self.computer and reward == 1):  # if playerO is computer and won, display computer won
                #print('computer won! in O')
                font = pygame.font.Font(None, 18)
                text = font.render('computer won! Press any key to continue', 1, (10, 10, 10))
                self.surface.fill((250, 250, 250), (0, 300, 300, 25))
                self.surface.blit(text, (10, 230))

        if (reward == 0.5):  # draw, then display draw
            #print('Draw Game! in O')
            font = pygame.font.Font(None, 18)
            text = font.render('Draw Game! Press any key to continue', 1, (10, 10, 10))
            self.surface.fill((250, 250, 250), (0, 300, 300, 25))
            self.surface.blit(text, (10, 230))
            return reward, done

        return reward, done

    # mouseClick position
    def mouseClick(self):
        (mouseX, mouseY) = pygame.mouse.get_pos()
        if (mouseY < 75):
            row = 0
        elif (mouseY < 150):
            row = 1
        else:
            row = 2

        if (mouseX < 75):
            col = 0
        elif (mouseX < 150):
            col = 1
        else:
            col = 2
        return row * 3 + col + 1

     # update state
    def updateState(self, isX):
        pos = self.mouseClick()
        reward, done = self.drawMove(pos, isX)
        return reward, done

    # show display
    def showboard(self):
        self.ttt.blit(self.surface, (0, 0))
        pygame.display.flip()

    # begin training
    def startTraining(self, player1, player2):
        if(isinstance(player1, Qlearning) and isinstance(player2, Qlearning)):
            self.training = True
            self.player1 = player1
            self.player2 = player2

    # tarin function
    def train(self, iterations):
        if(self.training):
            for i in range(iterations):
                print("trainining", i)
                self.player1.game_begin()
                self.player2.game_begin()
                self.reset()
                done = False
                isX = random.choice([True, False])
                while not done:
                    if isX:
                        move = self.player1.epslion_greedy(self.board, self.possible_moves())
                    else:
                        move = self.player2.epslion_greedy(self.board, self.possible_moves())

                    reward, done = self.step(isX, move)

                    if (reward == 1):  # won
                        if (isX):
                            self.player1.updateQ(reward, self.board, self.possible_moves())
                            self.player2.updateQ(-1 * reward, self.board, self.possible_moves())
                        else:
                            self.player1.updateQ(-1 * reward, self.board, self.possible_moves())
                            self.player2.updateQ(reward, self.board, self.possible_moves())

                    elif (reward == 0.5):  # draw
                        self.player1.updateQ(reward, self.board, self.possible_moves())
                        self.player2.updateQ(reward, self.board, self.possible_moves())

                    elif (reward == -5):  # illegal move
                        if (isX):
                            self.player1.updateQ(reward, self.board, self.possible_moves())
                        else:
                            self.player2.updateQ(reward, self.board, self.possible_moves())

                    elif (reward == 0):
                        if (isX):  # update opposite
                            self.player2.updateQ(reward, self.board, self.possible_moves())
                        else:
                            self.player1.updateQ(reward, self.board, self.possible_moves())

                    isX = not isX  #

    # save Qtables
    def saveStates(self):
        self.player1.saveQtable("player1states")
        self.player2.saveQtable("player2states")

    # start game human vs AI or human vs random

    def startGame(self, playerX, playerO):
        if (isinstance(playerX, Humanplayer)):
            self.humman, self.computer = True, False
            if (isinstance(playerO, Qlearning)):  # if AI
                self.ai = playerO
                self.ai.loadQtable("player2states")  # load saved Q table
                self.ai.epsilon = 0  # set eps to 0 so always choose greedy step
                self.isAI = True
            elif (isinstance(playerO, Randomplayer)):  # if random
                self.ai = playerO
                self.isAI = False

        elif (isinstance(playerO, Humanplayer)):
            self.humman, self.computer = False, True
            if (isinstance(playerX, Qlearning)):  # if AI
                self.ai = playerX
                self.ai.loadQtable("player1states")  # load saved Q table
                self.ai.epsilon = 0  # set eps to 0 so always choose greedy step
                self.isAI = True
            elif(isinstance(playerX, Randomplayer)):  # if random
                self.ai = playerX
                self.isAI = False

    def render(self):
        running = 1
        done = False
        pygame.event.clear()
        while (running == 1):
            if (self.humanTurn):  # humman click
                print("Human player turn")
                event = pygame.event.wait()
                while event.type != pygame.MOUSEBUTTONDOWN:
                    event = pygame.event.wait()
                    self.showboard()
                    if event.type == pygame.QUIT:
                        running = 0
                        print("pressed quit")
                        pygame.display.quit()
                        break
                if running == 1:
                    reward, done = self.updateState(self.humman)  # if random
                    self.showboard()
                    if (done):  # if done reset
                        # time.sleep(1)
                        while event.type != pygame.KEYDOWN:
                            event = pygame.event.wait()
                            self.showboard()
                            if event.type == pygame.QUIT:
                                running = 0
                                print("pressed quit")
                                pygame.display.quit()
                                break
                        pygame.event.clear()
                        self.reset()

            else:  # AI or random turn
                if(self.isAI):
                    moves = self.ai.epslion_greedy(self.board, self.possible_moves())
                    reward, done = self.drawMove(moves, self.computer)
                    print("computer's AI player turn")
                    self.showboard()
                else:  # random player
                    moves = self.ai.move(self.possible_moves())  # random player
                    reward, done = self.drawMove(moves, self.computer)
                    print("computer's random player turn")
                    self.showboard()

                if (done):  # if done reset
                    # time.sleep(1)
                    while event.type != pygame.KEYDOWN:
                        event = pygame.event.wait()
                        self.showboard()
                        if event.type == pygame.QUIT:
                            running = 0
                            print("pressed quit")
                            pygame.display.quit()
                            break
                    pygame.event.clear()
                    self.reset()

            self.humanTurn = not self.humanTurn


class Qlearning:
    def __init__(self, epsilon=0.2, alpha=0.3, gamma=0.9):
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.Q = {}  # Q table
        self.last_board = None
        self.q_last = 0.0
        self.state_action_last = None

    def game_begin(self):
        self.last_board = None
        self.q_last = 0.0
        self.state_action_last = None

    def epslion_greedy(self, state, possible_moves):  # esplion greedy algorithm
        # return  action
        self.last_board = tuple(state)
        if(random.random() < self.epsilon):
            move = random.choice(possible_moves)  # action
            self.state_action_last = (self.last_board, move)
            self.q_last = self.getQ(self.last_board, move)
            return move
        else:  # greedy strategy
            Q_list = []
            for action in possible_moves:
                Q_list.append(self.getQ(self.last_board, action))
            maxQ = max(Q_list)

            if Q_list.count(maxQ) > 1:
                # more than 1 best option; choose among them randomly
                best_options = [i for i in range(len(possible_moves)) if Q_list[i] == maxQ]
                i = random.choice(best_options)
            else:
                i = Q_list.index(maxQ)
            self.state_action_last = (self.last_board, possible_moves[i])
            self.q_last = self.getQ(self.last_board, possible_moves[i])
            return possible_moves[i]

    def getQ(self, state, action):  # get Q states
        if(self.Q.get((state, action))) is None:
            self.Q[(state, action)] = 1.0
        return self.Q.get((state, action))

    def updateQ(self, reward, state, possible_moves):  # update Q states using Qleanning
        q_list = []
        for moves in possible_moves:
            q_list.append(self.getQ(tuple(state), moves))
        if q_list:
            max_q_next = max(q_list)
        else:
            max_q_next = 0.0
        updatedScore = self.q_last + self.alpha * ((reward + self.gamma*max_q_next) - self.q_last)
        self.Q[self.state_action_last] = updatedScore

    def saveQtable(self, file_name):  # save table
        with open(file_name, 'wb') as handle:
            pickle.dump(self.Q, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def loadQtable(self, file_name):  # load table
        with open(file_name, 'rb') as handle:
            self.Q = pickle.load(handle)


# Training
numiter = 10000
game = TicTacToe(True)  # game instance, True means training
player1 = Qlearning()  # player1 learning agent
player2 = Qlearning()  # player2 learning agent
game.startTraining(player1, player2)  # start training
game.train(numiter)  # train for 200,000 iterations
game.saveStates()  # save Qtable

game = TicTacToe()  # game instance
player1 = Humanplayer()  # human player
player2 = Qlearning()  # agent
game.startGame(player1, player2)  # player1 is X, player2 is 0
game.reset()  # reset
game.render()  # render display
