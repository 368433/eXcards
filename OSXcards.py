import pandas as pd
from cryptography.fernet import Fernet
import sqlalchemy
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
        # engine creation done in DMM file
        conn = engine.connect()
        Base.metadata.create_all(engine)

        #Set up the tables in db and files to import
        model_data = {'billingcode':'Model/billingcode.csv',
                    'facility':'Model/facility.csv',
                    'secteur':'Model/secteur.csv'}
        # TO ADD: cmqdb for physician table
        # TO ADD: MIEE data for MIEE table
        #'icdcode':'Model/ramqicd9.csv'

        for k, v in model_data.items():
            tableToWriteTo = k
            fileToRead = v
            # Panda to create a lovely dataframe
            df_to_be_written = pd.read_csv(fileToRead)
            listToWrite = df_to_be_written.to_dict(orient='records')

            metadata = sqlalchemy.schema.MetaData(bind=engine,reflect=True)
            table = sqlalchemy.Table(tableToWriteTo, metadata, autoload=True)

            # Inser the dataframe into the database in one bulk
            conn.execute(table.insert(), listToWrite)

            # Commit the changes
            session.commit()

    except:
        raise
    # except ValueError as msg:
    #     print(msg)
    #     print("Databases were not created and not populated. Run on Mac")

if __name__ == '__main__':
    build_empty_db()
