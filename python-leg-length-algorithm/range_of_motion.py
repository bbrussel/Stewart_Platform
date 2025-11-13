
import numpy as np
import classes
import json
from datetime import datetime
import humanize
from tqdm import tqdm
import itertools
import copy

def print_progress(counter, total_iterations, startTime):
	print("")
	print(f"{100*counter/total_iterations:.1f}%")
	now = datetime.now()
	elapsedTime = now - startTime
	timePerIteration = elapsedTime.total_seconds() / (counter + 1)
	estimatedRemainingTime = timePerIteration * (total_iterations - counter)
	print(humanize.naturaldelta(elapsedTime), "elapsed")
	print(humanize.naturaldelta(estimatedRemainingTime), "remaining")

def generate_results_json(max_values_dict, xTranslation_values, yTranslation_values, zTranslation_values, pitch_values, roll_values, yaw_values, combinations):
	result_json = {}
	for key, value in max_values_dict.items():
		if hasattr(value, '__dict__'):  # Check if it's an object with attributes
			# Round all float values in the object's attributes to 2 decimal places
			result_json[key] = {k: round(v, 2) if isinstance(v, float) else v for k, v in vars(value).items()}
		else:  # It's a simple value like the height
			result_json[key] = round(value, 2) if isinstance(value, float) else value

	result_json["sweep_parameters"] = {
		"xTranslation": {
			"min": round(float(xTranslation_values.min()) if hasattr(xTranslation_values, 'min') else xTranslation_values[0], 2),
			"max": round(float(xTranslation_values.max()) if hasattr(xTranslation_values, 'max') else xTranslation_values[0], 2),
			"steps": len(xTranslation_values)
		},
		"yTranslation": {
			"min": round(float(yTranslation_values.min()) if hasattr(yTranslation_values, 'min') else yTranslation_values[0], 2),
			"max": round(float(yTranslation_values.max()) if hasattr(yTranslation_values, 'max') else yTranslation_values[0], 2),
			"steps": len(yTranslation_values)
		},
		"zTranslation": {
			"min": round(float(zTranslation_values.min()) if hasattr(zTranslation_values, 'min') else zTranslation_values[0], 2),
			"max": round(float(zTranslation_values.max()) if hasattr(zTranslation_values, 'max') else zTranslation_values[0], 2),
			"steps": len(zTranslation_values)
		},
		"pitch": {
			"min": round(float(pitch_values.min()) if hasattr(pitch_values, 'min') else pitch_values[0], 2),
			"max": round(float(pitch_values.max()) if hasattr(pitch_values, 'max') else pitch_values[0], 2),
			"steps": len(pitch_values)
		},
		"roll": {
			"min": round(float(roll_values.min()) if hasattr(roll_values, 'min') else roll_values[0], 2),
			"max": round(float(roll_values.max()) if hasattr(roll_values, 'max') else roll_values[0], 2),
			"steps": len(roll_values)
		},
		"yaw": {
			"min": round(float(yaw_values.min()) if hasattr(yaw_values, 'min') else yaw_values[0], 2),
			"max": round(float(yaw_values.max()) if hasattr(yaw_values, 'max') else yaw_values[0], 2),
			"steps": len(yaw_values)
		},
		"total_combinations": len(combinations)
	}

	return result_json

def range_of_motion():
	actuateLegs = False
	generatePlot = False
	config_file = r"C:\Users\Brian\Desktop\Stewart Platform\Stewart_Platform\python-leg-length-algorithm\configs\OSBS_24.json"
	with open(config_file, "r") as f:
		platform_config_dict = json.load(f)

	assemblyGeometry = classes.SP_assemblyGeometry()

	assemblyGeometry.ingest_dict(platform_config_dict)

	ser = None  # Initialize serial connection as None

	baseOrientation = classes.orientation() #Initialize orientation class for base
	baseOrientation.xTranslation = 0.0
	baseOrientation.yTranslation = 0.0
	baseOrientation.zTranslation = 0.0
	baseOrientation.pitchDegrees = 0.0
	baseOrientation.rollDegrees = 0.0
	baseOrientation.yawDegrees = 0.0

	platformOrientation = classes.orientation() #Initialize orientation class for platform
	platformOrientation.xTranslation = 0.0
	platformOrientation.yTranslation = 0.0
	platformOrientation.zTranslation = 0.0
	platformOrientation.pitchDegrees = 0.0
	platformOrientation.rollDegrees = 0.0
	platformOrientation.yawDegrees = 0.0
	
	max_values_dict = {
    "xTranslation": None,
	"xTranslation_height": None,
    "yTranslation": None,
	"yTranslation_height": None,
    "zTranslation": None,
	"zTranslation_height": None,
    "pitchDegrees": None,
	"pitchDegrees_height": None,
    "rollDegrees": None,
	"rollDegrees_height": None,
    "yawDegrees": None,
	"yawDegrees_height": None
	}

	# Set Sweep parameters here
	xTranslation_values = [0.0]
	yTranslation_values = [0.0]
	zTranslation_values = np.linspace(0, -200, 200)
	pitch_values = np.linspace(-90, 90, 360)
	roll_values = [0.0]
	yaw_values = [0.0]

	combinations = list(itertools.product(xTranslation_values, yTranslation_values, zTranslation_values, pitch_values, roll_values, yaw_values))

	# Iterate with progress bar
	for x, y, z, pitch, roll, yaw in tqdm(combinations, desc="Processing poses"):
		platformOrientation.xTranslation = x
		platformOrientation.yTranslation = y
		platformOrientation.zTranslation = z
		platformOrientation.pitchDegrees = pitch
		platformOrientation.rollDegrees = roll
		platformOrientation.yawDegrees = yaw
		ser, results = assemblyGeometry.processPose(platformOrientation, baseOrientation, ser, generatePlot, actuateLegs)
		
		if (results.min() > assemblyGeometry.actuatorClosedLength) and (results.max() < assemblyGeometry.actuatorFullLength):
			if max_values_dict["xTranslation"] is None:
				max_values_dict["xTranslation"] = copy.deepcopy(platformOrientation)
				max_values_dict["xTranslation_height"] = assemblyGeometry.platform_center_z
			elif abs(platformOrientation.xTranslation) > abs(max_values_dict["xTranslation"].xTranslation):
				max_values_dict["xTranslation"] = copy.deepcopy(platformOrientation)
				max_values_dict["xTranslation_height"] = assemblyGeometry.platform_center_z
			if max_values_dict["yTranslation"] is None:
				max_values_dict["yTranslation"] = copy.deepcopy(platformOrientation)
				max_values_dict["yTranslation_height"] = assemblyGeometry.platform_center_z
			elif abs(platformOrientation.yTranslation) > abs(max_values_dict["yTranslation"].yTranslation):
				max_values_dict["yTranslation"] = copy.deepcopy(platformOrientation)
				max_values_dict["yTranslation_height"] = assemblyGeometry.platform_center_z
			if max_values_dict["zTranslation"] is None:
				max_values_dict["zTranslation"] = copy.deepcopy(platformOrientation)
				max_values_dict["zTranslation_height"] = assemblyGeometry.platform_center_z
			elif abs(platformOrientation.zTranslation) > abs(max_values_dict["zTranslation"].zTranslation):
				max_values_dict["zTranslation"] = copy.deepcopy(platformOrientation)
				max_values_dict["zTranslation_height"] = assemblyGeometry.platform_center_z
			if max_values_dict["pitchDegrees"] is None:
				max_values_dict["pitchDegrees"] = copy.deepcopy(platformOrientation)
				max_values_dict["pitchDegrees_height"] = assemblyGeometry.platform_center_z
			elif abs(platformOrientation.pitchDegrees) > abs(max_values_dict["pitchDegrees"].pitchDegrees):
				max_values_dict["pitchDegrees"] = copy.deepcopy(platformOrientation)
				max_values_dict["pitchDegrees_height"] = assemblyGeometry.platform_center_z
			if max_values_dict["rollDegrees"] is None:
				max_values_dict["rollDegrees"] = copy.deepcopy(platformOrientation)
				max_values_dict["rollDegrees_height"] = assemblyGeometry.platform_center_z
			elif abs(platformOrientation.rollDegrees) > abs(max_values_dict["rollDegrees"].rollDegrees):
				max_values_dict["rollDegrees"] = copy.deepcopy(platformOrientation)
				max_values_dict["rollDegrees_height"] = assemblyGeometry.platform_center_z
			if max_values_dict["yawDegrees"] is None:
				max_values_dict["yawDegrees"] = copy.deepcopy(platformOrientation)
				max_values_dict["yawDegrees_height"] = assemblyGeometry.platform_center_z
			elif abs(platformOrientation.yawDegrees) > abs(max_values_dict["yawDegrees"].yawDegrees):
				max_values_dict["yawDegrees"] = copy.deepcopy(platformOrientation)
				max_values_dict["yawDegrees_height"] = assemblyGeometry.platform_center_z


	results_json = generate_results_json(max_values_dict, xTranslation_values, yTranslation_values, zTranslation_values, pitch_values, roll_values, yaw_values, combinations)
	# json.dump(result_json, open("range_of_motion_results.json", "w"), indent=4)
	print(json.dumps(results_json, indent=4))


range_of_motion()