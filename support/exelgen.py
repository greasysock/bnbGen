from support import version

__author__ = version.get_author()
__version__ = version.get_version()

import xlsxwriter, calendar, datetime, pprint
from support import baseconvert, parser

def report_list_compile(reports, tar_listing):
    accepted_type = {0:'abb', 1:'vrbo', 2:'vrbo'}
    out_list = list()
    for report in reports:
        for listing in report.pack():
            if listing == tar_listing:
                for entry in report.pack()[listing]:
                    edited_entry = entry
                    edited_entry['type'] = accepted_type[report.type()]
                    out_list.append(edited_entry)
    return out_list
def list_sort(entries,control):
    return sorted(entries, key=lambda x: x[control], reverse=True)
class __headcount_page():
    def __init__(self):
        self.page = -1
def month_end(month):
    return parser.date_to_epoch('{}/{}/{}'.format(month,calendar.monthrange(current_year(), month)[1],current_year()),0)
def month_start(month):
    return parser.date_to_epoch('{}/{}/{}'.format(month,1,current_year()), 0)
def current_year():
    return datetime.datetime.now().year
def current_month():
    return datetime.datetime.now().month
class Gen():
    def __init__(self, report, month):
        try:
            self.__month = month
            self.__date_end = month_end(self.__month)
            self.__date_start = month_start(self.__month)
            self.__combined_listings = report
            self.__totals_page = self.__report_sep_totals()
            self.__revenue_page = self.__report_sep_revenue()
        except:
            print('    ERROR: Invalid CSV file used.')
    def __report_sep_totals(self):
        out_dict = dict()
        epoch_day = 24 * 60 * 60
        for listing, entries in self.__combined_listings.items():
            out_dict[listing] = list()
            for entry in entries:
                try:
                    date_not_present = entry['start_date'] == -1
                except:
                    date_not_present = True
                try:
                    stay_not_present = entry['stay'] == -1
                except:
                    stay_not_present = True
                try:
                    money_negative = entry['earning'] < 0
                except:
                    money_negative = False
                try:
                    refund = entry['clean_fee'] < 50
                except:
                    refund = False
                if not date_not_present and not stay_not_present and not money_negative and not refund:
                    leave_night = (entry['stay'] * epoch_day) + entry['start_date']
                    if entry['start_date'] >= self.__date_start and entry['start_date'] <= self.__date_end and leave_night <= self.__date_end:
                        out_dict[listing].append(entry)
                    else:
                        '''
                        Carryover and Overstay detection types:
                        0 = carryover
                        1 = overstay
                        '''
                        leave_night = (entry['stay'] * epoch_day) + entry['start_date']
                        difference_end = ( (leave_night - self.__date_end ) / epoch_day ) - 1
                        difference_start = (leave_night - self.__date_start) / epoch_day
                        if difference_end < entry['stay'] and difference_end >= 1:
                            new_entry = entry
                            new_entry['stay'] = int(entry['stay'] - difference_end)
                            new_entry['special'] = 1
                            out_dict[listing].append(new_entry)
                        elif difference_start <= entry['stay'] and difference_start >= 1:
                            new_entry = entry
                            new_entry['stay'] = int(difference_start)
                            new_entry['special'] = 0
                            out_dict[listing].append(new_entry)
                else:
                    continue
            sorted_list = list_sort(out_dict[listing], 'start_date')
            out_dict[listing] = sorted_list
        return out_dict
    def __report_sep_revenue(self):
        out_dict = dict()
        for listing, entries in self.__combined_listings.items():
            out_dict[listing] = list()
            for entry in entries:
                try:
                    if entry['date'] >= self.__date_start and entry['date'] <= self.__date_end:
                        out_dict[listing].append(entry)
                    else:
                        continue
                except:
                    continue
            sorted_list = list_sort(out_dict[listing], 'date')
            out_dict[listing] = sorted_list
        return out_dict
    def report_gen(self, file):

            listings = list()
            workbook = xlsxwriter.Workbook(file)
            for listing, entries in self.__revenue_page.items():
                if listing not in listings:
                    listings.append(listing)

            for listing, entries in self.__totals_page.items():
                if listing not in listings:
                    listings.append(listing)
            for listing in listings:
                try:
                    if self.__revenue_page[listing] == list():
                        revenue_entries = -1
                    else:
                        revenue_entries = self.__revenue_page[listing]
                except:
                    revenue_entries = -1
                try:
                    if self.__totals_page[listing] == list():
                        nights_entries = -1
                    else:
                        nights_entries = self.__revenue_page[listing]
                except:
                    nights_entries = -1
                if revenue_entries != -1 or nights_entries != -1:
                    worksheet = workbook.add_worksheet(text_truncate(listing,31))
                    cur_row = 0
                    service = {0:'Airbnb',1:'VRBO',2:'VRBO'}
                    service['abb'] = service[0]
                    service['vrbo'] = service[1]
                    if revenue_entries != -1:
                        revenue_head = ['Service','Payment Date','Guest','Amount ($)']
                        worksheet, cur_row = self.__worksheet_write_list(worksheet, revenue_head, cur_row)
                        start_row = cur_row
                        abb_list = list()
                        vrbo_list = list()
                        for entry in self.__revenue_page[listing]:
                            revenue_line = [service[entry['type']],parser.epoch_to_date(entry['date']),entry['guest'],entry['earning']]
                            worksheet, cur_row = self.__worksheet_write_list(worksheet,revenue_line,cur_row)
                            if entry['type'] == 0:
                                abb_list.append(cur_row)
                            elif entry['type'] == 1:
                                vrbo_list.append(cur_row)
                            elif entry['type'] == 2:
                                vrbo_list.append(cur_row)
                        cur_row += 1
                        worksheet.write(cur_row,2,'{} TOTAL: '.format(service['abb']))
                        worksheet.write(cur_row, 3, '=SUM({})'.format(self.__ex_sum_gen(abb_list, 3)))
                        cur_row += 1
                        worksheet.write(cur_row, 2, '{} TOTAL: '.format(service['vrbo']))
                        worksheet.write(cur_row, 3, '=SUM({})'.format(self.__ex_sum_gen(vrbo_list, 3)))
                        cur_row += 1
                        worksheet.write(cur_row, 2, 'Overall TOTAL: ')
                        worksheet.write(cur_row, 3, '=SUM(D{}:D{})'.format(start_row + 1, cur_row-3))
                    if nights_entries != -1:
                        nights_head = ['Service','Stay Date', 'Guest', 'Stay']
                        cur_row += 2
                        worksheet, cur_row = self.__worksheet_write_list(worksheet,nights_head,cur_row)
                        start_row = cur_row
                        abb_list = list()
                        vrbo_list = list()
                        for entry in self.__totals_page[listing]:

                            try:
                                special = entry['special']
                            except:
                                special = -1
                            night_line = [service[entry['type']], parser.epoch_to_date(entry['start_date']), entry['guest'],
                                          entry['stay']]
                            if special == -1:
                                worksheet, cur_row = self.__worksheet_write_list(worksheet, night_line, cur_row)
                            elif special == 0:
                                sp_format = workbook.add_format({'font_color': 'green'})
                                worksheet, cur_row = self.__worksheet_write_list(worksheet, night_line, cur_row,format=sp_format)
                            elif special == 1:
                                sp_format1 = workbook.add_format({'font_color': 'red'})
                                worksheet, cur_row = self.__worksheet_write_list(worksheet, night_line, cur_row,format=sp_format1)
                            if entry['type'] == 0:
                                abb_list.append(cur_row)
                            elif entry['type'] == 1 or entry ['type'] == 2:
                                vrbo_list.append(cur_row)
                        cur_row += 1
                        worksheet.write(cur_row, 2, '{} TOTAL: '.format(service['abb']))
                        worksheet.write(cur_row, 3, '=SUM({})'.format(self.__ex_sum_gen(abb_list, 3)))
                        cur_row += 1
                        worksheet.write(cur_row, 2, '{} TOTAL: '.format(service['vrbo']))
                        worksheet.write(cur_row, 3, '=SUM({})'.format(self.__ex_sum_gen(vrbo_list, 3)))
                        cur_row += 1
                        worksheet.write(cur_row, 2, 'Overall TOTAL: ')
                        worksheet.write(cur_row, 3, '=SUM(D{}:D{})'.format(start_row + 1, cur_row - 3))
            workbook.close()

    def __worksheet_write_list(self,worksheet, list,cur_row, format=-1):
        cur_col = 0
        for entry in list:
            if format == -1:
                worksheet.write(cur_row, cur_col,entry)
            else:
                worksheet.write(cur_row, cur_col, entry,format)
            cur_col += 1
        cur_row += 1
        return worksheet, cur_row
    def __ex_sum_gen(self, row_pack, col_tar):
        convert = baseconvert.convert()
        col = convert.tran(col_tar)
        out_str = ''
        itera = 0
        for row in row_pack:
            if itera == 0:
                out_str += '{}{}'.format(col,row)
            elif itera > 0:
                out_str += '+{}{}'.format(col,row)
            itera += 1
        return out_str
    def year(self):
        return current_year()

def text_truncate(text, length):
    return text[:length] if len(text) > length else text