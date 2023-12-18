import matplotlib
matplotlib.use('Agg') 
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import json

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View, DeleteView
from django.http import JsonResponse

class Substation:
	line = '7-Line'
	def __init__(self, name, origdata, normdata, moddata, default, EV, batt, fly, supcap, PV, transientcoefficients, transientorigdata, transientregendata, transientmoddata): # assigns properties to Substation class object
		self.name, self.origdata, self.normdata, self.moddata, self.default, self.EV, self.batt, self.fly, self.supcap, self.PV, self.transientcoefficients, self.transientorigdata, self.transientregendata, self.transientmoddata = name, origdata, normdata, moddata, default, EV, batt, fly, supcap, PV, transientcoefficients, transientorigdata, transientregendata, transientmoddata

class PassStation:
	line = '7-Line'
	def __init__(self, name, default, EV, batt, fly, supcap, PV): # assigns properties to PassStation class object
		self.name, self.default, self.EV, self.batt, self.fly, self.supcap, self.PV = name, default, EV, batt, fly, supcap, PV

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

class UpdateGraphMultiple(View):
    def get(self, request):
        SheetSubstations = ['Spruce', 'St58', 'QueensBlvd', 'Lawrence', 'Corona', 'St78', 'Jackson', 'Ave50', 'Tudor', 'Ave7', 'Park', 'Ave10', 'Hudson34']
        # Load user input data
        print(json.loads(request.GET.get('value')),"+++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        sheet_substations_data = json.loads(request.GET.get('value'))['mta_chat_data']['power']
        sheet_passenger_stations_data = json.loads(request.GET.get('value'))['mta_chat_data']['passenger']
        sheet_transient_data = json.loads(request.GET.get('value'))['transient_data']
        print("\n\nsheet_substations_data----->",sheet_substations_data)
        print("\n\sheet_passenger_stations_data----->",sheet_passenger_stations_data)
        
        SubstationDict, PassStationDict, SolarCurve, Factors, LocalTrainProfileDict, ExpressTrainProfileDict = self.open_and_process_data()

        NamePassStations = ['HudsonYards','TimesSquare','Ave5','GrandCentral','Vernon','HuntersPoint','CourtSquare','QueensboroPlaza','St33','St40','St46','St52','St61','St69','St74','St82','St90','JunctionBlvd','St103','St111','WilletsPoint','MainSt']
        LocationPassStations = [0,4970,6630,8540,15540,16940,19540,21940,25360,27250,28860,30560,33240,35150,36560,38650,40650,42640,44650,46690,49650,54308]
        NameExpressPassStations = ['HudsonYards','TimesSquare','Ave5','GrandCentral','Vernon','HuntersPoint','CourtSquare','QueensboroPlaza','St61','JunctionBlvd','WilletsPoint','MainSt']
        LocationExpressPassStations = [0,4970,6630,8540,15540,16940,19540,21940,33240,42640,49650,54308]

        station_EV = 0
        station_batt = 0
        station_fly = 0
        station_PV = 0
        station_supcap = 0
        for SheetName in SubstationDict:
            if SheetName in sheet_substations_data:
                ParameterData = sheet_substations_data[SheetName] or {}
                SubstationDict[SheetName].default = 0
                if 'ev_size' in ParameterData:
                    if ParameterData['ev_size'] != '':
                        station_EV = float(ParameterData['ev_size'])
                if 'battery_size' in ParameterData:
                    if ParameterData['battery_size'] != '':
                        station_batt = float(ParameterData['battery_size'])
                if 'fly_size' in ParameterData:
                    if ParameterData['fly_size'] != '':
                        station_fly = float(ParameterData['fly_size'])
                if 'solar_size' in ParameterData:
                    if ParameterData['solar_size'] != '':
                        station_PV = float(ParameterData['solar_size'])
                if 'supercapacitor_size' in ParameterData:
                    if ParameterData['supercapacitor_size'] != '':
                        station_supcap = float(ParameterData['supercapacitor_size'])
            SubstationDict[SheetName].EV = station_EV
            SubstationDict[SheetName].batt = station_batt
            SubstationDict[SheetName].fly = station_fly
            SubstationDict[SheetName].PV = station_PV
            SubstationDict[SheetName].supcap = station_supcap
            
            # Reset the values
            station_EV = 0
            station_batt = 0
            station_fly = 0
            station_PV = 0
            station_supcap = 0
        
        passenger_EV = 0
        passenger_batt = 0
        passenger_fly = 0
        passenger_PV = 0
        passenger_supcap = 0
        for SheetName in PassStationDict:
            if SheetName in sheet_passenger_stations_data:
                ParameterData = sheet_passenger_stations_data[SheetName] or {}
                PassStationDict[SheetName].default = 0
                if 'ev_size' in ParameterData:
                    if ParameterData['ev_size'] != '':
                        passenger_EV = float(ParameterData['ev_size'])
                if 'battery_size' in ParameterData:
                    if ParameterData['battery_size'] != '':
                        passenger_batt = float(ParameterData['battery_size'])
                if 'fly_size' in ParameterData:
                    if ParameterData['fly_size'] != '':
                        passenger_fly = float(ParameterData['fly_size'])
                if 'solar_size' in ParameterData:
                    if ParameterData['solar_size'] != '':
                        passenger_PV = float(ParameterData['solar_size'])
                if 'supercapacitor_size' in ParameterData:
                    if ParameterData['supercapacitor_size'] != '':
                        passenger_supcap = float(ParameterData['supercapacitor_size'])
            PassStationDict[SheetName].EV = passenger_EV
            PassStationDict[SheetName].batt = passenger_batt
            PassStationDict[SheetName].fly = passenger_fly
            PassStationDict[SheetName].PV = passenger_PV
            PassStationDict[SheetName].supcap = passenger_supcap
            
            # Reset the values
            passenger_EV = 0
            passenger_batt = 0
            passenger_fly = 0
            passenger_PV = 0
            passenger_supcap = 0

        if len(sheet_transient_data) != 0:
            train = sheet_transient_data['train_type']
            originstation = sheet_transient_data['origin_station']
            destinationstation = sheet_transient_data['destination_station']

        exec(open('static/Calculate_SteadyState.py').read())
        exec(open('static/Plot_SteadyState.py').read())
        if len(sheet_transient_data) != 0:
            exec(open('static/Calculate_Transient.py').read())
            exec(open('static/Plot_Transient.py').read())
        
        data = {
            'graphs': SheetSubstations,
            'trasient_part': True if len(sheet_transient_data) != 0 else False
        }
        return JsonResponse(data)
        
    def open_and_process_data(self):
        Data = pd.ExcelFile('static/2018.xlsx')
        Factors = pd.ExcelFile('static/Factors.xlsx')
        SolarCurve = pd.ExcelFile('static/NYCAprilSolar_Data.xlsx').parse('Gaussian Expanded').iloc[0:96]
        LocalTrainProfiles = pd.ExcelFile('static/LocalTrainProfiles.xlsx')
        ExpressTrainProfiles = pd.ExcelFile('static/ExpressTrainProfiles.xlsx')
        Coefficients = pd.ExcelFile('static/Gauss2Coefficients.xlsx').parse('Sheet1').iloc[1:22]

        SheetSubstations = ['Spruce','St58','QueensBlvd','Lawrence','Corona','St78','Jackson','Ave50','Tudor','Ave7','Park','Ave10','Hudson34']
        SubstationDict = {}

        NamePassStations = ['HudsonYards','TimesSquare','Ave5','GrandCentral','Vernon','HuntersPoint','CourtSquare','QueensboroPlaza','St33','St40','St46','St52','St61','St69','St74','St82','St90','JunctionBlvd','St103','St111','WilletsPoint','MainSt']
        LocationPassStations = [0,4970,6630,8540,15540,16940,19540,21940,25360,27250,28860,30560,33240,35150,36560,38650,40650,42640,44650,46690,49650,54308]
        PassStationDict = {}

        NameExpressPassStations = ['HudsonYards','TimesSquare','Ave5','GrandCentral','Vernon','HuntersPoint','CourtSquare','QueensboroPlaza','St61','JunctionBlvd','WilletsPoint','MainSt']
        LocationExpressPassStations = [0,4970,6630,8540,15540,16940,19540,21940,33240,42640,49650,54308]

        i=0
        for SheetName in Data.sheet_names:
            if not 'Sheet' in SheetName:
                globals()[SheetSubstations[i]] = Substation(SheetName, Data.parse(SheetName).iloc[8:373], [], [], 1, 0, 0, 0, 0, 0, [], [], [], [])
                SubstationDict[SheetSubstations[i]] = globals()[SheetSubstations[i]]
                i=i+1

        for PassStationName in NamePassStations:
            globals()[PassStationName] = PassStation(PassStationName, 1, 0, 0, 0, 0, 0)
            PassStationDict[PassStationName] = globals()[PassStationName]

        # CLEAN AND REORGANIZE DATA
        for substation in SubstationDict.keys():
            SubstationDict[substation].origdata = SubstationDict[substation].origdata.set_index([SubstationDict[substation].origdata.iloc[:,0]])
            SubstationDict[substation].origdata = SubstationDict[substation].origdata.drop(SubstationDict[substation].origdata.columns[0],axis=1)
            SubstationDict[substation].origdata = SubstationDict[substation].origdata.rename_axis("Date")
            SubstationDict[substation].origdata = SubstationDict[substation].origdata.rename_axis("Interval", axis="columns")
            SubstationDict[substation].origdata = SubstationDict[substation].origdata.iloc[0:,1:].apply(pd.to_numeric, errors='coerce')
            SubstationDict[substation].origdata = SubstationDict[substation].origdata.dropna()

        Factors = Factors.parse('Final').iloc[1:36, 0:15]
        Factors = Factors.set_index(Factors.iloc[:,0])
        Factors = Factors.drop(Factors.columns[0:2],axis=1)
        Factors = Factors.rename_axis("Station")
        Factors = Factors.rename_axis("Substation", axis="columns")

        SolarCurve = SolarCurve.drop(SolarCurve.columns[0:1],axis=1)


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

        return SubstationDict, PassStationDict, SolarCurve, Factors, LocalTrainProfileDict, ExpressTrainProfileDict
    

def index(request):
    response = redirect('/')
    return render(request, 'index.html')


def mta_line(request):
    return render(request, 'mta7_line.html')


def about(request):
    return render(request, 'about.html')


def service(request):
    return render(request, 'service.html')


def blog(request):
    return render(request, 'blog.html')


def contact(request):
    return render(request, 'contact.html')
