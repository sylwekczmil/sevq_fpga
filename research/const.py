from pathlib import Path

THIS_PATH = Path(__file__).parent
RESULT_DIR = THIS_PATH / "combined"
RESULT_DIR.mkdir(exist_ok=True, parents=True)

RESULT_CSV = RESULT_DIR / "comparison.csv"

ARTICLE_DIR = THIS_PATH / "article"
ARTICLE_DIR.mkdir(exist_ok=True, parents=True)
