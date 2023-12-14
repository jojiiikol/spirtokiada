list1 = []
list2 = []
list3 = []

def add_el(list1, list2, list3, el):
    min_len = min(len(list1), len(list2), len(list3))

    if len(list1) == min_len:
        list1.append(el)
    else:
        if len(list2) == min_len:
            list2.append(el)
        else:
            list3.append(el)

elements = range(2, 12)
for i in elements:
    add_el(list1, list2, list3, i)

print(list1)
print(list2)
print(list3)