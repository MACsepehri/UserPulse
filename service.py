import pandas as pd
from assets import parse_jalali_datetime

# Iterate rows the correct way
# for idx, row in model.df.iterrows():
#     print(row['total_visit'])          # 3

# Or access the whole column
# print(model.df['total_visit'].tolist())  # [3]

# Or select a single value by label
# print(model.df.loc[0, 'user_info'])      # ['Aryan', ...]

# Or select a single value by label
# print(model.df.loc[0, 'user_info'])      # ['Aryan', ...]

#creating linear regression model
#loading arrays
    #each array base is this for each user:
    #-total_visit
    #-all_parts
    #-most_visit_part[most_visit_part,most_visit_part_total]
    #-most_visit_part_dates
    #-less_visit_part[less_visit_part,less_visit_part_total]
    #-less_visit_part_dates
    #-website_visit_dates
    #-user_info[...]
    #-user_column[...]

class BaseModel:
    def __init__(self):
        self.data = []
        self.__df = None

    def add_array(self, data: list):
        self.data.append(data)

    def create_df(self):
        self.__df = pd.DataFrame(
            self.data,
            columns=[
                'total_visit', 'all_parts',
                'most_visit_part', 'most_visit_part_dates',
                'less_visit_part', 'less_visit_part_dates',
                'website_visit_dates', 'user_info', 'user_column',
            ],
        )

    def to_dict(self):
        dict_data = []
        for _, row in self.__df.iterrows():
            dict_data.append(row.to_dict())
        return dict_data

    def check_user_visits_to_website(self):
        data = self.to_dict()
        result = []

        for user_data in data:
            dates = user_data['website_visit_dates']

            if not dates or len(dates) < 2:
                result.append([])
                continue

            parsed_dates = [
                parse_jalali_datetime(f'{date} 00:00:00')
                for date in dates
                if date != '-'
            ]

            if len(parsed_dates) < 2:
                result.append([])
                continue

            differences = []

            for i in range(1, len(parsed_dates)):
                difference = parsed_dates[i] - parsed_dates[i - 1]
                differences.append(int(difference))

            result.append(differences)

        return result

    def average(self, l: list):
        if not l:
            return 0

        num = 0

        for n in l:
            num += int(n)

        return num / len(l)

    def calculate_date_data(self, dates):
        if not dates or dates == ['-']:
            return {
                'valid': False,
                'differences': [],
                'max_difference': 0,
                'last_difference': 0,
                'average': 0,
            }

        valid_dates = []

        for date in dates:
            if date == '-':
                continue

            valid_dates.append(
                parse_jalali_datetime(f'{date} 00:00:00')
            )

        if len(valid_dates) < 2:
            return {
                'valid': False,
                'differences': [],
                'max_difference': 0,
                'last_difference': 0,
                'average': 0,
            }

        differences = []

        for i in range(1, len(valid_dates)):
            difference = valid_dates[i] - valid_dates[i - 1]
            differences.append(int(difference))

        return {
            'valid': True,
            'differences': differences,
            'max_difference': max(differences),
            'last_difference': differences[-1],
            'average': self.average(differences),
        }

    def get_website_warning(self, average):
        if average <= 3:
            return "🟢 (normal)"
        elif average <= 7:
            return "🟡 (unusual but okay)"
        elif average <= 14:
            return "🟠 (warning, it looks like user doesn't like website, becareful)"
        elif average <= 30:
            return "🔴 (high status, user almost wanna don't use website)"
        else:
            return "⚫ (very high usage interval)"

    def get_service_warning(self, average):
        if average <= 5:
            return "🟢 (good status)"
        elif average <= 10:
            return "🟡 (unusual)"
        elif average <= 15:
            return "🟠 (warning, it looks like user doesn't like service again, becareful)"
        elif average <= 20:
            return "🔴 (high status, user almost wanna don't use service)"
        else:
            return "⚫ (very high usage interval)"

    def calculate_service(self, service_name, total_visits, dates):
        date_data = self.calculate_date_data(dates)

        if not date_data['valid']:
            return {
                'name': service_name,
                'total_visits': total_visits,
                'dates': dates,
                'data': date_data,
                'warning': "⚪ (user didn't use the plan up to now)",
            }

        return {
            'name': service_name,
            'total_visits': total_visits,
            'dates': dates,
            'data': date_data,
            'warning': self.get_service_warning(
                date_data['average']
            ),
        }

    def calculate(self):
        users = self.to_dict()
        results = []

        for user_data in users:

            # handle website usage state
            website_data = self.calculate_date_data(
                user_data['website_visit_dates']
            )

            if website_data['valid']:
                website_warning = self.get_website_warning(
                    website_data['average']
                )
            else:
                website_warning = "⚪ (user didn't use the plan up to now)"

            # handle most usage state
            most_usage_state = []

            most_parts = user_data['most_visit_part']
            most_dates = user_data['most_visit_part_dates']

            for i, usage in enumerate(most_parts):

                service_name = usage[0]
                total_visits = usage[1]

                if i < len(most_dates):
                    service_dates = most_dates[i]
                else:
                    service_dates = ['-']

                # If the service has zero visits, do not calculate anything
                if total_visits == 0:
                    service_dates = ['-']

                service_result = self.calculate_service(
                    service_name,
                    total_visits,
                    service_dates
                )

                most_usage_state.append(service_result)

            # handle less usage state
            less_usage_state = []

            less_parts = user_data['less_visit_part']
            less_dates = user_data['less_visit_part_dates']

            for i, usage in enumerate(less_parts):

                service_name = usage[0]
                total_visits = usage[1]

                if i < len(less_dates):
                    service_dates = less_dates[i]
                else:
                    service_dates = ['-']

                # If the service has zero visits, do not calculate anything
                if total_visits == 0:
                    service_dates = ['-']

                service_result = self.calculate_service(
                    service_name,
                    total_visits,
                    service_dates
                )

                less_usage_state.append(service_result)

            results.append({
                'user_info': user_data['user_info'],
                'total_visit': user_data['total_visit'],
                'website_data': website_data,
                'website_warning': website_warning,
                'most_usage_part_data': most_usage_state,
                'less_usage_part_data': less_usage_state,
            })

        msg = 'model result :\n\n'

        msg += 'Status legend\n'
        msg += '-----------------------------------------------------------\n'
        msg += '🟢 = Good / Normal\n'
        msg += '🟡 = Unusual but okay\n'
        msg += '🟠 = Warning\n'
        msg += '🔴 = High warning\n'
        msg += '⚫ = Very high usage interval / Very high warning\n'
        msg += '⚪ = No valid usage data\n'
        msg += '___________________________________________________________\n\n'

        for index, result in enumerate(results, start=1):

            msg += f'User {index}\n\n'

            msg += f'User info: {result["user_info"]}\n'
            msg += f'Total visits: {result["total_visit"]}\n\n'

            msg += 'Website usage\n'
            msg += '-----------------------------------------------------------\n'

            website_data = result['website_data']

            if not website_data['valid']:
                msg += "Status: ⚪ (user didn't use the plan up to now)\n"
            else:
                msg += f'Max difference: {website_data["max_difference"]} days\n'
                msg += f'Last difference: {website_data["last_difference"]} days\n'
                msg += f'Average usage interval: {website_data["average"]:.2f} days\n'
                msg += f'Day usage differences: {website_data["differences"]}\n'
                msg += f'Usage dates warning: {result["website_warning"]}\n'

            msg += '___________________________________________________________\n\n'

            msg += f'Most usage parts (total: {len(result["most_usage_part_data"])}) :\n\n'

            for usage in result['most_usage_part_data']:

                msg += f'Service name: {usage["name"]}\n'
                msg += f'Total visits: {usage["total_visits"]}\n'

                if not usage['data']['valid']:
                    msg += f'Usage dates: {usage["dates"]}\n'
                    msg += "Status: ⚪ (user didn't use the plan up to now)\n"
                else:
                    msg += f'Usage dates: {usage["dates"]}\n'
                    msg += f'Max difference: {usage["data"]["max_difference"]} days\n'
                    msg += f'Last difference: {usage["data"]["last_difference"]} days\n'
                    msg += f'Average usage interval: {usage["data"]["average"]:.2f} days\n'
                    msg += f'Day usage differences: {usage["data"]["differences"]}\n'
                    msg += f'Status: {usage["warning"]}\n'

                msg += '-----------------------------\n'

            msg += '\n'

            msg += f'Less usage parts (total: {len(result["less_usage_part_data"])}) :\n\n'

            for usage in result['less_usage_part_data']:

                msg += f'Service name: {usage["name"]}\n'
                msg += f'Total visits: {usage["total_visits"]}\n'

                if not usage['data']['valid']:
                    msg += f'Usage dates: {usage["dates"]}\n'
                    msg += "Status: ⚪ (user didn't use the plan up to now)\n"
                else:
                    msg += f'Usage dates: {usage["dates"]}\n'
                    msg += f'Max difference: {usage["data"]["max_difference"]} days\n'
                    msg += f'Last difference: {usage["data"]["last_difference"]} days\n'
                    msg += f'Average usage interval: {usage["data"]["average"]:.2f} days\n'
                    msg += f'Day usage differences: {usage["data"]["differences"]}\n'
                    msg += f'Status: {usage["warning"]}\n'

                msg += '-----------------------------\n'

            msg += '___________________________________________________________\n\n'

        total_users = len(results)
        total_website_visits = 0
        total_service_visits = 0

        website_max_differences = []
        website_last_differences = []
        website_average_intervals = []
        website_all_differences = []

        service_max_differences = []
        service_last_differences = []
        service_average_intervals = []
        service_all_differences = []

        total_services = 0
        valid_website_users = 0
        valid_services = 0

        for result in results:

            total_website_visits += int(result['total_visit'])

            website_data = result['website_data']

            if website_data['valid']:
                valid_website_users += 1
                website_max_differences.append(
                    website_data['max_difference']
                )
                website_last_differences.append(
                    website_data['last_difference']
                )
                website_average_intervals.append(
                    website_data['average']
                )
                website_all_differences.extend(
                    website_data['differences']
                )

            for usage in result['most_usage_part_data']:
                total_services += 1
                total_service_visits += int(usage['total_visits'])

                if usage['data']['valid']:
                    valid_services += 1
                    service_max_differences.append(
                        usage['data']['max_difference']
                    )
                    service_last_differences.append(
                        usage['data']['last_difference']
                    )
                    service_average_intervals.append(
                        usage['data']['average']
                    )
                    service_all_differences.extend(
                        usage['data']['differences']
                    )

            for usage in result['less_usage_part_data']:
                total_services += 1
                total_service_visits += int(usage['total_visits'])

                if usage['data']['valid']:
                    valid_services += 1
                    service_max_differences.append(
                        usage['data']['max_difference']
                    )
                    service_last_differences.append(
                        usage['data']['last_difference']
                    )
                    service_average_intervals.append(
                        usage['data']['average']
                    )
                    service_all_differences.extend(
                        usage['data']['differences']
                    )

        msg += 'ALL DATA STATISTICS\n'
        msg += '===========================================================\n\n'

        msg += f'Total users: {total_users}\n'
        msg += f'Total website visits: {total_website_visits}\n'
        msg += f'Total services: {total_services}\n'
        msg += f'Total service visits: {total_service_visits}\n\n'

        msg += 'Website usage - all users\n'
        msg += '-----------------------------------------------------------\n'

        if valid_website_users == 0:
            msg += "Status: ⚪ (no valid website usage data)\n"
        else:
            overall_website_max = self.average(
                website_max_differences
            )
            overall_website_last = self.average(
                website_last_differences
            )
            overall_website_average = self.average(
                website_average_intervals
            )
            overall_website_difference_average = self.average(
                website_all_differences
            )

            msg += f'Users with valid data: {valid_website_users}\n'
            msg += f'Average max difference: {overall_website_max:.2f} days\n'
            msg += f'Average last difference: {overall_website_last:.2f} days\n'
            msg += f'Average usage interval: {overall_website_average:.2f} days\n'
            msg += f'Overall day usage difference average: {overall_website_difference_average:.2f} days\n'
            msg += f'Status: {self.get_website_warning(overall_website_average)}\n'

        msg += '\n'

        msg += 'Services usage - all users\n'
        msg += '-----------------------------------------------------------\n'

        if valid_services == 0:
            msg += "Status: ⚪ (no valid service usage data)\n"
        else:
            overall_service_max = self.average(
                service_max_differences
            )
            overall_service_last = self.average(
                service_last_differences
            )
            overall_service_average = self.average(
                service_average_intervals
            )
            overall_service_difference_average = self.average(
                service_all_differences
            )

            msg += f'Services with valid data: {valid_services}\n'
            msg += f'Average max difference: {overall_service_max:.2f} days\n'
            msg += f'Average last difference: {overall_service_last:.2f} days\n'
            msg += f'Average usage interval: {overall_service_average:.2f} days\n'
            msg += f'Overall day usage difference average: {overall_service_difference_average:.2f} days\n'
            msg += f'Status: {self.get_service_warning(overall_service_average)}\n'

        msg += '___________________________________________________________\n\n'

        return msg

    def to_html(self,text,file='index.html'):
        with open(file, 'w', encoding='utf-8') as file:
            file.write(f'''
<title>Model Result</title>
<div class='model-result'>
    <h3>Result :</h3>
    <pre>{text}</pre>
</div>
''')

    @property
    def df(self):
        return self.__df


mydata = [
    3,
    ['django', 'flask', 'fastapi'],
    [('django', 19), ('flask', 2)],
    [
        ['12/9/1402', '13/9/1402'],
        ['12/9/1402', '15/9/1402'],
    ],
    [('fastapi', 0)],
    [
        ['-'],
    ],
    ['11/9/1402', '12/9/1402', '13/9/1402', '15/10/1402', '16/10/1402'],
    ['Aryan', 'Sepehri Mehr', '09123456789', 'macsepehri@gmail.com'],
    ['name', 'lastname', 'phonenumber', 'email'],
]

model = BaseModel()
model.add_array(mydata)
model.create_df()
result = model.calculate()
model.to_html(result)