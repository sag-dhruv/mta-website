# Traveling Train's Power Profile----------
plt.rcParams["figure.autolayout"] = True
plt.rcParams["lines.linewidth"] = 2.5
plt.rcParams["font.family"] = "cursive"
plt.rcParams["font.size"] = "12"
plt.xlabel('Time [s]', fontsize=16)
plt.ylabel('Power [MW]', fontsize=16)
plt.title('7-Train Power Profile',fontsize=20)
plt.xlim(0,max(TransientTrainTimeProfile))
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.plot(TransientTrainTimeProfile, TransientTrainPowerProfile, color='blue') # original data
#plt.show() # to view graph in display
plt.savefig('static/TrainGraphs_Transient/' + 'TrainPower' + '.png')
plt.cla()

# Traveling Train's Current Profile----------
plt.rcParams["figure.autolayout"] = True
plt.rcParams["lines.linewidth"] = 2.5
plt.rcParams["font.family"] = "cursive"
plt.rcParams["font.size"] = "12"
plt.xlabel('Time [s]', fontsize=16)
plt.ylabel('Current [A]', fontsize=16)
plt.title('7-Train Current Profile',fontsize=20)
plt.xlim(0,max(TransientTrainTimeProfile))
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.plot(TransientTrainTimeProfile, TransientTrainPowerProfile/650, color='blue') # original data
#plt.show() # to view graph in display
plt.savefig('static/TrainGraphs_Transient/' + 'TrainCurrent' + '.png')
plt.cla()

# Traveling Train's Distance Profile----------
plt.rcParams["figure.autolayout"] = True
plt.rcParams["lines.linewidth"] = 2.5
plt.rcParams["font.family"] = "cursive"
plt.rcParams["font.size"] = "12"
plt.xlabel('Time [s]', fontsize=16)
plt.ylabel('Distance [ft]', fontsize=16)
plt.title('7-Train Distance Profile',fontsize=20)
plt.xlim(0,max(TransientTrainTimeProfile))
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.plot(TransientTrainTimeProfile, TransientTrainDistanceProfile, color='blue') # original data
#plt.show() # to view graph in display
plt.savefig('static/TrainGraphs_Transient/' + 'TrainDistance' + '.png')
plt.cla()

# Traveling Train's Speed Profile----------
plt.rcParams["figure.autolayout"] = True
plt.rcParams["lines.linewidth"] = 2.5
plt.rcParams["font.family"] = "cursive"
plt.rcParams["font.size"] = "12"
plt.xlabel('Time [s]', fontsize=16)
plt.ylabel('Speed [mph]', fontsize=16)
plt.title('7-Train Speed Profile',fontsize=20)
plt.xlim(0,max(TransientTrainTimeProfile))
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.plot(TransientTrainTimeProfile, TransientTrainSpeedProfile, color='blue') # original data
#plt.show() # to view graph in display
plt.savefig('static/TrainGraphs_Transient/' + 'TrainSpeed' + '.png')
plt.cla()

# Traveling Train's Acceleration Profile----------
plt.rcParams["figure.autolayout"] = True
plt.rcParams["lines.linewidth"] = 2.5
plt.rcParams["font.family"] = "cursive"
plt.rcParams["font.size"] = "12"
plt.xlabel('Time [s]', fontsize=16)
plt.ylabel('Acceleration [mphps]', fontsize=16)
plt.title('7-Train Acceleration Profile',fontsize=20)
plt.xlim(0,max(TransientTrainTimeProfile))
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.plot(TransientTrainTimeProfile, TransientTrainAccelerationProfile, color='blue') # original data
#plt.show() # to view graph in display
plt.savefig('static/TrainGraphs_Transient/' + 'TrainAcceleration' + '.png')
plt.cla()

# Traveling Train's Location Profile (Along the Entire Line)----------
plt.rcParams["figure.autolayout"] = True
plt.rcParams["lines.linewidth"] = 2.5
plt.rcParams["font.family"] = "cursive"
plt.rcParams["font.size"] = "12"
plt.xlabel('Time [s]', fontsize=16)
plt.ylabel('Location [ft]', fontsize=16)
plt.title('7-Train Location Profile',fontsize=20)
plt.xlim(0,max(TransientTrainTimeProfile))
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.plot(TransientTrainTimeProfile, TransientTrainLocationProfile, color='blue') # original data
#plt.show() # to view graph in display
plt.savefig('static/TrainGraphs_Transient/' + 'TrainLocation' + '.png')
plt.cla()

# Substation Power Profiles as Train Travels By
for substation in SubstationDict.keys():
		
	plt.rcParams["figure.autolayout"] = True
	plt.rcParams["lines.linewidth"] = 2.5
	plt.rcParams["font.family"] = "cursive"
	plt.rcParams["font.size"] = "12"

	#plt.title(substation,fontsize=20)
	plt.xlabel('Time [s]', fontsize=16)
	plt.ylabel('Power [MW]', fontsize=16)
	plt.xlim(0,max(TransientTrainTimeProfile))
	plt.ylim(-0.5,7)
	plt.xticks(fontsize=12)
	plt.yticks(fontsize=12)

	#plt.show() # to view graph in display	
	plt.plot(TransientTrainTimeProfile, SubstationDict[substation].transientorigdata, color='blue') # original data
	
	plt.plot(TransientTrainTimeProfile, SubstationDict[substation].transientmoddata, color='red') # modified data
	plt.legend(['Original', 'Modified'], loc = "upper right", fontsize=12)

	plt.savefig(f'static/ModGraphs_Transient/{substation}.png')
	plt.cla()