import sys
import csv
import queue
from multiprocessing import Queue, Process


queue1 = Queue()
queue2 = Queue()

# 处理命令行参数类
class Args(object):

    def __init__(self):
        self.args = sys.argv[1:]

    def _value_option(self, option):
        try:
            index = self.args.index(option) # 获取参数的索引位置
            return self.args[index + 1] # 返回参数后面的配置文件
        except (ValueError, IndexError) as e:
            print(e)
            exit()

    @property
    def config_path(self):
        return self._value_option('-c') # 社保配置文件

    @property
    def userdata_path(self):
        return self._value_option('-d') # 用户工资文件

    @property
    def export_path(self):
        return self._value_option('-o') # 输出文件

args = Args()

# 配置文件类
class Config(object):

    def __init__(self):
        self.config = self._read_config()

    def _read_config(self):
        config = {}
        with open(args.config_path) as f:
            for line in f.readlines():
                try:
                    key, value = line.split('=')
                    config[key.strip()] = float(value.strip())
                except ValueError as e:
                    print(e)
                    exit()
        return config

    @property
    def jishu_low(self): # 低于此金额, 按此金额计算社保
        return self._read_config().get('JiShuL', int(0))

    @property
    def jishu_high(self): # 高于此金额, 按此金额计算社保
        return self._read_config().get('JiShuH', int(0))

    @property
    def shebao_rate(self): # 返回社保各基数总和
        return sum([self._read_config().get('YangLao', int(0)),
                    self._read_config().get('YiLiao', int(0)),
                    self._read_config().get('ShiYe', int(0)),
                    self._read_config().get('GongShang', int(0)),
                    self._read_config().get('ShengYu', int(0)),
                    self._read_config().get('GongJiJin', int(0))])

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
            data = (user_id, income, shebao, Tax, remain)
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
