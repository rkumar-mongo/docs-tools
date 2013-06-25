from fabric.api import task, local, env, puts
from droopy.factory import DroopyFactory
from droopy.lang.english import English
import json

@task
def file(fn):
    env.input_file = fn

def report_statement(fn, test, number):
    puts("[stats]: '{0}' has a {1} of {2}".format(fn, test, number))

def _report(droopy):
    report_statement(env.input_file, 'coleman-liau', droopy.coleman_liau)
    report_statement(env.input_file, 'flesch-level', droopy.flesch_grade_level)
    report_statement(env.input_file, 'flesch-ease', droopy.flesch_reading_ease)
    report_statement(env.input_file, 'smog', droopy.smog)

@task
def report():
    with open(env.input_file, 'r') as f:
        document = f.read()

    droopy = DroopyFactory.create_full_droopy(document, English())

    _report(droopy)

@task
def jreport():
    with open(env.input_file, 'r') as f:
        text = json.loads(f.read())['text']

    droopy = DroopyFactory.create_full_droopy(text, English())

    _report(droopy)

