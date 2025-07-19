from euth import Euth

if __name__ == "__main__":
    system = Euth()
    # Password is "NNBBNNBNBBNNNBNNBNBNNNBBNNNBNBBBNNBBNNNBBNBNBNNNNNNBNBBNNBBBNNBBNBB"
    if system.auth(password="f16408113e6036d1dd65bd9042e7f6d8f1c7a789ed7ab514c0a103d44b0825cd", verbose=1):
        print("\nAccess granted")
    else:
        print("\nAccess denied")
