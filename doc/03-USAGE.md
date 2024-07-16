# Usage
Once everything is installed as described in [01-INSTALLATION.md](01-INSTALLATION.md) and the project is configured as described in [02-CONFIGURATION.md](02-CONFIGURATION.md), you can move on to starting the application.

First, ensure that you have activated your python environment:

```bash
pyenv activate seek2judge-env
```

Then you may proceed in starting the application with the following command:

```bash
streamlit run src/app.py
```

You should see something resembling the following output:
```bash
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.178.168.11:8501
  External URL: http://192.178.168.11:8501
```

When running on your local system the *Local URL* (`http://localhost:8501`) will suffice to access the application. Once you have opened that link in your browser, the application should look something like this:

![Webpage Annotation Interface](../screenshot.png)

## Exploration
Let's explore the interface a little.

As you can see, the interface consists of a little sidebar on the left and a more substantial main panel to the right.

### Sidebar
The **sidebar** consists of
1. the **task navigator**
2. the **annotation section**
3. the **shortcode overview**
4. the **download annotations button**

The **task navigator** indicates the current position within the tasks to the `ANNOTATOR`. They may navigate through the tasks by clicking the plus and minus buttons on the right of the input field or by typing a task number directly into the input field and pressing enter.

If the current task is already annotated the `ANNOTATOR` may press the *"Find next incomplete task"* button to jump to the next unannotated task.

Additionally, the `ANNOTATOR` may use the *auto-advance* option to automatically jump to the next task, once the task has been labeled.

The **annotation section** includes up to ten toggles for the first ten `LABELS` such that a quick annotation can be achieved. Alternatively all `LABELS` can be found in the dropdown menu below the toggles labeled *"Selected Tags"*.
Moreover, it contains a text area for additional comments.

The **shortcut overview** reveals several keyboard shortcuts for task navigation as well as label selection:

| Keyboard Shortcut | Description |
| :-: | :- |
| w \| . \| + \| ] \| Enter | next task |
| q \| , \| - \| [ \| Backspace | previous task |
| F \| f \| = | find next incomplete task |
| 1 \| 2 \| ... \| 9 \| 0 | toggle respective label |

Pressing the **download annotations button** will start a download of the `annotations.csv` file, which includes the `task_id`, `ANNOTATOR01_labels`, `ANNOTATOR01_comment`, ..., `ANNOTATORXY_labels`, `ANNOTATORXY_comment`, `url`.

### Main Panel
The **main panel** consists of several tabs:
1. Text
2. Webpage Snapshot
3. URL Anatomy
4. Task

<!-- TODO: continue work on documentation>