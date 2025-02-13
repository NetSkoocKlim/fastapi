
try:
    raise IndentationError
except (IndexError, IndentationError):
    print('fzz')
    pass
