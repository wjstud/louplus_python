# -*- coding: utf-8 -*-
from collections import namedtuple


IncomeTaxQuickLookupItem = namedtuple(
        'IncomeTaxQuickLookupItem',
        ['start_point', 'tax_rate', 'quick_subtractor']
        )

INCOME_TAX_START_POINT = 3500 # 起征点
SOCIAL_SECUROTY = 0 # 社保费用

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
    '''

    taxable_part = income - SOCIAL_SECUROTY - INCOME_TAX_START_POINT
    
    if taxable_part <= 0:
        return '0.00'

    for item in INCOME_TAX_QUICK_LOOKUP_TABLE:
        if taxable_part > item.start_point:
            tax = taxable_part * item.tax_rate - item.quick_subtractor
            return '{:.2f}'.format(tax) # 保留2位小数

def main():
    ''' 验证参数 '''
    
    import sys
    
    if len(sys.argv) == 2:
        try:
            income = int(sys.argv[1])
            print(calc_income_tax(income))
        except ValueError as e:
            print(e)
            exit()
    else:
        print('Parameter len(sys.argv) Error')
        exit()

if __name__ == '__main__':
    main()
