from datetime import timedelta
import pendulum
import yaml


class YamlDateTimeObject(yaml.YAMLObject):
    yaml_tag = '!date'

    def __init__(self, exec_date):
        self.exec_date = exec_date

    def __repr__(self):
        return self.exec_date.__repr__()

    @classmethod
    def from_yaml(cls, loader, node):
        node_d = {key_node.value: value_node.value for key_node, value_node in node.value}
        exec_date = node_d['datetime']
        if exec_date == 'now':
            now = pendulum.now()
            start_of = {}
            if 'start_of' in node_d:
                start_of = {
                    key_node.value: int(getattr(now, key_node.value)) // int(value_node.value) * int(value_node.value)
                    for key_node, value_node in node_d['start_of']
                }
                interval_names = iter(('microsecond', 'second', 'minute', 'hour', 'day', 'month', 'year'))
                while (interval_name := next(interval_names)) not in start_of:
                    start_of[interval_name] = 0
            interval = {key_node.value: int(value_node.value) for key_node, value_node in node_d.get('interval', [])}
            exec_date = now.replace(**start_of) - timedelta(**interval)
        else:
            exec_date = pendulum.parse(exec_date).replace()

        return exec_date

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_scalar(cls.yaml_tag, data.callable.__name__)


class YamlTimedeltaObject(yaml.YAMLObject):
    yaml_tag = '!timedelta'

    def __init__(self, timedelta_params: dict):
        self.timedelta = timedelta(**timedelta_params)
        self.timedelta_params = timedelta_params

    def __repr__(self):
        return self.timedelta.__repr__()

    @classmethod
    def from_yaml(cls, loader, node):
        timedelta_params = {key_node.value: int(value_node.value) for key_node, value_node in node.value}
        return YamlTimedeltaObject(timedelta_params).timedelta

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_mapping(cls.yaml_tag, data.timedelta_params)


def register_yaml_objects():
    yaml_objs = [
        YamlDateTimeObject,
        YamlTimedeltaObject,
    ]

    for obj in yaml_objs:
        yaml.SafeLoader.add_constructor(obj.yaml_tag, obj.from_yaml)
        yaml.SafeDumper.add_representer(obj, obj.to_yaml)
