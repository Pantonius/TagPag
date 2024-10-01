# Configuration
The configuration of the annotation interface is done via a `.env` file in the root directory of the project. See the [.env-example](../.env-example) for an example configuration.

You may skip this section if you only want to play around with the interface. **If no `.env` file is specified, the [.env-example](../.env-example) is copied into a new `.env` file such that the [example data](../example_workdir) is used.**

Notice that you will have to restart the application if you make any changes to the configuration.

## Environment Variables
When you take a look into the [.env-example](../.env-example), you will find the following environment variables. Most environment variables have a default value within the [config.py](../src/utils/config.py).


| Variable              | Description                                                                                                                                                                         | .env-example               |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------|
| `ANNOTATOR`        | Some ID for the annotator of the dataset. This ID will be used as a prefix for the `comment` and `labels` fields of the [output.csv](03-USAGE.md).                                    | `annotator_name`         |
| `RANDOM_SEED`      | The random seed for the application. This is used to shuffle the tasks before they are presented to the annotator. `None` means no randomization.                                                                    | `None`                       |
| `LABELS`              | A comma-separated list of labels that the `ANNOTATOR` may use for the tasks of the `TASKS_FILE`.                                                                                     | `Children,Energy,Cannabis` |
| `TASKS_ID_COLUMN`     | The column of the `TASKS_FILE` that uniquely identifies each annotation task.                                                                                                        | `_id`                      |
| `TASKS_URL_COLUMN`    | The column of the `TASKS_FILE` that holds the URL to be annotated.                                                                                                                   | `url`                      |
| `WORKING_DIR`         | The directory that will hold the `TASKS_FILE`, the annotations directory, the raw text directory, the cleaned text directory, and the html directory (see below).                                 | `example_workdir`          |
| `TASKS_FILE`          | The CSV file that holds the annotation tasks (including the `TASKS_ID_COLUMN` and `TASKS_URL_COLUMN`).                                                                                | `tasks.csv`                |
| `ANNOTATIONS_DB`      | The sqlite file in the `WORKING_DIR` that will hold all annotations.                                                                                                                 | `annotations.sqlite`       |
| `RAW_TEXT_DIR`        | The directory in the `WORKING_DIR` that will hold the extracted (raw) text of the html content of each task. Each text file will follow the naming scheme: `.txt`.                    | `raw_text`                 |
| `CLEANED_TEXT_DIR`    | The directory in the `WORKING_DIR` that will hold the extracted and cleaned text of the html content of each task. Each cleaned text file will follow the naming scheme: `.txt`.      | `cleaned_text`             |
| `HTML_DIR`            | The directory in the `WORKING_DIR` that holds the HTML content of each task as a result of scraping done beforehand. Each HTML file is expected to follow the naming scheme: `TASK_ID.html`, where `TASK_ID` is the value in the `TASKS_ID_COLUMN` of the corresponding row in the `TASKS_FILE`. | `html`                     |
| `URL_QUERY_PARAMS`    | Parameters used to find search terms in URLs.                                                                                                                                       | `q,p,query,text,search_query,search,psg` |
| `NOT_SEO_TITLES`      | A list of common URL path segments to exclude when identifying SEO titles (e.g., slugs) from URLs.                                                                                   | `cgi-bin,fast-cgi,...,login,tv-sender`   |
| `SPECIAL_CHARACTER_MAP` | A mapping dictionary for converting non-special characters (e.g., German umlauts) to their plain equivalents.                                                                     | `{"ß": "ss", "ä": "ae", "ö": "oe", "ü": "ue"}` |
| `COMMON_EXTENSIONS`   | A list of common file extensions found in slugs (URL segments) that should be recognized and handled.                                                                                | `html,htm,pdf,php,aspx,asp,php` |

## File Structure
As you can see from the [environment variables](02-CONFIGURATION#environment-variables), the file structure corresponds to:

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

2. You will notice that the `.env-example` already includes all [environment variables](02-CONFIGURATION#environment-variables) that we have described previously.

3. You will notice that the `example_workdir` already includes a file called `tasks.csv` and an accompanying directory called `html` -- these correspond to the `TASKS_FILE` and `HTML_DIR` [environment variables](02-CONFIGURATION#environment-variables) respectively. `example_workdir` corresponds to `WORKING_DIR`.

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

4. Feel free to adapt any of the preset [environment variables](02-CONFIGURATION#environment-variables) to your liking. Keep in mind: `TASKS_FILE` and `HTML_DIR` have to be in the `WORKING_DIR`.

5. Move on to [03-USAGE.md](03-USAGE.md) to start the application and play around with the example data.
