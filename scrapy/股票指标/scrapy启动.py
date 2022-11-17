import os, shutil, time


def scrapy_file(area, projectName):
    os.makedirs(f'./{area}', exist_ok=True)
    os.chdir(os.path.join(os.getcwd(), area))

    spider = 'spider'
    web = 'demo.com'
    os.system('scrapy startproject ' + projectName)
    time.sleep(2)
    os.chdir(os.path.join(os.getcwd(), projectName))
    os.system("scrapy genspider " + spider + " " + web)


if __name__ == '__main__':
    area = '郑州商品交易所'
    projectName = 'www.czce.com.cn'
    projectName = projectName.replace('.', '_').replace('-', '_')
    scrapy_file(area, projectName)
    print(projectName)
