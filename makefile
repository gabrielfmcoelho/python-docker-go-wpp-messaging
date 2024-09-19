.PHONY: dependencies run

dependencies:
    python3 -m pip install -r requirements.txt
run: dependencies
    python3 -m uvicorn app.app:app --reload