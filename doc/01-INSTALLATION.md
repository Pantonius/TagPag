# Installation

## Clone the Repository
Start by cloning the repository to your desired location and navigating into the local repository:
```bash
git clone https://gitlab.inf.uni-konstanz.de/anton.pogrebnjak/tagpag.git
cd tagpag
```

## Virtual Environment

It is best practice to run python applications in their own environments such that dependencies of different projects don't interfere with each other. An easy way to create such python environments is `pyenv`:

1. Install `pyenv` by following the instructions in the [official documentation](https://github.com/pyenv/pyenv#installation).

2. Create a virtual environment for this application using `pyenv`. Open your terminal and execute the following commands:

   ```bash
   pyenv install 3.12.7
   pyenv virtualenv 3.12.7 tagpag-env
   ```

3. Activate the virtual environment:

   ```bash
   pyenv activate tagpag-env
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the Project
   ```bash
   streamlit run src/app.py
   ```

An example configuration (see [.env-example](.env-example)) should be loaded with some example data (see [example_workdir](example_workdir)).