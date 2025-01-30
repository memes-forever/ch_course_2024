import codecs
from typing import Any

import yaml
from airflow_ext.utils.yaml_extensions import register_yaml_objects


class Yaml:
    """
    Yaml class
    """

    def __init__(self):
        register_yaml_objects()

    @staticmethod
    def read_file(file: str):
        with open(file, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def read_yaml_str(string: str, loader=yaml.SafeLoader) -> Any:
        return yaml.load(string, loader)

    @staticmethod
    def read_yaml(file: str, loader=yaml.SafeLoader) -> Any:
        """
        Method for read yml
        Args:
             file: file path
             loader: type of loader
        Returns:
            loaded yaml file
        """
        with open(file, 'r', encoding="utf-8") as yml:
            return yaml.load(yml, loader)

    @staticmethod
    def dump_yaml(obj: Any, dumper=yaml.Dumper, **kwargs):
        kwargs['allow_unicode'] = kwargs.get('allow_unicode', True)
        kwargs['sort_keys'] = kwargs.get('sort_keys', False)
        return yaml.dump(obj, Dumper=dumper, **kwargs).encode().decode('utf-8')

    def save_yaml(self, obj: Any, file: str, dumper=yaml.Dumper, **kwargs):
        """
        Method for save yml
        Args:
            obj: any object to save (dict, list, etc)
            file: file
            dumper: type of dumper
        """
        with codecs.open(file, "w", encoding="utf-8") as f:
            f.write(self.dump_yaml(obj, dumper, **kwargs))
