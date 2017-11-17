import pandas as pd
from cryptography.fernet import Fernet
from DMM import *

#############################################################
# password key to encrypt and decrypt Patient entries
# patientpwd = b'fWB2ISaUuCJhLzZCGxGTLW2yDE2zmfPnxzWeEiN_7TM='
# f = Fernet(patientpwd)
#############################################################

def build_empty_db():
    try:
        if platform.system().startswith('iP'):
            raise ValueError("You are running on IOS")
        df = pd.read_csv('Model/Billingcodes.csv')
        Base.metadata.create_all(engine)
        df.to_sql('BillingCode, engine')
    except ValueError as msg:
        print(msg)
        print("Databases were not created and not populated. Run on Mac")

if __name__ == '__main__':
    build_empty_db()
