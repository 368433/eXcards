##########################################
# note: odo requires sqlalchemy
# install in virt env before using odo
##########################################

from odo import odo
from odo import discover, resource

#populating the ramqcodes Table
def populate():
    dshape = discover(resource('csvdb/codes.csv'))
    odo('csvdb/codes.csv', 'sqlite:///test.db::billingcode', dshape=dshape)

    dshape = discover(resource('csvdb/type_of_work.csv'))
    odo('csvdb/type_of_work.csv', 'sqlite:///test.db::type_of_work', dshape=dshape)

    dshape = discover(resource('csvdb/hospitals.csv'))
    odo('csvdb/hospitals.csv', 'sqlite:///test.db::location', dshape=dshape)

    #populate locations

    #populating the PhysicianRegistry table
    #dshape = discover(resource('cmqphysicians.csv'))
    #odo('cmqphysicians.csv', 'sqlite:///test.db', dshape=dshape)

if __name__ == '__main__':
    populate()
