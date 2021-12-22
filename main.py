
import sys
import datetime
import click
import requests
import json


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

URL_BASE = "http://localhost/WSConnectorREST"


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('-b', '--base', type=str, default=URL_BASE, show_default=True, help="Data Connector Service Base URL")
@click.option('-u', '--user', type=str, default='amis', show_default=True, help="User login")
@click.option('-p', '--password', default='amis', show_default=True, type=str,  help="User password")
@click.option('--pretty', type=bool, default=False, is_flag=True, show_default=True, help="print pretty formatted output")
@click.pass_context
def cli(ctx, base, user, password, pretty):
    """
    STAPRO Data Connector Client - tools for calling services through the REST API.

    This tools are intended for testing purposes only.
    """

    ctx.ensure_object(dict)
    ctx.obj.update({
        'base': base.rstrip('/'),
        'user': user,
        'password': password,
        'pretty': pretty,
    })


@cli.command('version')
@click.pass_context
def get_api_version(ctx):
    """
    Get software version information.
    """
    params = {
    }
    data = call_api(ctx.obj['base'] + '/GetWebServiceVersion', params=params, auth=(ctx.obj['user'], ctx.obj['password']))
    if ctx.obj['pretty']:
        print(json.dumps(json.loads(data), indent=4))
    else:
        print(data)


@cli.command('status')
@click.pass_context
def get_service_status(ctx):
    """
    Get service status information.
    """
    params = {
    }
    data = call_api(ctx.obj['base'] + '/GetWebServiceState', params=params, auth=(ctx.obj['user'], ctx.obj['password']))
    if ctx.obj['pretty']:
        print(json.dumps(json.loads(data), indent=4))
    else:
        print(data)


@cli.command('patsum')
@click.option('--rc', type=str, required=True, show_default=True, help="Patient ID - rodne cislo")
@click.option('--from', 'from_date', type=click.DateTime(), help="Clinical events younger than this day [default: 1970-01-01]")
@click.option('--to', 'to_date', type=click.DateTime(), help="Clinical events older than this day [default: current()]")
@click.pass_context
def get_patient_summary(ctx, rc, from_date, to_date):
    """
    Get Patient Emergency Information Summary.
    """
    params = {
        'RodneCislo': rc,
        'DateFrom': (from_date or datetime.datetime(1970, 1, 1)).replace(microsecond=0).isoformat(),
        'DateTo': (to_date or datetime.datetime.now()).replace(microsecond=0).isoformat(),
    }
    data = call_api(ctx.obj['base'] + '/PatientInfo', data=params, auth=(ctx.obj['user'], ctx.obj['password']))
    if ctx.obj['pretty']:
        print(json.dumps(json.loads(data), indent=4))
    else:
        print(data)


def call_api(url, *, data=None, headers=None, auth=(), accept_codes=()):
    try:
        resp = requests.post(url, json=data, headers=headers)
        # print(resp.request.method, resp.request.url)
        # print(*[f"{k}: {v}" for k, v in resp.request.headers.items()], sep='\n')
        # print()
        # print(resp.request.body.decode())

        if resp.status_code in accept_codes:
            return None
        # print(">>> ", resp.text, " ... ", resp.reason)
        resp.raise_for_status()
        return resp.text
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    cli(obj={})     # pylint: disable=unexpected-keyword-arg, no-value-for-parameter
