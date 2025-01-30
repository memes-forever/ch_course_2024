import os
from typing import Union

import jinja2


class Jinja2:
    def __init__(self, template_dir: Union[str, os.PathLike], add_jinja_filter=True, **kwargs):
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), **kwargs)
        if add_jinja_filter:
            self._add_jinja_filter()

    def _add_jinja_filter(self):
        self.env.filters['add_alias'] = lambda x, y: f'{y}.{x}'
        self.env.filters['strip'] = str.strip
