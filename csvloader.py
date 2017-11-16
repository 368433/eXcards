##########################################
# note: odo requires sqlalchemy
# install in virt env before using odo
##########################################

from odo import odo
from odo import discover, resource

#populating the ramqcodes Table
def populate():
    dshape = discover(resource('Model/Billingcodes.csv'))
    odo('Model/Billingcodes.csv', 'sqlite:///test.db::billingcode', dshape=dshape)

    #populate locations

    #populating the PhysicianRegistry table
    #dshape = discover(resource('cmqphysicians.csv'))
    #odo('cmqphysicians.csv', 'sqlite:///test.db', dshape=dshape)

if __name__ == '__main__':
    populate()
