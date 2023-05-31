# Seek2Judge: Webpage Annotations

## Description

This web application is designed to label scraped webpages. It allows users to annotate and tag web content for further analysis. With this application, you can easily label and categorize webpages based on your specific requirements.

![Application Screenshot](screenshot.png)

## Installation

To set up this application and create a virtual environment, follow these steps:

1. Install `pyenv` by following the instructions in the [official documentation](https://github.com/pyenv/pyenv#installation).

2. Create a virtual environment for this application using `pyenv`. Open your terminal and execute the following commands:

   ```bash
   pyenv install 3.9.6
   pyenv virtualenv 3.9.6 seek2judge-env
   pyenv activate seek2judge-env
   ```

3. Install the required dependencies by running the following command:

   ```bash
   pip install -r requirements.txt
   ```

4. To configure the MongoDB database connection, rename the .env-example file to .env and add your MongoDB connection key. For example:
   ```text
   CONNECTION_STRING="mongodb://localhost:27017/"
   DATABASE_NAME="webpagesDB"
   ```

## Usage

To run this application, execute the following command:

```bash
streamlit run src/app.py
```

The application will launch in your web browser, and you can start labeling webpages.

## Development

If you make any changes to the dependencies in your development environment, update the `requirements.txt` file using the following command:

```bash
pip freeze > requirements.txt
```

## Additional Resources

For more information on how to use Streamlit, refer to the [Streamlit Documentation](https://docs.streamlit.io/library/api-reference).
