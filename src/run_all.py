from core.dataset_loader.loader import get_datasets
from core.module_loader import import_func_from_pyfile
from core.paths import BASE_DIR
import inspect
import asyncio

datasets = get_datasets(debug=True)

for dataset in datasets:
    script_path = BASE_DIR / dataset.script

    fn = import_func_from_pyfile(script_path, "Callback")

    if fn is None:
        raise FileNotFoundError(f"Cant find fn for script {str(script_path)}")

    fn(dataset)

    if inspect.iscoroutinefunction(fn):
        asyncio.run(fn(dataset))
    else:
        fn(dataset)

print("done")
exit()