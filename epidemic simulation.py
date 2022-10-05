#imports needed libraries
import math
import numpy
import random
import matplotlib.pyplot
import matplotlib.animation


#class for the epidemic simulator
class disease():
    def __init__(self, characteristics):
        #create plot using polar coordinates
        self.figure = matplotlib.pyplot.figure(figsize=(8.5,5.5), facecolor=("lightsteelblue"))
        self.figure.canvas.manager.set_window_title("epidemic simulation")
        self.axis = self.figure.add_subplot(111, projection="polar")
        self.axis.set_xticklabels([])
        self.axis.set_yticklabels([])
        self.axis.set_ylim(0, 1)
        self.axis.grid(False)
        
        #set the traits for the disease as part of the class
        self.totalNumberInfected = 0
        self.numberCurrentlyInfected = 0
        self.numberRecovered = 0
        self.numberDeaths = 0
        self.day = 0
        self.r0 = characteristics["r0"]
        self.percentMild = characteristics["percent mild"]
        self.percentSevere = characteristics["percent severe"]
        self.fatalityRate = characteristics["fatality rate"]
        self.serialInterval = characteristics["serial interval"]
        self.susceptibility = characteristics["susceptibility"]

        #combine the incubation peorid with the recovery to get the entire interval od the disease
        self.mildFast = characteristics["incubation"] + characteristics["mild recovery"][0]
        self.mildSlow = characteristics["incubation"] + characteristics["mild recovery"][1]
        self.severeFast = characteristics["incubation"] + characteristics["severe recovery"][0]
        self.severeSlow = characteristics["incubation"] + characteristics["severe recovery"][1]
        self.deathFast = characteristics["incubation"] + characteristics["severe death"][0]
        self.deathSlow = characteristics["incubation"] + characteristics["severe death"][1]

        self.mild = {i: {"angles": [], "radi": []} for i in range(self.mildFast, 365)}
        self.severe = {"recovery": {i: {"angles": [], "radi": []} for i in range(self.severeFast, 365)},
                       "death": {i: {"angles": [], "radi": []} for i in range(self.deathFast, 365)}}

        self.exposedBefore = 0
        self.exposedAfter = 1
        
        #create text
        self.infectedText = self.axis.annotate("Infected: 0", xy=[(math.pi/2) * 3, 1], color=red, ha="center", va="top")
        self.deathsText = self.axis.annotate("\nDeaths: 0", xy=[(math.pi/2) * 3, 1], color=black, ha="center", va="top")
        self.recoveredText = self.axis.annotate("\n\nRecovered: 0", xy=[(math.pi/2) * 3, 1], color=green, ha="center", va="top")
        self.dayText = self.axis.annotate("Day 0", xy=[(math.pi/2), 1], color=black, ha="center", va="bottom")

        #create the initial population
        self.initialPopulation()


    #creates population
    def initialPopulation(self):
        population = 5000
        indices = []
        counter = 0
        while counter < 5000:
            indices.append(counter)
            counter = counter + 1
        self.angles = [( i * math.pi * ((5**0.5)+1)) for i in indices]
        self.radi = [(math.sqrt(i / population)) for i in indices]
        self.plot = self.axis.scatter(self.angles, self.radi, s=5, color=grey)
        
        #first person infected
        self.numberCurrentlyInfected = 1
        self.totalNumberInfected = 1
        self.axis.scatter(self.angles[0], self.radi[0], s=5, color=red)
        self.mild[self.mildFast]["angles"].append(self.angles[0])
        self.mild[self.mildFast]["radi"].append(self.radi[0])

    #procudure for the virus spreading
    def spread(self, i):
        self.exposedBefore = self.exposedAfter
        if self.exposedBefore < 5000 and (self.day % self.serialInterval == 0):
            self.numberNewInfected = round(self.totalNumberInfected * self.r0)
            self.exposedAfter = self.exposedAfter + (round((1 + self.susceptibility) * self.numberNewInfected))
            if self.exposedAfter > 5000:
                self.exposedAfter = 5000
                self.numberNewInfected = round((1 - self.susceptibility) * (5000 - self.exposedBefore))
                
            self.numberCurrentlyInfected = self.numberCurrentlyInfected + self.numberNewInfected
            self.totalNumberInfected = self.totalNumberInfected + self.numberNewInfected
            self.newInfectedIndices =  list(numpy.random.choice(range(self.exposedBefore, self.exposedAfter),self.numberNewInfected, replace=False))

            #get the angle and radius values for these indicies
            angles = [self.angles[i] for i in self.newInfectedIndices]
            radi = [self.radi[i] for i in self.newInfectedIndices]

            #pauses the animation
            self.anim.event_source.stop()

            #determins how to animate based on how much there is to plot
            if len(self.newInfectedIndices) > 24:
                sizeList = round(len(self.newInfectedIndices) / 24)
                angleChunks = list(self.generator(angles, sizeList))
                radiusChunks = list(self.generator(radi, sizeList))
                self.anim2 = matplotlib.animation.FuncAnimation(
                    self.figure,
                    self.individual,
                    interval=50,
                    frames=len(angleChunks),
                    fargs=(angleChunks, radiusChunks, red))
            else:
                self.anim2 = matplotlib.animation.FuncAnimation(self.figure,self.individual,interval=50,frames=len(angles),fargs=(angles, radi, red))
            self.symptoms()

        #sets the next day
        self.day = self.day + 1

        #updates the status and text
        self.updateStatus()
        self.updateText()

    #procedure for giving symptons
    def symptoms(self):
        numberMild = round(self.percentMild * self.numberNewInfected)
        numberSevere = round(self.percentSevere * self.numberNewInfected)
        self.mildIndices = random.sample(self.newInfectedIndices, numberMild)
        remainingIndices = [i for i in self.newInfectedIndices if i not in self.mildIndices]
        percentSevereRecovery = 1 - (self.fatalityRate / self.percentSevere)
        numberSevereRecovery = round(numberSevere * percentSevereRecovery)
        self.severeIndices = []
        self.deathIndices = []
        if remainingIndices:
            self.severeIndices = random.sample(remainingIndices, numberSevereRecovery)
            self.deathIndices = [i for i in remainingIndices if i not in self.severeIndices]

        #get the amount of people recovered and who died
        low =  self.mildFast + self.day
        high = self.mildSlow + self.day

        #loop over mild indicies and randomly choose a recovery day in the range
        for mild in self.mildIndices:
            mildAngle = self.angles[mild]
            mildRadius = self.radi[mild]
            recoveryDay = random.randint(low, high)
            self.mild[recoveryDay]["angles"].append(mildAngle)
            self.mild[recoveryDay]["radi"].append(mildRadius)
            
        low = self.severeFast + self.day
        high = self.severeSlow + self.day

        #loop over severe indicies and randomly choose a recovery day in the range 
        for recovery in self.severeIndices:
            recoveryAngle = self.angles[recovery]
            recoveryRadius = self.radi[recovery]
            recoveryDay = random.randint(low, high)
            self.severe["recovery"][recoveryDay]["angles"].append(recoveryAngle)
            self.severe["recovery"][recoveryDay]["radi"].append(recoveryRadius)
            
        low =  self.deathFast + self.day
        high = self.deathSlow + self.day 

        #loop over severe indicies and randomly choose the date of death in the range 
        for death in self.deathIndices:
            deathAngle = self.angles[death]
            deathRadius = self.radi[death]
            deathDay = random.randint(low, high)
            self.severe["death"][deathDay]["angles"].append(deathAngle)
            self.severe["death"][deathDay]["radi"].append(deathRadius)

    #procudre for updating the status
    def updateStatus(self):
        if self.mildFast <= self.day:
            mildAngles = self.mild[self.day]["angles"]
            mildRadi = self.mild[self.day]["radi"]
            self.axis.scatter(mildAngles, mildRadi, s=5, color=green)
            self.numberRecovered = self.numberRecovered + len(mildAngles)
            self.numberCurrentlyInfected = self.numberCurrentlyInfected - len(mildAngles)
        if self.severeFast <=  self.day:
            recAngles = self.severe["recovery"][self.day]["angles"]
            recRadi = self.severe["recovery"][self.day]["radi"]
            self.axis.scatter(recAngles, recRadi, s=5, color=green)
            self.numberRecovered = self.numberRecovered + len(recAngles)
            self.numberCurrentlyInfected = self.numberCurrentlyInfected - len(recAngles)
        if self.deathFast <=  self.day:
            deathAngles = self.severe["death"][self.day]["angles"]
            deathRadi = self.severe["death"][self.day]["radi"]
            self.axis.scatter(deathAngles, deathRadi, s=5, color=black)
            self.numberDeaths = self.numberDeaths + self.numberDeaths + len(deathAngles)
            self.numberCurrentlyInfected = self.numberCurrentlyInfected - len(deathAngles)

    #this divides a given list into equally sized sections
    def generator(self, aList, n):
        for i in range(0, len(aList), n):
            yield aList[i:i + n]

    #plots points individually
    def individual(self, i, angles, radi, color):
        self.axis.scatter(angles[i], radi[i], s=5, color=color)
        if i == (len(angles) - 1):
            self.anim2.event_source.stop()
            self.anim.event_source.start()



    #procudure for updating the text
    def updateText(self):
        self.dayText.set_text("Day {}".format(self.day))
        self.infectedText.set_text("Infected: {}".format(self.numberCurrentlyInfected))
        self.recoveredText.set_text("\n\nRecovered: {}".format(self.numberRecovered))
        self.deathsText.set_text("\nDeaths: {}".format(self.numberDeaths))

        
#animate it using matplot libs animation class
    def animate(self):
        self.anim = matplotlib.animation.FuncAnimation(self.figure,self.spread,frames=self.generate,repeat=True)

    #passes to frames in the animation
    def generate(self):
        while self.totalNumberInfected > (self.numberDeaths + self.numberRecovered):
            yield

    



### main program ###

#gets inputs and validates them
while True:
    try:
        r0Input = float(input("What is the R0 value of your disease? "))
        incubationInput = int(input("What is the incubation peorid? "))
        mildLowerRecoveryInput = int(input("What is the lowest amount of days it takes people with mild symptoms to recover? "))
        mildHigherRecoveryInput = int(input("What is the highest amount of days it takes people with mild symptoms to recover? "))
        severeLowerRecoveryInput = int(input("What is the lowest amount of days it takes people with severe symptoms to recover? "))
        severeHigherRecoveryInput = int(input("What is the highest amount of days it takes people with severe symptoms to recover? "))
        deathTimeLower = int(input("What is the lowest amount of days it takes people with severe symptoms to die? "))
        deathTimeHigher = int(input("What is the highest amount of days it takes people with severe symptoms to die? "))
        severePercentageInput = float(input("What percentage of cases are severe? "))
        if 0 < severePercentageInput < 1:
            fatalityRateInput = float(input("What is the fatality rate of the disease? "))
            if 0 < fatalityRateInput < 1:
                serialIntervalInput = int(input("What is the serial interval of the disease? "))
                susceptibilityInput = float(input("What percentage of the population don't contract the disease when exposed to it? "))
                if 0 < susceptibilityInput < 1:
                    break
                else:
                    print("The susceptibility rate must be between 0 and 1")
            else:
                print("The falality rate  rate must be between 0 and 1")
        else:
            print("The severe infection rate must be between 0 and 1")
    except KeyboardInterrupt:
        print("that is not a valid input")
    except ValueError:
        print("that is not a valid input")


#shows the status of the person
black = (0, 0, 0)
red = (0.96, 0.15, 0.15)
grey = (0.78, 0.78, 0.78)  
green = (0, 0.86, 0.03) 

#dictionary to store information about the virus from given inputs
diseaseStats = {
    "r0": r0Input,
    "incubation": incubationInput,
    "percent mild": (1 - severePercentageInput),
    "mild recovery": (mildLowerRecoveryInput, mildHigherRecoveryInput),
    "percent severe": severePercentageInput,
    "severe recovery": (severeLowerRecoveryInput, severeHigherRecoveryInput),
    "severe death": (deathTimeLower, deathTimeHigher),
    "fatality rate": fatalityRateInput,
    "serial interval": serialIntervalInput,
    "susceptibility": susceptibilityInput
}



#calls the procedures
infection = disease(diseaseStats)
infection.animate()
matplotlib.pyplot.show()


