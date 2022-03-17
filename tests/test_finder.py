from count_comments.commeng_lines import find_standalone_string

code = '''"""top of the file"""
a = 1
b = 1
"""anywhere of top namespace"""

"""multi line
should be good


"""
def test():
    \'\'\'function's __doc__ should be good\'\'\'
    "event single quote should be ok"
    'str in expression' == 'not good'
if "str" == (
    "edge case" # very likely, but not
    ,"str wrapped should be exclude"
):
    ...

class HelloWorld:
    """Class Doc String"""

    def __init__(self) -> None:
        """method doc string
        """

"""of course the last line"""'''


def test_standalone_finder():
    result = find_standalone_string(code)
    assert len(result) == 8