# -*- coding: utf-8 -*-
import sys, csv
from collections import namedtuple


IncomeTaxQuickLookupItem = namedtuple(
        'IncomeTaxQuickLookupItem',
        ['start_point', 'tax_rate', 'quick_subtractor']
        )

INCOME_TAX_START_POINT = 3500 # 起征点

# 税率及速算扣除数对应表(应纳税所得额, 税率, 速算扣除数)
INCOME_TAX_QUICK_LOOKUP_TABLE = [
        IncomeTaxQuickLookupItem(80000, 0.45, 13505),
        IncomeTaxQuickLookupItem(55000, 0.35, 5505),
        IncomeTaxQuickLookupItem(35000, 0.3, 2755),
        IncomeTaxQuickLookupItem(9000, 0.25, 1005),
        IncomeTaxQuickLookupItem(4500, 0.2, 555),
        IncomeTaxQuickLookupItem(1500, 0.1, 105),
        IncomeTaxQuickLookupItem(0, 0.03, 0)
        ]

class Args(object):
    
    # 初始化的时候读取命令行所有的参数到 self.args 列表
    def __init__(self):
        self.args = sys.argv[1:]

    #  用来获取参数 -c/-d/-o 后面的值
    def _value_after_option(self, option):
        try:
            # 首先获得参数 -c/-d/-o 在列表 sys.args 中的索引值
            index = self.args.index(option)
            # -c/-d/-o 索引值 +1 就是其后面的值
            return self.args[index + 1]
        except (ValueError, IndexError) as e:
            print(e)
            exit()

    @property
    def config_path(self):
        return self._value_after_option('-c')
    
    @property
    def userdata_path(self):
        return self._value_after_option('-d')

    @property
    def export_path(self):
        return self._value_after_option('-o')

args = Args()

class Config(object):

    # 初始化的时候调用内部接口 self._read_config() 读取配置文件中的所有内容
    def __init__(self):
        self.config = self._read_config()

    def _read_config(self):
        ''' 内部函数, 读取配置文件内容并保存为配置字典 '''
        config_path = args.config_path
        config = {}
        with open(config_path) as f:
            for line in f.readlines():
                key, value = line.strip().split(' = ')
                try:
                    config[key.strip()] = float(value.strip())
                except ValueError as e:
                    print(e)
                    exit()
        return config

    def _get_config(self, key):
        ''' 内部函数, 获取配置的值 '''
        try:
            return self.config[key]
        except KeyError as e:
            print(e)
            exit()

    @property
    def social_insurance_baseline_low(self):
        return self._get_config('JiShuL')

    @property
    def social_insurance_baseline_high(self):
        return self._get_config('JiShuH')

    @property
    def social_insurance_total_rate(self):
        return sum([
            self._get_config('YangLao'),
            self._get_config('YiLiao'),
            self._get_config('ShiYe'),
            self._get_config('GongShang'),
            self._get_config('ShengYu'),
            self._get_config('GongJiJin')
            ])

config = Config()

class UserData(object):
    
    def __init__(self):
        self.userdata = self._read_userdata()

    def _read_userdata(self):
        userdata_path = args.userdata_path
        userdata = []
        with open(userdata_path) as f:
            for line in f.readlines():
                user_id, user_income = line.strip().split(',')
                try:
                    income = int(user_income)
                    userdata.append((user_id, income))
                except ValueError as e:
                    print(e)
                    exit()
        return userdata

    def __iter__(self):
        ''' 使 UserData 对象成为可迭代对象'''
        return iter(self.userdata)

class IncomeTaxCalculator(object):
    
    # 初始化的时候传人UserData 对象, 传进来后赋值给self.userdata
    def __init__(self, userdata):
        self.userdata = userdata

    @staticmethod
    def calc_social_insurance_money(income):
        ''' 静态方法: 运行时不需要实例参与, 完全可以单独实现, 仅仅是因为与工资计算类有一些关联才放进类中
            计算需要缴纳的社保金额, 传人的参数为工资金额 '''
        if income < config.social_insurance_baseline_low:
            return config.social_insurance_baseline_low * \
                    config.social_insurance_total_rate
        if income > config.social_insurance_baseline_high:
            return config.social_insurance_baseline_high * \
                    config.social_insurance_total_rate
        return income * config.social_insurance_total_rate

    @classmethod
    def calc_income_tax(cls, income):
        ''' 类方法: 不需要实例化类也能调用, 需要传人代表类的 cls
            计算税额：应纳税所得额 = 工资金额 － 各项社会保险费 - 起征点(3500元)
                   应纳税额 = 应纳税所得额 × 税率 － 速算扣除数
            计算工资：到手工资金额 = 工资金额 - 社保金额 - 应纳税额 
    '''
        social_insurance_money = cls.calc_social_insurance_money(income)
        real_income = income - social_insurance_money
        taxable_part = real_income - INCOME_TAX_START_POINT
    
        if taxable_part <= 0:
            return '0.00', '{:.2f}'.format(real_income)

        for item in INCOME_TAX_QUICK_LOOKUP_TABLE:
            if taxable_part > item.start_point:
                tax = taxable_part * item.tax_rate - item.quick_subtractor
                return '{:.2f}'.format(tax), '{:.2f}'.format(real_income - tax)

    def calc_all_user(self):
        ''' 计算所有用户工资 '''
        result = []
        for user_id, user_income in self.userdata:
            data = [user_id, user_income]
            social_insurance_money = '{:.2f}'.format(self.calc_social_insurance_money(user_income))
            tax, remain = self.calc_income_tax(user_income)
            data += [social_insurance_money, tax, remain]
            result.append(data)
        return result

    def export(self, file_type='csv'):
        ''' 导出工资数据, 传人的参数用来指定导出文件的类型, 此处用于未来扩展 '''
        result = self.calc_all_user()
        with open(args.export_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(result)

if __name__ == '__main__':
    calculator = IncomeTaxCalculator(UserData())
    calculator.export()
