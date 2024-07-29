# Installation

## Clone the Repository
Start by cloning the repository to your desired location and navigating into the local repository:
```bash
git clone https://gitlab.inf.uni-konstanz.de/julian.schelb/seek2judge-annotations.git
cd seek2judge-annotations
```

## Virtual Environment
As you may know: It is best practice to run python applications in their own environments such that dependencies of different projects don't interfere with each other.

An easy way to create such python environments is `pyenv`:

1. Install `pyenv` by following the instructions in the [official documentation](https://github.com/pyenv/pyenv#installation).

2. Create a virtual environment for this application using `pyenv`. Open your terminal and execute the following commands:

   ```bash
   pyenv install 3.10.12
   pyenv virtualenv 3.10.12 seek2judge-env
   ```

3. Activate the virtual environment:

   ```bash
   pyenv activate seek2judge-env
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. To get a basic configuration of the application, rename the `.env-example` file to `.env` and adapt it as you see fit. We discuss the details of the configuration in [02-CONFIGURATION.md](doc/02-CONFIGURATION.md).