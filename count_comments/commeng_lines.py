import glob
import io
import tokenize
from typing import List, Tuple

from rich.console import Console
from rich.style import Style
from rich.table import Table


def find_standalone_string(source: str) -> List[str]:
    """寻找独立的字符串
    独立字符串指没有参与任何计算的字符串，不能赋值给某一个变量，也不能在括号当中
    结合Python的基本语法，总结出两个寻找独立字符串的最简规则：
    
    - 独立字符串左侧应该不存在任何非空字符，其前方必然是换行符+空格
    - 独立字符串一定不能在()[]{}之中

    > 因为只有使用()才有可能出现表达式换行，
    >>> a = (
    >>>      "str1",
    >>>      "str2",    
    >>>    )
      因此不在任意一个括号当中时，不会出现跨行参与表达式的情况

    根据这两个规则，使用tokenize方法，对代码进行过滤

    """
    tokens = tokenize.tokenize(io.BytesIO(source.encode()).readline)

    state = {
        "(": 0,
        "[": 0,
        "{": 0,
    }
    reverse = {
        "(": ")",
        "[": "]",
        "{": "}",
        "}": "{",
        "]": "[",
        ")": "(",
    }

    def inside():
        # 判断是否在某个括号中
        return sum(state.values()) > 0

    clean_line = True
    comments = []
    pending = None
    next(tokens)  # skip encoding
    for toknum, tokstr, *_ in tokens:
        # 处理Pending的情况，Pending的产生见后续逻辑
        if pending:
            if toknum in (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT,
                          tokenize.DEDENT, tokenize.COMMENT):
                comments.append(pending)
            pending = None

        # 进入了新的空行，处理仍有可能出现独立字符串的情况
        if toknum in (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT,
                      tokenize.DEDENT):
            clean_line = True
        # 是字符串，并且起始行至今没有任何INDENT之外的其他内容
        # 并且要求这个tok后边必须是换行符或注释，暂时将tokstr放入pending状态
        # 主要是回避以下这种情况
        # """str1""" > """str2"""

        elif toknum == tokenize.STRING and clean_line:
            if not inside():
                pending = tokstr
                continue
        else:
            # 本行已经不可能出现独立字符串
            # 维护好各种括号的状态
            clean_line = False
            if toknum == tokenize.OP:
                if tokstr in "([{":
                    state[tokstr] += 1
                if tokstr in ")]}":
                    state[reverse[tokstr]] -= 1

    if pending:
        comments.append(pending)
    pending = None
    return comments


def find_oneline_comments(source: str):
    tokens = tokenize.tokenize(io.BytesIO(source.encode()).readline)
    comments = []

    for toknum, tokstr, *_ in tokens:
        if toknum is tokenize.COMMENT:
            comments.append(tokstr)
    return comments


def count_number_oneline_comment(source: str):
    return len(find_oneline_comments(source))


def analyze_code(filename):
    '''
        打开一个py文件，统计其中的代码行数，包括空行和注释
        返回含该文件代码行数，注释行数，空行数的列表
    '''

    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.split("\n")
    total = len(lines)
    blank = sum(line.strip() == "" for line in lines)
    standalone_strings = find_standalone_string(content)
    standalone_strings_line_count = sum(
        len(comment.split("\n")) for comment in standalone_strings)
    comment_lines = count_number_oneline_comment(
        content) + standalone_strings_line_count

    return comment_lines, blank, total


def format_value(comment: int, blank: int, total: int, with_percent=False):
    comment_percent = None
    if total - blank > 0:
        comment_percent = comment / (total - blank) * 100
    return [
        f"{comment}",
        f"{total-blank}",
        f"{comment_percent:.2f}%" if comment_percent is not None else "-",
        f"{total}",
    ]


def postprocess(rows: List[Tuple[str]]):
    """对图表数据的处理,如排序等"""
    ...


def run(root_dir: str = "."):

    #   将项目下所有的.py文件目录输出
    file_list = glob.glob(f"{root_dir}/**/**.py", recursive=True)
    comment = blank = total = 0
    table = Table("文件名", "(含)注释行数", "非空行数", "注释占比", "总行数(不含空行)")
    rows = []
    for filename in file_list:
        line = analyze_code(filename)
        rows.append((filename, *format_value(*line)))
        comment += line[0]
        blank += line[1]
        total += line[2]
    postprocess(rows)
    for row in rows:
        table.add_row(*row)

    table.add_row("合计", *format_value(comment, blank, total,
                                      with_percent=True))
    c = Console(style=Style(bgcolor="black"))
    c.print(table)
    c.print("*一行中可能同时包含注释和代码, 注释覆盖率指所有非空行数中，包含注释的行所占比例",
            style=Style(color="yellow", italic=True))


if __name__ == '__main__':
    run()
