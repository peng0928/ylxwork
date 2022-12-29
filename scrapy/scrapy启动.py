import os, shutil, time

def scrapy_file(area, projectName):
    os.makedirs(f'./{area}', exist_ok=True)
    os.chdir(os.path.join(os.getcwd(), area))

    spider = 'spider'
    web = 'demo.com'
    os.system('scrapy startproject '+ projectName)
    time.sleep(2)
    os.chdir(os.path.join(os.getcwd(), projectName))
    os.system("scrapy genspider " + spider + " " + web)

def copy_file(area, projectName):
    shutil.copyfile('../../work_file/python-tools/pymysql_connection.py', f'./{area}/{projectName}/{projectName}/pymysql_connection.py')
    shutil.copyfile('../../work_file/python-tools/data_process.py', f'./{area}/{projectName}/{projectName}/data_process.py')
    shutil.copyfile('../../work_file/python-tools/redis_conn.py', f'./{area}/{projectName}/{projectName}/redis_conn.py')
    shutil.copyfile('../../work_file/python-tools/useragent.py', f'./{area}/{projectName}/{projectName}/useragent.py')


if __name__ == '__main__':
    area = 'test'
    projectName = 'test01'
    projectName = projectName.replace('.', '_').replace('-', '_')
    scrapy_file(area, projectName)
    print(projectName)