print("Wing Design Tool")
print("\tB05")

while True:
    command = input("> ").lower().split()

    if command[0] == "graph":
        print("graph")

    elif command[0] == "exit":
        raise SystemExit
    else:
        print("Unrecognized command")
