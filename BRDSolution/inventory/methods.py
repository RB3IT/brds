## Builtin
import pathlib

def testfileintegrity(file):
    if not file: return
    file = pathlib.Path(file).resolve()
    if not file.exists(): return
    return file