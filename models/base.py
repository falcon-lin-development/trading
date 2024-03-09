import json
from typing import List
from IPython.display import JSON

class PythonDictObject:
    def to_dict(self, flatten=False):
        # Simple conversion using a comprehension, directly utilizing self.__dict__
        result = {k: self._value_to_dict(v, flatten) for k, v in self.__dict__.items()}
        return self._flatten_dict(result) if flatten else result

    def _value_to_dict(self, value, flatten):
        # Convert values based on their type
        if hasattr(value, 'to_dict'):  # Custom objects
            return value.to_dict(flatten)
        elif isinstance(value, dict):
            return {k: self._value_to_dict(v, flatten) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._value_to_dict(v, flatten) for v in value]
        else:
            return value

    def _flatten_dict(self, d, parent_key='', sep='_'):
        # Flatten nested dictionaries
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

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
