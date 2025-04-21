import sys
import math
import socket


def sqroots(coeffs: str) -> str:
    try:
        a, b, c = list(map(int, coeffs.split()))
    except Exception:
        raise ValueError
    D = b * b - 4 * a * c
    if D < 0:
        return ""
    elif D == 0:
        if a == 0:
            raise ValueError
        else:
            x = -b / (2 * a)
            return str(x)
    else:
        if a == 0:
            raise ValueError
        else:
            x1 = (-b + D ** 0.5) / (2 * a)
            x2 = (-b - D ** 0.5) / (2 * a)
            return str(x1) + " " + str(x2)


def sqrootnet(line, sock):
    sock.sendall((line + "\n").encode())
    return sock.recv(128).decode().strip()


if __name__ == "__main__":
    match sys.argv:
        case [prog, args]:
            print(sqroots(sys.args))
        case [prog, args, host, port]:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, int(port)))
                print(sqrootnet(args, s))
