1. Create a virtualenv: python3 -m virtualenv .venv
2. Activate it: . .venv/bin/activate
3. Install maturin & pyside6: pip install maturin pyside6
4. Build the rust module: maturin develop
5. Run the python main: python py/main.py
