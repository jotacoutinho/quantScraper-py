class Period:
    def __init__(self, days, df, adf, beta, stdDev, fisherMin, fisherMax, fin, halfLife):
        self.days = days
        self.df = df
        self.adf = adf
        self.beta = beta
        self.stdDev = stdDev
        self.fisherMin = fisherMin
        self.fisherMax = fisherMax
        self.fin = fin
        self.halfLife = halfLife 
    
    def print(self, period):
        print('days: ' + period.days + '\n')
        print('df: ' + period.df + '\n')
        print('adf: ' + period.adf + '\n')
        print('beta: ' + period.beta + '\n')
        print('stdDev: ' + period.stdDev + '\n')
        print('fisherMin: ' + period.fisherMin + '\n')
        print('fisherMax: ' + period.fisherMax + '\n')
        print('fin: ' + period.fin + '\n')
        print('halfLife: ' + period.halfLife + '\n')