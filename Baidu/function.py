import time

def fun_o(e):
    t = []
    for n in range(len(e)):
        r = e[n][0]
        while r <= e[n][1]:
            t.append(chr(r))
            r += 1
    return t


def fun_r(e, t):
    n = list(t)
    for r in range(len(e)):
        o = r % len(n)
        o = ord(n[o][0])
        o %= len(e)
        a = e[r]
        e[r] = e[o]
        e[o] = a
    return e


def fun_a(e, t):
    n = ''
    r = abs(int(e))
    if r:
        while r:
            n += t[r % len(t)]
            r = int(r / len(t))
    else:
        n = t[0]
    return n


def fun_bary(e, r):
    t = 0
    n = {}
    for r in range(len(e)):
        if e[r] > t:
            t = e[r]
            n[e[r]] = True
    o = int(t / 6)
    o += 1 if t % 6 else 0
    a = ''
    for r in range(o):
        d = 0
        i = 6 * r
        for c in range(6):
            if n[i]:
                d += pow(2, c)
                i += 1
        a += r[0][d]
    return a


def fun_str(e, r):
    t = []
    for n in range(len(e)):
        r_ = ord(e[n])
        if 1 <= r_ <= 127:
            t.append(r_)
        elif r_ > 2047:
            t.append(224 | r_ >> 12 & 15)
            t.append(128 | r_ >> 6 & 63)
            t.append(128 | r_ >> 0 & 63)
        else:
            t.append(192 | r_ >> 6 & 31)
            t.append(128 | r_ >> 6 & 63)
    o = ''
    n = 0
    a = len(t)
    while n < a:
        i = t[n]
        n += 1
        if n >= a:
            o += r[0][i >> 2]
            o += r[0][(3 & i) << 4]
            o += "__"
            break
        d = t[n]
        n += 1
        if n >= a:
            o += r[0][i >> 2]
            o += r[0][(3 & i) << 4 | (240 & d) >> 4]
            o += r[0][(15 & d) << 2]
            o += "_"
            break
        c = t[n]
        n += 1
        o += r[0][i >> 2]
        o += r[0][(3 & i) << 4 | (240 & d) >> 4]
        o += r[0][(15 & d) << 2 | (192 & c) >> 6]
        o += r[0][63 & c]
    return o


def cal_dv(tk):
    params = {
        'browserInfo': "2,2,75",
        'flashInfo': None,
        'keyDown': "",
        'loadTime': round(time.time(), 3),
        'location': "https://pan.baidu.com/,undefined",
        'mouseDown': "",
        'mouseMove': "",
        'screenInfo': "44,10,390,735,1706,960,1707,1687,888",
        'token': tk,
        'version': 26
    }
    t = [[48, 57], [65, 90], [97, 122], [45, 45], [126, 126]]
    n = fun_o(t)
    a = fun_o(t[1:])
    n = fun_r(n, tk)
    a = fun_r(a, tk)
    r = [n, a]
    o = {
        'flashInfo': 0,
        'mouseDown': 1,
        'keyDown': 2,
        'mouseMove': 3,
        'version': 4,
        'loadTime': 5,
        'browserInfo': 6,
        'token': 7,
        'location': 8,
        'screenInfo': 9
    }
    t = ''
    e = [2]
    for n in range(len(e)):
        r_ = fun_a(e[n], r[1])
        t += str(len(r_) - 2) + r_ if len(r_) > 1 else r_
    a = [t]
    for i in params:
        d = params[i]
        if d != 0 and o[i] != 0:
            if isinstance(d, int) or isinstance(d, float):
                c = 1 if d >= 0 else 2
                d = fun_a(d, r[0])
            elif isinstance(d, bool):
                c = 3
                d = fun_a(1 if d else 0)
            elif isinstance(d, list):
                c = 4
                d = fun_bary(d, r)
            else:
                c = 0
                d = fun_str(d, r)
            if d:
                t = ''
                e = [o[i], c, len(d)]
                for n in range(len(e)):
                    r_ = fun_a(e[n], r[1])
                    t += str(len(r) - 2) + r_ if len(r_) > 1 else r_
                a.append(t + d)
    return ''.join(a)