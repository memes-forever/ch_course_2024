from datetime import datetime

from airflow.models import Pool
from airflow_ext.constant import LOCAL_TZ

all_pools: dict = {}


def get_or_create_pool(name: str, **kwargs) -> Pool:
    """
    Get or create pool slot
    :param name: pool name
    :param slots: slots count
    :param pools: pools, if exist
    :return: Pool class
    """
    global all_pools

    # name = f"source_{src_name}"
    if 'slots' not in kwargs:
        kwargs['slots'] = 16

    if 'description' not in kwargs:
        kwargs['description'] = f'upd: {datetime.now(tz=LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S")}'

    if 'include_deferred' not in kwargs:
        kwargs['include_deferred'] = False

    if not all_pools:
        all_pools = {pool.pool: pool for pool in Pool.get_pools()}

    if name not in all_pools:
        all_pools[name] = Pool.create_or_update_pool(name=name, **kwargs)

    return all_pools[name]
