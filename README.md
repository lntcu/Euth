Note that this project is not to be taken seriously, just like DOOM Captcha. It provides no security and should never be used as actual authentication. Please do not use this for anything other than for fun.

# Euth Authentication

Euth is a Python authentication library that uses blinks to authenticate a user instead of typing out their passwords. The facial authentication method provides several advantages, such as preventing shoulder surfing, whereby passersby look while you are typing your password, and figuring out your password by looking at stains on the keyboard. Blinking is a natural and unsuspecting gesture, preventing others from knowing that one is typing in their password.

## How it Works

Euth uses the webcam to track and detect blinks. Every blink appends a "B" to the password, while every non-blink appends an "N" to the password. The password is then hashed using SHA256 and compared with the actual hash. Shaking your head clears the password.

## Example Usage

```py
from euth import Euth

if __name__ == "__main__":
    system = Euth()
    # Password is "NNBBNNBNBBNNNBNNBNBNNNBBNNNBNBBBNNBBNNNBBNBNBNNNNNNBNBBNNBBBNNBBNBB"
    if system.auth(password="f16408113e6036d1dd65bd9042e7f6d8f1c7a789ed7ab514c0a103d44b0825cd", verbose=1):
        print("\nAccess granted")
    else:
        print("\nAccess denied")
```

The code initialises an Euth Authenticator with default parameters. If the user is authenticated, the system prints "Access granted".

For more information about the functions, the file `euth.py` has documentation for each function and their parameters. The library itself is really short and not meant for actual use.
