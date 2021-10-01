# Defectio

![revolt-api](https://img.shields.io/npm/v/revolt-api?label=Revolt%20API) [![Documentation Status](https://readthedocs.org/projects/defectio/badge/?version=latest)](https://defectio.readthedocs.io/en/latest/?badge=latest) [![All Contributors](https://img.shields.io/badge/all_contributors-7-orange.svg)](#contributors-)


**defectio** is a direct implementation of the entire Revolt API and provides a way to authenticate and start communicating with Revolt servers. Similar interface to discord.py

## Example Usage

```python3
import defectio

client = defectio.Client()


@client.event
async def on_ready():
    print("We have logged in.")


@client.event
async def on_message(message: defectio.Message):
    if message.author == client.user:
        return
    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")


client.run("your token here")
```

## Contribute

Join our server [here](https://app.revolt.chat/invite/FfbwgFDk)

## License

Licensed under an MIT license

Based on discord.py by Rapptz [here](https://github.com/Rapptz/discord.py)

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://github.com/nixonjoshua98"><img src="https://avatars.githubusercontent.com/u/22799825?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Joshua Nixon</b></sub></a><br /><a href="https://github.com/Darkflame72/defectio/commits?author=nixonjoshua98" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/LimeProgramming"><img src="https://avatars.githubusercontent.com/u/29736217?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Adam</b></sub></a><br /><a href="https://github.com/Darkflame72/defectio/commits?author=LimeProgramming" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/jottew"><img src="https://avatars.githubusercontent.com/u/71946106?v=4?s=100" width="100px;" alt=""/><br /><sub><b>jotte</b></sub></a><br /><a href="https://github.com/Darkflame72/defectio/commits?author=jottew" title="Code">💻</a></td>
    <td align="center"><a href="https://insrt.uk"><img src="https://avatars.githubusercontent.com/u/38285861?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Paul Makles</b></sub></a><br /><a href="https://github.com/Darkflame72/defectio/issues?q=author%3Ainsertish" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/Cearaj"><img src="https://avatars.githubusercontent.com/u/75398448?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Cearaj</b></sub></a><br /><a href="https://github.com/Darkflame72/defectio/commits?author=Cearaj" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/jafreli"><img src="https://avatars.githubusercontent.com/u/31709372?v=4?s=100" width="100px;" alt=""/><br /><sub><b>jafreli</b></sub></a><br /><a href="https://github.com/Darkflame72/defectio/commits?author=jafreli" title="Code">💻</a></td>
    <td align="center"><a href="https://dark42ed.cf/"><img src="https://avatars.githubusercontent.com/u/74568473?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Dark42ed</b></sub></a><br /><a href="https://github.com/Darkflame72/defectio/commits?author=Dark42ed" title="Documentation">📖</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
