import csv
import math

class Markov:
    # List with the data from the csv as it is
    rowList = []
    # List with the data of the csv where the traffic is named in state form
    reducedList = []
    # Name of the csv with the data
    dataFile = ""
    # List with all the possible directions
    actions = []
    # List with the individual letters that form states
    letters = []
    # List with each state and their letter
    transformations = []
    # List with all the possible states
    states = []
    # Cost of turning a traffic light on
    globalCost = -1
    # List of the values of bellman equations
    bellman = []
    # Number of iterations after computing the bellman equation
    iterations = -1
    # Coded name of the goal state
    goal = ""
    # Dictionary with the optimal policy of each state
    optPol = {}

    def __init__(self,inputFile):
        # These functions will be executed when creating the class and will compute everything
        self.dataFile = inputFile
        self.rowList = self.fill(self.dataFile)
        self.reducedList = self.createReduced()
        self.states = self.listStates()
        self.goal = self.takeGoal()

        # Writting the key of the dictionary optPol letting the values blank
        for state in self.states:
            # The goal state doesn't have and optimal policy
            if state == self.goal:
                self.optPol[state] = None
            else:
                self.optPol[state] = ""

        cost = input("Introduce the cost of each operation:\n")
        # Check if the cost introduced is a number over or equal to 1
        if not cost.isdigit() or int(cost) <= 0:
            exit("The value of the global cost is not valid. Exiting...")
        self.globalCost = int(cost)

        self.bellman = self.initBell()
        print("Processing the data. This operation might take a while...")
        self.iterations = self.bellmanEq()


    # Method to transform the csv into a list of rows
    def fill(self,fileName):
        rows = []
        # Opening the csv
        with open(fileName, newline='') as File:
            info = csv.reader(File)
            take = False
            for row in info:
                # We don't take the data of the first line (it is the names of each column)
                if not take:
                    take = True
                # As the function reader returns a list of one element each, we split each parameter
                else:
                    separated = row[0].split(";")
                    rows.append(separated)
        return rows

    # Method to transform the list of rows to show elements as states
    def createReduced(self):
        # Storage for found traffic states
        found = []
        # Storage for found traffic states and their assigned letter or letters
        combined = []
        # Storage for the used letters to name states
        used = []
        # List where the different actions found will be stored and returned from
        direc = []
        # Storage for all the converted rows to be returned
        reducedData = []

        for row in self.rowList:
            current = []
            # String with the first state
            initial = ""
            # String with the final state
            final = ""

            # We find the letter for the first 3 states and join them
            # If it is the first time a word appears
            if row[0] not in found:
                counter = 1
                # The number of letters needed will increase until they haven't been used
                while row[0][0:counter] in used:
                    counter += 1
                # Recording this state information for future reference
                used.append(row[0][0:counter])
                found.append(row[0])
                combined.append([row[0],row[0][0:counter]])
                # Join the letter to the string
                initial = initial + row[0][0:counter]
            else:
                # If it had appeared before we just find the letter corresponding and add it to the string
                for state in combined:
                    if state[0] == row[0]:
                        initial = initial + state[1]

            if row[1] not in found:
                counter = 1
                while row[1][0:counter] in used:
                    counter += 1
                used.append(row[1][0:counter])
                found.append(row[1])
                combined.append([row[1], row[1][0:counter]])
                initial = initial + row[1][0:counter]
            else:
                for state in combined:
                    if state[0] == row[1]:
                        initial = initial + state[1]

            if row[2] not in found:
                counter = 1
                while row[2][0:counter] in used:
                    counter += 1
                used.append(row[2][0:counter])
                found.append(row[2])
                combined.append([row[2], row[2][0:counter]])
                initial = initial + row[2][0:counter]
            else:
                for state in combined:
                    if state[0] == row[2]:
                        initial = initial + state[1]

            # The now complete initial state and the action are appended
            current.append(initial)
            current.append(row[3])
            if row[3] not in direc:
                # If the action is the first time that appears we record it
                direc.append(row[3])

            # Same process as with the first 3 but for the last 3
            if row[4] not in found:
                counter = 1
                while row[4][0:counter] in used:
                    counter += 1
                used.append(row[4][0:counter])
                found.append(row[4])
                combined.append([row[4], row[4][0:counter]])
                final = final + row[4][0:counter]
            else:
                for state in combined:
                    if state[0] == row[4]:
                        final = final + state[1]

            if row[5] not in found:
                counter = 1
                while row[5][0:counter] in used:
                    counter += 1
                used.append(row[5][0:counter])
                found.append(row[5])
                combined.append([row[5], row[5][0:counter]])
                final = final + row[5][0:counter]
            else:
                for state in combined:
                    if state[0] == row[5]:
                        final = final + state[1]

            if row[6] not in found:
                counter = 1
                while row[6][0:counter] in used:
                    counter += 1
                used.append(row[6][0:counter])
                found.append(row[6])
                combined.append([row[6], row[6][0:counter]])
                final = final + row[6][0:counter]
            else:
                for state in combined:
                    if state[0] == row[6]:
                        final = final + state[1]

            current.append(final)
            # Converted row is added to the list
            reducedData.append(current)

        # Some data can be extracted to have more information about the model
        self.letters = used
        self.actions = direc
        self.transformations = combined
        return reducedData

    # Method to create a list with all the possible states that can be found in the model
    def listStates(self):
        states = []
        # Loops to combine all the letters in words of 3
        for letter1 in self.letters:
            for letter2 in self.letters:
                for letter3 in self.letters:
                    states.append(letter1 + letter2 + letter3)
        return states

    # Method to calculate the probability of going from a state to another when a specific action
    # Example probability: P(HHL / HHH, W)
    def calcProb(self,initialState,action,finalState):
        total = 0
        count = 0
        probability = 0
        # We count how many times the initial state with the specific action appears
        # We also count how many times the 3 elements appear together
        for element in self.reducedList:
            if element[0] == initialState and element[1] == action:
                total += 1
                if element[2] == finalState:
                    count += 1
        if total == 0:
            probability = 0
        else:
            probability = count / total
            # Probability rounded to 6 decimal values
            probability = round(probability,6)
        return probability

    # Method to find the goal state in the markov model
    def takeGoal(self):
        remaining = []
        for state in self.states:
            remaining.append(state)
        for initial in self.states:
            for final in self.states:
                for action in self.actions:
                    probability = self.calcProb(initial,action,final)
                    # If an initial state can go to another, it is removed from the list of possible goal states
                    if probability != 0 and initial in remaining:
                        remaining.remove(initial)

        # If the process was successfull, the list should only contain one state that is the goal
        if len(remaining) == 1:
            return remaining[0]
        # If not, we will print all the states and ask the user what is their choice as a goal state
        else:
            print(remaining)
            for state in self.states:
                print(state)
            selection = input("The algorithm couldn't find a goal state. Please, select one from the above:\n")
            print("Goal state selected")
            return selection

    # Method to set the initial bellman values to 0 for all states
    def initBell(self):
        initial = []
        for state in self.states:
            initial.append([0,state,0])
        return initial

    # Method to compute the bellman equations and obtain the optimal policy
    def bellmanEq(self):
        finish = False
        counter = 1

        # The loop won't finish until 2 iterations result on the same values
        while not finish:
            for state in self.states:
                best = float("inf")
                result = 0
                for action in self.actions:
                    # We need to check if we are working with the goal state as the initial state to keep it 0
                    if state == self.goal:
                        option = 0
                    else:
                        # The cost of an action is the starting value of each operation
                        option = self.globalCost
                    for final in self.states:
                        probability = self.calcProb(state, action, final)
                        if probability != 0:
                            for bellman in self.bellman:
                                # The code needs to find the V values of previous iterations to multiply them to the probability
                                if bellman[0] == counter - 1 and bellman[1] == final:
                                    # We multiply the probability by the V value and use 6 decimal values
                                    addition = round(probability * bellman[2],6)
                                    # Every combination is added to the cost
                                    option = option + addition
                    # If the current operation is smaller than the one that was set before, it becomes the optimal policy
                    if option < best:
                        # The dictionary is updated each iteration
                        self.optPol[state] = action
                        best = option
                # We record the result of each iteration
                self.bellman.append([counter,state,round(best,6)])

            # Loop to check if the process should finish
            control = 0
            for state in self.states:
                control2 = 0
                for bellman in self.bellman:
                    if bellman[1] == state:
                        if bellman[0] == counter:
                            current = bellman[2]
                            control2 += 1
                        elif bellman[0] == counter - 1:
                            past = bellman[2]
                            control2 += 1
                if control2 != 2:
                    print("THERE WAS AN ERROR DURING BELLMAN")
                    return -1
                # control will increase one unit every time we find a result in the current iteration different from the previous
                if current != past:
                    control += 1
            # control = 0 means there was nothing different and so we have to finish
            if control == 0:
                finish = True
            counter += 1
            # Print to update the user on how the process is going (as the code takes a long time)
            if (counter % 100) == 0:
                print("Reached iteration "+str(counter))
        # The goal state must have always None as the policy as it doesn't have any
        self.optPol[self.goal] = None
        counter -= 1
        return counter
