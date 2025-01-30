from pathlib import Path
from pendulum import timezone
from pendulum.tz.timezone import Timezone

HOME_DIR = Path(__file__).parent.parent.parent
LOCAL_TZ: Timezone = timezone('Europe/Moscow')
