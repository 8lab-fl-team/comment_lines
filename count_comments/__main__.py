from pathlib import Path
from sys import path

path.append(Path(__file__).absolute().parent.parent.as_posix())
from typer import Argument, Typer

from count_comments.commeng_lines import run

app = Typer(name="count_comments")


@app.command()
def count(root_dir: Path = Argument(".", help="需要统计的目录")):
    run(root_dir)


if __name__ == "__main__":
    app()
