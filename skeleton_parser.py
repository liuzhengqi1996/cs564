
"""
FILE: skeleton_parser.py
------------------
Author: Firas Abuzaid (fabuzaid@stanford.edu)
Author: Perth Charernwattanagul (puch@stanford.edu)
Modified: 04/21/2014

Skeleton parser for CS564 programming project 1. Has useful imports and
functions for parsing, including:

1) Directory handling -- the parser takes a list of eBay json files
and opens each file inside of a loop. You just need to fill in the rest.
2) Dollar value conversions -- the json files store dollar value amounts in
a string like $3,453.23 -- we provide a function to convert it to a string
like XXXXX.xx.
3) Date/time conversions -- the json files store dates/ times in the form
Mon-DD-YY HH:MM:SS -- we wrote a function (transformDttm) that converts to the
for YYYY-MM-DD HH:MM:SS, which will sort chronologically in SQL.

Your job is to implement the parseJson function, which is invoked on each file by
the main function. We create the initial Python dictionary object of items for
you; the rest is up to you!
Happy parsing!
"""

import sys
from json import loads
from re import sub
import csv

columnSeparator = "|"

# Initialize all the dictonaries
item_entity = {}
Bidder_entity = {}
Seller_entity = {}
Bids_entity = {}
category_entity={}

def checkEmptyStr(string):
    if string is None or len(string)==0:
        return "NULL"
    return string

# Dictionary of months used for date transformation
MONTHS = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06',\
        'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}

"""
Returns true if a file ends in .json
"""
def isJson(f):
    return len(f) > 5 and f[-5:] == '.json'

"""
Converts month to a number, e.g. 'Dec' to '12'
"""
def transformMonth(mon):
    if mon in MONTHS:
        return MONTHS[mon]
    else:
        return mon

"""
Transforms a timestamp from Mon-DD-YY HH:MM:SS to YYYY-MM-DD HH:MM:SS
"""
def transformDttm(dttm):
    dttm = dttm.strip().split(' ')
    dt = dttm[0].split('-')
    date = '20' + dt[2] + '-'
    date += transformMonth(dt[0]) + '-' + dt[1]
    return date + ' ' + dttm[1]

"""
Transform a dollar value amount from a string like $3,453.23 to XXXXX.xx
"""

def transformDollar(money):
    if money == None or len(money) == 0:
        return money
    return sub(r'[^\d.]', '', money)

def InitDicts():
    item_entity.setdefault('ItemID',[])
    item_entity.setdefault('Name',[])
    item_entity.setdefault('First_Bid',[])
    item_entity.setdefault('Location',[])
    item_entity.setdefault('Seller',[])
    item_entity.setdefault('Country',[])
    item_entity.setdefault('Currently',[])
    item_entity.setdefault('Started',[])
    item_entity.setdefault('Ends',[])
    item_entity.setdefault('Description',[])
    item_entity.setdefault('Number_of_Bids',[])
    item_entity.setdefault('First_Bid',[])
    item_entity.setdefault('Buy_Price',[])
    # Init Bidder
    Bidder_entity.setdefault("UserID",[])
    Bidder_entity.setdefault("Rating",[])
    Bidder_entity.setdefault("Country",[])
    Bidder_entity.setdefault("Location",[])
    # Init Bids
    Bids_entity.setdefault("ItemID",[])
    Bids_entity.setdefault("Bidder",[])
    Bids_entity.setdefault("Time",[])
    Bids_entity.setdefault("Amount",[])
    # Init Seller
    Seller_entity.setdefault("UserID",[])
    Seller_entity.setdefault("Rating",[])
    # Inir Category
    category_entity.setdefault("ItemID",[])
    category_entity.setdefault("Category",[])

InitDicts()

"""
Parses a single json file. Currently, there's a loop that iterates over each
item in the data set. Your job is to extend this functionality to create all
of the necessary SQL tables for your database.
"""
def parseJson(json_file):
    with open(json_file, 'r') as f:
        items = loads(f.read())['Items']
        for item in items:
            # Add to Items
            if item['ItemID'] not in item_entity:
                item_entity['ItemID'].append(item['ItemID'])
                item_entity['Name'].append(checkEmptyStr(item['Name']))
                item_entity['Location'].append(item['Location'])
                item_entity['Seller'].append(item['Seller']['UserID'])
                item_entity['Country'].append(item['Country'])
                item_entity['Currently'].append(transformDollar(item['Currently']))
                item_entity['Started'].append(transformDttm(item['Started']))
                item_entity['Ends'].append(transformDttm(item['Ends']))
                item_entity['Description'].append(checkEmptyStr(item['Description']))
                item_entity['Number_of_Bids'].append(checkEmptyStr(item['Number_of_Bids']))
                item_entity['First_Bid'].append(transformDollar(item['First_Bid']))
                if 'Buy_Price' in item:
                    item_entity['Buy_Price'].append(transformDollar(item['Buy_Price']))
                else:
                    item_entity['Buy_Price'].append(0)
                
                # Add to Seller
                Seller_entity['UserID'].append(item['Seller']['UserID'])
                Seller_entity['Rating'].append(item['Seller']['Rating'])
                # Add to category
                
                for category in item['Category']:
                    category_entity['Category'].append(category)
                    category_entity['ItemID'].append(item['ItemID'])
            
            # Add to Bidder
            if item['Bids']:
                for bid in item['Bids']:
                    if 'Country' in bid['Bid']['Bidder']:
                        Bidder_entity['Country'].append(checkEmptyStr(bid['Bid']['Bidder']['Country']))
                    if 'Location' in bid['Bid']['Bidder']:
                        Bidder_entity['Location'].append(checkEmptyStr(bid['Bid']['Bidder']['Location']))
                    Bidder_entity['Rating'].append(checkEmptyStr(bid['Bid']['Bidder']['Rating']))
                    Bidder_entity['UserID'].append(checkEmptyStr(bid['Bid']['Bidder']['UserID']))
                    #Add to Bids
                    Bids_entity['ItemID'].append(item['ItemID'])
                    Bids_entity['Bidder'].append(checkEmptyStr(bid['Bid']['Bidder']['UserID']))
                    Bids_entity['Amount'].append(checkEmptyStr(bid['Bid']['Amount']))
                    Bids_entity['Time'].append(transformDttm(bid['Bid']['Time']))

"""
Loops through each json files provided on the command line and passes each file
to the parser
"""
def main(argv):
    if len(argv) < 2:
        print >> sys.stderr, 'Usage: python skeleton_json_parser.py <path to json files>'
        sys.exit(1)
    # loops over all .json files in the argument
    for f in argv[1:]:
        if isJson(f):
            parseJson(f)
            print "Success parsing " + f

    with open("items.dat", "wb") as items_file:
        writer1 = csv.writer(items_file,delimiter="|")
        writer1.writerows(zip(*item_entity.values()))

    with open("bids.dat", "wb") as bids_file:
        writer2 = csv.writer(bids_file,delimiter="|")
        writer2.writerows(zip(*Bids_entity.values()))
    
    with open("bidder.dat", "wb") as bidder_file:
        writer3 = csv.writer(bidder_file,delimiter="|")
        writer3.writerows(zip(*Bidder_entity.values()))
    
    with open("seller.dat", "wb") as seller_file:
        writer4 = csv.writer(seller_file,delimiter="|")
        writer4.writerows(zip(*Seller_entity.values()))
    
    with open("categories.dat", "wb") as categories_file:
        writer5 = csv.writer(categories_file,delimiter="|")
        writer5.writerows(zip(*category_entity.values()))

    items_file.close()
    bids_file.close()
    bidder_file.close()
    seller_file.close()
    categories_file.close()

if __name__ == '__main__':
    main(sys.argv)