# Archivatix
> Archive FTP files / folders that are too old

[![Code Climate](https://codeclimate.com/github/codeclimate/codeclimate/badges/gpa.svg)](https://codeclimate.com/github/davidbonachera/Archivatix)

![header](https://user-images.githubusercontent.com/1730152/82173392-a5904780-98ff-11ea-902b-d1ae711c8ec9.png)

The idea is simple, this script will find all your files and apply rules to know if a file should be selected.

For example, all files that are older than 2020-01-01 which are bigger than 0.01 MB would be selected by default.

From that point there's two behaviors:
- The first one is to put all those files in a yearly folder (files from 2019 will 
be grouped in one folder). 
- The second one would be to delete all those selected files.

## Usage

1. Rename `config.yaml.dist` to `config.yaml`
2. Edit and add as many FTP you want.
3. Define your archiving rules within the archivatix.py
4. Run the script within the venv:
```sh
python archivatix.py
```

## Release History

* 0.1.0
    * The first proper release

## Meta

David Bonachera – [@CarreTriangle](https://twitter.com/CarreTriangle)

Distributed under the MIT license. See ``LICENSE`` for more information.

## Contributing

1. Fork it (<https://github.com/yourname/yourproject/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request
