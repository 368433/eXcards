def find_payment(loan, r, m):
    return loan*((r*(1+r)**m)/((1+r)**m-1))
