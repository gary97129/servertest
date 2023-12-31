# Generated by Django 3.2 on 2023-03-05 06:51

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Clinic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, help_text='創建時間', verbose_name='創建時間')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='修改時間', verbose_name='修改時間')),
                ('is_deleted', models.BooleanField(default=False, help_text='刪除標記', verbose_name='刪除標記')),
                ('name', models.CharField(max_length=32, verbose_name='診所名稱')),
                ('title_name', models.CharField(max_length=32, verbose_name='抬頭')),
                ('Unified_compilation', models.CharField(max_length=32, verbose_name='統一編號')),
                ('phone_number', models.CharField(max_length=32, null=True, unique=True, verbose_name='電話')),
                ('address', models.CharField(max_length=100, null=True, unique=True, verbose_name='地址')),
                ('payment_method', models.CharField(max_length=32, null=True, verbose_name='收款方式')),
                ('roles', models.ManyToManyField(blank=True, to='system.Role', verbose_name='角色')),
            ],
            options={
                'verbose_name': '診所',
                'verbose_name_plural': '診所',
            },
        ),
        migrations.CreateModel(
            name='manufacturers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, help_text='創建時間', verbose_name='創建時間')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='修改時間', verbose_name='修改時間')),
                ('is_deleted', models.BooleanField(default=False, help_text='刪除標記', verbose_name='刪除標記')),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='名稱')),
                ('parentId', models.IntegerField(blank=True, verbose_name='樹狀')),
                ('long', models.CharField(max_length=50, null=True, verbose_name='長度')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, help_text='創建時間', verbose_name='創建時間')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='修改時間', verbose_name='修改時間')),
                ('is_deleted', models.BooleanField(default=False, help_text='刪除標記', verbose_name='刪除標記')),
                ('name', models.CharField(max_length=32, verbose_name='病患名稱')),
                ('gender', models.CharField(max_length=32, verbose_name='性別')),
                ('date_birth', models.CharField(max_length=32, verbose_name='出生年月日')),
                ('Medical_record_number', models.CharField(max_length=32, null=True, unique=True, verbose_name='病歷號')),
                ('Drug_allergy', models.CharField(max_length=32, null=True, verbose_name='藥物過敏')),
                ('phone', models.CharField(max_length=32, null=True, verbose_name='電話')),
                ('remark', models.CharField(max_length=64, null=True, verbose_name='備註')),
            ],
            options={
                'verbose_name': '病患名稱',
                'verbose_name_plural': '病患名稱',
            },
        ),
        migrations.AlterModelOptions(
            name='historicaldict',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical 字典', 'verbose_name_plural': 'historical 字典'},
        ),
        migrations.RemoveField(
            model_name='user',
            name='dept',
        ),
        migrations.RemoveField(
            model_name='user',
            name='position',
        ),
        migrations.RemoveField(
            model_name='user',
            name='superior',
        ),
        migrations.AddField(
            model_name='user',
            name='Unified_compilation',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='統一編號'),
        ),
        migrations.AddField(
            model_name='user',
            name='address',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True, verbose_name='地址'),
        ),
        migrations.AddField(
            model_name='user',
            name='parentId',
            field=models.CharField(blank=True, default=0, max_length=32, verbose_name='上下級'),
        ),
        migrations.AddField(
            model_name='user',
            name='payment_method',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='收款方式'),
        ),
        migrations.AddField(
            model_name='user',
            name='title_name',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='抬頭'),
        ),
        migrations.AddField(
            model_name='user',
            name='type',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='職務類型'),
        ),
        migrations.AlterField(
            model_name='dicttype',
            name='code',
            field=models.CharField(max_length=30, unique=True, verbose_name='代號'),
        ),
        migrations.AlterField(
            model_name='historicaldict',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='permission',
            name='is_frame',
            field=models.BooleanField(default=False, verbose_name='外部鏈接'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='電子郵件'),
        ),
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='使用者名稱'),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, help_text='創建時間', verbose_name='創建時間')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='修改時間', verbose_name='修改時間')),
                ('is_deleted', models.BooleanField(default=False, help_text='刪除標記', verbose_name='刪除標記')),
                ('order_number', models.CharField(max_length=32, verbose_name='訂單號')),
                ('clinic', models.CharField(max_length=32, null=True, verbose_name='診所')),
                ('docter', models.CharField(max_length=32, verbose_name='醫師')),
                ('patient', models.CharField(max_length=32, null=True, verbose_name='病患')),
                ('order_method', models.CharField(max_length=32, null=True, verbose_name='入單方式')),
                ('tooth_position', models.CharField(max_length=32, null=True, verbose_name='齒位')),
                ('Implant_brand', models.TextField(max_length=32, null=True, verbose_name='植體廠牌')),
                ('Implant_size', models.CharField(max_length=32, null=True, verbose_name='植體尺寸')),
                ('equipment_rental', models.CharField(max_length=32, null=True, verbose_name='租借器械')),
                ('metal_scattering', models.CharField(max_length=32, null=True, verbose_name='CBCT 是否有金屬散射')),
                ('surgical_method', models.CharField(max_length=32, null=True, verbose_name='手術方式')),
                ('surgery_date', models.CharField(max_length=32, null=True, verbose_name='手術日期')),
                ('remark', models.CharField(blank=True, max_length=64, null=True, verbose_name='備註')),
                ('avatar_3d_palate', models.CharField(blank=True, max_length=100, null=True, verbose_name='3D上顎模型')),
                ('avatar_3d_palate_Scanbody', models.CharField(blank=True, max_length=100, null=True, verbose_name='3D上顎模型Scanbody')),
                ('avatar_3d_palate_Denture', models.CharField(blank=True, max_length=100, null=True, verbose_name='3D上顎模型Denture')),
                ('avatar_3d_palate_RayTray', models.CharField(blank=True, max_length=100, null=True, verbose_name='3D上顎模型Ray Tray')),
                ('avatar_3d_palate_Bite', models.CharField(blank=True, max_length=100, null=True, verbose_name='3D上顎模型Bite')),
                ('avatar_3d_jaw', models.CharField(blank=True, max_length=100, null=True, verbose_name='3D下顎模型')),
                ('avatar_3d_jaw_Scanbody', models.CharField(blank=True, max_length=100, null=True, verbose_name='3D下顎模型Scanbody')),
                ('avatar_3d_jaw_Denture', models.CharField(blank=True, max_length=100, null=True, verbose_name='3D下顎模型Denture')),
                ('avatar_3d_jaw_RayTray', models.CharField(blank=True, max_length=100, null=True, verbose_name='3D下顎模型Ray Tray')),
                ('avatar_3d_jaw_Bite', models.CharField(blank=True, max_length=100, null=True, verbose_name='3D下顎模型Bite')),
                ('avatar_image1', models.CharField(blank=True, max_length=100, null=True, verbose_name='病患照片1')),
                ('avatar_image2', models.CharField(blank=True, max_length=100, null=True, verbose_name='病患照片2')),
                ('avatar_image3', models.CharField(blank=True, max_length=100, null=True, verbose_name='病患照片3')),
                ('avatar_image4', models.CharField(blank=True, max_length=100, null=True, verbose_name='病患照片4')),
                ('avatar_image5', models.CharField(blank=True, max_length=100, null=True, verbose_name='病患照片5')),
                ('avatar_image6', models.CharField(blank=True, max_length=100, null=True, verbose_name='病患照片6')),
                ('avatar_image7', models.CharField(blank=True, max_length=100, null=True, verbose_name='病患照片7')),
                ('avatar_image8', models.CharField(blank=True, max_length=100, null=True, verbose_name='病患照片8')),
                ('avatar_image9', models.CharField(blank=True, max_length=100, null=True, verbose_name='病患照片9')),
                ('avatar_project', models.CharField(blank=True, max_length=100, null=True, verbose_name='專案')),
                ('avatar_CT', models.CharField(blank=True, max_length=100, null=True, verbose_name='CT')),
                ('Order_Status', models.IntegerField(blank=True, null=True, verbose_name='訂單進度')),
                ('action_required', models.CharField(blank=True, max_length=32, null=True, verbose_name='接受訂單')),
                ('design', models.CharField(blank=True, max_length=100, null=True, verbose_name='設計師設計檔')),
                ('patients', models.ManyToManyField(blank=True, to='system.Patient', verbose_name='病患名稱')),
            ],
            options={
                'verbose_name': '訂單資訊',
                'verbose_name_plural': '訂單資訊',
            },
        ),
        migrations.CreateModel(
            name='Laboratories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, help_text='創建時間', verbose_name='創建時間')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='修改時間', verbose_name='修改時間')),
                ('is_deleted', models.BooleanField(default=False, help_text='刪除標記', verbose_name='刪除標記')),
                ('name', models.CharField(max_length=32, verbose_name='技工所名稱')),
                ('title_name', models.CharField(max_length=32, verbose_name='抬頭')),
                ('Unified_compilation', models.CharField(max_length=32, verbose_name='統一編號')),
                ('phone_number', models.CharField(max_length=32, null=True, unique=True, verbose_name='電話')),
                ('address', models.CharField(max_length=100, null=True, unique=True, verbose_name='地址')),
                ('payment_method', models.CharField(max_length=32, null=True, verbose_name='收款方式')),
                ('roles', models.ManyToManyField(blank=True, to='system.Role', verbose_name='角色')),
            ],
            options={
                'verbose_name': '技工所',
                'verbose_name_plural': '技工所',
            },
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, help_text='創建時間', verbose_name='創建時間')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='修改時間', verbose_name='修改時間')),
                ('is_deleted', models.BooleanField(default=False, help_text='刪除標記', verbose_name='刪除標記')),
                ('name', models.CharField(max_length=32, verbose_name='醫師名稱')),
                ('email', models.CharField(max_length=32, null=True, verbose_name='電子郵件')),
                ('phone_number', models.CharField(max_length=32, null=True, unique=True, verbose_name='手機號碼')),
                ('type', models.CharField(max_length=100, verbose_name='類型')),
                ('payment_method', models.CharField(max_length=32, null=True, verbose_name='入單方式')),
                ('clinic', models.ManyToManyField(blank=True, to='system.Clinic', verbose_name='診所')),
                ('roles', models.ManyToManyField(blank=True, to='system.Role', verbose_name='角色')),
            ],
            options={
                'verbose_name': '醫師',
                'verbose_name_plural': '醫師',
            },
        ),
    ]
