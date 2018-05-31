import sys
import csv
import queue # 导入处理多进程异常包
from multiprocessing import Queue, Process # 导入多进程包
import configparser # 模块读取配置文件包
from getopt import getopt, GetoptError # 模块处理命令行参数包
from datetime import datetime

queue1 = Queue()
queue2 = Queue()

# 处理命令行参数类
class Args(object):

    def __init__(self):
        self.options = self._options()

    def _options(self):
        try:
            opts, _ = getopt(sys.argv[1:], 'hC:c:d:o:', ['help']) # 后面有 : 表示必须
        except GetoptError as e:
            print(e)
            exit()
        options = dict(opts) # 将所有参数按照 '-C': 'beijing' 做成字典存储
        if '-h' in options or '--help' in options: # 打印使用方法
            print('Usage: calculator.py -C cityname -c configfile -d userdata -o resultdata')
            exit()
        return options

    @property
    def city(self):
        return self.options.get('-C') # 城市

    @property
    def config_path(self):
        return self.options.get('-c') # 社保配置文件

    @property
    def userdata_path(self):
        return self.options.get('-d') # 用户工资文件

    @property
    def export_path(self):
        return self.options.get('-o') # 输出文件

args = Args()

# 配置文件类
class Config(object):

    def __init__(self):
        self.config = self._read_config()

    def _read_config(self):
        config = configparser.ConfigParser() # 模块读取配置文件, 按照 [DEFAULT] 分段
        config.read(args.config_path)
        if args.city.upper() in config.sections():
            return config[args.city.upper()]
        else:
            return config['DEFAULT']

    @property
    def jishu_low(self): # 低于此金额, 按此金额计算社保
        return float(self.config.get('JiShuL', int(0))) # 因返回是字符所以需要 float

    @property
    def jishu_high(self): # 高于此金额, 按此金额计算社保
        return float(self.config.get('JiShuH', int(0)))

    @property
    def shebao_rate(self): # 返回社保各基数总和
        return sum([float(self.config.get('YangLao', int(0))),
                    float(self.config.get('YiLiao', int(0))),
                    float(self.config.get('ShiYe', int(0))),
                    float(self.config.get('GongShang', int(0))),
                    float(self.config.get('ShengYu', int(0))),
                    float(self.config.get('GongJiJin', int(0)))])

config = Config()

# 用户数据类
class UserData(Process):
    # 通过继承 Process 类, 并实现 run 方法
    def __init__(self):
        self.userdata = self._read_users_data()

    def _read_users_data(self):
        with open(args.userdata_path) as f:
            for line in f.readlines():
                try:
                    user_id, income_string = line.split(',')
                    income = int(income_string)
                except ValueError as e:
                    print(e)
                    exit()
                yield (user_id, income)

    def run(self):
        for data in self.userdata:
            queue1.put(data) # 将解析出的每一行数据放到队列中

class Execute(Process):

    def calc_for_all_user(self):
        while True:
            try:
                user_id, income = queue1.get(timeout=1)
            except queue.Empty:
                return
            # 计算社保金额          
            if income > config.jishu_high:
                shebao = config.jishu_high * config.shebao_rate
            elif income < config.jishu_low:
                shebao = config.jishu_low * config.shebao_rate
            else:
                shebao = income * config.shebao_rate
            # 工资减去社保后金额
            real_income = income - shebao
            # 应纳税所得额 = 工资 - 社保 - 起征点
            ynssde = real_income - 3500
            # 计算税额
            if ynssde > 80000:
                tax = ynssde * 0.45 - 13505
            elif ynssde > 55000:
                tax = ynssde * 0.35 - 5505
            elif ynssde > 35000:
                tax = ynssde * 0.3 - 2755
            elif ynssde > 9000:
                tax = ynssde * 0.25 - 1005
            elif ynssde > 4500:
                tax = ynssde * 0.2 - 555
            elif ynssde > 1500:
                tax = ynssde * 0.1 - 105
            elif ynssde > 0:
                tax = ynssde * 0.03
            else:
                tax = 0
            shebao = '{:.2f}'.format(shebao)
            Tax = '{:.2f}'.format(tax)
            remain = '{:.2f}'.format(real_income - tax)
            data = (user_id, income, shebao, Tax, remain, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            yield data

    def run(self):
        for data in self.calc_for_all_user():
            queue2.put(data)

# 导出数据类
class Export(Process):

    def run(self):
        with open(args.export_path, 'w', newline='') as f:
            while True:
                writer = csv.writer(f)
                try:
                    item = queue2.get(timeout=1)
                except queue.Empty:
                    return
                writer.writerow(item)

if __name__ == '__main__':
    workers = [UserData(), Execute(), Export()]
    for worker in workers:
        worker.run()
