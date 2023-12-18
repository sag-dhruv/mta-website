#mypath = os.path.abspath(__file__) # locates current (absolute) path of file if needed

Data = pd.ExcelFile('static/2018.xlsx') # imports measured power profiles of each 7-line substation from 2018
Factors = pd.ExcelFile('static/Factors.xlsx') # imports factor matrix for each substation (substation contribution as a function of every station's location along the 7-line; with origin being at Hudson34)
SolarCurve = pd.ExcelFile('static/NYCAprilSolar_Data.xlsx').parse('Gaussian Expanded').iloc[0:96] # imports normalized solar curve for New York City in April
LocalTrainProfiles = pd.ExcelFile('static/LocalTrainProfiles.xlsx') # imports local train profiles for each station travel (Sheet 1 being HudsonYards to TimesSquare, Sheet 2 being TimesSquare to Ave5, etc.)
ExpressTrainProfiles = pd.ExcelFile('static/ExpressTrainProfiles.xlsx') # imports express train profiles (Sheet 1 being HudsonYards to TimesSquare, Sheet 2 being TimesSquare to Ave5, etc.)
Coefficients = pd.ExcelFile('static/Gauss2Coefficients.xlsx').parse('Sheet1').iloc[1:22] # imports coefficients for gauss2 equation representing each substation's contribution based on load location

class Substation:
	line = '7-Line'
	def __init__(self, name, origdata, normdata, moddata, default, EV, batt, fly, supcap, PV, transientcoefficients, transientorigdata, transientregendata, transientmoddata): # assigns properties to Substation class object
		self.name, self.origdata, self.normdata, self.moddata, self.default, self.EV, self.batt, self.fly, self.supcap, self.PV, self.transientcoefficients, self.transientorigdata, self.transientregendata, self.transientmoddata = name, origdata, normdata, moddata, default, EV, batt, fly, supcap, PV, transientcoefficients, transientorigdata, transientregendata, transientmoddata
# Note: Software user interface should prevent PV selection at some substations (in code, default is hence set to 0)

class PassStation:
	line = '7-Line'
	def __init__(self, name, default, EV, batt, fly, supcap, PV): # assigns properties to PassStation class object
		self.name, self.default, self.EV, self.batt, self.fly, self.supcap, self.PV = name, default, EV, batt, fly, supcap, PV	 
# Note: Software user interface should prevent PV selection at some passenger stations (in code, default is hence set to 0)

SheetSubstations = ['Spruce','St58','QueensBlvd','Lawrence','Corona','St78','Jackson','Ave50','Tudor','Ave7','Park','Ave10','Hudson34'] # substation order as per '2018.xlsx' excel file
SubstationDict = {} # creates a single dictionary of substations to loop through, allowing alteration of multiple substations at once

NamePassStations = ['HudsonYards','TimesSquare','Ave5','GrandCentral','Vernon','HuntersPoint','CourtSquare','QueensboroPlaza','St33','St40','St46','St52','St61','St69','St74','St82','St90','JunctionBlvd','St103','St111','WilletsPoint','MainSt'] # actual passenger station order (left to right)
LocationPassStations = [0,4970,6630,8540,15540,16940,19540,21940,25360,27250,28860,30560,33240,35150,36560,38650,40650,42640,44650,46690,49650,54308] # actual passenger station distances (left to right)
PassStationDict = {} # creates a single dictionary of passenger stations to loop through, allowing alteration of multiple passenger stations at once (if needed)

NameExpressPassStations = ['HudsonYards','TimesSquare','Ave5','GrandCentral','Vernon','HuntersPoint','CourtSquare','QueensboroPlaza','St61','JunctionBlvd','WilletsPoint','MainSt'] # actual express passenger station order (left to right)
LocationExpressPassStations = [0,4970,6630,8540,15540,16940,19540,21940,33240,42640,49650,54308] # actual express passenger station distances (left to right)

i=0
for SheetName in Data.sheet_names:
	if not 'Sheet' in SheetName: # ignores empty sheets in excel file
		globals()[SheetSubstations[i]] = Substation(SheetName, Data.parse(SheetName).iloc[8:373], [], [], 1, 0, 0, 0, 0, 0, [], [], [], []) # assigns each substation's original 2018 data to a variable named after the substation
		SubstationDict[SheetSubstations[i]] = globals()[SheetSubstations[i]] # makes substation a member of its dictionary
		i=i+1

for PassStationName in NamePassStations:
	globals()[PassStationName] = PassStation(PassStationName, 1, 0, 0, 0, 0, 0) # assigns each passenger station's original 2018 data to a variable named after the passenger station
	PassStationDict[PassStationName] = globals()[PassStationName] # makes passenger station a member of its dictionary

# CLEAN AND REORGANIZE DATA #-----------------------------
for substation in SubstationDict.keys():
	SubstationDict[substation].origdata = SubstationDict[substation].origdata.set_index([SubstationDict[substation].origdata.iloc[:,0]]) # sets date column as row index
	SubstationDict[substation].origdata = SubstationDict[substation].origdata.drop(SubstationDict[substation].origdata.columns[0],axis=1) # removes date column still in data
	SubstationDict[substation].origdata = SubstationDict[substation].origdata.rename_axis("Date") # renames row axis "Date"
	SubstationDict[substation].origdata = SubstationDict[substation].origdata.rename_axis("Interval", axis="columns") # renames column axis "Interval"
	SubstationDict[substation].origdata = SubstationDict[substation].origdata.iloc[0:,1:].apply(pd.to_numeric, errors='coerce') # replaces missing/bad data with NaN
	SubstationDict[substation].origdata = SubstationDict[substation].origdata.dropna() # removes rows with bad data (NaN from previous line)

Factors = Factors.parse('Final').iloc[1:36, 0:15] # extracts only final factors from excel file
Factors = Factors.set_index(Factors.iloc[:,0]) # sets station names (passenger stations and substations) as index
Factors = Factors.drop(Factors.columns[0:2],axis=1) # removes station name column still in data
Factors = Factors.rename_axis("Station") # renames row axis "Station"
Factors = Factors.rename_axis("Substation", axis="columns") # renames column axis "Substation"

SolarCurve = SolarCurve.drop(SolarCurve.columns[0:1],axis=1) # removes number column still in imported solar data

#---------------------------------------------------------
# Each substation and its data, inputs, etc. can now be referred to from the dictionary
# For example: the original data from Tudor Substation: SubstationDict['Tudor'].origdata
#              the selected EV size at 58 St Substation: SubstationDict['St58'].EV
#
# Each passenger station and its inputs can now be referred to from the dictionary
# For example: the selected supercapacitor size at Vernon Passenger Station: PassStationDict['Vernon'].supcap
#              the selected battery size at TimesSquare Passenger Station: PassStationDict['TimesSquare'].batt

# TRANSIENT DATA #----------------------------------------------------------------------------------------------------
class LocalTrainProfile:
	train = 'Local'
	line = '7-Line'
	def __init__(self, number, data, normdata, originstation, destinationstation):
		self.number, self.data, self.normdata, self.originstation, self.destinationstation = number, data, normdata, originstation, destinationstation

class ExpressTrainProfile:
	train = 'Express'
	line = '7-Line'
	def __init__(self, number, data, normdata, originstation, destinationstation):
		self.number, self.data, self.normdata, self.originstation, self.destinationstation = number, data, normdata, originstation, destinationstation

i=1
LocalTrainProfileDict = {} # creates a single dictionary of local train profiles to loop through, allowing alteration of multiple profiles at once
for SheetName in LocalTrainProfiles.sheet_names:
	globals()[SheetName.replace("Sheet", "LocalTrainProfile")] = LocalTrainProfile(i, LocalTrainProfiles.parse(SheetName), [], NamePassStations[i-1], NamePassStations[i]) # assigns each traveling local train's data to a variable named 'LocalTrainProfile' and numbered based on the Excel Sheet #
	LocalTrainProfileDict[SheetName.replace("Sheet", "LocalTrainProfile")] = globals()[SheetName.replace("Sheet", "LocalTrainProfile")]
	i=i+1

i=1
ExpressTrainProfileDict = {} # creates a single dictionary of express train profiles to loop through, allowing alteration of multiple profiles at once
for SheetName in ExpressTrainProfiles.sheet_names:
	globals()[SheetName.replace("Sheet", "ExpressTrainProfile")] = ExpressTrainProfile(i, ExpressTrainProfiles.parse(SheetName), [], NameExpressPassStations[i-1], NameExpressPassStations[i]) # assigns each traveling express train's data to a variable named 'ExpressTrainProfile' and numbered based on the Excel Sheet #
	ExpressTrainProfileDict[SheetName.replace("Sheet", "ExpressTrainProfile")] = globals()[SheetName.replace("Sheet", "ExpressTrainProfile")]
	i=i+1

#---------------------------------------------------------
# Each local or express train profile and its data can now be referred to from the dictionary
# For example: the profile number : LocalTrainProfileDict["LocalTrainProfile1"].number
#              the profile's data :	LocalTrainProfileDict["LocalTrainProfile21"].data
#			   the profile's normalized data : LocalTrainProfileDict["LocalTrainProfile12"].normdata
#			   the profile's origin station : ExpressTrainProfileDict["ExpressTrainProfile1"].originstation
#			   the profile's destination station : ExpressTrainProfileDict["ExpressTrainProfile11"].destinationstation