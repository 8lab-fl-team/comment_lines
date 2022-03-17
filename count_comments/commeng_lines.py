import glob
import io
import tokenize

from rich.console import Console
from rich.table import Table


def count_number_sing_comment(source: str):
    tokens = tokenize.tokenize(io.BytesIO(source.encode()).readline)
    comment_lines = 0
    for toknum, *_ in tokens:
        if toknum is tokenize.COMMENT:
            comment_lines += 1
    return comment_lines


def analyze_code(filename):
    '''
        打开一个py文件，统计其中的代码行数，包括空行和注释
        返回含该文件代码行数，注释行数，空行数的列表
    '''
    with open(filename, 'r', encoding='utf-8') as f:

        comment_lines = 0  #注释行数
        comment_lines += count_number_sing_comment(f.read())
        f.seek(0)
        # 代码行数 空白行数
        code_lines, blank_lines = 0, 0
        is_comment = False
        start_comment_index = 0  #记录以'''或"""开头的注释位置
        for index, raw_line in enumerate(f, start=1):
            line = raw_line.strip()  #去除开头和结尾的空白符
            #判断多行注释是否已经开始
            if not is_comment:
                if line.startswith("'''") or line.startswith('"""'):
                    if line.endswith(line[:3]) and len(line) >= 6:
                        comment_lines += 1
                    else:
                        is_comment = True
                        start_comment_index = index
                #空白行
                elif line == '':
                    blank_lines += 1
                #代码行
                else:
                    code_lines += 1

            #多行注释已经开始
            else:
                if line.endswith("'''") or line.endswith('"""'):
                    is_comment = False
                    comment_lines += index - start_comment_index + 1
                else:
                    pass

    return code_lines, comment_lines, blank_lines


def format_value(code: int, comment: int, blank: int, with_percent=False):
    total = code + comment
    code_percent = f"({(code / total * 100):.2f}%)" if total and with_percent else ""
    comment_percent = f"({(comment / total * 100):.2f}%)" if total and with_percent else ""
    return [
        f"{code}{code_percent}",
        f"{comment}{comment_percent}",
        f"{blank}",
        f"{total}",
        f"{total+blank}",
    ]


def run(root_dir: str = "."):

    #   将项目下所有的.py文件目录输出
    file_list = glob.glob(f"{root_dir}/**/**.py", recursive=True)

    total_code_lines, total_comment_lines, total_blank_lines = 0, 0, 0
    table = Table("文件名", "代码行数", "注释行数", "空白行数", "总行数(不含空行)", "总行数(包含空行)")
    for i in file_list:
        line = analyze_code(i)
        table.add_row(i, *format_value(*line))
        total_code_lines += line[0]
        total_comment_lines += line[1]
        total_blank_lines += line[2]
    table.add_row(
        "合计",
        *format_value(total_code_lines,
                      total_comment_lines,
                      total_blank_lines,
                      with_percent=True))
    c = Console()
    c.print(table)


if __name__ == '__main__':
    run()
