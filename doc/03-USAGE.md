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

**Notice that you will have to restart the application if you [change the configuration file](doc/02-CONFIGURATION).**

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

The **annotation section** includes up to ten toggles for the first ten `LABELS` such that a quick annotation can be achieved. Alternatively all `LABELS` can be found in the dropdown menu below the toggles labeled *"Selected Labels"*.
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
The **main panel** consists of **several tabs** that make up most of the viewport. Those are described below.

Above those tabs there is a brief information about the **full url** of the current task as well as a **brief url decomposition** with **three links**: The first link opens the url, the second opens the corresponding page in the web archive (there may not exist an archived version of the current webpage) and thre third link open the save version in the `HTML_DIR`.

In the main part of the interface, there are three tabs:

1. **Text**
2. **URL Anatomy**
3. **Task**

The **Text tab** offers a cleaned and raw text version of the current website content. One may edit the cleaned version directly in the text area as well as reset said text area to its original form via the **"Reset Clean Text"** button below.

Another button called **"Copy Raw Text"** directly copies the *raw text* content into the *cleaned text* text area.

To get a better grasp of the conjugate parts of the url, there is the option of visiting the **URL Anatomy tab** to take a quick look at a technical decomposition.

The **Task tab** holds a JSON representation of the task at hand, as given in the underlying `TASKS_FILE`, with an added `annotations` field, containing  a JSON representation of the corresponding annotation by the current `ANNOTATOR` as given in the corresponding annotation file within the `ANNOTATIONS_DIR`.