from invoke import task, run


@task
def release(version):
    run('git tag -s "{}"'.format(version))
    run('python setup.py sdist bdist_wheel')
    run('twine upload/alchimia-{}*'.format(version))
