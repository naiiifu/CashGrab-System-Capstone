import math


# https://www.grad.hr/nastava/gs/prg/NumericalRecipesinC.pdf

def gammln(xx):
    cof =[76.18009172947146,-86.50532032941677,
    24.01409824083091,-1.231739572450155,
    0.1208650973866179e-2,-0.5395239384953e-5]

    y=x=xx
    tmp=x+5.5
    tmp -= (x+0.5)*math.log(tmp)
    ser=1.000000000190015
    
    for j in range (0, 6):
        y = y + 1
        ser += cof[j]/y

    return -tmp+math.log(2.5066282746310005*ser/x)

def betacf(a, b, x):
    MAXIT = 100
    EPS = 3.0e-7
    FPMIN = 1.0e-30

    qab = a + b
    qap = a + 1
    qam = a - 1
    c = 1
    d = 1 - qab * x / qap

    if( math.fabs(d) < FPMIN):
        d = FPMIN
    
    d = 1 / d
    h = d

    for m in range(1, MAXIT):
        m2 = 2 * m
        aa = m * (b-m) * x / ( (qam+m2) * (a+m2) )
        d=1.0+aa*d

        if math.fabs(d) < FPMIN:
            d = FPMIN
        
        c=1.0+aa/c

        if math.fabs(c) < FPMIN:
            c=FPMIN
        
        d=1.0/d
        h *= d*c
        aa = -(a+m)*(qab+m)*x/((a+m2)*(qap+m2))
        d=1.0+aa*d

        if (math.fabs(d) < FPMIN):
            d=FPMIN

        c=1.0+aa/c

        if (math.fabs(c) < FPMIN):
            c=FPMIN

        d=1.0/d
        dl = d*c
        h *= dl

        if (math.fabs(dl-1.0) < EPS):
            break
            
    if (m > MAXIT):
        return math.nan
    
    return h

def ibeta(a, b, x):
    if x < 0 or x > 1:
        return -1
    
    if x == 0 or x == 1:
        bt = 0
    else:
        bt = math.exp(gammln(a+b) - gammln(a) - gammln(b) + a * math.log(x) + b * math.log(1.0 - x))

    if( x < (a + 1) / (a + b + 2)):
        return bt * betacf(a,b,x) / a
    else:
        return 1.0 - bt * betacf(b, a, 1.0-x) / b