
from django.db import models
from django.utils.safestring import mark_safe

# 用户数据库
class User(models.Model):
    id = models.AutoField('id',primary_key=True)
    username = models.CharField(verbose_name="姓名", max_length=22, default='')
    password = models.CharField(verbose_name="密码", max_length=32, default='')
    phone = models.CharField(verbose_name="手机号", max_length=11, default='')
    email = models.CharField(verbose_name="邮箱", max_length=22, default='')
    time = models.DateField(verbose_name="创建时间", auto_now_add=True)
    avatar = models.FileField(verbose_name="头像", default='user/avatar/default.gif', upload_to="user/avatar/")
    def admin_sample(self):
        return mark_safe('<img src="/media/%s" height="60" width="60" />' % (self.avatar,))
    admin_sample.short_description = '用户头像'
    admin_sample.allow_tags = True
    def __str__(self):
        return self.username
    class Meta:
        db_table = 'User'
        verbose_name_plural = '用户管理'
# 新房房源
class House(models.Model):
    title = models.CharField(max_length=100, verbose_name='房源名称')
    type = models.CharField(max_length= 100,verbose_name='房源类型')
    building=models.CharField(max_length=100,verbose_name='房源地址')
    city=models.CharField(max_length=100,verbose_name='行政区')
    street=models.CharField(max_length=300,verbose_name='街道')
    area=models.IntegerField(verbose_name='房源面积')
    direct=models.CharField(max_length=100,verbose_name='朝向')
    price=models.IntegerField(verbose_name='价钱')
    link=models.CharField(max_length=100, verbose_name='链接详情')
    tag = models.CharField(max_length=30,verbose_name='标签',default='')
    img = models.CharField(max_length=300,verbose_name='图片链接',default="https://image1.ljcdn.com/110000-inspection/b588e9e8-92a3-469f-a216-a01b98843a50.jpg!m_fill,w_250,h_182,l_flianjia_black,o_auto")
    class Meta:
        db_table = "house"
    class Meta:
        db_table = 'House'
        verbose_name_plural = '房源管理'

class Histroy(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    house = models.ForeignKey(House,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    count = models.IntegerField("点击次数",default=1)
    class Meta:
        db_table = "histroy"
    class Meta:
        db_table = 'History'
        verbose_name_plural = '房源收藏'
