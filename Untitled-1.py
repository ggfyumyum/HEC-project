class Counter:
    count = 0

    def __init__(self):
        Counter.count +=1



one = Counter()
two = Counter()
three = Counter()

print(Counter.count)

