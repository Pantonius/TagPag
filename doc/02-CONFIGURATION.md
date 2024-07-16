# Configuration
The entire configuration of the annotation interface is done via a `.env` file in the root directory of the project. See the [.env-example](../.env-example) for an example configuration.

## Environment Variables
When you take a look into the [.env-example](../.env-example), you will find the following environment variables. Most of them have a default value within the [config.py](../src/utils/config.py).

| Variable | Description | default |
| :- | :- | :- |
| `ANNOTATOR` | Some ID for the annotator of the dataset. This ID will be used as a prefix for the `comment` and `labels` fields of the [output.csv](03-USAGE.md). | - |
| `LABELS` | A comma-seperated list of labels that the `ANNOTATOR` may use for the tasks of the `TASKS_FILE`. | `""` (which results in an empty list) |
| `TASKS_ID_COLUMN` | The column of the `TASKS_FILE` that uniquely identifies each annotation task. | `_id` |
| `TASKS_URL_COLUMN` | The column of the `TASKS_FILE` that holds the url to be annotated. | `target_url` |
| `WORKING_DIR` | The directory that will hold the `TASKS_FILE`, the annotations directory, the raw text directory, the cleaned text directory and the html directory (more on those later). | `data` |
| `TASKS_FILE` | The CSV file that holds the annotation tasks (including the `TASKS_ID_COLUMN` and `TASKS_URL_COLUMN`) | `tasks.csv` |
| `ANNOTATIONS_DIR` | The directory in the `WORKING_DIR` that will hold all annotations as JSON files. Each annotation will follow the naming scheme: `<TASK_ID>.json` | `annotations` |
| `RAW_TEXT_DIR` | The directory in the `WORKING_DIR` that will hold the extracted (raw) text of the html content of each task. Each text file will follow the naming scheme: `<TASK_ID>.txt`. | `raw_text` |
| `CLEANED_TEXT_DIR` | The directory in the `WORKING_DIR` that will hold the extracted and cleaned text of the html content of each task. Each cleaned text file will follow the naming scheme: `<TASK_ID>.txt`. | `cleaned_text` |
| `HTML_DIR` | The directory in the `WORKING_DIR` that holds the html content of each task as a result of scraping done before-hand. Each html file is expected to follow the naming scheme: `<TASK_ID>.html` | `html` |

## File Structure
As you can see from the [environment variables](02-CONFIGURATION#L4), the file structure corresponds to:

```
WORKING_DIR
├── TASKS_FILE
├── ANNOTATIONS_DIR
├── RAW_TEXT_DIR
├── CLEANED_TEXT_DIR
└── HTML_DIR
```

`TASKS_FILE` and `HTML_DIR` need to be in the specified `WORKING_DIR`, for the application interface to function properly. Mind the naming scheme of the html files: `<TASK_ID>.html`.

Every other directory (`ANNOTATIONS_DIR`, `RAW_TEXT_DIR` and `CLEANED_TEXT_DIR`) will be created automatically if they don't already exist. You can interpret those as *internal data dumps*.

## Example Configuration
Let's make a configuration for the example data in the [example_workdir](../example_workdir/). Here's a step-by-step description:

1. Copy the `.env-example` into the same directory that it currently resides in and rename it to `.env`

2. You will notice that the `.env-example` already includes all [environment variables](02-CONFIGURATION#L4) that we have described previously.

3. You will notice that the `example_workdir` already includes a file called `tasks.csv` and an accompanying directory called `html` -- these correspond to the `TASKS_FILE` and `HTML_DIR` [environment variables](02-CONFIGURATION#L4) respectively. `example_workdir` corresponds to `WORKING_DIR`.

    ```
    WORKING_DIR/
    ├── TASKS_FILE
    └── HTML_DIR
    ```

    ```
    example_workdir
    ├── tasks.csv
    └── html
    ```

4. Feel free to adapt any of the preset [environment variables](02-CONFIGURATION#L4) to your liking. Keep in mind: `TASKS_FILE` and `HTML_DIR` have to be in the `WORKING_DIR`.

5. Move on to [03-USAGE.md](03-USAGE.md) to start the application and play around with the example data.