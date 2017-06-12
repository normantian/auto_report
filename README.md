# 自动报表生成python小程序
****
  *本程序的目的是通过python小程序自动化办公。将数据库报表自动生成并发送邮件给你的领导及相关人员。有了这个小程序，无论日报、周报、月报，妈妈再也不用担心你漏发而丢掉工作了:-)*
  
## 1.环境准备
首先，你需要安装python环境，本程序开发环境是python2.7(mac自带python2)，然后需要执行命令,安装依赖包：

`pip install records`

`pip install MySQL-python`   
*ps:我的目标数据库是mysql，如不是mysql可以自行baidu安装相应的数据库驱动包*

## 2.如何使用
我们仅仅需要修改两个配置文件：

1. 修改sql/query.sql文件，里面就一条select的语句，即你要生成报表的sql语句。
2. 修改config/config.conf
	
		[db]
    	url = mysql://ip:port/db_name?user=user_name&passwd=dbpassword&charset=utf8

		[email]
	
		smtp = smtp.xxx.com
	
		email_address = your_email
	
		password = your_email_password
	
		to = 收件人地址，以英文逗号分隔
	
		cc = 抄送人地址，以英文逗号分隔
	
		title = 邮件标题
	
		content = <html><body>尊敬的XXX，<br /> 请您查收附件</body><html>

3. 运行下`python auto_report.py` 测试一下是否运行成功，并可以发送邮件。 report目录下会生成一个excel文件，可以验证sql的正确性。
4. 如第三步没有问题，可以配置定时任务，仅以mac os举例:

	- 终端运行 `sudo crontab -e` 运行后打开一个vim。
	- 编辑一行 `分(0-59) 时(0-24) 日(1-31) 月(1-12) 周（0-6,0或7代表周日） {python所在目录}/python /{文件所在目录}/auto_report.py`
	- 样例中，30 9 * * 1 代表每周一早上九点半执行
	- 退出vim 保存文件。sudo crontab -l 显示刚刚配置的定时任务
	
5. 可以验证定时任务 配置一行 `* * * * * echo "hello" >> ~/1.txt` 每分钟执行一个hello并输出到用户目录下的1.txt文本中。然后过几分钟查看该文件是否有内容。
6. 如果定时任务不执行，可以执行`sudo touch /etc/crontab`
7. 如果需要删除任务可以 `sudo crontab -e` 删除配置的行即可

# 大功告成！年底升职加薪！good luck! 


