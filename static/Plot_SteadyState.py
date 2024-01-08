# Substation 24 Hr Power Profiles
for substation in SubstationDict.keys(): # for each substation
		
	#plt.rcParams["figure.figsize"] = [7.00, 5.00] # if want to set figure size
	plt.rcParams["figure.autolayout"] = True # allows figure to autodimension
	plt.rcParams["lines.linewidth"] = 2.5
	plt.rcParams["font.family"] = "cursive" # makes plot "cartoonish"
	plt.rcParams["font.size"] = "12"

	#plt.title(substation,fontsize=20)
	plt.xlabel('Time [Hr]', fontsize=16)
	plt.ylabel('Power [MW]', fontsize=16)
	plt.xlim(0,95)
	#plt.ylim(0,10)
	plt.xticks(np.arange(0,95,95/12), np.arange(0,24,2), fontsize=12) # sets x-axis in Hrs
	plt.yticks(fontsize=12)

	#plt.show() # to view graph in display
	#plt.grid() # to add grid to background of figure
	plt.plot(SubstationDict[substation].origdata, color='blue') # original data
	
	plt.plot(SubstationDict[substation].moddata, color='red') # modified data
	plt.legend(['Original', 'Modified'], loc = "lower right", fontsize=12)	

	plt.savefig(f'static/ModGraphs_SteadyState/{substation}.png') # to save in corresponding folder
	plt.cla() # to clear display to show next figure in loop