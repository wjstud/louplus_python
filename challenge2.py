# -*- coding: utf-8 -*-
from collections import namedtuple


IncomeTaxQuickLookupItem = namedtuple(
        'IncomeTaxQuickLookupItem',
        ['start_point', 'tax_rate', 'quick_subtractor']
        )

INCOME_TAX_START_POINT = 3500 # 起征点

# 社保计算比例(养老, 医疗, 失业, 工伤, 生育, 公积金)
SOCIAL_INSURANCE_MONEY_RATE = {
        'endowment_insurance': 0.08,
        'medical_insurance': 0.02,
        'unemployment_insurance': 0.005,
        'employment_injury_insurance': 0,
        'maternity_insurance': 0,
        'public_accumulation_funds': 0.06
        }

# 税率及速算扣除数对应表(应纳税额, 税率, 速算扣除数)
INCOME_TAX_QUICK_LOOKUP_TABLE = [
        IncomeTaxQuickLookupItem(80000, 0.45, 13505),
        IncomeTaxQuickLookupItem(55000, 0.35, 5505),
        IncomeTaxQuickLookupItem(35000, 0.3, 2755),
        IncomeTaxQuickLookupItem(9000, 0.25, 1005),
        IncomeTaxQuickLookupItem(4500, 0.2, 555),
        IncomeTaxQuickLookupItem(1500, 0.1, 105),
        IncomeTaxQuickLookupItem(0, 0.03, 0)
        ]

def calc_income_tax(income):
    '''  计算税额：应纳税所得额 = 工资金额 － 各项社会保险费 - 起征点(3500元)
                   应纳税额 = 应纳税所得额 × 税率 － 速算扣除数
         计算工资：到手工资金额 = 工资金额 - 社保金额 - 应纳税额 
    '''

    social_insurance_money = income * sum(SOCIAL_INSURANCE_MONEY_RATE.values())
    real_income = income - social_insurance_money
    taxable_part = real_income - INCOME_TAX_START_POINT
    
    if taxable_part <= 0:
        return '0.00', '{:.2f}'.format(real_income)

    for item in INCOME_TAX_QUICK_LOOKUP_TABLE:
        if taxable_part > item.start_point:
            tax = taxable_part * item.tax_rate - item.quick_subtractor
            return '{:.2f}'.format(tax), '{:.2f}'.format(real_income - tax)

def main():
    ''' 验证参数 + 支持多个参数，格式为：“工号：工资” '''
    
    import sys
    
    for item in sys.argv[1:]:
        try:
            user_id, user_income = item.split(':')
            income = int(user_income)
            _, remain = calc_income_tax(income)
            print('{}:{}'.format(user_id, remain))
        except ValueError as e:
            print(e)

if __name__ == '__main__':
    main()
