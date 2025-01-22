# Testing
Testing is accomplished via [pytest](https://docs.pytest.org/en/stable/index.html). For more detailed information refer to the [pytest documentation](https://docs.pytest.org/en/stable/index.html).

To get started first install the latest version of pytest as per [their instructions](https://docs.pytest.org/en/stable/getting-started.html#get-started):
```sh
pip install -U pytest
```

## Test Location
Currently all tests are located in `src/tests`.

## Running Tests
To start a complete testing run, simply run `pytest` in the project directory:
```sh
pytest
```

If you only want to run **all tests for a file** that's:
```sh
pytest path/to/test_file.py
```

If you want to run a **certain test for a file** that's:
```sh
pytest path/to/test_file.py::test_function_name
```

Pytest will look for files that match `*_test.py` or `test_*.py` when searching for tests.

More detailed information about invoking pytest in the pytest docs: _["How to invoke pytest"](https://docs.pytest.org/en/stable/how-to/usage.html)_

## Writing Tests
When adding to this project you will want to ensure proper functionality by writing your own tests.