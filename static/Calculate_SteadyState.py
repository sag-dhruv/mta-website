# TIME: YEARLY AVERAGE (for now) #------------------------------------------------------------------------------------------------------------------------
# Original Curve Generation----------
for substation in SubstationDict.keys(): # for each substation
		SubstationDict[substation].origdata = SubstationDict[substation].origdata.mean()*4 # takes average of all rows (in column direction) and multiplies by 4 (due to there being 15-minute power measurements)
		SubstationDict[substation].origdata = SubstationDict[substation].origdata/1000 # converts power data from kW to MW
		SubstationDict[substation].normdata = SubstationDict[substation].origdata/max(SubstationDict[substation].origdata) # creates equivalent normalized curves for ESS integration (more apparent when larger power values exist due to there being more trains)
		
#---------------------------------------------------------------------------------------------------------------------------------------------------------
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

	# Modified Curve Generation----------
	SubstationDict[substation].moddata = SubstationDict[substation].origdata - np.multiply(SubstationDict[substation].origdata, 0.4*TotalESSContribution, SubstationDict[substation].normdata) # power reduction due to ESS (0.4 comes from derived equation where decimal reduction = 0.4 * (ESS Size))

	EVregen = np.multiply(np.subtract(1, SubstationDict[substation].normdata), TotalEVContribution) # allows train's regenerative power to flow to EV
	SubstationDict[substation].moddata = SubstationDict[substation].moddata + EVregen # power increase due to EV

	SubstationDict[substation].moddata = np.stack(SubstationDict[substation].moddata.values) - np.multiply(TotalPVContribution, SolarCurve.iloc[:,0]) # power reduction due to PV

	SubstationDict[substation].moddata[SubstationDict[substation].moddata < 0] = 0 # removes negative values (rectified power)