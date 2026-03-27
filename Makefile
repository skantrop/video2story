.PHONY: backend frontend dev install-backend install-frontend

BACKEND_VENV = backend/.venv
BACKEND_UVICORN = $(BACKEND_VENV)/bin/uvicorn

backend:
	cd backend && ../$(BACKEND_UVICORN) app.main:app --reload

frontend:
	cd frontend && npm run dev

dev:
	@echo "Starting backend and frontend..."
	make -j2 backend frontend

install-backend:
	cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

test:
	cd backend && PYTHONPATH=. pytest tests -v