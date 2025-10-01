# Standard libraries
import json
import logging


def read_json_config(json_config_path: str) -> dict:
	"""_summary_

	Args:
		json_config_path (str): _description_

	Returns:
		dict: _description_
	"""

	try:
		with open(file=json_config_path, encoding='utf-8') as file:
			configuration = json.load(file)
	
		return configuration
	
	except FileNotFoundError:
		raise ValueError("Path not available")
	
def create_logger(logger_file_name: str) -> logging.Logger:
	"""_summary_

	Args:
		logger_file_name (str): _description_

	Returns:
		logging.Logger: _description_
	"""
	
	# Configure logging
	logging.basicConfig(
		filename=logger_file_name,
		level=logging.INFO,
		format='%(asctime)s - %(levelname)s - %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S'
	)

	return logging.getLogger(__name__)