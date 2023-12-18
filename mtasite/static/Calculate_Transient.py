Coefficients = pd.ExcelFile('static/Gauss2Coefficients.xlsx').parse('Sheet1').iloc[1:22]
if train == 'Express':
	Profiles = ExpressTrainProfileDict # uses express train profiles
	ListStations = NameExpressPassStations # uses express passenger stations
	ListLocations = LocationExpressPassStations # uses names of express passenger stations
	originnumber = ListStations.index(originstation) # locates originstation in list of stations
	destinationnumber = ListStations.index(destinationstation) # locates destinationstation in list of stations
elif train == 'Local':
	Profiles = LocalTrainProfileDict # uses local train profiles
	ListStations = NamePassStations # uses local (all) passenger stations
	ListLocations = LocationPassStations # uses names of local (all) passenger stations
	originnumber = ListStations.index(originstation) # locates originstation in list of stations
	destinationnumber = ListStations.index(destinationstation) # locates destinationstation in list of stations

if originnumber > destinationnumber:
	direction = 'Manhattanbound' # identifies direction of train travel
	d = -1 # negative to iterate from a larger distance downwards
else:
	direction = 'Queensbound' # identifies direction of train travel
	d = 1

TransientTrainTimeProfile= [0]
TransientTrainPowerProfile= [0]
TransientTrainDistanceProfile= [0]
TransientTrainSpeedProfile= [0]
TransientTrainAccelerationProfile= [0]

# Train Curve Generation----------
for i in range(originnumber, destinationnumber, d):
	for profile in Profiles.keys():
		if direction == 'Queensbound':
			if Profiles[profile].originstation == ListStations[i]:
				TransientTrainTimeProfile = np.concatenate((TransientTrainTimeProfile, np.add(np.stack(Profiles[profile].data[Profiles[profile].data.columns[0]]), max(TransientTrainTimeProfile)))) # train time profile
				TransientTrainPowerProfile = np.concatenate((TransientTrainPowerProfile, np.stack(Profiles[profile].data[Profiles[profile].data.columns[1]]))) # train power profile
				TransientTrainDistanceProfile = np.concatenate((TransientTrainDistanceProfile, np.add(np.stack(Profiles[profile].data[Profiles[profile].data.columns[2]]), max(TransientTrainDistanceProfile)))) # train distance profile
				TransientTrainSpeedProfile = np.concatenate((TransientTrainSpeedProfile, np.stack(Profiles[profile].data[Profiles[profile].data.columns[3]]))) # train speed profile
				TransientTrainAccelerationProfile = np.concatenate((TransientTrainAccelerationProfile, np.stack(Profiles[profile].data[Profiles[profile].data.columns[4]]))) # train acceleration profile

				TransientTrainLocationProfile = np.add(TransientTrainDistanceProfile, ListLocations[originnumber]) # train location profile

		if direction == 'Manhattanbound':
			if Profiles[profile].destinationstation == ListStations[i]:
				TransientTrainTimeProfile = np.concatenate((TransientTrainTimeProfile, np.add(np.stack(Profiles[profile].data[Profiles[profile].data.columns[0]]), max(TransientTrainTimeProfile)))) # train time profile
				TransientTrainPowerProfile = np.concatenate((TransientTrainPowerProfile, np.stack(Profiles[profile].data[Profiles[profile].data.columns[1]]))) # train power profile
				TransientTrainDistanceProfile = np.concatenate((TransientTrainDistanceProfile, np.add(np.stack(Profiles[profile].data[Profiles[profile].data.columns[2]]), max(TransientTrainDistanceProfile)))) # train distance profile
				TransientTrainSpeedProfile = np.concatenate((TransientTrainSpeedProfile, np.stack(Profiles[profile].data[Profiles[profile].data.columns[3]]))) # train speed profile
				TransientTrainAccelerationProfile = np.concatenate((TransientTrainAccelerationProfile, np.stack(Profiles[profile].data[Profiles[profile].data.columns[4]]))) # train acceleration profile

				TransientTrainLocationProfile = np.subtract(ListLocations[originnumber], TransientTrainDistanceProfile) # train location profile

skip = 10 # used to skip rows to reduce time
# Reduce Time
TransientTrainTimeProfile = TransientTrainTimeProfile[::skip]
TransientTrainPowerProfile = TransientTrainPowerProfile[::skip]
TransientTrainDistanceProfile = TransientTrainDistanceProfile[::skip]
TransientTrainSpeedProfile = TransientTrainSpeedProfile[::skip]
TransientTrainAccelerationProfile = TransientTrainAccelerationProfile[::skip]
TransientTrainLocationProfile = TransientTrainLocationProfile[::skip]

# Substation Curve Generation [Based on Just Train]: 'origdata'-----------------------------------------------------------------------------------------------------------------------

TrainAcceleratingPowerProfile = np.copy(TransientTrainPowerProfile) # isolates train's accelerating power values
TrainDeceleratingPowerProfile = np.copy(TransientTrainPowerProfile) # isolates train's decelerating power values (regeneration)

TrainAcceleratingPowerProfile[TrainAcceleratingPowerProfile < 0] = 0
TrainDeceleratingPowerProfile[TrainDeceleratingPowerProfile > 0] = 0

SubstationFactors = pd.DataFrame()
for substation in SubstationDict.keys():

	SubstationDict[substation].transientcoefficients = Coefficients.loc[:, substation] # imports each substation's polynomial coefficients

	a1 = SubstationDict[substation].transientcoefficients.loc[1]
	b1 = SubstationDict[substation].transientcoefficients.loc[2]
	c1 = SubstationDict[substation].transientcoefficients.loc[3]
	a2 = SubstationDict[substation].transientcoefficients.loc[4]
	b2 = SubstationDict[substation].transientcoefficients.loc[5]
	c2 = SubstationDict[substation].transientcoefficients.loc[6]

	SubstationFactors.loc[:, substation] = np.multiply(a1, np.exp(np.multiply(np.power(np.divide(np.subtract(TransientTrainLocationProfile,b1),c1),2),-1))) + np.multiply(a2, np.exp(np.multiply(np.power(np.divide(np.subtract(TransientTrainLocationProfile,b2),c2),2),-1))) # applies gaussian equation (substation contribution factor as a function of train location)

	SubstationFactors.loc[:, substation][SubstationFactors.loc[:, substation] < 0] = 0 # turns negative substation contribution factors to zero

SubstationFactors_New = pd.DataFrame()
SubstationOrder = ['Hudson34','Ave10','Ave7','Park','Tudor','Ave50','Jackson','QueensBlvd','St58','St78','Spruce','Corona','Lawrence'] # actual substation order (left to right)
for i in range(0, len(SubstationFactors.columns)):
	SubstationFactors_New.loc[:, i] = SubstationFactors.loc[:, SubstationOrder[i]] # reorders substation factor matrix columns for indexing

# Sorted Values
for i in range(0,len(SubstationFactors_New.index)): # indexing by row
	for j in range(0, len(SubstationFactors_New.columns)): # indexing by column

		if j > SubstationFactors_New.iloc[i, :].idxmax() and j+1 < len(SubstationFactors_New.columns):
			SubstationFactors_New.iloc[i,j:len(SubstationFactors_New.columns)+1] = sorted(SubstationFactors_New.iloc[i,j:len(SubstationFactors_New.columns)+1], reverse = True) # sorts values to the right of maximum diagonal in decreasing order (horizontally)
		if j < SubstationFactors_New.iloc[i, :].idxmax(): 
			SubstationFactors_New.iloc[i, 0:j+1] = sorted(SubstationFactors_New.iloc[i, 0:j+1]) # sorts values to the left of maximum diagonal in increasing order (horizontally)

# Sum = 1 horizontally
for i in range(0,len(SubstationFactors_New.index)):

	if sum(SubstationFactors_New.iloc[i, :]) != 0: # to avoid NaN if dividing by zero sum
		SubstationFactors_New.iloc[i, :] = np.divide(SubstationFactors_New.iloc[i, :],sum(SubstationFactors_New.iloc[i, :])) # sets sum of factors row horizontally equal to 1

SubstationFactors_New.columns = SubstationOrder # renames substation factor matrix columns
#SubstationFactors_New.to_excel('SubstationPythonFactors.xlsx', sheet_name='Sheet1', index = False) # saves in excel file to view

for substation in SubstationDict.keys(): # for each substation

	SubstationDict[substation].transientorigdata = np.multiply(SubstationFactors_New.loc[:, substation],TrainAcceleratingPowerProfile) # power output by substation for each train acceleration cycle
	SubstationDict[substation].transientorigdata = SubstationDict[substation].transientorigdata/1000000 # in MW

	SubstationDict[substation].transientregendata = np.multiply(SubstationFactors_New.loc[:, substation],TrainDeceleratingPowerProfile) # power sent back by each train regeneration cycle
	SubstationDict[substation].transientregendata = SubstationDict[substation].transientregendata/1000000 # in MW

# Substation Curve Generation [Based on Train and Inputs]: 'moddata'-------------------------------------------------------------------------------------------------------------------

for substation in SubstationDict.keys(): # for each substation
	
	SubstationESSInputs = []
	SubstationEVInputs = []
	SubstationPVInputs = []

	for station in SubstationDict.keys():
		SubstationESSInputs.append(sum([SubstationDict[station].batt, SubstationDict[station].fly, SubstationDict[station].supcap])) # vector of all substation ESS inputs for each substation
		SubstationEVInputs.append(SubstationDict[station].EV) # vector of all substation EV inputs for each substation
		SubstationPVInputs.append(SubstationDict[station].PV/1000) # vector of all substation PV inputs for each substation

	SubstationFactors = Factors.loc[:,substation].loc[list(SubstationDict)] # vector of all substation factors (from factor matrix) for each substation (column-wise)

	SubstationESSContributions = np.multiply(SubstationESSInputs, SubstationFactors) # multiplies inputs and factors vectors to determine ESS contribution from each substation for each substation
	SubstationEVContributions = np.multiply(SubstationEVInputs, SubstationFactors) # multiplies inputs and factors vectors to determine EV contribution from each substation for each substation
	SubstationPVContributions = np.multiply(SubstationPVInputs, SubstationFactors) # multiplies inputs and factors vectors to determine PV contribution from each substation for each substation

	PassStationESSInputs = []
	PassStationEVInputs = []
	PassStationPVInputs = []

	for station in PassStationDict.keys():
		PassStationESSInputs.append(sum([PassStationDict[station].batt, PassStationDict[station].fly, PassStationDict[station].supcap]))  # vector of all passenger station ESS inputs for each substation
		PassStationEVInputs.append(PassStationDict[station].EV)  # vector of all passenger station EV inputs for each substation
		PassStationPVInputs.append(PassStationDict[station].PV/1000)  # vector of all passenger station PV inputs for each substation

	PassStationFactors = Factors.loc[:,substation].loc[list(PassStationDict)] # vector of all passenger station factors (from factor matrix) for each substation (column-wise)

	PassStationESSContributions = np.multiply(PassStationESSInputs, PassStationFactors) # multiplies inputs and factors vectors to determine ESS contribution from each passenger station for each substation
	PassStationEVContributions = np.multiply(PassStationEVInputs, PassStationFactors) # multiplies inputs and factors vectors to determine EV contribution from each passenger station for each substation
	PassStationPVContributions = np.multiply(PassStationPVInputs, PassStationFactors) # multiplies inputs and factors vectors to determine PV contribution from each passenger station for each substation

	TotalESSContribution = np.add(sum(SubstationESSContributions), sum(PassStationESSContributions)) # sums all ESS contributions (from both substations and passenger stations) for each substation
	TotalEVContribution = np.add(sum(SubstationEVContributions), sum(PassStationEVContributions)) # sums all EV contributions (from both substations and passenger stations) for each substation
	TotalPVContribution = np.add(sum(SubstationPVContributions), sum(PassStationPVContributions)) # sums all PV contributions (from both substations and passenger stations) for each substation

	# Modified Curve Generation
	SubstationDict[substation].transientmoddata = SubstationDict[substation].transientorigdata - np.multiply(SubstationDict[substation].transientorigdata, 0.4*TotalESSContribution) # power reduction due to ESS (0.4 comes from derived equation where decimal reduction = 0.4 * (ESS Size))
	
	EVregen = np.copy(SubstationDict[substation].transientregendata) + TotalEVContribution # allows train's regenerative power to flow to EV
	EVregen[EVregen < 0] = 0
	SubstationDict[substation].transientmoddata = SubstationDict[substation].transientmoddata + EVregen # power increase due to EV

	SubstationDict[substation].transientmoddata = np.stack(SubstationDict[substation].transientmoddata.values) - TotalPVContribution # power reduction due to PV

	SubstationDict[substation].transientmoddata[SubstationDict[substation].transientmoddata < 0] = 0 # removes negative values (rectified power)