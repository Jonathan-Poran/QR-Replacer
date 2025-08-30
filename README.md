# QR-Replacer

A FastAPI-based server for handel replacement qr in event ticket imege in supabase , a data base of swapit project

## Installation

1. Clone the repo:

```bash
git clone <repo-url>
cd <repo-folder>
```

2. Create and activate virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/Mac
.\.venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. (Optional) Deactivate virtual environment when done:

```bash
deactivate
```

## Configuration

1. Copy `.env.example` to create your development and production environment files:
   `.env`
2. Set server host and port:
   Edit `.env` to configure the server host and port according to your environment.

## Running the Server

Start the server:

```bash
python -m src.server
```

## Tests:

### Run replacement test:

```bash
python -m src.tests.test_qr_replacement
```

## API Endpoints

| Endpoint | Method | Description |
| -------- | ------ | ----------- |
