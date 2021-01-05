import json
from dataclasses import dataclass
from typing import List, Dict
import re

import requests
import click
from bs4 import BeautifulSoup

@dataclass
class Config:

    @dataclass
    class Crawl:
        url: str
        selector: str
        regex: str

        @staticmethod
        def from_json(data: Dict):
            return Config.Crawl(data['url'], data['selector'], data['regex'])

    crawls: List[Crawl]
    slack_webhook: str
    slack_channel: str

    @staticmethod
    def from_json(data: Dict):
        return Config(
            [Config.Crawl.from_json(crl) for crl in data['crawls']],
            data['slack_webhook'],
            data['slack_channel'],
        )


def slack_notify(webhook: str, channel: str, text: str):
    payload = {'text': text, 'channel': channel}
    res = requests.post(webhook, data=json.dumps(payload))
    res.raise_for_status()

def crawl2slack(config: Config, crawl: Config.Crawl):
    regex = re.compile(crawl.regex)
    res = requests.get(crawl.url)
    res.raise_for_status()
    bs = BeautifulSoup(res.text, 'html.parser')
    for element in bs.select(crawl.selector):
        if element.find(string=regex):
            slack_notify(
                config.slack_webhook, config.slack_channel,
                f'Matched!! URL: {crawl.url}, Selector: {crawl.selector}, RegEx: {crawl.regex}'
            )
            return


@click.command(context_settings={'auto_envvar_prefix': 'CRAWL2SLACK'})
@click.option('--config', help='Config json location', type=str, required=True, show_envvar=True)
def main(config: str):
    cfg = Config.from_json(json.load(open(config)))
    for crawl in cfg.crawls:
        crawl2slack(cfg, crawl)

if __name__ == '__main__':
    main()
