import sys




path = sys.argv[1]


text: str
with open(path, "r") as fp:
    text = fp.read()


counter = 0
while "primitive seq3 (" in text:
    text = text.replace("seq3 ", f"seq3_{counter} ", 1)
    text = text.replace("seq3(", f"seq3_{counter}(", 1)
    counter += 1

with open(path, "w") as fp:
    fp.write(text)