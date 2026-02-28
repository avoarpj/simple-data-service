from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from core.dataset_loader.loader import get_datasets
from core.module_loader import import_func_from_pyfile
from core.paths import BASE_DIR
import inspect
import asyncio

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}

scheduler = BlockingScheduler(jobstores=jobstores)

datasets = get_datasets()

for dataset in datasets:
    script_path = BASE_DIR / dataset.script

    fn = import_func_from_pyfile(script_path, "Callback")

    if fn is None:
        raise FileNotFoundError(f"Cant find fn for script {str(script_path)}")

    trigger = CronTrigger.from_crontab(expr=dataset.updates.cron_expr) # type: ignore
    
    def cb():
        if inspect.iscoroutinefunction(fn):
            asyncio.run(fn(dataset))
        else:
            fn(dataset)

    scheduler.add_job( # type: ignore
        func=cb,
        trigger=trigger,
        id=dataset.id,
        replace_existing=True,
        coalesce=True,
        misfire_grace_time=2629800 # 1 month
    )

print("started scheduler")
scheduler.start() # type: ignore
