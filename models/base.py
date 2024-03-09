import json
from typing import List
from IPython.display import JSON

class PythonDictObject:
    def to_dict(self):
        def convert(obj):
            if hasattr(obj, "to_dict"):  # Check if the object has a to_dict method
                return obj.to_dict()  # Use it to convert the object to a dictionary
            elif isinstance(
                obj, dict
            ):  # For dictionaries, recursively convert their values
                return {k: convert(v) for k, v in obj.items()}
            elif isinstance(obj, list):  # For lists, recursively convert their items
                return [convert(v) for v in obj]
            else:
                return obj  # Return the object itself if it's neither

        return {k: convert(v) for k, v in self.__dict__.items()}

    def to_json_pretty(self) -> str:
        # Convert the Market object to a dictionary
        dict_representation = self.to_dict()
        # Return a pretty-printed JSON string
        return json.dumps(dict_representation, indent=4)

    def to_display_json(self):
        # Convert the Market object to a dictionary
        dict_representation = self.to_dict()
        # Use the display() function with a JSON object for pretty, interactive rendering
        return JSON(dict_representation)
