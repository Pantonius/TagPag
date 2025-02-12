#### Installation

## Clone the Repository
Start by cloning the repository to your desired location and navigating into the local repository:
```bash
git clone https://gitlab.inf.uni-konstanz.de/anton.pogrebnjak/tagpag.git
cd tagpag
```

## Virtual Environment

It is best practice to run python applications in their own environments such that dependencies of different projects don't interfere with each other. Below are instructions on how to set up a virtual environment for this project using `pyenv` or `conda`.

### Using `pyenv`

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

4. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```


### Using `conda` (for Windows)

1. Install `conda` by following the instructions in the [official documentation](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).

2. Create a virtual environment for this application using `conda`. Open your terminal and execute the following commands:

   ```bash
   conda create --name tagpag-env python=3.12.7
   ```

3. Activate the virtual environment:

   ```bash
   conda activate tagpag-env
   ```

4. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```


## Start the Project

1. Activate the environment depending on your setup:

   - If you are using `pyenv`, activate the virtual environment by running:
     ```bash
     pyenv activate tagpag-env
     ```

   - If you are using `conda`, activate the environment by running:
     ```bash
     conda activate tagpag-env
     ```


2. Run the streamlit app:
   ```bash
   streamlit run src/app.py
   ```

An example configuration (see [.env-example](.env-example)) should be loaded with some example data (see [example_workdir](example_workdir)).