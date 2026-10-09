a = int(input("Введите число >> "))
pl = input("Введите +/-/* >> ")
b = int(input("Введите число >> "))
if pl == "+":
    sm = a + b
    print(sm)
elif pl == "-":
    df = a - b
    print(df)
else:
    mlt = a * b
    print(mlt)
