from support import version

__author__ = version.get_author()
__version__ = version.get_version()

import csv, datetime, time, re

abb_header = ['\ufeffDate', 'Type', 'Confirmation Code', 'Start Date', 'Nights', 'Guest', 'Listing', 'Details', 'Reference', 'Currency', 'Amount', 'Paid Out', 'Host Fee', 'Cleaning Fee']
vrbo_r_header = ['\ufeffReservation ID', 'Listing Number', 'Property Name', 'Created On', 'Email', 'Inquirer', 'Phone', 'Check-in', 'Check-out', 'Nights Stay', 'Adults', 'Children', 'Status', 'Source']
vrbo_p_header = ['\ufeffRefID', 'Reservation ID', 'Check In', 'Check Out', 'Number of Nights', 'Payment Date', 'Payment Type', 'Property ID', 'Guest Name', 'Payment Method', 'Taxable Revenue', 'Non-Taxable Revenue', 'Tax', 'Service Fee', 'Currency', 'Paid By Guest', 'Your Revenue', 'Payment Processing Fee', 'hac.list.payments.ha.taxes.collected', 'hac.list.payments.partner.taxes.collected', 'Deposit Amount', 'Payable To You']
vrbo_p1_header = ['\ufeffRefID', 'Reservation ID', 'Check In', 'Check Out', 'Number of Nights', 'Payment Date', 'Disbursement Date', 'Payment Type', 'Property ID', 'Guest Name', 'Payment Method', 'Taxable Revenue', 'Non-Taxable Revenue', 'Tax', 'Service Fee', 'Currency', 'Paid By Guest', 'Your Revenue', 'Payment Processing Fee', 'hac.list.payments.ha.taxes.collected', 'hac.list.payments.partner.taxes.collected', 'Deposit Amount', 'Payable To You']
vrbo_p2_header = ['\ufeffRefID', 'Reservation ID', 'Check In', 'Check Out', 'Number of Nights', 'Payment Date', 'Payment Type', 'Property ID', 'Guest Name', 'Payment Method', 'Taxable Revenue', 'Non-Taxable Revenue', 'Tax', 'Service Fee', 'Currency', 'Paid By Guest', 'Your Revenue', 'Payment Processing Fee', 'Stay Tax We Remit', 'Stay Tax You Remit', 'Deposit Amount', 'Payable To You']
vrbo_p3_header = ['\ufeffRefID', 'Reservation ID', 'Check In', 'Check Out', 'Number of Nights', 'Source', 'Payment Date', 'Disbursement Date', 'Payment Type', 'Property ID', 'Guest Name', 'Payment Method', 'Taxable Revenue', 'Non-Taxable Revenue', 'Tax', 'Service Fee', 'Currency', 'Guest Payment', 'Your Revenue', 'Commission', 'VAT on Commission', 'Payment Processing Fee', 'Stay Tax We Remit', 'Stay Tax You Remit', 'Refundable deposit', 'Payable To You', 'Payout']

def digit_clean(dirty_text):
    return re.search('\d+', dirty_text).group(0)
def epoch_to_date(epoch):
    return time.strftime('%Y-%m-%d', time.localtime(epoch))
def date_to_epoch(date, report_type):
    #May need timezone revision
    if report_type == 0:
        return time.mktime(datetime.datetime.strptime(date, "%m/%d/%Y").timetuple())
    elif report_type == 1:
        return time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d").timetuple())
    elif report_type == 2:
        months = {
            'Jan':1,
            'Feb':2,
            'Mar':3,
            'Apr':4,
            'May':5,
            'Jun':6,
            'Jul':7,
            'Aug':8,
            'Sep':9,
            'Oct':10,
            'Nov':11,
            'Dec':12
        }
        date_split = str(date).split()
        month = months[date_split[0]]
        day = date_split[1].split(',')[0]
        year = date_split[2]
        formal_date = '{} {}, {}'.format(month, day, year)
        return time.mktime(datetime.datetime.strptime(formal_date, "%m %d, %Y").timetuple())
def money_clean(money):
    money = money.split('$')[1]
    money = re.sub('[,]', '', money)
    try:
        return float(money)
    except:
        money = re.sub('[)]', '', money)
        return float('-{}'.format(money))
class report():
    def __init__(self, raw_report):
        self.__raw_report = raw_report
        self.__report = self.__report_grab(self.__raw_report)
        '''
        Report types:

        -1: Not Valid
        0: ABB
        1: VRBO Reservations
        2: VRBO Payment Stub
        3: VRBO Payment Stub V2
        4: VRBO Payment Stub V3
        '''
        self.__report_type = self.__report_check()
        if self.__report_type == 0:
            self.__abb_report_parse()
        elif self.__report_type == 1:
            self.__vrbo_r_parse()
        elif self.__report_type == 2:
            self.__vrbo_p_parse()
        elif self.__report_type == 3:
            self.__vrbo_p1_parse()
        elif self.__report_type == 4:
            self.__vrbo_p2_parse()
        elif self.__report_type == 5:
            self.__vrbo_p3_parse()
    def __report_grab(self, report):
        raw_report = list()
        vraw_report = csv.reader(report, delimiter=',')
        for listing in vraw_report:
            raw_report.append(listing)
        return raw_report
    def __report_check(self):
        header = self.__report[0]
        if header == abb_header:
            return 0
        elif header == vrbo_r_header:
            return 1
        elif header == vrbo_p_header:
            return 2
        elif header == vrbo_p1_header:
            return 3
        elif header == vrbo_p2_header:
            return 4
        elif header == vrbo_p3_header:
            return 5
        else:
            return -1
    def __abb_report_parse(self):
        main_dict = dict()
        for listing in self.__report:
            if listing[2] != '' and listing[2] != 'Confirmation Code':
                try:
                    main_dict[listing[6]].append({'date': date_to_epoch(listing[0],self.type()),'start_date':date_to_epoch(listing[3],self.type()), 'guest': listing[5],
                                                         'earning': float(listing[10]), 'stay': int(listing[4]), 'clean_fee':int(float(listing[13]))})
                except:
                    main_dict[listing[6]] = list()
                    main_dict[listing[6]].append({'date': date_to_epoch(listing[0],self.type()),'start_date':date_to_epoch(listing[3],self.type()), 'guest': listing[5],
                                                         'earning': float(listing[10]), 'stay': int(listing[4]),'clean_fee':int(float(listing[13]))})
        self.__pack = main_dict
    def __vrbo_r_parse(self):
        main_dict = dict()
        for listing in self.__report:
            if listing[0] != '' and listing[0] != vrbo_r_header[0]:
                try:
                    main_dict[listing[2]].append({'start_date':date_to_epoch(listing[7],self.type()),'guest':listing[5],'stay':int(listing[9]), 'listing':listing[1]})
                except:
                    main_dict[listing[2]] = list()
                    main_dict[listing[2]].append({'start_date': date_to_epoch(listing[7],self.type()), 'guest': listing[5], 'stay': int(listing[9]), 'listing':listing[1]})
        self.__pack = main_dict
    def __vrbo_p1_parse(self):
        main_dict = dict()
        for listing in self.__report:
            try:
                if listing[0] != '' and listing[0] != vrbo_p_header[0]:
                    try:
                        main_dict[digit_clean(listing[8])].append({'date':date_to_epoch(listing[6],self.type()),'guest':listing[9],'earning':money_clean(listing[21])})
                    except:
                        main_dict[digit_clean(listing[8])] = list()
                        main_dict[digit_clean(listing[8])].append({'date': date_to_epoch(listing[6],self.type()), 'guest': listing[9],
                                                             'earning': money_clean(listing[21])})
            except IndexError:
                continue
        self.__pack = main_dict
    def __vrbo_p2_parse(self):
        main_dict = dict()
        for listing in self.__report:
            try:
                if listing[0] != '' and listing[0] != vrbo_p_header[0]:
                    try:
                        main_dict[digit_clean(listing[7])].append({'date':date_to_epoch(listing[5],self.type()),'guest':listing[8],'earning':money_clean(listing[25])})
                    except:
                        main_dict[digit_clean(listing[7])] = list()
                        main_dict[digit_clean(listing[7])].append({'date': date_to_epoch(listing[5],self.type()), 'guest': listing[8],
                                                             'earning': money_clean(listing[25])})
            except IndexError:
                continue
        self.__pack = main_dict
    def __vrbo_p3_parse(self):
        main_dict = dict()
        for listing in self.__report:
            try:
                if listing[0] != '' and listing[0] != vrbo_p_header[0]:
                    try:
                        main_dict[digit_clean(listing[9])].append({'date':date_to_epoch(listing[7],self.type()),'guest':listing[10],'earning':money_clean(listing[21])})
                    except:
                        main_dict[digit_clean(listing[9])] = list()
                        main_dict[digit_clean(listing[9])].append({'date': date_to_epoch(listing[7],self.type()), 'guest': listing[10],
                                                             'earning': money_clean(listing[21])})
            except IndexError:
                continue
        self.__pack = main_dict
    def __vrbo_p_parse(self):
        main_dict = dict()
        for listing in self.__report:
            try:
                if listing[0] != '' and listing[0] != vrbo_p_header[0]:
                    try:
                        main_dict[digit_clean(listing[7])].append({'date':date_to_epoch(listing[5],self.type()),'guest':listing[8],'earning':money_clean(listing[20])})
                    except:
                        main_dict[digit_clean(listing[7])] = list()
                        main_dict[digit_clean(listing[7])].append({'date': date_to_epoch(listing[5],self.type()), 'guest': listing[8],
                                                             'earning': money_clean(listing[20])})
            except IndexError:
                continue
        self.__pack = main_dict
    def pack(self):
        try:
            return self.__pack
        except:
            return -1
    def type(self):
        if self.__report_type == 3 or self.__report_type == 4 or self.__report_type == 5:
            return 2
        else:
            return self.__report_type
    def combine_listing(self, main_listing, new_listing):
        return  main_listing + new_listing
    def listings(self):
        listings = list()
        for listing in self.__pack:
            listings.append(listing)
        return listings
    def resort_pack(self, rules):
        try:
            new_dict = dict()
            for listing in self.__pack:
                if listing in rules.keys():
                    new_dict[listing] = self.__pack[listing]
                else:
                    found = list()
                    for rule, subrule in rules.items():
                        if listing in subrule:
                            try:
                                not_present = new_dict[rule] == -1
                            except:
                                not_present = True
                            if not_present:
                                new_dict[rule] = self.__pack[listing]
                            else:
                                new_dict[rule] = self.combine_listing(new_dict[rule], self.__pack[listing])
                            found.append(listing)
                    if listing not in found:
                        print('    WARNING: Listing \'{}\' not found in rules.ini'.format(listing))
                        new_dict[listing] = self.__pack[listing]
            self.__pack = new_dict
        except:
            print('    WARNING: No rules.ini in client folder')