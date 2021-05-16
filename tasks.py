from invoke import task

@task
def start(ctx):
    ctx.run("python3 src/main.py")

@task
def test(ctx):
    ctx.run("pytest src")

@task
def coverage(ctx):
    ctx.run("coverage run --branch -m pytest src")

@task
def coverage_only_unit(ctx):
    ctx.run("coverage run --branch -m pytest src --ignore=./src/tests/integration/")

@task(coverage)
def coverage_report(ctx):
    ctx.run("coverage html")

@task(coverage_only_unit)
def coverage_report_only_unit(ctx):
    ctx.run("coverage html")

@task
def lint(ctx):
    ctx.run("pylint src")

@task
def format(ctx):
    ctx.run("autopep8 --in-place --recursive src")

@task
def init_database(ctx):
    ctx.run("python3 src/init_database.py")
