from Period import Period
import json

class Pair:
    def __init__(self, index, cointegratedPair, periods):
        self.index = index
        self.cointegratedPair = cointegratedPair
        self.periods = periods

    @classmethod
    def print(self, pair):
        print(pair.cointegratedPair + ' (id: ' + pair.index + ')\nPeriods:\n')
        for period in pair.periods:
            print('days: ' + period.days )
            print('df: ' + period.df)
            print('adf: ' + period.adf)
            print('beta: ' + period.beta)
            print('stdDev: ' + period.stdDev)
            print('fisherMin: ' + period.fisherMin)
            print('fisherMax: ' + period.fisherMax)
            print('fin: ' + period.fin)
            print('halfLife: ' + period.halfLife + '\n')

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)