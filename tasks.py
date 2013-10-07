from invoke import task, run


@task
def release(version):
    """
    Version should be a string like '0.4' or '1.0'
    """
    run('git tag -s "{}"'.format(version))
    run('python setup.py sdist bdist_wheel')
    run('twine upload -s dist/alchimia-{}*'.format(version))
