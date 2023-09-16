# Generated by Django 3.2.6 on 2022-08-21 15:24

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('name', models.CharField(blank=True, max_length=20, null=True, verbose_name='姓名')),
                ('phone', models.CharField(blank=True, max_length=11, null=True, unique=True, verbose_name='手機號碼')),
                ('avatar', models.CharField(blank=True, default='/media/default/avatar.png', max_length=100, null=True, verbose_name='頭像')),
            ],
            options={
                'verbose_name': '用戶信息',
                'verbose_name_plural': '用戶信息',
                'ordering': ['id'],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Dict',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, help_text='創建時間', verbose_name='創建時間')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='修改時間', verbose_name='修改時間')),
                ('is_deleted', models.BooleanField(default=False, help_text='刪除標記', verbose_name='刪除標記')),
                ('name', models.CharField(max_length=60, verbose_name='名稱')),
                ('code', models.CharField(blank=True, max_length=30, null=True, verbose_name='編號')),
                ('description', models.TextField(blank=True, null=True, verbose_name='描述')),
                ('sort', models.IntegerField(default=1, verbose_name='排序')),
                ('is_used', models.BooleanField(default=True, verbose_name='是否有效')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='system.dict', verbose_name='父')),
            ],
            options={
                'verbose_name': '字典',
                'verbose_name_plural': '字典',
            },
        ),
        migrations.CreateModel(
            name='DictType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, help_text='創建時間', verbose_name='創建時間')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='修改時間', verbose_name='修改時間')),
                ('is_deleted', models.BooleanField(default=False, help_text='刪除標記', verbose_name='刪除標記')),
                ('name', models.CharField(max_length=30, verbose_name='名稱')),
                ('code', models.CharField(max_length=30, unique=True, verbose_name='編號')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='system.dicttype', verbose_name='父')),
            ],
            options={
                'verbose_name': '字典類型',
                'verbose_name_plural': '字典類型',
            },
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, help_text='創建時間', verbose_name='創建時間')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='修改時間', verbose_name='修改時間')),
                ('is_deleted', models.BooleanField(default=False, help_text='刪除標記', verbose_name='刪除標記')),
                ('name', models.CharField(max_length=60, verbose_name='名稱')),
                ('type', models.CharField(choices=[('公司', '公司'), ('部門', '部門')], default='部門', max_length=20, verbose_name='類型')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='system.organization', verbose_name='父')),
            ],
            options={
                'verbose_name': '組織架構',
                'verbose_name_plural': '組織架構',
            },
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, help_text='創建時間', verbose_name='創建時間')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='修改時間', verbose_name='修改時間')),
                ('is_deleted', models.BooleanField(default=False, help_text='刪除標記', verbose_name='刪除標記')),
                ('name', models.CharField(max_length=30, verbose_name='名稱')),
                ('type', models.CharField(choices=[('目錄', '目錄'), ('菜單', '菜單'), ('介面', '介面')], default='介面', max_length=20, verbose_name='類型')),
                ('is_frame', models.BooleanField(default=False, verbose_name='外部連接')),
                ('sort', models.IntegerField(default=1, verbose_name='排序標記')),
                ('method', models.CharField(blank=True, max_length=50, null=True, verbose_name='方法/代號')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='system.permission', verbose_name='父')),
            ],
            options={
                'verbose_name': '功能權限表',
                'verbose_name_plural': '功能權限表',
                'ordering': ['sort'],
            },
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, help_text='創建時間', verbose_name='創建時間')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='修改時間', verbose_name='修改時間')),
                ('is_deleted', models.BooleanField(default=False, help_text='刪除標記', verbose_name='刪除標記')),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='名稱')),
                ('description', models.CharField(blank=True, max_length=50, null=True, verbose_name='描述')),
            ],
            options={
                'verbose_name': '職位/崗位',
                'verbose_name_plural': '職位/崗位',
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, help_text='創建時間', verbose_name='創建時間')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='修改時間', verbose_name='修改時間')),
                ('is_deleted', models.BooleanField(default=False, help_text='刪除標記', verbose_name='刪除標記')),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='角色')),
                ('datas', models.CharField(choices=[('全部', '全部'), ('自定義', '自定義'), ('同級及以下', '同級及以下'), ('本級及以下', '本級及以下'), ('本級', '本級'), ('僅本人', '僅本人')], default='本級及以下', max_length=50, verbose_name='數據權限')),
                ('description', models.CharField(blank=True, max_length=50, null=True, verbose_name='描述')),
                ('depts', models.ManyToManyField(blank=True, related_name='roles', to='system.Organization', verbose_name='權限範圍')),
                ('perms', models.ManyToManyField(blank=True, to='system.Permission', verbose_name='功能權限')),
            ],
            options={
                'verbose_name': '角色',
                'verbose_name_plural': '角色',
            },
        ),
        migrations.CreateModel(
            name='HistoricalDict',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, help_text='創建時間', verbose_name='創建時間')),
                ('update_time', models.DateTimeField(blank=True, editable=False, help_text='修改時間', verbose_name='修改時間')),
                ('is_deleted', models.BooleanField(default=False, help_text='刪除標記', verbose_name='刪除標記')),
                ('name', models.CharField(max_length=60, verbose_name='名稱')),
                ('code', models.CharField(blank=True, max_length=30, null=True, verbose_name='編號')),
                ('description', models.TextField(blank=True, null=True, verbose_name='描述')),
                ('sort', models.IntegerField(default=1, verbose_name='排序')),
                ('is_used', models.BooleanField(default=True, verbose_name='是否有效')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='system.dict', verbose_name='父')),
                ('type', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='system.dicttype', verbose_name='類型')),
            ],
            options={
                'verbose_name': 'historical 字典',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, help_text='創建時間', verbose_name='創建時間')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='修改時間', verbose_name='修改時間')),
                ('is_deleted', models.BooleanField(default=False, help_text='刪除標記', verbose_name='刪除標記')),
                ('name', models.CharField(blank=True, max_length=100, null=True, verbose_name='名稱')),
                ('size', models.IntegerField(blank=True, default=1, null=True, verbose_name='文件大小')),
                ('file', models.FileField(upload_to='%Y/%m/%d/', verbose_name='文件')),
                ('mime', models.CharField(blank=True, max_length=120, null=True, verbose_name='文件格式')),
                ('type', models.CharField(choices=[('文檔', '文檔'), ('視頻', '視頻'), ('音頻', '音頻'), ('圖片', '圖片'), ('其它', '其它')], default='文檔', max_length=50, verbose_name='文件類型')),
                ('path', models.CharField(blank=True, max_length=200, null=True, verbose_name='地址')),
                ('create_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='file_create_by', to=settings.AUTH_USER_MODEL, verbose_name='創建人')),
                ('update_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='file_update_by', to=settings.AUTH_USER_MODEL, verbose_name='最後編輯人')),
            ],
            options={
                'verbose_name': '文件庫',
                'verbose_name_plural': '文件庫',
            },
        ),
        migrations.AddField(
            model_name='dict',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.dicttype', verbose_name='類型'),
        ),
        migrations.AddField(
            model_name='user',
            name='dept',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='system.organization', verbose_name='組織'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='position',
            field=models.ManyToManyField(blank=True, to='system.Position', verbose_name='崗位'),
        ),
        migrations.AddField(
            model_name='user',
            name='roles',
            field=models.ManyToManyField(blank=True, to='system.Role', verbose_name='角色'),
        ),
        migrations.AddField(
            model_name='user',
            name='superior',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='上級主管'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.AlterUniqueTogether(
            name='dict',
            unique_together={('name', 'is_used', 'type')},
        ),
    ]
