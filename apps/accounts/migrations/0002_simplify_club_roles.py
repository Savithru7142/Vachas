from django.db import migrations, models


def core_team_to_member(apps, schema_editor):
    ClubMembership = apps.get_model('accounts', 'ClubMembership')
    ClubMembership.objects.filter(role='CORE_TEAM').update(role='MEMBER')


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(core_team_to_member, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='clubmembership',
            name='role',
            field=models.CharField(
                choices=[('MEMBER', 'Member'), ('LEAD', 'Club Lead')],
                default='MEMBER',
                max_length=20,
            ),
        ),
    ]
