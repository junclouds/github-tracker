# GitHub Trending Tracker

A Python tool that tracks trending repositories on GitHub for Python and Java projects.

## Features

- Tracks top 5 trending repositories for Python and Java
- Updates data twice daily (8 AM and 8 PM)
- Saves data in JSON format
- Displays results grouped by programming language

## Requirements

- Python 3.7+
- GitHub Personal Access Token

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/github-tracker.git
cd github-tracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root directory and add your GitHub token:
```
GITHUB_TOKEN=your_github_token_here
```

## Usage

### Running the tracker directly:
```bash
python src/github_tracker.py
```

### Running with scheduler:
```bash
python main.py
```

## Data Format

The data is saved in JSON format:
```json
{
  "timestamp": "2024-03-21T12:34:56",
  "trending_repositories": {
    "description": "Top 5 trending Python and Java projects created in the last week",
    "data": [
      {
        "name": "username/repo",
        "description": "Project description",
        "stars": 1234,
        "url": "https://github.com/username/repo",
        "language": "Python"
      }
    ]
  }
}
```

## Project Structure

```
github_tracker/
├── src/
│   ├── __init__.py
│   ├── github_tracker.py
│   └── scheduler.py
├── data/                  # Generated data files (gitignored)
├── main.py
├── requirements.txt
└── README.md
```

## Configuration

- Data is saved in the `data` directory
- Tracking interval can be modified in `src/scheduler.py`
- Target languages can be modified in `src/github_tracker.py`

## Note

Make sure to keep your GitHub token private and never commit it to the repository. 