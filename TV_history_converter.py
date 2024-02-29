import os
import csv
import re

in_account_history_file = './out/paper-trading-account-history.csv'
out_folder = './out'
out_history_file = out_folder + '/created_history.csv'

if not os.path.exists(out_folder):
    os.makedirs(out_folder)

out_file_header = ['Symbol', 'Side', 'Type', 'Qty', 'Price', 'Fill Price', 'Status', 'Commission', 'Placing Time',
                   'Closing Time', 'Order id']
out_file_content = [out_file_header]

action_regex = r'Close (?P<position>long|short) position for symbol (?P<symbol>.*) at price (?P<close_price>.*) for (?P<shares>\d*) shares\. Position AVG Price was (?P<open_price>.*), currency: (?P<currency>.*), point value: (?P<point_value>.*)'

i = 0


def convert_row(row):
    global i
    closing_time = row[0]
    placing_time = row[0]  # as we do not know, we just use the closing time here as well

    action_string = row[4]
    match = re.match(action_regex, action_string)
    if match:
        symbol = match.group('symbol')
        position = match.group('position')
        shares = match.group('shares')
        open_price = match.group('open_price')
        close_price = match.group('close_price')

        open_order = [symbol, 'Buy' if position == 'long' else 'Sell', 'Market',
                      shares, open_price, open_price, 'Filled', '',
                      placing_time,
                      placing_time, i]
        i += 1

        close_order = [symbol, 'Sell' if position == 'long' else 'Buy', 'Market', shares, close_price, close_price,
                       'Filled', '', closing_time, closing_time, i]
        i += 1

        return [open_order, close_order]
    else:
        print('Could not match action: ' + str(action_string))

    return None


with open(in_account_history_file, newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in spamreader:
        converted_rows = convert_row(row)
        if converted_rows:
            open_order = converted_rows[0]
            close_order = converted_rows[1]
            if None in open_order or None in close_order:
                print(f'Could not convert all properties of {str(row)}: {str(open_order)} | {str(close_order)}')
            else:
                out_file_content.append(open_order)
                out_file_content.append(close_order)

with open(out_history_file, 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for row in out_file_content:
        spamwriter.writerow(row)
