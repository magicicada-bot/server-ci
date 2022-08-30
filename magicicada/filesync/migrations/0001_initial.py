# Generated by Django 1.9 on 2016-05-02 00:13


import magicicada.filesync.managers
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0007_alter_validators_add_error_messages'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShareVolumeDelta',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                (
                    'name',
                    models.TextField(
                        validators=[magicicada.filesync.managers.validate_name]
                    ),
                ),
                (
                    'kind',
                    models.CharField(
                        choices=[
                            ('File', 'File'),
                            ('Directory', 'Directory'),
                            ('Symlink', 'Symlink'),
                        ],
                        max_length=128,
                    ),
                ),
                (
                    'when_created',
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    'when_last_modified',
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    'status',
                    models.CharField(
                        choices=[('Dead', 'Dead'), ('Live', 'Live')],
                        default='Live',
                        max_length=128,
                    ),
                ),
                ('path', models.TextField()),
                ('mimetype', models.TextField()),
                ('public_uuid', models.UUIDField(null=True, unique=True)),
                ('generation', models.BigIntegerField(default=0)),
                ('generation_created', models.BigIntegerField(default=0)),
                ('share_id', models.UUIDField()),
            ],
            options={
                'db_table': 'share_delta_view',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='StorageUser',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'password',
                    models.CharField(max_length=128, verbose_name='password'),
                ),
                (
                    'last_login',
                    models.DateTimeField(
                        blank=True, null=True, verbose_name='last login'
                    ),
                ),
                (
                    'is_superuser',
                    models.BooleanField(
                        default=False,
                        help_text='Designates that this user has all permissions without explicitly assigning them.',
                        verbose_name='superuser status',
                    ),
                ),
                (
                    'username',
                    models.CharField(
                        error_messages={
                            'unique': 'A user with that username already exists.'
                        },
                        help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.',
                        max_length=30,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                '^[\\w.@+-]+$',
                                'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.',
                            )
                        ],
                        verbose_name='username',
                    ),
                ),
                (
                    'first_name',
                    models.CharField(
                        blank=True, max_length=30, verbose_name='first name'
                    ),
                ),
                (
                    'last_name',
                    models.CharField(
                        blank=True, max_length=30, verbose_name='last name'
                    ),
                ),
                (
                    'email',
                    models.EmailField(
                        blank=True,
                        max_length=254,
                        verbose_name='email address',
                    ),
                ),
                (
                    'is_staff',
                    models.BooleanField(
                        default=False,
                        help_text='Designates whether the user can log into this admin site.',
                        verbose_name='staff status',
                    ),
                ),
                (
                    'is_active',
                    models.BooleanField(
                        default=True,
                        help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.',
                        verbose_name='active',
                    ),
                ),
                (
                    'date_joined',
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name='date joined',
                    ),
                ),
                ('email_notification', models.BooleanField(default=False)),
                (
                    'active_from',
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ('active_until', models.DateTimeField(blank=True, null=True)),
                ('locked', models.BooleanField(default=False)),
                (
                    'max_storage_bytes',
                    models.BigIntegerField(default=21990232555520),
                ),
                ('used_storage_bytes', models.BigIntegerField(default=0)),
                (
                    'groups',
                    models.ManyToManyField(
                        blank=True,
                        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
                        related_name='user_set',
                        related_query_name='user',
                        to='auth.Group',
                        verbose_name='groups',
                    ),
                ),
                (
                    'user_permissions',
                    models.ManyToManyField(
                        blank=True,
                        help_text='Specific permissions for this user.',
                        related_name='user_set',
                        related_query_name='user',
                        to='auth.Permission',
                        verbose_name='user permissions',
                    ),
                ),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', magicicada.filesync.managers.StorageUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ContentBlob',
            fields=[
                (
                    'hash',
                    models.BinaryField(primary_key=True, serialize=False),
                ),
                ('crc32', models.BigIntegerField(default=0)),
                ('size', models.BigIntegerField(default=0)),
                ('storage_key', models.UUIDField(null=True)),
                ('deflated_size', models.BigIntegerField(null=True)),
                ('content', models.BinaryField(null=True)),
                (
                    'status',
                    models.CharField(
                        choices=[('Dead', 'Dead'), ('Live', 'Live')],
                        default='Live',
                        max_length=128,
                    ),
                ),
                ('magic_hash', models.BinaryField(null=True)),
                (
                    'when_created',
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
            ],
        ),
        migrations.CreateModel(
            name='Download',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                ('file_path', models.TextField()),
                ('download_url', models.TextField()),
                ('download_key', models.TextField(null=True)),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('Queued', 'Queued'),
                            ('Downloading', 'Downloading'),
                            ('Complete', 'Complete'),
                            ('Error', 'Error'),
                        ],
                        default='Queued',
                        max_length=128,
                    ),
                ),
                (
                    'status_change_date',
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ('error_message', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='MoveFromShare',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                (
                    'name',
                    models.TextField(
                        validators=[magicicada.filesync.managers.validate_name]
                    ),
                ),
                (
                    'kind',
                    models.CharField(
                        choices=[
                            ('File', 'File'),
                            ('Directory', 'Directory'),
                            ('Symlink', 'Symlink'),
                        ],
                        max_length=128,
                    ),
                ),
                (
                    'when_created',
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    'when_last_modified',
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    'status',
                    models.CharField(
                        choices=[('Dead', 'Dead'), ('Live', 'Live')],
                        default='Live',
                        max_length=128,
                    ),
                ),
                ('path', models.TextField()),
                ('mimetype', models.TextField()),
                ('public_uuid', models.UUIDField(null=True, unique=True)),
                ('generation', models.BigIntegerField(default=0)),
                ('generation_created', models.BigIntegerField(default=0)),
                ('share_id', models.UUIDField()),
                ('node_id', models.UUIDField()),
                (
                    'content_blob',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to='filesync.ContentBlob',
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='ResumableUpload',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                ('volume_path', models.TextField()),
                ('size', models.BigIntegerField()),
                (
                    'when_started',
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    'when_last_active',
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    'status',
                    models.CharField(
                        choices=[('Dead', 'Dead'), ('Live', 'Live')],
                        default='Live',
                        max_length=128,
                    ),
                ),
                ('storage_key', models.UUIDField()),
                ('part_count', models.BigIntegerField(default=0)),
                ('uploaded_bytes', models.BigIntegerField(default=0)),
                ('hash_context', models.BinaryField(null=True)),
                ('magic_hash_context', models.BinaryField(null=True)),
                ('crc_context', models.IntegerField(null=True)),
                (
                    'owner',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='Share',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                ('email', models.TextField(blank=True)),
                (
                    'name',
                    models.TextField(
                        validators=[magicicada.filesync.managers.validate_name]
                    ),
                ),
                ('accepted', models.BooleanField(default=False)),
                (
                    'access',
                    models.CharField(
                        choices=[('View', 'View'), ('Modify', 'Modify')],
                        max_length=128,
                    ),
                ),
                (
                    'when_shared',
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    'when_last_changed',
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    'status',
                    models.CharField(
                        choices=[('Dead', 'Dead'), ('Live', 'Live')],
                        default='Live',
                        max_length=128,
                    ),
                ),
                (
                    'shared_by',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='sharedby_folders',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'shared_to',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='sharedto_folders',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='StorageObject',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                (
                    'name',
                    models.TextField(
                        validators=[magicicada.filesync.managers.validate_name]
                    ),
                ),
                (
                    'kind',
                    models.CharField(
                        choices=[
                            ('File', 'File'),
                            ('Directory', 'Directory'),
                            ('Symlink', 'Symlink'),
                        ],
                        max_length=128,
                    ),
                ),
                (
                    'when_created',
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    'when_last_modified',
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    'status',
                    models.CharField(
                        choices=[('Dead', 'Dead'), ('Live', 'Live')],
                        default='Live',
                        max_length=128,
                    ),
                ),
                ('path', models.TextField()),
                ('mimetype', models.TextField()),
                ('public_uuid', models.UUIDField(null=True, unique=True)),
                ('generation', models.BigIntegerField(default=0)),
                ('generation_created', models.BigIntegerField(default=0)),
                (
                    'content_blob',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to='filesync.ContentBlob',
                    ),
                ),
                (
                    'parent',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='children',
                        to='filesync.StorageObject',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UploadJob',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('chunk_count', models.IntegerField(default=0)),
                ('hash_hint', models.BinaryField()),
                ('crc32_hint', models.BigIntegerField()),
                (
                    'when_started',
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    'when_last_active',
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    'status',
                    models.CharField(
                        choices=[('Dead', 'Dead'), ('Live', 'Live')],
                        default='Live',
                        max_length=128,
                    ),
                ),
                ('multipart_key', models.UUIDField(null=True)),
                ('uploaded_bytes', models.BigIntegerField(default=0)),
                (
                    'node',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='filesync.StorageObject',
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='UserVolume',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                (
                    'path',
                    models.TextField(
                        validators=[
                            magicicada.filesync.managers.validate_volume_path
                        ]
                    ),
                ),
                (
                    'when_created',
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    'status',
                    models.CharField(
                        choices=[('Dead', 'Dead'), ('Live', 'Live')],
                        default='Live',
                        max_length=128,
                    ),
                ),
                ('generation', models.BigIntegerField(default=0)),
                (
                    'owner',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name='storageobject',
            name='volume',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='filesync.UserVolume',
            ),
        ),
        migrations.AddField(
            model_name='share',
            name='subtree',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='filesync.StorageObject',
            ),
        ),
        migrations.AddField(
            model_name='movefromshare',
            name='old_parent',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='old_children',
                to='filesync.StorageObject',
            ),
        ),
        migrations.AddField(
            model_name='movefromshare',
            name='parent',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='children',
                to='filesync.MoveFromShare',
            ),
        ),
        migrations.AddField(
            model_name='movefromshare',
            name='volume',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='filesync.UserVolume',
            ),
        ),
        migrations.AddField(
            model_name='download',
            name='node',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='filesync.StorageObject',
            ),
        ),
        migrations.AddField(
            model_name='download',
            name='volume',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='filesync.UserVolume',
            ),
        ),
        migrations.AlterUniqueTogether(
            name='storageobject',
            unique_together=set([('volume', 'generation')]),
        ),
        migrations.AlterUniqueTogether(
            name='movefromshare',
            unique_together=set([('node_id', 'share_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='download',
            unique_together=set([('volume', 'file_path', 'download_url')]),
        ),
    ]
